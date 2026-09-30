# Día 17: Búsqueda Híbrida (Hybrid Search)

## 1. Limitaciones de la Búsqueda Vectorial Pura (Dense Retrieval)
La búsqueda semántica mediante embeddings (`gemini-embedding-001`) sobresale al comprender conceptos, sinonimia y contexto conceptual general. Sin embargo, presenta deficiencias críticas en documentación de ingeniería embebida:
- **Pérdida de precisión en identificadores exactos:** Términos como nombres de registros (`ADCSRA`, `TWBR`), pines (`GPIO34`, `PB5`) o números de modelo (`ATmega328P`, `TB6600`) pueden diluirse en el espacio latente del embedding.
- **Sensibilidad a variaciones de códigos/hexadecimales:** Direcciones de memoria o banderas (`0x1F`, `0x00`) no tienen representación conceptual fuerte en modelos de lenguaje generales.

## 2. Fundamentos de BM25 (Keyword Retrieval)
BM25 (Best Matching 25) es un algoritmo de recuperación léxica probabilístico derivado de TF-IDF. Evalúa la frecuencia de término (TF) y la frecuencia inversa de documento (IDF) penalizando la longitud excesiva del documento:

$$\text{Score}_{\text{BM25}}(D, Q) = \sum_{i=1}^{n} \text{IDF}(q_i) \cdot \frac{f(q_i, D) \cdot (k_1 + 1)}{f(q_i, D) + k_1 \cdot (1 - b + b \cdot \frac{|D|}{\text{avgdl}})}$$

- **Tokenizador Técnico Personalizado:** Implementado con regex `\w+|0x[0-9a-fA-F]+` en [`BM25Index`](file:///C:/Users/THINKPAD/Desktop/Cursos%202026/RAG-Arduino/src/retrieval/bm25_index.py) para preservar números de pines y direcciones hexadecimales exactas.

## 3. Comparativa: Búsqueda Semántica vs. Léxica

| Característica | Búsqueda Semántica (Dense) | Búsqueda Textual (BM25) |
|---|---|---|
| **Mecanismo** | Distancia vectorial latente | Coincidencia exacta de tokens |
| **Fortaleza** | Conceptos, intenciones, paráfrasis | Nombres de registros, pines, códigos exactos |
| **Debilidad** | Coincidencias literales de acrónimos | Variaciones léxicas y sinonimia |
| **Ejemplo ideal** | "¿Cómo reducir el consumo en ESP32?" | "ADCSRA ATmega328P" |

## 4. Arquitectura Híbrida e Integración

```text
Pregunta
   ↓
Query Analysis & Metadata Filter
   ↓
┌────────────────────────────────────────────────────────┐
│  Dense Retrieval (gemini-embedding-001 + ChromaDB)     │
│  +                                                     │
│  Keyword Retrieval (BM25Index)                         │
└────────────────────────────────────────────────────────┘
   ↓
Weighted Score Fusion
(Hybrid Score = 0.7 * Norm_Dense + 0.3 * Norm_BM25)
   ↓
Context Builder → Gemini LLM
```

- **Módulos Creados:**
  - [`src/retrieval/bm25_index.py`](file:///C:/Users/THINKPAD/Desktop/Cursos%202026/RAG-Arduino/src/retrieval/bm25_index.py): Índice BM25 en memoria.
  - [`src/retrieval/keyword_retriever.py`](file:///C:/Users/THINKPAD/Desktop/Cursos%202026/RAG-Arduino/src/retrieval/keyword_retriever.py): Servicio de recuperación léxica.
  - [`src/retrieval/fusion.py`](file:///C:/Users/THINKPAD/Desktop/Cursos%202026/RAG-Arduino/src/retrieval/fusion.py): Weighted Score Fusion normalizado.
  - [`src/retrieval/hybrid_retriever.py`](file:///C:/Users/THINKPAD/Desktop/Cursos%202026/RAG-Arduino/src/retrieval/hybrid_retriever.py): Orquestador híbrido.
  - [`src/retrieval/retrieval_service.py`](file:///C:/Users/THINKPAD/Desktop/Cursos%202026/RAG-Arduino/src/retrieval/retrieval_service.py): Soporte para `mode="dense"|"keyword"|"hybrid"`.

## 5. Resultados Obtenidos
La evaluación cuantitativa se encuentra registrada en [`evaluation/hybrid_comparison.json`](file:///C:/Users/THINKPAD/Desktop/Cursos%202026/RAG-Arduino/evaluation/hybrid_comparison.json).

- **Consultas Conceptuales:** Dense y Hybrid alcanzan máxima cobertura semántica.
- **Consultas Exactas (Registros/Pines):** BM25 y Hybrid incrementan la precisión recuperando fragmentos exactos que Dense omitía.
- **Modo Debug:** Ejecutable mediante `python src/cli_chat.py --debug` mostrando la descomposición de scores DENSE, KEYWORD y FUSION.
