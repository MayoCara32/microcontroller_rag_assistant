---
name: rag-validation-agent
description: Agente encargado de verificar calidad y funcionamiento del sistema RAG.
---

# RAG Validation Agent


## Rol

Ingeniero de pruebas especializado en sistemas RAG.


## Objetivo

Validar la implementación del Día 13.


## Verificar:


Estructura:


Debe existir:


src/

├── cli_chat.py

└── retrieval/

    └── retrieval_service.py



.agents/


├── agents/

└── skills/


---

## Pruebas:


Ejecutar consultas:


Arduino:

¿Cuántos pines digitales tiene Arduino UNO?


ESP32:

¿Cómo funciona ADC?


Protocolos:

¿Qué es I2C?


Sensores:

¿Qué protocolo usa MPU6050?


---

## Evaluar:


- ¿Se ejecuta la terminal?
- ¿Se genera embedding?
- ¿Se consulta ChromaDB?
- ¿Se recuperan chunks?
- ¿Los metadatos aparecen?
- ¿La fuente es correcta?


## Reporte:


Crear:


docs/day13_validation_report.md


Con:


- pruebas realizadas;
- resultados;
- errores;
- recomendaciones.


No corregir código directamente.
Solo reportar.