---
name: rag-terminal-interface
description: Gestiona la interacción por terminal para recibir consultas técnicas de microcontroladores y presentar de forma estructurada los fragmentos de evidencia documental recuperados desde ChromaDB. No genera respuestas sintetizadas, código ni explicaciones con LLM en esta etapa.
---

# RAG Terminal Interface Skill

## Objetivo

Proporcionar una interfaz interactiva de línea de comandos (CLI) limpia y estructurada que permita a los usuarios ingresar consultas técnicas sobre microcontroladores y periféricos, gestionando el ciclo de recuperación vectorial y desplegando estrictamente los fragmentos documentales devueltos por ChromaDB con sus metadatos y distancias métricas.

## Cuándo Utilizar esta Skill

Utiliza esta Skill cuando:
- El usuario interactúe con el sistema a través de la terminal o consola de comandos.
- Se requiera capturar una pregunta técnica (ej. pines, voltajes, periféricos, registros, buses de comunicación).
- Se deba delegar la búsqueda semántica en el `RetrievalService` o `retrieval-agent`.
- Se deban formatear y presentar los fragmentos documentales recuperados de forma legible y verificable.

## Cuándo NO Utilizar esta Skill

No utilices esta Skill cuando:
- Se solicite responder a la pregunta del usuario utilizando conocimiento propio del LLM o síntesis generativa (prohibido en Día 13).
- Se solicite mantener una conversación multi-turno con memoria o contexto acumulado.
- Se requiera redactar código de firmware o diseñar esquemáticos electrónicos.
- Se pretenda aplicar algoritmos de reordenamiento (reranking con Cross-Encoder) o filtros léxicos BM25 (reservados para etapas posteriores).

## Flujo Operativo Estricto

```text
Entrada del Usuario (Terminal)
           ↓
   Captura y Validación
           ↓
    RetrievalService
           ↓
  Embedding RETRIEVAL_QUERY
           ↓
   Búsqueda en ChromaDB
           ↓
 Top-K Chunks + Metadatos
           ↓
 Visualización en Terminal (FIN DEL FLUJO)
```

1. **Recepción de la Consulta:**
   - Capturar el texto ingresado por el usuario sin alterar su sentido semántico.
   - Validar que la cadena no esté vacía ni compuesta únicamente por espacios en blanco.
2. **Notificación de Estado:**
   - Informar al usuario las fases en ejecución:
     - `generando embedding...`
     - `buscando información...`
3. **Invocación del Servicio de Recuperación:**
   - Invocar `RetrievalService.search(query)`.
   - Recuperar el conjunto de resultados conteniendo `chunk_id`, `texto`, `metadata` y `distancia`.
4. **Presentación de Evidencia Documental:**
   - Si existen resultados, presentar cada fragmento con la estructura obligatoria de reporte.
   - Si no existen resultados o la base está vacía, emitir el mensaje estándar de ausencia documental.
5. **Control de Errores:**
   - Manejar fallas de inicialización de ChromaDB (`FileNotFoundError`) o excepciones de la API de embeddings (`RuntimeError`) informando el motivo técnico de forma clara sin interrumpir inesperadamente el bucle interactivo.

## Formato de Salida Obligatorio

### 1. Cuando se recupera evidencia:

```text
Resultado [Número de Resultado]

Documento:
[Nombre del archivo fuente / Hoja de datos]

Categoría:
[Categoría técnica del componente o microcontrolador]

Fragmento:
[Texto completo del fragmento recuperado]

--------------------------------
```

### 2. Cuando no se encuentra información:

```text
[Resultado]: No se encontró información suficiente en la base documental para la consulta solicitada.
```

## Restricciones Críticas

Nunca:
- Redactar respuestas a las preguntas del usuario ni parafrasear la información técnica.
- Usar conocimiento propio del modelo de lenguaje para responder o complementar datos faltantes.
- Intentar simular un asistente conversacional o chatbot con memoria de turnos anteriores.
- Inventar nombres de hojas de datos, números de pines, registros o valores eléctricos.
- Ocultar errores de conexión con el almacén vectorial o con la API de embeddings.
