---
name: vector-search
description: Ejecuta la búsqueda semántica vectorial sobre la base de datos ChromaDB utilizando embeddings de consulta de Gemini. Recupera los chunks más cercanos sin redactar respuestas finales. Utilízala cuando el usuario o un agente solicite buscar información en la documentación de microcontroladores. No utilizar para generar respuestas RAG aumentadas ni para aplicar reranking o filtros BM25 en esta etapa.
---

# Vector Search Skill

## Objetivo

Recuperar de forma determinista y precisa los fragmentos técnicos más relevantes almacenados en la base vectorial ChromaDB, basándose en la proximidad semántica en el espacio vectorial `gemini-embedding-001`.

## Cuándo Utilizar esta Skill

Utilizar esta Skill cuando:
- Una consulta técnica de usuario requiera localizar evidencia en las hojas de datos y manuales procesados.
- El agente `retrieval-agent` o `rag-orchestrator` deba recuperar el Top-K de fragmentos documentales para una pregunta sobre pines, voltajes, periféricos o registros.

## Cuándo NO Utilizar esta Skill

No utilizar cuando:
- Se requiera redactar una respuesta explicativa final (en el Día 12 el flujo se detiene en la recuperación).
- Se pretendan aplicar algoritmos de reordenamiento avanzado (Cross-Encoder / FlashRank) o búsqueda léxica (BM25), reservados para sesiones futuras.
- Se estén procesando documentos crudos o generando la base de datos (usar las skills de ingesta).

## Proceso de Ejecución

1. **Recepción de la consulta técnica:** Recibir la cadena exacta formulada por el usuario (ej. *"¿Cuál es el voltaje máximo de operación del ATmega328P?"*).
2. **Generación de embedding de consulta:**
   - Invocar el servicio de embeddings con `embed_query()`.
   - Utilizar el modelo `gemini-embedding-001` con configuración `task_type="RETRIEVAL_QUERY"` y dimensión 768.
3. **Búsqueda vectorial en ChromaDB:**
   - Consultar la colección persistente (`microcontrollers_kb`) utilizando el vector de consulta.
   - Configurar inicialmente `top_k = 5` resultados.
4. **Inspección de metadatos y distancias:**
   - Extraer `chunk_id`, `file_name`, `category`, `component` y la métrica de `distance` L2 reportada por ChromaDB.
5. **Ordenación y entrega estructurada:**
   - Ordenar de menor a mayor distancia (mayor proximidad vectorial).
   - Entregar estrictamente los fragmentos recuperados **sin responder la consulta ni agregar texto de síntesis**.

## Formato de Salida Obligatorio

```text
Consulta: [Texto de la consulta]

Resultado 1:
Chunk ID: [ID del fragmento]
Documento: [Nombre del archivo fuente]
Categoría: [Categoría del microcontrolador/protocolo]
Componente: [Dispositivo asociado]
Tema: [Tema o sección si existe]
Distancia: [Valor numérico de distancia vectorial]
Contenido:
[Texto íntegro del fragmento recuperado]

Resultado 2:
...
```

## Restricciones Estrictas

Nunca:
- Redactar una respuesta a la pregunta del usuario.
- Inventar resultados o fragmentos que no provengan de ChromaDB.
- Modificar el texto recuperado de las hojas de datos.
- Tratar una distancia vectorial como si fuera un porcentaje de confianza sin explicitar su naturaleza métrica.
- Afirmar que existe evidencia cuando ChromaDB devuelva una lista vacía o distancias no convergentes.
