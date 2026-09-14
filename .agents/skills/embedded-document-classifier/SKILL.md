---
name: embedded-document-classifier
description: Clasifica documentos técnicos de sistemas embebidos en categorías jerárquicas estandarizadas (microcontroladores, protocolos, periféricos, electrónica analógica/digital). Utilízala al catalogar nuevos archivos en data/raw o data/processed. No utilizar para segmentar texto ni para calcular embeddings vectoriales.
---

# Embedded Document Classifier Skill

## Rol

Actúa como arquitecto de información especializado en taxonomía y catalogación de documentación técnica de ingeniería electrónica y sistemas embebidos.

## Objetivo

Clasificar documentos técnicos en categorías y metadatos jerárquicos coherentes para facilitar el filtrado y la recuperación semántica dentro de la base vectorial.

## Cuándo utilizar esta Skill

Utiliza esta Skill cuando:
- Se incorporen nuevos documentos a `data/raw/` o `data/processed/`.
- Se deba determinar la categoría, subcategoría y dispositivo objetivo de un archivo.
- Se preparen metadatos que acompañarán a los chunks en ChromaDB.

## Cuándo NO utilizar esta Skill

No utilizar cuando:
- Se deba limpiar ruido visual o encabezados (usar `technical-document-cleaner`).
- Se requiera dividir el texto en fragmentos (usar `rag-chunk-designer`).
- Se ejecute una búsqueda de consulta de usuario (usar `vector-search`).

## Taxonomía de Categorías Principales

1. **Microcontroladores y SoCs:**
   - Arduino (AVR: ATmega328P, ATmega2560, etc.)
   - ESP32 / ESP8266 (Xtensa, RISC-V)
   - Raspberry Pi Pico (RP2040, RP2350, ARM Cortex-M0+/M33)
   - STM32 (ARM Cortex-M)
2. **Protocolos de Comunicación:**
   - Seriales síncronos/asíncronos: UART, USART, SPI, I2C
   - Industriales y automotrices: CAN Bus, Modbus RTU/TCP, RS-485, LIN
3. **Módulos y Periféricos:**
   - Convertidores: ADC, DAC
   - Temporizadores y moduladores: Hardware Timers, PWM, Watchdog
   - Controladores de potencia: Drivers de motor (H-Bridge, ULN2003, L298N)
   - Sensores y actuadores (temperatura, I2C displays, IMUs)

## Proceso de Clasificación

1. **Inspección de metadatos de archivo:** Analizar nombre del archivo, fabricante y portada.
2. **Validación de contenido real:** Buscar palabras clave, nombres de registros y diagramas para confirmar el tema real (no fiarse únicamente del nombre del archivo).
3. **Generación de esquema de clasificación:**
```json
{
  "document": "esp32_datasheet_en.pdf",
  "category": "ESP32",
  "subcategory": "Microcontrollers",
  "device": "ESP32",
  "family": "Xtensa LX6",
  "topics": ["Wi-Fi", "Bluetooth", "ADC", "GPIO", "Power Management"]
}
```

## Restricciones
- No clasificar nunca basándose únicamente en la extensión o el título; validar el contenido.
- Mantener nombres de categorías estandarizados para que los filtros de ChromaDB coincidan exactamente.
