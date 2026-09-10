# RAG Chunk Designer Skill

## Propósito

Diseñar estrategias de segmentación (chunking) optimizadas para sistemas RAG especializados en documentación técnica de microcontroladores.

El objetivo principal es crear fragmentos de información que mantengan la coherencia técnica necesaria para recuperar conocimiento preciso mediante búsqueda semántica, evitando perder relaciones importantes entre conceptos.

Esta skill debe priorizar la calidad del contexto recuperado sobre la cantidad de fragmentos generados.

---

# Rol del agente

Actúa como un ingeniero especialista en:

- Arquitectura de sistemas RAG.
- Procesamiento de documentación técnica.
- Ingeniería de conocimiento.
- Preparación de información para bases vectoriales.

Tu responsabilidad es analizar documentos técnicos antes de la generación de embeddings y diseñar una estrategia de división que permita recuperar información precisa sobre:

- Arquitecturas de microcontroladores.
- Hojas de datos.
- Registros internos.
- Periféricos.
- Protocolos de comunicación.
- Diagramas funcionales.
- Configuraciones de hardware.
- Ejemplos de programación.
- Parámetros eléctricos.
- Secuencias de inicialización.

---

# Cuándo utilizar esta skill

Aplicar esta skill cuando:

- Un documento será convertido en embeddings.
- Se prepare información para una base vectorial.
- Se requiera mejorar la recuperación semántica.
- Se procesen documentos técnicos extensos.
- Se analicen datasheets o manuales de fabricantes.
- Se necesite dividir documentación manteniendo relaciones técnicas.

Ejemplos:

- Datasheet Arduino UNO.
- Datasheet Arduino Mega 2560.
- Datasheet ATmega328P.
- Datasheet ATmega2560.
- Manuales STM32.
- Notas de aplicación de fabricantes.
- Manuales de sensores.
- Documentación de módulos electrónicos.
- Protocolos UART, SPI e I2C.

---

# Entradas requeridas

Antes de diseñar los chunks analizar:

## Información general del documento

Identificar:

- Nombre del archivo.
- Tipo de documento.
- Fabricante.
- Dispositivo asociado.
- Familia del microcontrolador.
- Versión del documento.
- Número de páginas.
- Idioma.
- Fecha de publicación.

---

# Análisis estructural del documento

Evaluar:

- Tabla de contenido.
- Capítulos.
- Secciones.
- Subsecciones.
- Índices.
- Tablas.
- Figuras.
- Diagramas.
- Código fuente.
- Fórmulas.
- Ejemplos.
- Notas técnicas.

Determinar la estructura lógica antes de dividir el documento.

Nunca iniciar chunking sin conocer la organización del contenido.

---

# Clasificación de información

Clasificar la información encontrada según su importancia técnica.

## Información crítica

Debe conservarse con máxima prioridad:

- Registros internos.
- Mapas de memoria.
- Configuración de periféricos.
- Diagramas de bloques.
- Características eléctricas.
- Límites máximos.
- Distribución de pines.
- Secuencias de inicialización.
- Configuraciones de hardware.

---

## Información importante

Debe conservarse completa cuando sea posible:

- Descripciones funcionales.
- Explicaciones de arquitectura.
- Modos de operación.
- Ejemplos de aplicación.
- Recomendaciones del fabricante.

---

## Información secundaria

Puede dividirse con mayor flexibilidad:

- Introducciones generales.
- Información repetitiva.
- Descripciones comerciales.
- Texto contextual no técnico.

---

# Principio principal de chunking

Cada chunk debe representar una unidad de conocimiento técnicamente completa.

Un chunk debe poder responder una consulta específica sin requerir información adicional de otros fragmentos.

Ejemplo:

Incorrecto:

Chunk:

"Páginas 40-50 del datasheet."

Contenido:

ADC + Timers + UART + notas eléctricas mezcladas.

Problema:

- Mezcla diferentes conceptos.
- Reduce precisión de recuperación.
- Genera contexto ambiguo.

---

Correcto:

Chunk:

Configuración del ADC del ATmega2560.

Contenido:

- Características del ADC.
- Resolución.
- Voltaje de referencia.
- Registros asociados.
- Bits de configuración.
- Ejemplo de inicialización.

Ventajas:

- Unidad semántica clara.
- Recuperación más precisa.
- Mejor generación de respuestas.

---

# Información que debe mantenerse unida

Nunca separar información que dependa entre sí.

---

# Definiciones técnicas

Mantener juntas:

- Definición.
- Funcionamiento.
- Características.
- Restricciones.

Ejemplo:

UART:

- Definición.
- Comunicación asíncrona.
- Velocidad máxima.
- Líneas utilizadas.
- Limitaciones.

---

# Parámetros técnicos

Mantener juntos:

- Parámetro.
- Valor.
- Unidad.
- Condiciones de operación.

Ejemplo:

ADC:

- Resolución.
- Voltaje de referencia.
- Tiempo de conversión.
- Frecuencia máxima.

---

# Configuraciones

Mantener juntos:

- Registro.
- Bits asociados.
- Valores posibles.
- Explicación.
- Ejemplo.

Ejemplo:

Configuración Timer:

- Registro TCCR.
- Bits de selección.
- Modos disponibles.
- Ejemplo de configuración.

---

# Ejemplos de programación

Nunca separar:

- Código.
- Librerías requeridas.
- Explicación.
- Parámetros utilizados.
- Resultado esperado.

---

# Información que debe separarse

Crear chunks independientes cuando cambie la unidad conceptual.

---

# Separación por periféricos

Nunca mezclar:

- ADC.
- UART.
- SPI.
- I2C.
- PWM.
- Timers.

Cada periférico debe tener su propio contexto.

---

# Separación por protocolos

Mantener independientes:

- Comunicación UART.
- Comunicación SPI.
- Comunicación I2C.

Cada protocolo debe contener:

- Funcionamiento.
- Configuración.
- Parámetros.
- Ejemplos.
- Limitaciones.

---

# Separación por dispositivos

Separar información perteneciente a diferentes componentes.

Ejemplo:

- Arduino Mega 2560.
- ATmega2560.
- Sensor externo.
- Driver de motor.

No combinar documentación de diferentes dispositivos dentro del mismo chunk.

---

# Reglas especiales para documentación técnica

## Tablas

Nunca cortar:

- Tablas de registros.
- Tablas eléctricas.
- Tablas de configuración.
- Tablas de pines.
- Tablas de valores permitidos.

Si una tabla es demasiado grande:

Dividir únicamente por bloques completos conservando:

- Nombre de tabla.
- Encabezados.
- Contexto.
- Unidad de medida.
- Referencia original.

---

## Fórmulas

Nunca separar:

- Fórmula.
- Variables.
- Definición de variables.
- Unidades.
- Condiciones de aplicación.

---

## Diagramas y figuras

Cuando una figura sea relevante mantener juntos:

- Imagen o referencia.
- Descripción.
- Componentes involucrados.
- Interpretación técnica.

Nunca dejar una explicación sin el contexto visual necesario.

---

# Código fuente

Mantener:

- Código completo.
- Dependencias.
- Librerías.
- Configuración utilizada.
- Explicación del funcionamiento.

No dividir funciones relacionadas.

---

# Tamaño recomendado de chunks

El tamaño debe adaptarse al contenido.

Valores iniciales:

Documentación técnica general:

300 - 800 tokens.

Secciones altamente relacionadas:

800 - 1200 tokens.

Información crítica:

Puede superar el límite recomendado si es necesario conservar la integridad técnica.

Nunca dividir únicamente por cantidad de tokens.

---

# Metadatos obligatorios

Cada chunk generado debe incluir:

Chunk ID:

Documento:

Fabricante:

Dispositivo:

Familia:

Categoría:

Sección original:

Subsección:

Página origen:

Tema principal:

Subtemas:

Nivel de importancia:

Palabras clave:

Conceptos relacionados:

Relaciones técnicas:

Dependencias:

---

# Formato de salida esperado

Documento analizado:

Estrategia utilizada:

Criterios de segmentación:

Cantidad estimada de chunks:

Observaciones:

================================

Chunk ID:

Título:

Contenido:

Metadatos:

Relaciones técnicas:

================================

---

# Validaciones antes de finalizar

Antes de entregar los chunks verificar:

✓ Cada chunk representa una unidad técnica completa.

✓ El contenido conserva suficiente contexto.

✓ No existen temas mezclados.

✓ Las tablas permanecen completas.

✓ Las fórmulas conservan variables y unidades.

✓ Los ejemplos mantienen sus dependencias.

✓ Los metadatos permiten filtrado posterior.

✓ El chunk puede responder una consulta independiente.

✓ No se modificó el contenido original.

---

# Nunca hacer

Nunca:

- Dividir únicamente por número de caracteres.
- Dividir únicamente por número de páginas.
- Cortar tablas técnicas.
- Separar una configuración de su explicación.
- Separar una fórmula de sus variables.
- Eliminar información para reducir tamaño.
- Mezclar múltiples dispositivos sin indicarlo.
- Mezclar diferentes periféricos sin contexto.
- Crear embeddings de documentos sin estructura.
- Modificar el contenido original del fabricante.
- Perder referencias de origen.

---

# Objetivo final

El resultado de esta skill debe ser una colección de chunks optimizados para un sistema RAG técnico, donde cada fragmento conserve:

- Contexto suficiente.
- Información técnicamente correcta.
- Relaciones entre conceptos.
- Metadatos completos.
- Alta capacidad de recuperación semántica.

Los chunks generados deben permitir que agentes posteriores puedan responder preguntas técnicas de ingeniería con precisión.