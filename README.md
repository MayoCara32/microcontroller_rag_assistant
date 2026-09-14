# Microcontroller RAG Assistant

## Objetivo

**Microcontroller RAG Assistant** es un sistema de Recuperación Aumentada por Generación (RAG) especializado en documentación técnica de ingeniería electrónica, microcontroladores y sistemas embebidos.

Su propósito fundamental es permitir a ingenieros y desarrolladores consultar de forma semántica y determinista hojas de datos (datasheets), manuales de referencia y notas de aplicación de arquitecturas como **Arduino (AVR ATmega328P/ATmega2560)**, **ESP32 (Xtensa)**, **Raspberry Pi Pico (RP2040)** y protocolos de comunicación física e industrial (**I2C, SPI, UART, CAN Bus, Modbus**).

---

## Tecnologías

* **Python 3.10+** (Lenguaje base modular sin dependencias de frameworks caja negra como LangChain)
* **Google Gemini API** (`google-genai` SDK con modelo `gemini-embedding-001`)
* **ChromaDB** (Almacén vectorial local persistente)
* **Antigravity** (Definición y coordinación multiagente local en `.agents/`)
* **MCP (Model Context Protocol)** (Servidor `filesystem` estandarizado)
* **PyMuPDF & pdfplumber** (Extracción documental de alta fidelidad)
* **Typer & Rich** (Interfaz de línea de comandos e inspección interactiva)

---

## Arquitectura Actual (Día 12)

El pipeline implementado y activo corresponde estrictamente a la fase de **ingesta documental y recuperación semántica vectorial**:

```text
PDF / Documentos Técnicos
          ↓
     Extracción
          ↓
      Limpieza
          ↓
     Metadatos
          ↓
      Chunking
          ↓
      Overlap
          ↓
Document Embeddings (gemini-embedding-001, RETRIEVAL_DOCUMENT, 768d)
          ↓
      ChromaDB
          ↓
 Query Embedding (gemini-embedding-001, RETRIEVAL_QUERY, 768d)
          ↓
  Semantic Search
          ↓
    Top-K Chunks
```

---

## Configuración y Puesta en Marcha

Sigue estos pasos reproducibles para configurar el entorno y ejecutar la búsqueda semántica:

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd microcontroller_rag_assistant
```

### 2. Crear y activar el entorno virtual
```bash
python -m venv .venv
# En Windows (PowerShell):
.venv\Scripts\Activate.ps1
# En Linux/macOS:
source .venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Copia el archivo de plantilla a `.env`:
```bash
cp .env.example .env
```

### 5. Colocar tu API Key de Gemini
Edita `.env` y añade tu clave:
```env
EMBEDDING_PROVIDER=google
DEFAULT_EMBEDDING_MODEL=gemini-embedding-001
EMBEDDING_DIMENSION=768
GEMINI_API_KEY=tu_api_key_aqui
ALLOW_TEST_EMBEDDINGS=false
```

### 6. Preparar documentos
Coloca los datasheets y manuales técnicos en `data/raw/` o los documentos convertidos a Markdown en `data/processed/`.

### 7. Ejecutar procesamiento e indexación
Indexa los documentos en ChromaDB ejecutando:
```bash
python src/api/cli.py ingest
```

### 8. Ejecutar búsqueda semántica
Puedes probar consultas interactivas mediante el script didáctico de Día 12:
```bash
python scripts/day12_semantic_search.py
```
O directamente mediante la CLI:
```bash
python src/api/cli.py query "¿Cuál es el voltaje de alimentación del ATmega328P?" --top-k 5
```

---

## Estado del Curso

* **Actualmente implementado:**  
  `Vector Search / Retrieval básico` (Extracción, Limpieza, Metadatos, Chunking con Overlap continuo, Embeddings diferenciados en 768 dimensiones, Persistencia en ChromaDB y Búsqueda Semántica Top-K).

* **Próximas etapas (Día 13+):**  
  * Síntesis de respuesta final aumentada con Gemini (`Hardware Expert`).
  * Búsqueda híbrida léxico-semántica con BM25 (`HybridSearchEngine`).
  * Re-ranking de alta precisión mediante Cross-Encoder (`CrossEncoderReranker`).
  * Guardrails de seguridad eléctrica deterministas (`ElectricalSafetyGuardrails`).
  * Auditoría de firmware embebido (`Embedded Code Reviewer`).
  * Validación estricta de citas y detección de alucinaciones (`Citation Source Validator`).
