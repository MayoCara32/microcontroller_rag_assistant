---
name: technical-document-cleaner
description: Limpia texto técnico desordenado procedente de OCR o extracción de PDFs eliminando encabezados repetitivos y ruido sin alterar unidades de medida, tablas ni advertencias eléctricas. Utilízala después del parseo de documentos y antes del chunking. No utilizar para recortar código ni para omitir parámetros de hojas de datos.
---

# Technical Document Cleaner Skill

## Rol

Actúa como especialista en preparación e higienización de datos documentales para sistemas RAG técnicos.

## Objetivo

Transformar el texto crudo extraído de PDFs y datasheets técnicos en texto limpio, cohesivo y normalizado, eliminando artefactos de formato sin comprometer ninguna especificación técnica, tabla o parámetro numérico.

## Cuándo utilizar esta Skill

Utilizar esta Skill cuando:
- Se haya completado la extracción de texto mediante `PDFParser` o herramientas OCR.
- El texto contenga encabezados de página repetitivos (ej. "Atmel-2549Q-AVR-02/2014"), numeraciones sueltas ("Page 12 of 435") o saltos de línea arbitrarios en medio de oraciones.
- Se deban normalizar tablas en Markdown para que las columnas coincidan.

## Cuándo NO utilizar esta Skill

No utilizar cuando:
- Se pretenda resumir o sintetizar el contenido (el texto técnico debe permanecer íntegro).
- Se busque clasificar documentos (usar `embedded-document-classifier`).
- Se requiera fragmentar el documento en chunks (usar `rag-chunk-designer`).

## Artefactos y Ruido a Eliminar

1. **Encabezados y pies de página periódicos:** Números de revisión de documento, logos textuales y cláusulas de confidencialidad repetidas en cada página.
2. **Numeración de página aislada:** Líneas con patrones como `- 45 -`, `Page 12`, `12/150`.
3. **Caracteres de control y corrupción OCR:** Secuencias no imprimibles, saltos de página erráticos o caracteres ASCII huérfanos.
4. **Espacios en blanco desordenados:** Normalizar múltiples espacios horizontales consecutivos a un único espacio, preservando sangrías de tablas y bloques de código.

## Elementos Sagrados (Nunca Modificar ni Eliminar)

- **Unidades de medida:** Preservar estrictamente $V$, $mV$, $mA$, $\mu A$, $MHz$, $kHz$, $k\Omega$, $pF$, $nF$, $dBm$, $baud$.
- **Límites máximos y condiciones:** Rangos absolutos de voltaje ($V_{CC} \pm 0.5V$), tiempos de subida/bajada de señal ($t_r$, $t_f$) y notas de temperatura.
- **Tablas de registros:** Conservar encabezados, bits (7 down to 0), nombres de registros (`TCCR1A`, `TWBR`, etc.) y valores de reset.
- **Advertencias de seguridad:** Secciones con leyendas "Warning", "Caution", "Absolute Maximum Ratings".

## Resultado Esperado

Un documento normalizado en texto plano o Markdown donde cada párrafo y tabla conserve su coherencia semántica original, listo para ser consumido por el algoritmo de segmentación (`rag-chunk-designer`).
