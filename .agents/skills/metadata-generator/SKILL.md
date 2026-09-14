---
name: metadata-generator
description: Extrae y formaliza metadatos técnicos (fabricante, familia, modelo, interfaces, voltaje, categoría) a partir de documentos técnicos para enriquecer los chunks en ChromaDB. Utilízala durante la etapa de ingesta previa a la indexación. No utilizar para generar respuestas de consulta al usuario final.
---

# Metadata Generator Skill

## Rol

Actúa como especialista en catalogación y extracción de metadatos de sistemas embebidos y hardware.

## Objetivo

Garantizar que todo documento técnico y fragmento (chunk) cuente con metadatos descriptivos normalizados que permitan filtrar con precisión en ChromaDB y rastrear el origen de cualquier información recuperada.

## Cuándo Utilizar esta Skill

Utilizar esta Skill cuando:
- Se procese un nuevo documento en `data/processed/`.
- Se deban generar o enriquecer los archivos JSON de metadatos en `data/metadata/`.
- Se requiera asociar metadatos consistentes a los chunks creados por `rag-chunk-designer`.

## Cuándo NO Utilizar esta Skill

No utilizar cuando:
- Se requiera realizar una búsqueda por similitud vectorial (usar `vector-search`).
- Se esté limpiando ruido del documento (usar `technical-document-cleaner`).

## Esquema Estándar de Metadatos

Cada archivo analizado debe producir un diccionario con la siguiente estructura formal:

```json
{
  "file_name": "A000066-datasheet.pdf",
  "source_path": "data/raw/Arduino/A000066-datasheet.pdf",
  "category": "Arduino",
  "family": "AVR",
  "component": "ATmega328P",
  "manufacturer": "Microchip",
  "document_type": "Datasheet",
  "interfaces": ["UART", "SPI", "I2C", "ADC", "PWM", "GPIO"],
  "operating_voltage": "5V",
  "keywords": ["Arduino UNO", "ATmega328P", "8-bit", "AVR", "Bootloader"]
}
```

## Reglas de Inferencia y Asignación

1. **Jerarquía de Componentes:**
   - Si el documento es de una placa de desarrollo (ej. Arduino UNO R3), asociar tanto la placa (`Arduino UNO`) como el microcontrolador principal (`ATmega328P`).
   - Si es un SoC (ej. ESP32-WROOM-32), asociar fabricante (`Espressif`) y familia (`ESP32`).
   - Si es Raspberry Pi Pico, asociar microcontrolador (`RP2040` o `RP2350`).
2. **Detección Determinista de Interfaces:**
   - Escanear palabras clave normalizadas: `I2C`, `SPI`, `UART`, `USART`, `CAN`, `ADC`, `DAC`, `PWM`, `GPIO`, `USB`, `I2S`.
3. **Manejo de Valores No Determinables:**
   - Si el fabricante o la versión no pueden determinarse inequívocamente en el texto, asignar cadena vacía `""` o `"unknown"`.
   - **Nunca** inventar datos de modelos, familias o voltajes que no figuren en la fuente.
