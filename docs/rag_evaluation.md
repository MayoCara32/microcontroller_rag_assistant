# Módulo de Evaluación RAG (Retrieval-Augmented Generation)

Este documento describe la arquitectura, métricas, interpretación de resultados y estrategias de optimización para el módulo de evaluación de **Microcontroller RAG Assistant**.

---

## 1. Arquitectura y Flujo de Evaluación

El sistema de evaluación se conecta de manera no invasiva al pipeline RAG existente, garantizando la preservación de la base vectorial ChromaDB, los modelos de embeddings y los componentes de generación.

```
Pregunta de Evaluación
        │
        ▼
   RAG Pipeline
        │
        ▼
    Retrieval (ChromaDB + BM25 Híbrido)
        │
        ▼
Documentos Recuperados ───► [ Retrieval Precision Evaluator ]
        │             ───► [ Retrieval Recall Evaluator ]
        ▼
Generation (Gemini + PromptBuilder)
        │
        ▼
Respuesta Generada    ───► [ Faithfulness Evaluator (LLM Judge) ]
        │
        ▼
Evaluation Engine (RAGEvaluator)
        │
        ▼
Reporte JSON (`evaluation/results/report.json`)
```

---

## 2. Métricas Implementadas

### A. Retrieval Precision (Precisión de Recuperación)
Mide la proporción de documentos recuperados que son genuinamente relevantes para resolver la consulta formulada.

$$\text{Precision} = \frac{|\text{Documentos Relevantes Recuperados}|}{|\text{Total de Documentos Recuperados}|}$$

- **Rango:** `0.0` a `1.0`.
- **Objetivo:** Maximizar la densidad de información útil enviada al LLM y minimizar ruido contextual superfluo.

### B. Retrieval Recall (Exhaustividad de Recuperación)
Mide la capacidad del sistema de recuperar todos los documentos esenciales definidos en el ground truth para responder la pregunta técnica.

$$\text{Recall} = \frac{|\text{Documentos Esperados Encontrados}|}{|\text{Total de Documentos Esperados}|}$$

- **Rango:** `0.0` a `1.0`.
- **Objetivo:** Evitar la omisión de hojas de datos o manuales de referencia necesarios.

### C. Faithfulness (Fidelidad Factual)
Mide si cada una de las afirmaciones técnicas presentes en la respuesta generada por el LLM está estrictamente fundamentada y verificable en el contexto documental provisto.

$$\text{Faithfulness} = \frac{|\text{Afirmaciones SUPPORTED}| + 0.5 \times |\text{Afirmaciones PARTIALLY\_SUPPORTED}|}{|\text{Total de Afirmaciones Fácticas}|}$$

- **Rango:** `0.0` a `1.0`.
- **Categorías de Clasificación:**
  - `SUPPORTED`: La afirmación está directamente respaldada por los fragmentos recuperados.
  - `UNSUPPORTED`: La afirmación no aparece en el contexto, contradice las especificaciones o constituye una alucinación.
  - `PARTIALLY_SUPPORTED`: La afirmación contiene elementos correctos pero agrega inferencias sin evidencia explícita.
- **Caso Especial de Rechazo Honesto:** Si el modelo indica explícitamente que no posee información en la documentación (`NO_CONTEXT_FALLBACK`), el puntaje asignado es `1.0` (fidelidad perfecta por abstención justificada).

---

## 3. Guía de Interpretación de Resultados

| Escenario | Diagnóstico Técnico | Causa Raíz Probable | Acción Correctiva Recomendada |
| :--- | :--- | :--- | :--- |
| **Alto Recall, Baja Precision** | El sistema recupera el documento correcto pero incluye demasiados documentos irrelevantes. | `TOP_K` excesivamente alto o ponderación híbrida (`HYBRID_ALPHA`) sesgada hacia términos genéricos. | Reducir `TOP_K_RETRIEVAL`, incrementar umbral de similitud o aplicar reranking más estricto. |
| **Bajo Recall, Alta Precision** | Los pocos documentos recuperados son correctos, pero falta información complementaria. | La consulta utiliza vocabulario técnico que no coincide semántica ni léxicamente con los chunks. | Implementar Query Expansion, ajustar tamaño de chunk overlap o calibrar `HYBRID_ALPHA`. |
| **Bajo Recall, Baja Precision** | Falla severa en la etapa de recuperación. | La base vectorial carece de la documentación o el embedding no indexó los términos clave del componente. | Revisar indexación en ChromaDB, catalogación de metadata y verificar presencia de la hoja de datos en `data/raw`. |
| **Alto Recall, Baja Faithfulness** | La evidencia documental está presente, pero el LLM genera datos falsos o distorsiona especificaciones. | Temperatura del LLM demasiado alta o prompt permisivo que incentiva conocimiento paramétrico externo. | Ajustar temperatura a `0.0` - `0.2`, reforzar instrucción de "Responde ÚNICAMENTE con el contexto" y forzar citación de fuentes. |
| **Alto Recall, Alta Faithfulness** | **Estado Óptimo de Producción.** El sistema responde con rigor técnico respaldado punto a punto por los datasheets. | Configuración balanceada entre recuperación híbrida y generación determinista. | Mantener parámetros y monitorear deriva ante nuevos documentos agregados. |

---

## 4. Ejecución del Módulo de Evaluación

### Comando Básico
Evalúa el dataset completo de 20 preguntas y persiste el reporte en `evaluation/results/report.json`:

```bash
python src/evaluate.py
```

### Opciones de Línea de Comandos (CLI)

```bash
# Evaluar únicamente una muestra rápida (ej. 3 preguntas)
python src/evaluate.py --limit 3

# Evaluar únicamente la etapa de recuperación sin consumir tokens de generación/evaluación LLM
python src/evaluate.py --skip-faithfulness

# Especificar archivo de preguntas y destino de reporte personalizado
python src/evaluate.py --questions evaluation/questions.json --output evaluation/results/mi_reporte.json

# Modificar el valor de top_k durante la corrida
python src/evaluate.py --top-k 5
```

---

## 5. Estrategias de Optimización del Pipeline RAG

1. **Calibración de Búsqueda Híbrida (`HYBRID_ALPHA`):**
   - Para datasheets con números de parte y registros exactos (ej. `ADCSRA`, `CAN_H`, `RT6150B`), aumentar el peso léxico BM25 (`alpha = 0.3` a `0.4`).
   - Para preguntas conceptuales (ej. "¿Cómo funciona el prescaler?"), favorecer embeddings densos (`alpha = 0.6` a `0.7`).

2. **Ajuste del Context Window y Chunk Overlap:**
   - Si los términos quedan cortados entre fragmentos, incrementar `CHUNK_OVERLAP` de 150 a 200 caracteres para preservar la continuidad de tablas de pines y registros.

3. **Filtrado Jerárquico por Metadatos:**
   - Utilizar el campo `category` (`Arduino`, `ESP32`, `Raspberry`, `Protocolos`, `Drivers`) al invocar `retriever.search(query, filters={"category": "ESP32"})` cuando el contexto de la consulta determine la familia tecnológica.

4. **Validación Automática de Citaciones:**
   - Activar `ENFORCE_CITATION_VALIDATION = True` en `configs/settings.py` para rechazar respuestas cuyas fuentes no provengan estrictamente de los chunks entregados en el prompt.
