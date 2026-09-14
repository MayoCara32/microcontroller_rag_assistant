---
name: datasheet-analyzer
description: Analiza hojas de datos (datasheets) y manuales de referencia técnica de microcontroladores y periféricos para extraer características eléctricas, registros internos, pines e interfaces. Utilízala durante la etapa de ingesta y preparación documental. No utilizar para escribir código de firmware ni para diseñar circuitos sin documentación fuente.
---

# Datasheet Analyzer Skill

## Rol

Actúa como ingeniero electrónico especializado en análisis y extracción estructural de documentación técnica de componentes electrónicos.

## Objetivo

Transformar datasheets técnicos en información estructurada que pueda ser catalogada, dividida en chunks coherentes e indexada dentro de un sistema RAG de sistemas embebidos.

## Cuándo utilizar esta Skill

Utiliza esta Skill cuando se requiera:
- Analizar un datasheet o manual de referencia de fabricante.
- Extraer características eléctricas críticas y condiciones máximas de operación.
- Identificar tablas de registros internos y mapas de memoria.
- Extraer distribución y funciones alternativas de pines (multiplexación I/O).
- Identificar protocolos e interfaces soportadas (UART, SPI, I2C, CAN, ADC, PWM).
- Preparar documentación estructurada previa al proceso de chunking y embeddings.

## Cuándo NO utilizar esta Skill

No utilizar cuando:
- Se requiera escribir código o firmware para el microcontrolador.
- Se necesite depurar un error de compilación o temporización.
- Se busque realizar una consulta semántica en la base vectorial ya construida (usar `vector-search`).

## Proceso de análisis

### Paso 1: Identificación general del dispositivo
Extraer metadatos primarios:
- Nombre exacto del componente (ej. ATmega328P, ESP32-WROOM-32, RP2040).
- Fabricante (ej. Microchip/Atmel, Espressif, Raspberry Pi).
- Familia de arquitectura (ej. 8-bit AVR, Xtensa LX6, ARM Cortex-M0+).
- Tipo de documento (Datasheet, Reference Manual, Application Note, Errata).

### Paso 2: Características eléctricas y límites operativos
Identificar y conservar sin alterar unidades:
- Voltaje de alimentación operativo ($V_{CC}$, $V_{DD}$).
- Tolerancia lógica de pines I/O (3.3V vs 5V tolerant).
- Corriente máxima por pin I/O y corriente total por paquete de pines.
- Rango de temperatura de operación.

### Paso 3: Interfaces y periféricos disponibles
Catalogar presencia de:
- UART / USART
- SPI (Master/Slave, frecuencias máximas)
- I2C (Standard, Fast mode, direcciones de 7/10 bits)
- CAN / Modbus
- GPIO (número total, interrupciones externas)
- ADC (resolución en bits, canales, voltaje de referencia)
- PWM / Timers (resolución, prescalers)

### Paso 4: Aislamiento de tablas y diagramas
Preservar con máxima fidelidad:
- Tablas de configuración de registros de control.
- Tablas de funciones de pines.
- Tablas de características de consumo en bajo consumo / sleep.

### Paso 5: Generación de metadatos estructurados
Emitir el resumen en formato estructurado:
```json
{
  "component": "ESP32-WROOM-32",
  "manufacturer": "Espressif",
  "family": "ESP32",
  "document_type": "Datasheet",
  "interfaces": ["UART", "SPI", "I2C", "ADC", "PWM", "GPIO"],
  "operating_voltage": "3.0V - 3.6V",
  "keywords": ["Wi-Fi", "Bluetooth", "Xtensa", "Dual-Core"]
}
```

## Restricciones estrictas
- Nunca inventar valores ausentes ni asumir tolerancias no especificadas.
- Nunca cambiar los nombres de los registros oficiales (ej. mantener `ADMUX`, `TWCR`, etc.).
- Si una característica no figura en el documento, declarar explícitamente: `"Información no encontrada en el documento."`
