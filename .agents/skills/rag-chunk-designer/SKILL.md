---
name: rag-chunk-designer
description: Diseña y optimiza chunks para documentación técnica de microcontroladores y periféricos, preservando contexto, tablas completas, fórmulas, configuraciones de registros y relaciones semánticas con overlap verificable. Utilízala antes de generar embeddings. No utilizar para indexar directamente en ChromaDB ni para calcular distancias vectoriales.
---

# RAG Chunk Designer Skill

## Propósito

Diseñar estrategias de segmentación (chunking) optimizadas para sistemas RAG especializados en documentación técnica de microcontroladores y hardware embebido.

El objetivo principal es crear fragmentos de información que mantengan la coherencia técnica necesaria para recuperar conocimiento preciso mediante búsqueda semántica vectorial en ChromaDB, evitando la pérdida de relaciones críticas entre registros, pines y parámetros operativos.

Esta skill prioriza la integridad de la unidad de conocimiento sobre la uniformidad arbitraria del conteo de caracteres.

---

## Rol del Agente

Actúa como un ingeniero especialista en arquitectura de conocimiento para sistemas RAG, procesamiento documental y modelado de datos para bases vectoriales en ingeniería electrónica.

Tu responsabilidad es analizar documentos técnicos antes de la generación de embeddings y diseñar una estrategia de división que permita recuperar información precisa sobre:
- Arquitecturas de microcontroladores y mapas de memoria.
- Hojas de datos (datasheets) y manuales de referencia.
- Registros internos y secuencias de inicialización.
- Periféricos (ADC, Timers, PWM, USART, SPI, I2C, CAN).
- Diagramas funcionales y tablas de multiplexación de pines.
- Parámetros eléctricos y especificaciones máximas absolutas.

---

## Cuándo Utilizar esta Skill

Aplicar esta skill cuando:
- Un documento técnico limpio vaya a ser dividido para posterior vectorización.
- Se prepare información técnica para indexar en ChromaDB.
- Se requiera evaluar o ajustar el tamaño de chunk y la ventana de overlap.
- Se procesen datasheets extensos que contienen tablas de registros o características eléctricas.

## Cuándo NO Utilizar esta Skill

No utilizar cuando:
- El documento no ha sido limpiado de encabezados o números de página (usar `technical-document-cleaner`).
- Se requiera calcular los embeddings vectoriales directamente (usar `Embedding Engineer`).
- Se esté ejecutando una consulta de búsqueda de usuario (usar `vector-search`).

---

## Principio Fundamental de Chunking Técnico

> **Cada chunk debe representar una unidad de conocimiento técnicamente completa y autocontenida.**

Un chunk debe ser capaz de responder a una consulta específica sobre una función, registro o periférico sin requerir información truncada de otro chunk.

### Reglas de Preservación Contextual

1. **Encabezado Contextual Obligatorio:**
   Cada fragmento generado debe incluir un prefijo de metadatos contextuales:
   ```text
   [Componente: <nombre> | Categoría: <categoría> | Sección: <sección>]
   ```
2. **Tablas Técnicas Indivisibles:**
   - Nunca cortar tablas de configuración de registros de control.
   - Si una tabla de características eléctricas cabe dentro de $1.5 \times \text{chunk\_size}$, debe mantenerse en un único chunk.
   - Si la tabla excede el límite razonable, debe dividirse únicamente por bloques enteros de filas, repitiendo siempre la fila de encabezados en cada fragmento.
3. **Fórmulas y Cálculos Operativos:**
   - Toda fórmula (ej. cálculo de Baud Rate de UART o frecuencia de corte de timer) debe conservarse junto con la definición de cada una de sus variables y las unidades requeridas.
4. **Registros y Bits Asociados:**
   - Nunca separar el nombre del registro (ej. `ADMUX`) de la descripción de sus bits individuales (`REFS1`, `REFS0`, `ADLAR`, `MUX3:0`).
5. **Separación Conceptual por Periféricos:**
   - No mezclar en un mismo chunk explicaciones de periféricos no relacionados (ej. no mezclar la configuración del ADC con la del bus SPI).

---

## Dimensionamiento y Overlap Verificable

### Tamaño Recomendado
- **Documentación general y descripciones funcionales:** 500 a 800 tokens (o ~800 caracteres con margen de palabras).
- **Tablas de configuración de registros:** Hasta 1200 tokens si es indispensable para conservar la tabla completa.
- Nunca forzar un corte arbitrario a mitad de una palabra o de una tabla.

### Lógica de Overlap Verificable
- El overlap (típicamente 100 a 150 caracteres/tokens) debe ser una región compartida real y continua entre el final efectivo del Chunk $N$ y el inicio del Chunk $N+1$.
- El punto de inicio del siguiente fragmento debe derivarse del final real (`actual_end`) del fragmento anterior menos el overlap, asegurando que:
  $$\text{inicio}_{N+1} = \text{fin\_real}_N - \text{overlap}$$
- Debe comprobarse que la subcadena de overlap del Chunk $N$ esté idénticamente presente al comienzo del cuerpo del Chunk $N+1$.

---

## Metadatos Obligatorios por Chunk

Cada fragmento estructurado debe exportar como mínimo:
```json
{
  "chunk_id": "esp32_datasheet_chunk_042",
  "file_name": "esp32_datasheet_en.pdf",
  "source_path": "data/processed/esp32/esp32_datasheet_en.md",
  "category": "ESP32",
  "component": "ESP32",
  "document_type": "Datasheet",
  "topic": "ADC Configuration",
  "section": "Analog to Digital Converter",
  "page": 28
}
```

---

## Validaciones Previas a la Indexación

Antes de enviar los fragmentos al `Embedding Engineer`, verificar:
- [x] No existen chunks vacíos o con solo espacios.
- [x] Todos los IDs de chunks son únicos en la colección.
- [x] Las palabras no están truncadas al inicio o final del fragmento.
- [x] El overlap existe y es verificable entre fragmentos adyacentes de una misma sección.
- [x] Los metadatos de componente y categoría son válidos y consistentes.
