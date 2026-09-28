# Día 16: Metadata Filtering en Sistemas RAG para Microcontroladores

## 1. Limitaciones del Vector Search Puro (Búsqueda Densa k-NN)

En sistemas RAG para ingeniería de hardware y sistemas embebidos, la búsqueda vectorial pura (`dense retrieval` mediante embeddings como `gemini-embedding-001`) enfrenta serias limitaciones inherentes a la alta simetría conceptual entre diferentes arquitecturas:

1. **Ambigüedad Transversal de Periféricos:** Conceptos como *UART*, *SPI*, *I2C*, *PWM*, *ADC* o *Timers* existen en prácticamente todos los microcontroladores (Arduino Uno ATmega328P, Arduino Mega ATmega2560, Espressif ESP32, Raspberry Pi RP2040) y en chips controladores dedicados (TL5001A, TI Keystone).
2. **Falsos Positivos Inter-Plataforma:** Al consultar *"¿Cómo configurar el bus UART a 115200 baudios en ESP32?"*, un modelo de embeddings puro enfocado en la semántica de comunicación serial puede otorgar distancias vectoriales muy cortas a fragmentos de las hojas de datos de Texas Instruments (`sprugp1.pdf`) o Microchip AVR (`atmega328ds.pdf`), desplazando los fragmentos pertinentes del manual de ESP32 (`esp32_technical_reference_manual_en.pdf`).
3. **Pérdida de Precisión (Pollution of Context Window):** Cuando fragmentos de diferentes fabricantes se mezclan en el Top-K recuperado, el LLM generador corre el riesgo de alucinar registros de una arquitectura en el código de otra (ej. intentar configurar registros `UBRR0` de AVR en un SoC ESP32).

---

## 2. ¿Qué es Metadata?

La metadata (metadatos) representa atributos estructurados y contextuales asociados a cada fragmento documental (`chunk`) almacenado en el almacén vectorial. Mientras que el vector captura la semántica del texto, los metadatos capturan la taxonomía y procedencia del dato:

* **Categoría Jerárquica (`category`):** Plataforma global (`Arduino`, `ESP32`, `Raspberry_Pi`, `Protocolos`, `Electronica`).
* **Componente Específico (`component`):** Identificador del dispositivo (`Arduino UNO R3`, `ESP32 SoC`, `RP2040 Microcontroller`, `TL5001A-Q1`).
* **Familia de Procesador (`family`):** Arquitectura (`AVR / Arduino UNO`, `ESP32 Series`, `RP2040 Silicon`).
* **Fabricante (`manufacturer`):** Empresa u organización emisora (`Arduino S.r.l`, `Espressif Systems`, `Raspberry Pi Ltd`, `Texas Instruments`).
* **Archivo Fuente (`file_name`):** Trazabilidad al documento exacto (`A000066-datasheet.pdf`, `esp32_datasheet_en.pdf`).
* **Interfaces Disponibles (`interfaces`):** Lista de buses y protocolos físicos (`UART, SPI, I2C, GPIO, ADC, PWM`).

---

## 3. Diferencia entre Búsqueda Semántica Pura y Filtrada

| Dimensión | Búsqueda Semántica Pura | Búsqueda con Metadata Filtering |
| :--- | :--- | :--- |
| **Espacio de Búsqueda** | Todo el corpus vectorial (286 chunks). | Subconjunto pre-restringido por condiciones booleanas. |
| **Criterio de Selección** | Distancia métrica L2 o similitud coseno. | Filtro lógico (`where`) + Proximidad métrica sobre el subconjunto. |
| **Control de Falsos Positivos** | Bajo (depende de la discriminación del embedding). | Muy Alto (elimina candidatos fuera del dominio). |
| **Retrieval Precision** | Moderada (~55% - 65% en corpus homogéneo). | Alta (>85% - 95% al aislar familia y dispositivo). |
| **Riesgo Operativo** | Ruido e interferencia de otras plataformas. | Si el filtro es excesivamente estricto, riesgo de reducir Recall. |

---

## 4. Arquitectura Implementada

El pipeline desacoplado implementado en el Día 16 introduce dos componentes esenciales previos al `RetrievalService`:

```text
Usuario
   ↓ (Pregunta: "¿Cómo configurar UART en ESP32?")
Query Analyzer (src/retrieval/query_analyzer.py)
   ↓ (Entidades: {hardware_family: "ESP32", component: "UART"})
Metadata Filter Builder (src/retrieval/filter_builder.py)
   ↓ (Filtro ChromaDB: {"category": "ESP32"})
Retrieval Service / DenseRetriever (src/retrieval/retrieval_service.py)
   ↓ (ChromaDB query con `where={"category": "ESP32"}`)
Top-K Chunks Relevantes (100% pertenecientes a ESP32)
   ↓
Prompt Builder (src/generation/prompt_builder.py)
   ↓
Gemini Client / Response Generator (src/generation/response_generator.py)
   ↓
Respuesta Precisa y Fundamentada
```

### Componentes Clave:
1. **`QueryAnalyzer` (`src/retrieval/query_analyzer.py`):**
   - Extrae entidades técnicas (familia, placa, componentes, interfaces, fabricante, dominio).
   - No interactúa con la base de datos ni altera embeddings. Si la consulta es genérica o no técnica, retorna `{}`.
2. **`MetadataFilterBuilder` (`src/retrieval/filter_builder.py`):**
   - Valida que los campos pertenezcan al esquema real de ChromaDB (`VALID_CHROMA_FIELDS`).
   - Mapea entidades lógicas a categorías canónicas (`HARDWARE_TO_CATEGORY`).
   - Ensambla operadores `$and` cuando existen múltiples restricciones.
   - Previene filtros contradictorios o vacíos.
3. **`DenseRetriever` y `RetrievalService` (`src/retrieval/`):**
   - Pasa las cláusulas `where` directamente al método `collection.query(..., where=filters)` de ChromaDB.
   - La restricción se ejecuta internamente dentro del motor de indexación de ChromaDB antes de calcular distancias.
4. **`RAGOrchestrator` (`src/agents/orchestrator.py`):**
   - Coordina el análisis automático y la recuperación restringida manteniendo desacopladas las fases de recuperación y generación.

---

## 5. Ejemplos de Funcionamiento

### Ejemplo 1: Consulta de Comunicación en ESP32
* **Pregunta:** *"¿Cómo configurar UART en ESP32?"*
* **Análisis:**
  * Hardware: `ESP32`
  * Componente: `UART`
* **Filtro Generado:** `{"category": "ESP32"}`
* **Documentos Recuperados:** `esp32_technical_reference_manual_en.pdf`, `esp32_datasheet_en.pdf`
* **Beneficio:** Se excluyen completamente las especificaciones de UART de Texas Instruments (`sprugp1.pdf`) y Arduino (`atmega328ds.pdf`).

### Ejemplo 2: Consulta de Placa Arduino Uno
* **Pregunta:** *"¿Cuál es la resolución ADC del Arduino UNO?"*
* **Análisis:**
  * Hardware: `Arduino`
  * Placa: `UNO`
  * Componente: `ADC`
* **Filtro Generado:** `{"category": "Arduino"}`
* **Documentos Recuperados:** `A000066-datasheet.pdf`, `atmega328ds.pdf`
* **Beneficio:** Se previene la recuperación de información del conversor SAR ADC del ESP32 o de la Raspberry Pi Pico.

### Ejemplo 3: Consulta de Electrónica de Potencia / Driver
* **Pregunta:** *"¿Cuál es el rango de voltaje del controlador PWM TL5001A-Q1?"*
* **Análisis:**
  * Hardware / Fabricante: `Texas Instruments`
  * Componente: `TL5001A-Q1`
  * Dominio: `Power`
* **Filtro Generado:** `{"$and": [{"category": "Electronica"}, {"component": "TL5001A-Q1"}]}`
* **Documentos Recuperados:** `tl5001a-q1.pdf`

---

## 6. Resultados Comparativos (Antes vs Después)

Basado en la evaluación sistemática sobre el conjunto canónico de 20 preguntas técnicas (`evaluation/metadata_filter_comparison.json`):

| Métrica | Sin Filtros (Búsqueda Libre) | Con Metadata Filtering | Delta / Impacto |
| :--- | :---: | :---: | :---: |
| **Retrieval Precision (Mean)** | ~0.5840 | **~0.9125** | **+56.25% de precisión** |
| **Retrieval Recall (Mean)** | ~0.9500 | **~0.9500** | **0.00% (Recall preservado)** |
| **Falsos Positivos Inter-Familia** | Frecuentes en periféricos compartidos | **Eliminados por filtrado `where`** | Reducción total de ruido |

### Conclusión Pedagógica
Metadata Filtering es el mecanismo óptimo para sistemas RAG con colecciones heterogéneas. La clave técnica radica en calibrar el filtro al nivel taxonómico adecuado (nivel `category` para periféricos generales, o `component` para circuitos integrados específicos), garantizando un salto sustancial en precisión sin comprometer la exhaustividad documental.
