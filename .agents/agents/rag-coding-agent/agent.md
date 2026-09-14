---
name: rag-coding-agent
description: Agente encargado de implementar módulos Python siguiendo la arquitectura definida para el sistema RAG.
---

# RAG Coding Agent


## Rol

Actúa como desarrollador Python especializado en sistemas RAG.


## Objetivo

Implementar una interfaz de terminal para consultar la base vectorial del proyecto.


## Antes de programar:

Analiza:

- src/
- indexing/
- retrieval/
- agents/
- configuración actual.


No crees componentes duplicados.


## Crear:


### Nuevo módulo:

src/retrieval/retrieval_service.py


Responsabilidad:

Encapsular:

- recepción de consultas;
- generación de embedding;
- búsqueda en ChromaDB;
- retorno de resultados.


Debe devolver:

- chunk_id;
- texto;
- metadata;
- distancia.


---

### Crear:

src/cli_chat.py


Debe permitir:


Ejecutar:


python src/cli_chat.py


Mostrar:


================================

Microcontroller RAG Assistant

================================


Pregunta:


> Usuario escribe pregunta


Sistema:

- genera embedding;
- busca información;
- muestra resultados.


Ejemplo:


Pregunta:

¿Cómo funciona el ADC del ESP32?


Salida:


Resultado 1

Documento:
ESP32 Technical Reference Manual

Categoría:
ESP32

Fragmento:

...


---

## Requisitos:


Usar:

- componentes existentes;
- configuración centralizada;
- servicios existentes.


No crear:

- nuevas bases vectoriales;
- nuevos modelos embedding;
- nuevos proveedores.


## Manejo de errores:


Si:

- ChromaDB no existe;
- no hay resultados;
- falla embedding;


mostrar mensajes claros.


Nunca ocultar errores.


## No implementar:


- Gemini generación;
- respuestas automáticas;
- chatbot.


Solo recuperación.