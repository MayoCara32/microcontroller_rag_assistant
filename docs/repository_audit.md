# Auditoría del Repositorio: Microcontroller RAG Assistant

**Fecha:** 14 de Septiembre de 2026  
**Objetivo de la auditoría:** Análisis exhaustivo para consolidación y estabilización del proyecto al nivel correspondiente al **final del Día 12** del curso (Pipeline Documental e Indexación Vectorial con Búsqueda Semántica Básica).

---

## 1. Estado General

El repositorio `microcontroller_rag_assistant` cuenta con una base sólida de código y documentación técnica para el procesamiento de hojas de datos de microcontroladores (Arduino UNO, Mega 2560, ATmega328P, ESP32, RP2040, protocolos de comunicación como I2C, SPI, UART, CAN).

Sin embargo, el proyecto presenta:
1. **Desalineación pedagógica**: Coexisten componentes diseñados para fases avanzadas del curso (Búsqueda híbrida con BM25, Cross-Encoder Reranker, guardrails de seguridad eléctrica, validación de citas y orquestación con agentes redactores de respuesta) con módulos esenciales que están incompletos o mal configurados.
2. **Inconsistencias en configuraciones**: Modelos de embeddings contradictorios entre `.env.example` (`text-embedding-3-small` de OpenAI) y `configs/settings.py` (`text-embedding-004` / `google`).
3. **Manejo de errores riesgoso**: El servicio de embeddings poseía un fallback silencioso que calculaba hashes pseudo-aleatorios cuando fallaba la API, ocultando errores reales e indexando basura matemática en la base vectorial.
4. **Desorganización en `.agents/`**: Nomenclaturas mixtas (carpetas con espacios vs kebab-case, `Skill.md` vs `SKILL.md`), archivos con contenido cruzado (ej. `.agents/agents/embedding-engineer/agent.md` que contenía la especificación de `Document Engineer`) y ausencia de frontmatter YAML estándar para su reconocimiento por el runtime de Antigravity.

---

## 2. Componentes Correctos

Los siguientes componentes cumplen con los principios de diseño y su funcionalidad base es correcta:

* **Estructura de directorios base**: Separación limpia entre `data/raw`, `data/processed`, `data/metadata`, `storage/`, `src/`, `configs/` y `tests/`.
* **Pipeline de limpieza de texto ([`DocumentCleaner`](file:///C:/Users/THINKPAD/Desktop/Cursos%202026/RAG-Arduino/src/ingestion/document_cleaner.py))**: Normalización de texto, eliminación de headers/footers recurrentes preservando unidades eléctricas.
* **Extracción de metadatos básicos ([`MetadataExtractor`](file:///C:/Users/THINKPAD/Desktop/Cursos%202026/RAG-Arduino/src/ingestion/metadata_extractor.py))**: Identificación heurística de interfaces de hardware (I2C, SPI, UART, ADC, PWM).
* **Indexación vectorial persistente ([`VectorIndexer`](file:///C:/Users/THINKPAD/Desktop/Cursos%202026/RAG-Arduino/src/indexing/vector_indexer.py))**: Conexión a ChromaDB en modo persistente local.
* **Corpus documental inicial**: Documentos técnicos y datasheets reales en `data/raw/` y archivos `.md` preprocesados en `data/processed/`.

---

## 3. Problemas Encontrados

### 3.1 Críticos

1. **Fallback silencioso de embeddings**:
   * *Ubicación:* `src/indexing/embedder.py`
   * *Problema:* Si la llamada a Google GenAI fallaba (por cuota, red o API key ausente), el código capturaba `except Exception: pass` y generaba vectores sintéticos basados en SHA256. Esto provoca que vectores no semánticos se guarden en ChromaDB sin alertar al alumno/desarrollador.
2. **Inconsistencia de proveedor y modelo de embeddings**:
   * *Ubicación:* `.env.example` vs `configs/settings.py` vs `src/indexing/embedder.py`
   * *Problema:* `.env.example` sugiere `text-embedding-3-small`, mientras que `configs/settings.py` tenía `text-embedding-004`. El estándar didáctico del Día 12 requiere explícitamente `gemini-embedding-001` con dimensión fija de `768` y distinción de `task_type` (`RETRIEVAL_DOCUMENT` vs `RETRIEVAL_QUERY`).
3. **Cálculo impreciso de ventana de overlap en el chunker**:
   * *Ubicación:* `src/indexing/chunker.py`
   * *Problema:* Al calcular el inicio del siguiente chunk como `start += (self.chunk_size - self.chunk_overlap)`, si el `end` del chunk actual se acortó para respetar saltos de línea o espacios, el overlap no coincide con el final real del chunk anterior o puede causar saltos incoherentes en el texto.
4. **Fallo en tests existentes por cruce de estado persistente**:
   * *Ubicación:* `tests/test_retrieval.py`
   * *Problema:* `test_hybrid_search_bm25_tokenization` falla en pytest porque consulta la colección real de ChromaDB que contiene datos previamente indexados de `A000066-datasheet.pdf_5`, en lugar de operar de manera aislada o con fixtures temporales.

### 3.2 Importantes

1. **Desorganización y duplicidad en `.agents/`**:
   * *Ubicación:* `.agents/agents/` y `.agents/Skills/`
   * *Problemas:*
     - `.agents/agents/embedding-engineer/agent.md` contiene el rol `# Document Engineer Agent`.
     - `.agents/agents/document-engineer/` y `.agents/agents/retrieval-agent/` son carpetas vacías.
     - `.agents/Skills/` utiliza mayúscula inicial y nombres de carpetas con espacios (`Citation Source Validator`, `Embedded Code Reviewer Skill`).
     - Faltan encabezados YAML frontmatter (`name`, `description`).
     - Falta la Skill `vector-search` requerida para el Día 12.
     - Duplicidad conceptual entre optimizadores y diseñadores de chunks.
2. **Ausencia de `embed_documents` y `embed_query` diferenciados**:
   * *Ubicación:* `src/indexing/embedder.py` e interfaces en `src/core/interfaces.py`
   * *Problema:* No se utilizan los modos específicos `RETRIEVAL_DOCUMENT` para la indexación y `RETRIEVAL_QUERY` para la búsqueda que exige la API de Gemini.
3. **Confusión conceptual entre Distancia y Similitud**:
   * *Ubicación:* `src/indexing/vector_indexer.py`
   * *Problema:* Se presentaba la distancia L2 transformada como un score absoluto sin explicitar la naturaleza métrica del vector store.

### 3.3 Menores

1. **Falta de `.agents/mcp_config.json`**: No existe configuración declarada de MCP para `filesystem` dentro del workspace.
2. **Falta de `.gitkeep` en directorios de datos y almacenamiento**: `data/processed`, `data/metadata`, `storage/vector_store` requieren `.gitkeep` para garantizar que la estructura exista en clones limpios.
3. **README desactualizado**: No describe el estado real del curso al Día 12 ni los pasos reproducibles de instalación y ejecución.

### 3.4 Código Adelantado respecto al Día 12 (A Aislar, No Eliminar)

El repositorio incluye módulos avanzados que no forman parte del pipeline de Día 12:
* `src/retrieval/hybrid_search.py` (Búsqueda híbrida con BM25)
* `src/retrieval/reranker.py` (Cross-Encoder / FlashRank)
* `src/validation/safety_guardrails.py` (Auditoría eléctrica heurística)
* `src/validation/citation_validator.py` (Validación de fuentes y citas)
* `src/agents/code_reviewer.py` (Revisor de código con reglas)
* `src/agents/embedded_expert.py` (Experto en hardware que genera respuestas finales)

*Decisión de diseño:* Estos archivos **se conservan íntegros**, se documentan como componentes de sesiones futuras (Día 13+) y se desacoplan del flujo activo del Día 12.

---

## 4. Archivos Afectados

| Archivo / Ruta | Acción Requerida |
| :--- | :--- |
| `.env.example` | Actualizar a `gemini-embedding-001`, proveedor `google`, dimensión `768`, `ALLOW_TEST_EMBEDDINGS=false`. |
| `configs/settings.py` | Alinear defaults de embedding a `gemini-embedding-001`, 768 dimensiones y flags de control. |
| `src/core/interfaces.py` | Incorporar métodos `embed_documents` y `embed_query` en `BaseEmbedder`. |
| `src/indexing/embedder.py` | Implementar `embed_documents` y `embed_query` con `RETRIEVAL_DOCUMENT` y `RETRIEVAL_QUERY`, eliminar fallback silencioso en producción. |
| `src/indexing/chunker.py` | Corregir cálculo de overlap real y validación de límites de palabras. |
| `src/indexing/vector_indexer.py` | Documentar y devolver distancias vectoriales claras. |
| `src/agents/orchestrator.py` | Limitar flujo al Día 12 (Recuperación vectorial pura -> Top-K sin generación final). |
| `src/api/cli.py` | Adaptar comandos `ingest` y `query` a búsqueda vectorial sin agentes de generación. |
| `.agents/` | Reestructurar carpetas a estándar kebab-case, añadir frontmatter YAML, unificar skills, crear `vector-search` y `mcp_config.json`. |
| `scripts/day12_semantic_search.py` | Crear script interactivo de búsqueda semántica pura de Día 12. |
| `docs/retrieval_tests.md` | Crear matriz de evaluación con 10 casos de prueba de hardware. |
| `README.md` | Documentar arquitectura, alcance al Día 12 y guía de reproducción. |
| `tests/` | Añadir pruebas de chunking, overlap, embeddings y vector store; aislar tests de componentes futuros. |

---

## 5. Plan de Actualización por Fases

1. **Fase 1: Configuración, Variables y MCP**
   - Actualizar `.env.example`, `configs/settings.py` y crear `.agents/mcp_config.json`.
   - Garantizar `.gitkeep` en directorios de almacenamiento y verificar `.gitignore`.

2. **Fase 2: Normalización de Antigravity (`.agents/`)**
   - Migrar carpetas a `.agents/agents/` y `.agents/skills/` con nomenclatura consistente.
   - Insertar YAML frontmatter (`name`, `description`) en todos los agentes y skills.
   - Consolidar skills duplicadas en `rag-chunk-designer`.
   - Crear skill `vector-search/SKILL.md`.
   - Ajustar el rol de `rag-orchestrator` y `retrieval-agent` al alcance estricto de Día 12.

3. **Fase 3: Corrección del Pipeline de Ingesta y Embeddings**
   - Refactorizar `src/indexing/embedder.py` con métodos tipados `embed_documents` y `embed_query`.
   - Implementar control estricto de excepciones (sin fallbacks silenciosos).
   - Refactorizar `src/indexing/chunker.py` para garantizar preservación de contexto y cálculo exacto de overlap continuo.
   - Ajustar `src/indexing/vector_indexer.py` para reportar métricas de distancia explícitas.

4. **Fase 4: Desacoplamiento del Pipeline Activo (Día 12)**
   - Desconectar generación final en `src/agents/orchestrator.py` y `src/api/cli.py`.
   - Marcar módulos futuros (`hybrid_search`, `reranker`, `guardrails`, `citation_validator`) como aislados para el Día 13+.

5. **Fase 5: Script Didáctico y Batería de Pruebas**
   - Crear `scripts/day12_semantic_search.py`.
   - Crear `docs/retrieval_tests.md` con 10 preguntas de prueba.
   - Desarrollar suite de tests unitarios automáticos (`tests/test_chunker.py`, `tests/test_embedder.py`, `tests/test_vector_store.py`).
   - Ejecutar `pytest` y `python -m compileall`.

6. **Fase 6: Documentación y Reporte Final**
   - Actualizar `README.md` y generar `docs/day12_status.md`.
