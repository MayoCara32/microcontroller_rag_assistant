"""Pruebas unitarias e integrales para Metadata Filtering (Día 16)."""
import pytest
from src.retrieval.query_analyzer import QueryAnalyzer
from src.retrieval.filter_builder import MetadataFilterBuilder
from src.retrieval.dense_retriever import DenseRetriever
from src.retrieval.retrieval_service import RetrievalService
from src.agents.orchestrator import RAGOrchestrator


@pytest.fixture
def analyzer():
    return QueryAnalyzer()


@pytest.fixture
def builder():
    return MetadataFilterBuilder()


# =========================================================================
# 20 CONSULTAS TÉCNICAS DISTRIBUIDAS (Arduino: 5, ESP32: 5, RPi: 3, Protocolos: 4, Drivers: 3)
# =========================================================================

QUERIES_20_DATASET = [
    # --- ARDUINO (5) ---
    {
        "category": "Arduino",
        "question": "¿Cuál es el voltaje de alimentación recomendado para la placa Arduino Uno R3?",
        "expected_entity_key": "hardware_family",
        "expected_entity_val": "Arduino",
        "expected_filter": {"category": "Arduino"},
        "expected_doc": "A000066-datasheet.pdf"
    },
    {
        "category": "Arduino",
        "question": "¿Cuántos pines digitales y canales PWM tiene la placa Arduino Mega 2560 Rev3?",
        "expected_entity_key": "hardware_family",
        "expected_entity_val": "Arduino",
        "expected_filter": {"category": "Arduino"},
        "expected_doc": "A000067-datasheet.pdf"
    },
    {
        "category": "Arduino",
        "question": "¿Cuál es el rango de voltaje y frecuencia máxima del microcontrolador ATmega328P?",
        "expected_entity_key": "hardware_family",
        "expected_entity_val": "Arduino",
        "expected_filter": {"category": "Arduino"},
        "expected_doc": "atmega328ds.pdf"
    },
    {
        "category": "Arduino",
        "question": "¿Cuánta memoria Flash, SRAM y EEPROM posee el microcontrolador ATmega2560?",
        "expected_entity_key": "hardware_family",
        "expected_entity_val": "Arduino",
        "expected_filter": {"category": "Arduino"},
        "expected_doc": "atmel-2549-8-bit-avr-microcontroller-atmega640-1280-1281-2560-2561_datasheet.pdf"
    },
    {
        "category": "Arduino",
        "question": "¿Cuánto espacio de memoria Flash reserva el bootloader en Arduino Uno ATmega328P?",
        "expected_entity_key": "hardware_family",
        "expected_entity_val": "Arduino",
        "expected_filter": {"category": "Arduino"},
        "expected_doc": "A000066-datasheet.pdf"
    },

    # --- ESP32 (5) ---
    {
        "category": "ESP32",
        "question": "¿Cuántos bits de resolución tiene el conversor ADC del SoC ESP32?",
        "expected_entity_key": "hardware_family",
        "expected_entity_val": "ESP32",
        "expected_filter": {"category": "ESP32"},
        "expected_doc": "esp32_datasheet_en.pdf"
    },
    {
        "category": "ESP32",
        "question": "¿Qué aceleradores criptográficos por hardware incorpora el SoC ESP32?",
        "expected_entity_key": "hardware_family",
        "expected_entity_val": "ESP32",
        "expected_filter": {"category": "ESP32"},
        "expected_doc": "esp32_technical_reference_manual_en.pdf"
    },
    {
        "category": "ESP32",
        "question": "¿Qué memoria Flash SPI integra el encapsulado SiP ESP32-PICO?",
        "expected_entity_key": "hardware_family",
        "expected_entity_val": "ESP32",
        "expected_filter": {"category": "ESP32"},
        "expected_doc": "esp32-pico_series_datasheet_en.pdf"
    },
    {
        "category": "ESP32",
        "question": "¿Cuáles son los requerimientos de corriente mínima de 3.3V del ESP32?",
        "expected_entity_key": "hardware_family",
        "expected_entity_val": "ESP32",
        "expected_filter": {"category": "ESP32"},
        "expected_doc": "esp-hardware-design-guidelines-en-master-esp32.pdf"
    },
    {
        "category": "ESP32",
        "question": "¿Cuál es la frecuencia máxima del núcleo Xtensa LX6 dual-core en ESP32?",
        "expected_entity_key": "hardware_family",
        "expected_entity_val": "ESP32",
        "expected_filter": {"category": "ESP32"},
        "expected_doc": "esp32_datasheet_en.pdf"
    },

    # --- RASPBERRY PI (3) ---
    {
        "category": "Raspberry_Pi",
        "question": "¿Cuál es el rango de voltaje aceptado en el pin VSYS de la placa Raspberry Pi Pico?",
        "expected_entity_key": "hardware_family",
        "expected_entity_val": "Raspberry Pi",
        "expected_filter": {"category": "Raspberry_Pi"},
        "expected_doc": "RP-008307-DS-2-pico-datasheet.pdf"
    },
    {
        "category": "Raspberry_Pi",
        "question": "¿Cuántos núcleos ARM Cortex-M0+ y cuánta memoria SRAM tiene el RP2040?",
        "expected_entity_key": "hardware_family",
        "expected_entity_val": "Raspberry Pi",
        "expected_filter": {"category": "Raspberry_Pi"},
        "expected_doc": "RP-008371-DS-1-rp2040-datasheet.pdf"
    },
    {
        "category": "Raspberry_Pi",
        "question": "¿Qué biblioteca del SDK de Raspberry Pi Pico se utiliza para controlar pines GPIO?",
        "expected_entity_key": "hardware_family",
        "expected_entity_val": "Raspberry Pi",
        "expected_filter": {"category": "Raspberry_Pi"},
        "expected_doc": "RP-009085-KB-2-raspberry-pi-pico-c-sdk.pdf"
    },

    # --- PROTOCOLOS (4) ---
    {
        "category": "Protocolos",
        "question": "¿Cuáles son las velocidades máximas de transmisión en la especificación I2C UM10204?",
        "expected_entity_key": "component",
        "expected_entity_val": "I2C",
        "expected_filter": {"category": "Protocolos"},
        "expected_doc": "UM10204.pdf"
    },
    {
        "category": "Protocolos",
        "question": "¿Qué valor de resistencia de terminación se requiere en el bus CAN según ISO 11898?",
        "expected_entity_key": "component",
        "expected_entity_val": "CAN",
        "expected_filter": {"category": "Protocolos"},
        "expected_doc": "kb-canbus-en.md"
    },
    {
        "category": "Protocolos",
        "question": "¿Cuáles son los códigos de función principales en el protocolo MODBUS para lectura?",
        "expected_entity_key": "component",
        "expected_entity_val": "MODBUS",
        "expected_filter": {"category": "Protocolos"},
        "expected_doc": "modbusprotocolspecification.pdf"
    },
    {
        "category": "Protocolos",
        "question": "¿Cómo se definen los cuatro modos de transmisión SPI según CPOL y CPHA?",
        "expected_entity_key": "component",
        "expected_entity_val": "SPI",
        "expected_filter": {"category": "Protocolos"},
        "expected_doc": "sboa621.pdf"
    },

    # --- DRIVERS / ELECTRÓNICA (3) ---
    {
        "category": "Electronica",
        "question": "¿Cuál es el rango de voltaje VCC del controlador PWM TL5001A-Q1 de Texas Instruments?",
        "expected_entity_key": "hardware_family",
        "expected_entity_val": "Texas Instruments",
        "expected_filter": {"$and": [{"category": "Electronica"}, {"component": "TL5001A-Q1"}]},
        "expected_doc": "tl5001a-q1.pdf"
    },
    {
        "category": "Electronica",
        "question": "¿Qué principios diferencian a un conversor ADC Flash de un conversor SAR?",
        "expected_entity_key": "component",
        "expected_entity_val": "ADC",
        "expected_filter": {"category": "Electronica"},
        "expected_doc": "note_1474198148.pdf"
    },
    {
        "category": "Electronica",
        "question": "¿Cómo afecta el prescaler a la frecuencia de desbordamiento en un temporizador de hardware (timers)?",
        "expected_entity_key": "component",
        "expected_entity_val": "Timers",
        "expected_filter": {"category": "Electronica"},
        "expected_doc": "L6-Timers-and-Interrupts.pdf"
    },
]


def test_20_queries_entity_extraction(analyzer, builder):
    """Verifica que las 20 consultas obligatorias extraigan metadatos y construyan filtros válidos."""
    assert len(QUERIES_20_DATASET) == 20

    for item in QUERIES_20_DATASET:
        q = item["question"]
        analysis = analyzer.analyze(q)
        assert bool(analysis), f"Fallo al analizar: {q}"
        assert item["expected_entity_key"] in analysis
        assert analysis[item["expected_entity_key"]] == item["expected_entity_val"]

        filt = builder.build_from_analysis(analysis)
        assert filt == item["expected_filter"], f"Filtro inesperado para '{q}': {filt} vs {item['expected_filter']}"


def test_query_analyzer_empty_and_generic(analyzer):
    """Verifica que consultas no técnicas devuelvan diccionario vacío."""
    assert analyzer.analyze("") == {}
    assert analyzer.analyze("   ") == {}
    assert analyzer.analyze("hola, ¿cómo estás hoy?") == {}
    assert analyzer.analyze("cuál es el sentido de la vida") == {}


def test_filter_builder_validation_and_operators(builder):
    """Verifica la validación de campos, valores y ensamblaje de operadores ChromaDB."""
    # Condición única
    f1 = builder.build_from_analysis({"hardware_family": "ESP32"})
    assert f1 == {"category": "ESP32"}

    # Múltiples condiciones combinadas con $and
    f2 = builder.build_filter(category="Arduino", manufacturer="Arduino S.r.l")
    assert f2 == {"$and": [{"category": "Arduino"}, {"manufacturer": "Arduino S.r.l"}]}

    # Categoría inexistente no debe incluirse
    f3 = builder.build_filter(category="NonExistentMcu")
    assert f3 is None

    # build_from_analysis con datos vacíos
    assert builder.build_from_analysis({}) is None
    assert builder.build_from_analysis(None) is None


def test_orchestrator_integration_with_filters():
    """Verifica que RAGOrchestrator aplique automáticamente los filtros sin romper el flujo."""
    orchestrator = RAGOrchestrator()
    res = orchestrator.execute_workflow(
        user_query="¿Cómo configurar UART en ESP32?",
        apply_automatic_filters=True
    )
    assert res["analysis"]["hardware_family"] == "ESP32"
    assert res["filters_applied"] == {"category": "ESP32"}
    assert res["chunks_retrieved"] > 0
    # Todos los chunks devueltos deben pertenecer estrictamente a la categoría ESP32
    for chunk in res["results"]:
        assert chunk["metadata"]["category"] == "ESP32"


def test_retrieval_service_filters_parameter():
    """Verifica que RetrievalService respete el parámetro filters=None y filters={"category": "Arduino"}."""
    retriever = RetrievalService()

    # Búsqueda sin filtros
    res_unfiltered = retriever.search("voltaje de alimentación", top_k=3, filters=None)
    assert len(res_unfiltered) > 0

    # Búsqueda con filtro estricto
    res_filtered = retriever.search("voltaje de alimentación", top_k=3, filters={"category": "Arduino"})
    assert len(res_filtered) > 0
    for r in res_filtered:
        assert r["metadata"]["category"] == "Arduino"
