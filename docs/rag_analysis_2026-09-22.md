# Análisis del sistema RAG — 22 de septiembre de 2026

El proyecto tiene una arquitectura modular útil para el curso y un flujo RAG implementado. Todavía no ofrece garantías suficientes para usar sus respuestas como referencia técnica: recuperar fragmentos y mostrar nombres de documentos no demuestra que cada afirmación esté sustentada. Las prioridades son preservar los datos originales, controlar qué evidencia llega al modelo y comprobar las afirmaciones producidas.

## Alcance y evidencia

Se revisaron código, configuración no secreta, pruebas existentes, documentos de estado y el almacén SQLite de Chroma **en modo de solo lectura**. Se ejecutaron cinco comprobaciones aisladas sin red y se verificó la sintaxis de 52 archivos Python. No se modificó el código de aplicación, la configuración ni la base vectorial.

El entorno de esta sesión no encuentra Python del proyecto; `py` no detecta instalaciones. El Python incluido con Codex permite las comprobaciones con biblioteca estándar, pero no tiene pytest, ChromaDB, google-genai, rank-bm25 ni pydantic-settings. **No se ejecutó la suite pytest ni consultas reales a Gemini**, y no se midieron calidad semántica, latencia ni coste. Las cifras históricas de tests aprobados no se presentan como validación actual.

Evidencia reproducible: `reports/audit/audit_rag_20260922.py` y `reports/audit/evidence_20260922.json`. El script usa dobles explícitos de BM25 y del cliente generativo para aislar dos rutas; no evalúa esos servicios reales. Carga las clases correspondientes por AST sin sus imports para evitar dependencias ausentes.

## Estado real

| Elemento | Resultado observado |
|---|---|
| PDFs en `data/raw` | 19 |
| Documentos Markdown preparados | 4 |
| Colección | `microcontrollers_kb` |
| Dimensión | 768 |
| Fragmentos persistidos | 94 |
| Arduino UNO, `A000066-datasheet.pdf` | 12 fragmentos |
| Arduino Mega, `A000067-datasheet.pdf` | 18 fragmentos |
| ESP32, `esp32_datasheet_en.pdf` | 32 fragmentos |
| CAN, `kb-canbus-en.md` | 32 fragmentos |

Los 94 textos y sus IDs coinciden con el resultado de aplicar el limpiador, los metadatos y el chunker actuales a los cuatro Markdown. Esta comprobación **no demuestra** que sus vectores provengan del modelo actual ni que los Markdown conserven toda la información del PDF. No se realizó una auditoría factual completa PDF–Markdown.

Las entradas ejecutan rutas diferentes:

```text
cli.py ingest → Markdown/TXT preparados → limpieza → metadatos
              → chunks → embeddings → Chroma

cli.py query  → RAGOrchestrator → embeddings → búsqueda densa → fragmentos

cli_chat.py   → RetrievalService → búsqueda densa + BM25 → RRF
              → PromptBuilder → Gemini → respuesta y lista de fuentes
```

BM25 ya está activo por defecto en `RetrievalService`, aunque su cabecera y el README lo sitúen entre los componentes futuros. El reranker y los validadores no se invocan en el chat. Algunas clases de agentes son esqueletos con `NotImplementedError`; sus nombres no implican orquestación multiagente ejecutándose.

Aspectos positivos: separación de responsabilidades, modos `RETRIEVAL_DOCUMENT`/`RETRIEVAL_QUERY`, errores explícitos de embeddings en producción, persistencia local, clientes inyectables y pruebas de componentes. El fallback sintético está desactivado en la configuración local revisada.

## Hallazgos y soluciones

### 1. Prioridad alta: la limpieza puede borrar datos técnicos

**Evidencia:** `src/ingestion/document_cleaner.py:23` elimina cualquier línea formada por un entero. La entrada `Parámetro\nValor\n16\nUnidad\nMHz` pierde el `16`. Puede afectar celdas numéricas extraídas de tablas, no solo números de página.

**Solución:** identificar pies y encabezados usando posición en página y repetición entre páginas; no eliminar números por su forma aislada. Conservar texto original y transformaciones aplicadas. Añadir casos con celdas numéricas, signos, exponentes y unidades.

**Aceptación:** ninguna cifra de una tabla de prueba desaparece; los pies conocidos sí se eliminan.

### 2. Prioridad alta: los filtros se pierden en la rama léxica

**Evidencia:** `src/retrieval/hybrid_search.py:51` pasa `filters` a Chroma, pero la selección BM25 de las líneas 53–75 recorre todo el corpus. El probe devuelve Arduino al pedir `category=ESP32`, con búsqueda densa vacía y puntuación BM25 simulada positiva. Además, `target_mcu` en `src/agents/orchestrator.py:35` solo se refleja en la salida: el argumento `--mcu` no construye un filtro.

**Solución:** definir un contrato común de filtros y aplicarlo a ambas ramas **antes de seleccionar candidatos**. Implementar `MetadataFilterBuilder`, distinguir placa, chip y variante, y conectar `--mcu` con ese filtro. Para preguntas comparativas, admitir varios dispositivos explícitos.

**Aceptación:** ninguna rama devuelve documentos ajenos a un filtro explícito; pruebas para igualdad, combinaciones y corpus sin coincidencias.

### 3. Prioridad alta: ausencia de evidencia suficiente no equivale a lista vacía

**Evidencia:** `src/generation/response_generator.py:68` solo comprueba si el contexto formateado está vacío. `PromptBuilder` añade encabezados incluso a fragmentos sin texto: un chunk vacío provoca una llamada al generador en el probe. Los vecinos más cercanos también pasan aunque su contenido sea irrelevante. `SIMILARITY_THRESHOLD` está declarado pero no se aplica.

**Solución:** descartar fragmentos vacíos antes de formatear; comprobar cobertura del dispositivo y de la pregunta; introducir una decisión explícita `answerable / insufficient_evidence`. Calibrarla con preguntas contestables y no contestables. Para consultas parcialmente cubiertas, responder solo la parte respaldada y señalar la restante.

**Aceptación:** contexto vacío no llama al LLM; preguntas de dispositivos ausentes se abstienen. No trasladar automáticamente el umbral histórico `1.20`: necesita calibración.

### 4. Prioridad alta: las fuentes se listan, pero las citas no se validan

**Evidencia:** `src/validation/citation_validator.py:37` devuelve `valid=True` y `confidence_score=0.95` siempre que exista algún chunk. Aceptó “999 TB” frente a una fuente de “2 KB”. Este validador está desconectado del chat; por tanto el fallo es latente, mientras que la ausencia de validación afecta al flujo activo. Los flags `ENFORCE_CITATION_VALIDATION` y `ENFORCE_STRICT_ELECTRICAL_CHECK` no se consumen en ese flujo.

**Solución:** devolver afirmaciones con IDs de evidencia; verificar existencia del ID, correspondencia de dispositivo/variante, números, unidades y condiciones. Distinguir comprobación de referencia de comprobación semántica. No convertir una lista de nombres de archivos en “fuentes validadas” ni asignar una confianza fija. Abstenerse ante contradicciones sin resolver.

**Aceptación:** una cita inexistente o una cifra contradictoria se rechaza; cada afirmación técnica enlaza con fragmento y ubicación documental verificables. Un verificador adicional basado en LLM puede apoyar esta tarea, pero tampoco constituye una garantía absoluta.

### 5. Prioridad alta: contrato vectorial incompleto

**Evidencia:** `src/indexing/embedder.py:102` almacena los vectores recibidos sin normalizarlos. El proyecto configura `gemini-embedding-001` a 768 dimensiones. Google exige normalización manual para ese modelo cuando se usan dimensiones distintas de 3072. [Documentación de embeddings](https://ai.google.dev/gemini-api/docs/embeddings).

La colección usa `l2`, cuya distancia en Chroma es **L2 al cuadrado**, aunque las interfaces la rotulan como L2. `1/(1+distancia)` no es probabilidad de acierto. [Configuración de Chroma](https://docs.trychroma.com/docs/collections/configure).

Además, `storage/last_embedding_summary.json` registra `text-embedding-004`, mientras la configuración local usa `gemini-embedding-001`. La colección no conserva una huella verificable del modelo usado para los vectores suministrados. **Esto es un indicio histórico, no prueba de una mezcla actual.** La función de embedding por defecto almacenada por Chroma tampoco demuestra el origen de vectores insertados explícitamente.

**Solución:** validar longitud, cantidad, finitud y norma de los vectores; normalizar documentos y consultas conforme al modelo. Registrar proveedor, modelo, dimensión, normalización, métrica y versión de preprocesado. Rechazar consultas con contratos incompatibles. Si no se puede demostrar la procedencia, reconstruir en una colección nueva y compararla antes de sustituir la activa.

**Aceptación:** un cambio de modelo no puede reutilizar silenciosamente la misma colección, aunque coincida la dimensión.

### 6. Prioridad media: puntuaciones engañosas y degradación silenciosa

**Evidencia:** los candidatos solo léxicos reciben `distance=0.0` en `hybrid_search.py:72`, aun sin distancia calculada. `RetrievalService` oculta errores de inicialización BM25 con `except Exception: pass`. Reconstruye el corpus completo al iniciar y no lo actualiza si cambia la colección durante la sesión.

**Solución:** separar `dense_distance`, `bm25_score`, `rrf_score` y `retrieval_channels`; usar `None` cuando una medida no exista. Registrar explícitamente si opera en modo híbrido o degradado. Asociar el índice léxico a una versión del corpus y refrescarlo al cambiar. Mantenerlo en memoria es razonable para 94 chunks; la persistencia adicional solo se justifica al medir su coste.

**Aceptación:** un resultado solo BM25 nunca se muestra como coincidencia vectorial perfecta; los fallos léxicos quedan visibles.

### 7. Prioridad alta documental: tablas y trazabilidad incompletas

**Evidencia:** `src/ingestion/pdf_parser.py:50` no extrae tablas y `extract_tables=True` no cambia ese comportamiento. El chunker usa caracteres, no tokens ni estructura de filas; una tabla larga del probe se dividió en cinco chunks, cuatro sin encabezados de columnas. La base no tiene metadatos de página o ruta de sección por fragmento.

**Solución:** extraer bloques y tablas con página y coordenadas; reservar OCR para páginas que lo requieran. Separar por sección y luego por presupuesto de tokens medido. Dividir tablas largas por grupos de filas repitiendo cabeceras, unidades y notas; conservar condiciones de prueba y distinción entre máximo absoluto y operación recomendada. Registrar `page_start`, `page_end`, `section_path`, `source_hash` y revisión.

**Aceptación:** cada chunk tabular conserva significado independiente y vuelve a su ubicación original. No basta con aumentar globalmente `CHUNK_SIZE`.

### 8. Prioridad media: ingesta parcial y actualizaciones no reconciliadas

**Evidencia:** `src/api/cli.py:44` recorre Markdown/TXT de `data/processed`; no procesa los PDFs de `data/raw`. Hay 4 documentos preparados frente a 19 PDFs. `chunk_id` usa nombre de archivo e índice; `VectorIndexer` solo hace `upsert` y no elimina chunks de revisiones anteriores. Si un documento pasa de 12 a 8 chunks, los IDs 8–11 permanecen. Dos documentos con el mismo nombre pueden colisionar.

**Solución:** crear comandos separados `prepare`, `validate`, `index` y `status`, más un manifiesto por documento. Usar identidad documental estable y hash de revisión. Actualizar por revisión o construir una colección nueva, verificarla y cambiar la referencia activa; conservar posibilidad de volver atrás. Procesar por lotes con reintentos limitados y checkpoints.

**Aceptación:** repetir la ingesta no duplica; reducir o eliminar un documento no deja evidencia obsoleta; archivos homónimos de fuentes distintas coexisten.

### 9. Prioridad media: metadatos ricos que se pierden al indexar

**Evidencia:** `VectorIndexer.index_documents` descarta diccionarios anidados, incluidos `voltage`, `critical_params`, `cpu` y `memory`; las listas se convierten en cadenas. CAN carece de JSON específico en la ubicación esperada y usa inferencia básica. El extractor carga JSON sin un esquema estricto y oculta errores de lectura.

**Solución:** separar el catálogo documental completo de los campos indexables. Definir un esquema validado con nombres canónicos, tipo de documento, chip, placa, variante, fabricante y versión. Aplanar solo campos útiles para filtrado; conservar el original. Para interfaces, adoptar representación consultable compatible con la versión fijada de Chroma. Reportar metadatos inválidos con causa y archivo.

### 10. Prioridad media: generación y configuración difíciles de verificar

El prompt incluye el texto `SYSTEM:` dentro de `contents`; no utiliza el campo `system_instruction` del cliente. No delimita expresamente la documentación recuperada como datos no confiables ni limita el presupuesto del contexto. La lista de fuentes incluye todo lo recuperado, no necesariamente lo utilizado. Faltan telemetría de tokens, latencia por etapa, reintentos acotados y pruebas de documentos con instrucciones adversarias.

**Solución:** usar la instrucción de sistema del SDK, separar reglas de evidencia, diseñar salida con citas estructuradas y presupuesto de contexto. Probar entradas adversarias y contradicciones. Ajustar parámetros de generación mediante evaluación del modelo elegido; cambiar la temperatura por sí solo no garantiza fidelidad.

La configuración local revisada usa `gemini-3.6-flash`; no se detectó que esté usando el viejo default del código. Sin embargo, `settings.py`, `.env.example` y el README siguen proponiendo `gemini-2.0-flash`, cuyo retiro figura para el 1 de junio de 2026. Deben alinearse para instalaciones nuevas y validar disponibilidad. [Calendario oficial](https://ai.google.dev/gemini-api/docs/deprecations).

También hay un defecto alternativo: `EmbeddingService` toma inicialmente la clave Gemini sin seleccionar por proveedor, por lo que puede enviarla a OpenAI si se cambia `provider`; además omite `GOOGLE_API_KEY` en esa ruta de embeddings. Resolver credenciales por proveedor y no permitir que una clave de otro servicio actúe como fallback.

## Plan recomendado y criterios de éxito

| Orden | Entrega | Criterio de cierre |
|---|---|---|
| 1 | Entorno reproducible, lock de dependencias y diagnóstico del índice | Suite existente ejecutable; manifiesto de colección; arranque sin crear una base vacía accidentalmente |
| 2 | Correcciones de limpieza, filtros, contexto vacío y métricas | Regresiones para los cinco probes; ningún filtro explícito ignorado |
| 3 | Ingesta con trazabilidad y revisión del corpus | Primero los 4 documentos actuales; luego los 15 PDFs restantes según prioridad; páginas, tablas y revisiones comprobables |
| 4 | Colección reconstruida con contrato vectorial | Normalización y procedencia verificadas; comparación antes de activar; rollback disponible |
| 5 | Evaluación de recuperación y abstención | Dataset versionado con fuentes y pasajes correctos; comparación densa frente a híbrida |
| 6 | Generación con citas verificables | Contradicciones y citas inventadas rechazadas; casos sin evidencia no generan afirmaciones técnicas |
| 7 | Experimento de reranking | Activarlo solo si mejora las métricas con coste/latencia aceptables, incluyendo consultas españolas y fuentes inglesas |

Preparar inicialmente 40–60 preguntas: pines y registros exactos, tablas eléctricas con condiciones, consultas en español sobre documentos ingleses, comparativas, preguntas ambiguas y dispositivos ausentes. Etiquetar pasajes válidos, no solo el nombre del PDF.

Medir **Recall@5** (cobertura de los pasajes correctos), **MRR** (posición del primer pasaje válido), precisión de citas, proporción de afirmaciones respaldadas, abstención correcta y respuestas parciales. Registrar también latencia p50/p95, tokens y coste por consulta. Objetivos iniciales propuestos, no resultados medidos: cero fugas de filtros y referencias inexistentes, Recall@5 ≥ 90 % en el conjunto etiquetado y abstención correcta ≥ 95 % en los casos sin evidencia. Reportar por tipo de pregunta y reservar casos de evaluación separados de los usados para ajustar umbrales.

Mantendría Python, Chroma y la arquitectura modular actual. La siguiente inversión debe ser un RAG verificable con corpus trazable y evaluación repetible; nuevas capas de agentes o frameworks no resuelven los defectos reproducidos.
