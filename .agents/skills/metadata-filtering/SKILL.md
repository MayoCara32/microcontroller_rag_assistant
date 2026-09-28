---
name: metadata-filtering
description: Mejora la precisión de recuperación vectorial aplicando filtros de metadata sobre ChromaDB a partir del análisis de entidades técnicas en la consulta.
---

# Metadata Filtering Skill

## Nombre
`metadata-filtering`

## Objetivo
Mejorar la precisión de recuperación (`Retrieval Precision`) y el control contextual en el sistema RAG mediante la aplicación de restricciones y filtros de metadatos sobre ChromaDB.

---

## Cuándo Usar

Utilizar esta habilidad cuando:
* Existan **muchos documentos similares** en la base vectorial (ej. múltiples notas de aplicación y manuales de referencia).
* Concurran **múltiples microcontroladores** o arquitecturas en el corpus (Arduino AVR ATmega328P, ATmega2560, Espressif ESP32, Raspberry Pi RP2040).
* Se consulten **componentes repetidos** presentes en múltiples plataformas (ej. UART, SPI, I2C, PWM, ADC).

---

## Flujo del Proceso

```text
Pregunta
   ↓
Identificación de entidades (Query Analyzer)
   ↓
Generación de filtros (Metadata Filter Builder)
   ↓
Vector Search Restringido (ChromaDB `where` filter)
   ↓
Top-K Chunks Relevantes
```

---

## Reglas de Validación

1. **Campos Válidos:** Solo utilizar campos existentes en ChromaDB (`category`, `component`, `family`, `manufacturer`, `file_name`).
2. **Sin Falsos Positivos:** Mapear conceptos genéricos a la categoría canónica real (`ESP32`, `Arduino`, `Raspberry_Pi`, `Protocolos`, `Electronica`).
3. **Sintaxis ChromaDB:** Utilizar pares clave-valor directos para una condición o `$and` para múltiples restricciones.

---

## Advertencia Crítica de Recall

> [!WARNING]
> **Filtros demasiado estrictos pueden reducir drásticamente el Recall.**
> Si se aplica un filtro a un campo inexistente o con un valor excesivamente específico (ej. exigir `component: UART` en un documento clasificado como `component: ESP32 SoC`), ChromaDB retornará cero resultados aunque exista información semánticamente idéntica en el texto del chunk. Ante la duda, filtrar por el nivel jerárquico más seguro (`category`).
