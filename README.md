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

## Arquitectura RAG

El sistema implementa el ciclo completo de Generación Aumentada por Recuperación (RAG):

```text
Usuario
   ↓
Pregunta
   ↓
Retrieval (ChromaDB + gemini-embedding-001)
   ↓
Top-K Chunks Recuperados
   ↓
Context Builder (Estructuración y Fuentes)
   ↓
Gemini API (gemini-3.8-flash / google-genai)
   ↓
Respuesta Generada y Fundamentada
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

### 8. Ejecutar Asistente en Modo CHAT (RAG con Gemini)
Inicia la terminal interactiva de consultas con generación de respuestas fundamentadas:
```bash
python src/cli_chat.py
```

Para inspeccionar los chunks recuperados, distancias y el prompt enviado a Gemini sin exponer credenciales:
```bash
python src/cli_chat.py --debug
```

### 9. Opcional: Búsqueda vectorial sin generación
Puedes probar consultas directas solo en ChromaDB:
```bash
python src/api/cli.py query "¿Cuál es el voltaje de alimentación del ATmega328P?" --top-k 5
```

---

## Estado del Curso

* **Actualmente implementado (Día 12 & 13):**  
  * `Vector Search / Retrieval básico`: Ingesta, limpieza, metadatos, chunking con overlap continuo, embeddings de 768 dimensiones y búsqueda k-NN en ChromaDB.
  * `Modo CHAT RAG con Gemini`: Cliente oficial `google-genai`, constructor estructurado de prompts, generador de respuestas fundamentadas con fuentes y CLI interactiva con soporte `--debug`.

* **Próximas etapas:**  
  * Búsqueda híbrida léxico-semántica con BM25 (`HybridSearchEngine`).
  * Re-ranking de alta precisión mediante Cross-Encoder (`CrossEncoderReranker`).
  * Guardrails de seguridad eléctrica deterministas (`ElectricalSafetyGuardrails`).
  * Auditoría de firmware embebido (`Embedded Code Reviewer`).
  * Validación estricta de citas y detección de alucinaciones (`Citation Source Validator`).
