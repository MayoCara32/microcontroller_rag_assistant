"""Script de evaluación de la búsqueda híbrida vs densa y léxica (Día 17)."""
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.retrieval.retrieval_service import RetrievalService

TEST_QUERIES = [
    # 1. Conceptuales
    {"query": "¿Qué es PWM?", "type": "conceptual", "terms": ["pwm", "pulse", "width", "modulation"]},
    {"query": "¿Qué es el bus I2C?", "type": "conceptual", "terms": ["i2c", "twi", "sda", "scl"]},
    {"query": "¿Qué es la comunicación SPI?", "type": "conceptual", "terms": ["spi", "miso", "mosi", "sck"]},
    {"query": "¿Qué es un temporizador o timer?", "type": "conceptual", "terms": ["timer", "prescaler", "counter"]},
    {"query": "¿Qué es la memoria EEPROM en AVR?", "type": "conceptual", "terms": ["eeprom", "flash", "memory"]},

    # 2. Técnicas
    {"query": "¿Cómo configurar UART ESP32?", "type": "tecnica", "terms": ["uart", "esp32", "baud", "tx", "rx"]},
    {"query": "¿Cómo funciona el ADC en ATmega328P?", "type": "tecnica", "terms": ["adc", "atmega328p", "analog", "channel"]},
    {"query": "¿Cómo usar interrupciones externas en RP2040?", "type": "tecnica", "terms": ["interrupt", "gpio", "rp2040", "handler"]},
    {"query": "Configuración de canal DMA en ESP32", "type": "tecnica", "terms": ["dma", "esp32", "channel", "buffer"]},
    {"query": "Modos de bajo consumo Deep Sleep ESP32", "type": "tecnica", "terms": ["sleep", "deep", "esp32", "power"]},

    # 3. Exactas
    {"query": "¿Qué registro controla ADC en ATmega328P?", "type": "exacta", "terms": ["adcsra", "admux", "adc", "atmega328p"]},
    {"query": "ADCSRA ATmega328P", "type": "exacta", "terms": ["adcsra", "atmega328p"]},
    {"query": "GPIO34 ESP32 ADC", "type": "exacta", "terms": ["gpio34", "esp32", "adc"]},
    {"query": "TWBR I2C prescaler", "type": "exacta", "terms": ["twbr", "twi", "i2c", "prescaler"]},
    {"query": "PORTB DDRB PINB ATmega328P", "type": "exacta", "terms": ["portb", "ddrb", "pinb", "atmega328p"]},

    # 4. Drivers
    {"query": "TB6600 ENA DIR driver motor paso a paso", "type": "driver", "terms": ["tb6600", "ena", "dir", "stepper"]},
    {"query": "L298N puente H motor DC control", "type": "driver", "terms": ["l298n", "bridge", "motor", "pwm"]},
    {"query": "MAX485 RS485 transceiver comunicación", "type": "driver", "terms": ["max485", "rs485", "transceiver"]},
    {"query": "MPU6050 acelerómetro giroscopio I2C", "type": "driver", "terms": ["mpu6050", "i2c", "gyro", "accel"]},
    {"query": "ESP32 Wi-Fi Bluetooth driver", "type": "driver", "terms": ["wifi", "bluetooth", "esp32", "phy"]}
]


def evaluate_retrieval():
    service = RetrievalService()
    results_summary = []

    print("Ejecutando evaluación de 20 consultas en 3 modos (dense, keyword, hybrid)...\n")

    for idx, item in enumerate(TEST_QUERIES, start=1):
        q = item["query"]
        q_type = item["type"]
        expected_terms = item["terms"]

        eval_modes = {}
        for mode in ["dense", "keyword", "hybrid"]:
            retrieved = service.search(query=q, top_k=5, mode=mode)
            if not retrieved:
                precision = 0.0
                recall = 0.0
            else:
                relevant_count = 0
                terms_found = set()
                for doc in retrieved:
                    text = (doc.get("text") or doc.get("texto", "")).lower()
                    has_match = False
                    for term in expected_terms:
                        if term in text:
                            terms_found.add(term)
                            has_match = True
                    if has_match:
                        relevant_count += 1

                precision = round(relevant_count / len(retrieved), 2)
                recall = round(len(terms_found) / len(expected_terms), 2)

            eval_modes[mode] = {
                "precision": precision,
                "recall": recall
            }

        entry = {
            "id": idx,
            "query": q,
            "type": q_type,
            "dense": eval_modes["dense"],
            "keyword": eval_modes["keyword"],
            "hybrid": eval_modes["hybrid"]
        }
        results_summary.append(entry)
        print(f"[{idx}/20] '{q}' ({q_type}) -> Dense: P={eval_modes['dense']['precision']} R={eval_modes['dense']['recall']} | Keyword: P={eval_modes['keyword']['precision']} R={eval_modes['keyword']['recall']} | Hybrid: P={eval_modes['hybrid']['precision']} R={eval_modes['hybrid']['recall']}")

    out_file = BASE_DIR / "evaluation" / "hybrid_comparison.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results_summary, f, indent=2, ensure_ascii=False)

    print(f"\nEvaluación guardada exitosamente en {out_file}")


if __name__ == "__main__":
    evaluate_retrieval()
