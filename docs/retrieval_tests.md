# Matriz de Pruebas de Recuperación Vectorial (Día 12)

**Objetivo:** Evaluar la precisión semántica y la relevancia del Top-1 y Top-K de fragmentos recuperados mediante ChromaDB y `gemini-embedding-001` sin generación aumentada.

---

## Tabla de Evaluación de Búsqueda Semántica

| # | Pregunta Técnica | Categoría Esperada | Documento Esperado | Primer Resultado Recuperado | ¿Es relevante? (Sí/No) | Observaciones |
| :---: | :--- | :--- | :--- | :--- | :---: | :--- |
| **1** | ¿Cuál es la tensión máxima de operación y la frecuencia de reloj del Arduino UNO R3? | Arduino | `A000066-datasheet.md` | *(A completar en ejecución de prueba)* | [ ] | Evaluar si recupera las especificaciones eléctricas de 5V y 16MHz. |
| **2** | ¿Cuáles son los registros de configuración del conversor analógico-digital (ADC) en el ATmega328P? | Arduino / AVR | `atmega328ds.pdf` o `A000066-datasheet.md` | *(A completar en ejecución de prueba)* | [ ] | Verificar presencia de `ADMUX`, `ADCSRA` y `ADCSRB`. |
| **3** | ¿Cuántos pines de entrada/salida digital y canales PWM posee la placa Arduino Mega 2560? | Arduino | `A000067-datasheet.md` | *(A completar en ejecución de prueba)* | [ ] | Verificar 54 pines I/O digitales y 15 salidas PWM. |
| **4** | ¿Cuál es el rango de voltaje de alimentación y los modos de bajo consumo del SoC ESP32? | ESP32 | `esp32_datasheet_en.md` | *(A completar en ejecución de prueba)* | [ ] | Verificar rango de 3.0V a 3.6V y modos Deep-Sleep / Light-Sleep. |
| **5** | ¿Cuáles son las características principales del procesador y memoria de la Raspberry Pi Pico? | Raspberry Pi Pico | `RP-008307-DS-2-pico-datasheet.pdf` | *(A completar en ejecución de prueba)* | [ ] | Verificar Cortex-M0+ dual core y 264KB de SRAM interna. |
| **6** | ¿Cómo se configuran los bloques programables de entrada/salida (PIO) en el microcontrolador RP2040? | Raspberry Pi / RP2040 | `RP-008371-DS-1-rp2040-datasheet.pdf` | *(A completar en ejecución de prueba)* | [ ] | Verificar si el chunk recupera las máquinas de estado PIO0 y PIO1. |
| **7** | ¿Qué valor de resistencia de pull-up se recomienda para las líneas SDA y SCL en el protocolo I2C? | Protocolos | `UM10204.pdf` (I2C Manual) | *(A completar en ejecución de prueba)* | [ ] | Evaluar si recupera tablas de cálculo para 100kHz Standard y 400kHz Fast Mode. |
| **8** | ¿Cuáles son las diferencias entre los modos de polaridad y fase (CPOL y CPHA) en el bus SPI? | Protocolos | `sprugp1.pdf` o datasheets de microcontroladores | *(A completar en ejecución de prueba)* | [ ] | Verificar los cuatro modos de reloj SPI (Modo 0, 1, 2, 3). |
| **9** | ¿Cómo se calcula el registro de tasa de baudios (UBRR) para comunicación serial USART en microcontroladores AVR? | Arduino / Protocolos | `atmega328ds.pdf` | *(A completar en ejecución de prueba)* | [ ] | Comprobar que la fórmula $UBRR = \frac{f_{OSC}}{16 \times BAUD} - 1$ se mantenga unida en el chunk. |
| **10** | ¿Cuáles son los voltajes de saturación y límites de corriente del driver de potencia para motores paso a paso? | Drivers_Modulos / Electrónica | Datasheets de drivers o `tl5001a-q1.pdf` | *(A completar en ejecución de prueba)* | [ ] | Verificar límites de corriente por canal y requerimientos de disipación térmica. |

---

## Procedimiento de Ejecución de las Pruebas

1. Iniciar la sesión de búsqueda semántica con:
   ```bash
   python scripts/day12_semantic_search.py
   ```
   o mediante la CLI:
   ```bash
   python src/api/cli.py query "<Pregunta Técnica>" --top-k 5
   ```
2. Registrar el `chunk_id` y el extracto del primer resultado devuelto.
3. Evaluar si el texto contiene la respuesta técnica directa o el contexto mínimo suficiente.
4. Anotar la distancia L2 en las observaciones para calibrar el umbral de filtrado semántico.
