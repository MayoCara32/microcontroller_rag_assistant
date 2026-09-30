---
name: hybrid-search
description: Combina búsqueda semántica (vectorial) y búsqueda textual (BM25) para mejorar la precisión de recuperación en documentación técnica.
---

# Skill: Hybrid Search

## Objetivo
Combinar la búsqueda semántica densa (embeddings) con la búsqueda léxica (BM25) para garantizar la recuperación precisa tanto de conceptos generales como de términos exactos de hardware.

## Cuándo utilizar
Utilizar esta técnica cuando las consultas involucren:
- Documentación técnica y hojas de datos (datasheets).
- Códigos hexadecimales y direcciones de memoria.
- Nombres de registros de microcontroladores (ej: `ADCSRA`, `TWBR`).
- Componentes y pines específicos (ej: `ATmega328P`, `GPIO34`, `TB6600`).

## Flujo de Trabajo

```text
Pregunta del usuario
        ↓
  Metadata Filter (opcional)
        ↓
┌───────────────────────────────┐
│ Dense Retrieval (Embeddings)  │
│ +                             │
│ Keyword Retrieval (BM25)      │
└───────────────────────────────┘
        ↓
Weighted Score Fusion / RRF
        ↓
Resultados finales ordenados
```

## Advertencias y Buenas Prácticas
- **No depender únicamente de palabras clave:** BM25 no entiende sinonimia ni contexto semántico.
- **No eliminar búsqueda semántica:** Los embeddings capturan variaciones conceptuales y paráfrasis.
- **Normalización indispensable:** Siempre normalizar los scores de BM25 y Dense antes de sumarlos.
