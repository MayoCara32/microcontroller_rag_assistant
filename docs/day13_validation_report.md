# Reporte de Validación Técnica: Interacción Terminal RAG (Día 13)

**Fecha:** 14 de Septiembre de 2026  
**Agente Evaluador:** RAG Validation Agent  
**Objetivo:** Evaluar el funcionamiento integral de la interacción de terminal, el servicio de recuperación (`RetrievalService`), la generación de embeddings y la consulta sobre ChromaDB sin generación LLM.

---

## 1. Pruebas Realizadas

Se ejecutó la batería de 4 consultas técnicas requeridas a través del pipeline activo (`RetrievalService` -> `EmbeddingService` -> `VectorIndexer`):

1. **Arduino:** `¿Cuántos pines digitales tiene Arduino UNO?`
2. **ESP32:** `¿Cómo funciona ADC?`
3. **Protocolos:** `¿Qué es I2C?`
4. **Sensores:** `¿Qué protocolo usa MPU6050?`

---

## 2. Resultados Obtenidos

### Caso 1: Arduino — *¿Cuántos pines digitales tiene Arduino UNO?*
* **Chunks Recuperados:** 3
* **Resultados:**
  1. **Chunk ID:** `A000066-datasheet.pdf_9`  
     * **Fuente:** `A000066-datasheet.pdf`  
     * **Categoría:** `Arduino` | **Componente:** `Arduino UNO R3`  
     * **Distancia L2:** `1.2428`  
     * **Contenido:** Sección de aplicaciones (Iniciación a la robótica, estándar industrial, etc.).
  2. **Chunk ID:** `A000066-datasheet.pdf_11`  
     * **Fuente:** `A000066-datasheet.pdf`  
     * **Categoría:** `Arduino` | **Componente:** `Arduino UNO R3`  
     * **Distancia L2:** `1.3093`  
     * **Contenido:** Descripción de traducción a chino y duplicidad física de pines I2C (SDA/SCL).
  3. **Chunk ID:** `A000066-datasheet.pdf_10`  
     * **Fuente:** `A000066-datasheet.pdf`  
     * **Categoría:** `Arduino` | **Componente:** `Arduino UNO R3`  
     * **Distancia L2:** `1.3132`  
     * **Contenido:** Limitaciones de tensión de entrada por pin VIN y puerto USB.

---

### Caso 2: ESP32 — *¿Cómo funciona ADC?*
* **Chunks Recuperados:** 3
* **Resultados:**
  1. **Chunk ID:** `A000066-datasheet.pdf_9`  
     * **Fuente:** `A000066-datasheet.pdf`  
     * **Categoría:** `Arduino` | **Componente:** `Arduino UNO R3`  
     * **Distancia L2:** `1.2912`  
     * **Contenido:** Sección de aplicaciones educativas e industriales.
  2. **Chunk ID:** `A000066-datasheet.pdf_11`  
     * **Fuente:** `A000066-datasheet.pdf`  
     * **Categoría:** `Arduino` | **Componente:** `Arduino UNO R3`  
     * **Distancia L2:** `1.3073`  
     * **Contenido:** Mención de pines I2C y traducción multilingüe.
  3. **Chunk ID:** `A000066-datasheet.pdf_1`  
     * **Fuente:** `A000066-datasheet.pdf`  
     * **Categoría:** `Arduino` | **Componente:** `Arduino UNO R3`  
     * **Distancia L2:** `1.3174`  
     * **Contenido:** Arquitectura AVR RISC, memoria y coprocesador USB ATmega16U2.

---

### Caso 3: Protocolos — *¿Qué es I2C?*
* **Chunks Recuperados:** 3
* **Resultados:**
  1. **Chunk ID:** `A000066-datasheet.pdf_11`  
     * **Fuente:** `A000066-datasheet.pdf`  
     * **Categoría:** `Arduino` | **Componente:** `Arduino UNO R3`  
     * **Distancia L2:** `1.2631`  
     * **Contenido:** Mención explícita: *"Los pines I2C (SDA/SCL) se encuentran duplicados físicamente en la cabecera..."*.
  2. **Chunk ID:** `A000066-datasheet.pdf_9`  
     * **Fuente:** `A000066-datasheet.pdf`  
     * **Categoría:** `Arduino` | **Componente:** `Arduino UNO R3`  
     * **Distancia L2:** `1.2828`  
  3. **Chunk ID:** `A000066-datasheet.pdf_4`  
     * **Fuente:** `A000066-datasheet.pdf`  
     * **Categoría:** `Arduino` | **Componente:** `Arduino UNO R3`  
     * **Distancia L2:** `1.2903`  
     * **Contenido:** Interfaces: GPIO (14 pines digitales), PWM (6 canales), ADC (Entradas analógicas).

---

### Caso 4: Sensores — *¿Qué protocolo usa MPU6050?*
* **Chunks Recuperados:** 3
* **Resultados:**
  1. **Chunk ID:** `A000066-datasheet.pdf_9`  
     * **Fuente:** `A000066-datasheet.pdf`  
     * **Categoría:** `Arduino` | **Componente:** `Arduino UNO R3`  
     * **Distancia L2:** `1.2470`  
  2. **Chunk ID:** `A000066-datasheet.pdf_11`  
     * **Fuente:** `A000066-datasheet.pdf`  
     * **Categoría:** `Arduino` | **Componente:** `Arduino UNO R3`  
     * **Distancia L2:** `1.2833`  
     * **Contenido:** Pines I2C (SDA/SCL).
  3. **Chunk ID:** `A000066-datasheet.pdf_4`  
     * **Fuente:** `A000066-datasheet.pdf`  
     * **Categoría:** `Arduino` | **Componente:** `Arduino UNO R3`  
     * **Distancia L2:** `1.3237`  
     * **Contenido:** 14 pines digitales, PWM, ADC.

---

## 3. Matriz de Evaluación

| Criterio Evaluado | Estado | Evidencia y Observaciones |
| :--- | :---: | :--- |
| **¿Se ejecuta la terminal?** | **CUMPLE** | Tanto `src/cli_chat.py` como `src/cli/terminal_interface.py` inician bucles interactivos limpios, capturan entradas, responden a comandos de salida (`exit`, `quit`, `q`, `salir`) y no se rompen ante entradas vacías. |
| **¿Se genera embedding?** | **CUMPLE** | Se invoca `embed_query()` usando el modelo oficial `gemini-embedding-001` con configuración `task_type="RETRIEVAL_QUERY"` y dimensión 768d. |
| **¿Se consulta ChromaDB?** | **CUMPLE** | `VectorIndexer` consulta la colección persistente `microcontrollers_kb` en `storage/vector_store/chroma.sqlite3`. |
| **¿Se recuperan chunks?** | **CUMPLE** | Se recuperan los Top-K fragmentos vectoriales ordenados de menor a mayor distancia euclidiana L2. |
| **¿Los metadatos aparecen?** | **CUMPLE** | Cada resultado incluye `chunk_id`, `file_name`, `category`, `component` y `distancia`. |
| **¿La fuente es correcta?** | **PARCIAL / CONDICIONAL** | **Correcta para Arduino**, pero **inadecuada para ESP32, Protocolos y Sensores**. Ver sección de errores. |

---

## 4. Errores y Hallazgos Críticos

> [!WARNING]
> **1. Base Vectorial Incompleta (Cobertura Documental Limitada):**
> La colección persistente en `storage/vector_store/` contiene únicamente **12 chunks indexados**, todos provenientes de un solo documento: `A000066-datasheet.pdf` (Arduino UNO R3). A pesar de que en `data/raw/Microcontroladores_RAG_Documentacion` existen carpetas con datasheets de ESP32, sensores y protocolos, estos documentos **no han sido vectorizados ni cargados en ChromaDB**.

> [!CAUTION]
> **2. Recuperación Forzada por Vecinos Más Cercanos:**
> Debido a que ChromaDB solo tiene 12 fragmentos disponibles en total, el algoritmo de k-NN vectorial devuelve obligatoriamente los vectores más cercanos dentro de esos 12 fragmentos de Arduino, independientemente de que la consulta pregunte por el "ESP32" o el "MPU6050". Esto se refleja en distancias métricas altas ($L_2 \approx 1.24 - 1.32$).

> [!NOTE]
> **3. Ausencia Positiva de Alucinación (Groundedness Estricto):**
> A pesar de la limitación del almacén documental, el sistema **no alucinó respuestas**. No se generaron textos ficticios sobre el ADC del ESP32 ni sobre el protocolo del MPU6050. El sistema se limitó estrictamente a entregar los fragmentos crudos recuperados de la base vectorial, cumpliendo con la regla de oro del Día 13.

---

## 5. Recomendaciones

1. **Ingesta e Indexación Masiva:**
   Ejecutar la vectorización de los documentos pendientes ubicados en `data/raw/Microcontroladores_RAG_Documentacion/` (`ESP32`, `Drivers_Modulos`, `Protocolos`) para poblar ChromaDB con la cobertura requerida.
2. **Umbral de Distancia (Distance Threshold Filter):**
   Implementar en el `RetrievalService` un umbral máximo de distancia L2 (por ejemplo, si `distancia > 1.20`, considerar que no hay convergencia semántica y desplegar: *"No se encontró información suficiente en la base documental para la consulta solicitada."*).
3. **Filtro por Metadatos Asistido:**
   Utilizar la clasificación temática inicial (Arduino, ESP32, etc.) para aplicar `where={"category": ...}` en ChromaDB, evitando que consultas de ESP32 devuelvan fragmentos de Arduino.
