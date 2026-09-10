# Embedding Report

## Documento

- **Nombre:** A000066-datasheet.md
- **Ruta procesada:** `data/processed/arduino/A000066-datasheet.md`
- **Ruta original:** `data/raw/Microcontroladores_RAG_Documentacion/Arduino/A000066-datasheet.pdf`
- **Metadatos asociados:** `data/metadata/arduino/A000066-datasheet.json`
- **Tipo:** User Manual / Datasheet estructurado en Markdown

---

## Evaluación previa

- **Estado:** ✅ **APROBADO**
- **Observaciones:** 
  - Documento extraído y procesado previamente por `Document Engineer Agent`.
  - Ausencia de ruidos de OCR y formato técnico consistente.
  - Bloques de parámetros eléctricos, componentes clave y límites operativos preservados íntegramente.
  - Tablas de pinout (`JANALOG` y `JDIGITAL`) y conectores `ICSP` debidamente estructurados con delimitadores Markdown estándar.

---

## Validación de metadatos

```yaml
metadata:
  fabricante: Arduino S.r.l
  familia: Arduino Classic Family / AVR
  dispositivo: Arduino UNO R3 (ATmega328P / ATmega16U2)
  tipo_documento: User Manual / Datasheet
  versión: Rev. A000066
  fecha: 2024
  fuente: Documentación Oficial Arduino S.r.l
  categoría: Placa de desarrollo / Microcontrolador
```

*Estado de metadatos:* **COMPLETO Y VALIDADO** (verificado contra `data/metadata/arduino/A000066-datasheet.json`).

---

## Estrategia de chunking

- **Método:** Segmentación semántica orientada a hardware (`SemanticHardwareChunker`) con preservación de tablas y fusión de títulos huérfanos.
- **Tamaño base objetivo:** 800 caracteres (~200 tokens)
- **Overlap:** 150 caracteres
- **Política de tablas:** Umbral ampliado (hasta 1.5x) para evitar la mutilación de filas o pérdida de cabeceras en tablas de asignación de pines.
- **Inyección contextual:** Cada fragmento incluye el prefijo autocontenido `[Componente: Arduino UNO R3 | Categoría: Arduino]`.

### Desglose de chunks generados:
1. `A000066-datasheet.pdf_0` (807 chars): Información general, SKU, fabricante y especificaciones del procesador ATmega328P.
2. `A000066-datasheet.pdf_1` (556 chars): Coprocesador USB ATmega16U2 y componentes clave de topología (U1, U3, U5, Y1, D1, X1, X2).
3. `A000066-datasheet.pdf_2` (818 chars): Características eléctricas (VIN 6-20V, VUSB 5.5V, IOREF 5V, rieles +5V/+3V3, límites térmicos).
4. `A000066-datasheet.pdf_3` (330 chars): Mecanismos de protección (Power On Reset, Brown Out Detection, Watchdog Timer).
5. `A000066-datasheet.pdf_4` (815 chars): Interfaces de comunicación I (14x GPIO, 6x PWM, 6x ADC, 1x USART, 1x SPI, 1x I2C).
6. `A000066-datasheet.pdf_5` (563 chars): Interfaces de comunicación II (Comparador analógico, 2x Timers 8-bit, 1x Timer 16-bit).
7. `A000066-datasheet.pdf_6` (937 chars): Mapeo de pines conector JANALOG (Pines 1 a 14: NC, IOREF, Reset, +3V3, +5V, GND, VIN, A0-A5/I2C).
8. `A000066-datasheet.pdf_7` (1232 chars): Mapeo de pines conector JDIGITAL (Pines 1 a 18: D0-D13, UART, PWM, SPI SS/MOSI/MISO/SCK, AREF, I2C duplicado).
9. `A000066-datasheet.pdf_8` (221 chars): Conectores ICSP (ATmega328P) e ICSP1 (ATmega16U2).
10. `A000066-datasheet.pdf_9` (464 chars): Aplicaciones operativas (Educación, PLCs industriales, instrumentación de laboratorio).
11. `A000066-datasheet.pdf_10` (664 chars): Límites operativos (Tensiones extremas, degradación térmica de EEPROM/cristal, distancia de seguridad RF).
12. `A000066-datasheet.pdf_11` (455 chars): Observaciones técnicas y redundancias (Duplicidad chino/inglés, pines I2C repetidos, consumo PMax indefinido).

---

## Embeddings

- **Proveedor:** Google GenAI
- **Modelo:** `text-embedding-004`
- **Dimensión del vector:** 768
- **Cantidad de chunks generados:** 12
- **Colección ChromaDB destino:** `microcontrollers_kb`
- **Almacenamiento persistente:** `storage/vector_store/chroma.sqlite3`
- **Fecha de generación:** 2026-09-10

---

## Validación de calidad

- [x] **Completitud:** Todos los fragmentos poseen información autocontenida y encabezados de contexto de hardware.
- [x] **Fragmentos vacíos:** Ningún fragmento vacío (longitud mínima: 221 caracteres, máxima: 1232 caracteres).
- [x] **Integridad de tablas:** Las tablas críticas de conectores JANALOG y JDIGITAL se conservaron sin rupturas de fila ni pérdida de encabezados.
- [x] **Trazabilidad:** Metadatos enriquecidos asociados a cada vector en ChromaDB (`file_name`, `category`, `component`).
- [x] **Validación de recuperación semántica:** Prueba de similitud vectorial ejecutada exitosamente:
  - *Query de prueba:* `"Cuáles son los pines I2C y entradas analógicas del Arduino UNO R3?"`
  - *Resultados recuperados:* Chunks `A000066-datasheet.pdf_7`, `A000066-datasheet.pdf_11` y `A000066-datasheet.pdf_6` en las tres primeras posiciones con correspondencia semántica exacta.

---

## Problemas encontrados

- Ninguno. El documento contaba con el preprocesamiento requerido y metadatos individuales completos.

---

## Criterio de aprobación

- [x] Extracción correcta y libre de errores
- [x] Metadatos completos y validados
- [x] Estrategia de chunking definida y optimizada
- [x] Embeddings generados e indexados correctamente
- [x] Reporte de validación emitido

**Dictamen final:** ✅ **APROBADO PARA RECUPERACIÓN SEMÁNTICA (RAG READY)**
