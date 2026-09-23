"""Generación de especificaciones Markdown, metadatos JSON para lote Electrónica."""
from pathlib import Path
import json

L6_TIMERS_MD = """# Información general

- **Nombre del componente:** Embedded Timers & Interrupt Systems
- **Documento:** ECE 18-349 Lecture 6: Timers and Interrupts
- **Autor / Institución:** Anthony Rowe, Carnegie Mellon University (ECE Department)
- **Familia:** Embedded Systems Fundamentals / Real-Time Systems Architecture
- **Tipo de documento:** Lecture Notes / Guía Técnica de Referencia Académica
- **Enfoque técnico:** Arquitectura de temporizadores por hardware, generación de señales PWM, captura/comparación y diseño determinista de sistemas dirigidos por interrupción

# Características operativas y conceptos clave

## Estructura de Temporizadores por Hardware
- **Reloj base (f_clk):** Fuente de frecuencia primaria provista por el oscilador del sistema o bus periférico.
- **Divisor previo (Prescaler - PSC):** Registro divisor que reduce la frecuencia base del temporizador:
  $$f_{\\text{timer}} = \\frac{f_{\\text{clk}}}{\\text{PSC} + 1}$$
- **Contador principal (Counter Register - CNT):** Registro de conteo progresivo (Up-counting), regresivo (Down-counting) o bidireccional (Center-aligned).
- **Registro de recarga automática (Auto-Reload Register - ARR / Period):** Determina el valor máximo de conteo antes del desbordamiento (Overflow/Update event):
  $$T_{\\text{periodo}} = \\frac{(\\text{ARR} + 1) \\times (\\text{PSC} + 1)}{f_{\\text{clk}}}$$
  $$f_{\\text{periodo}} = \\frac{f_{\\text{clk}}}{(\\text{ARR} + 1) \\times (\\text{PSC} + 1)}$$

## Modos de Operación de Temporizadores
- **Temporización periódica básica:** Generación de eventos periódicos para activación de tareas temporizadas o bases de tiempo del sistema operativo de tiempo real (RTOS tick).
- **Salida de Comparación (Output Compare - OC):**
  - Modifica el estado lógico de un pin de salida cuando el contador `CNT` alcanza el valor configurado en el registro de comparación `CCR`.
  - Permite generar pulsos de duración exacta sin intervención continua de la CPU.
- **Modulación por Ancho de Pulsos (PWM):**
  - Señal de frecuencia fija con ciclo de trabajo programable mediante el registro `CCR`:
    $$\\text{Duty Cycle (\\%)} = \\left( \\frac{\\text{CCR}}{\\text{ARR}} \\right) \\times 100\\%$$
  - Modos: PWM alineado al borde (Edge-aligned) y PWM centrado (Center-aligned para control de motores trifásicos y reducción de armónicos).
- **Captura de Entrada (Input Capture - IC):**
  - Almacena el valor instantáneo del contador `CNT` en un registro de retención ante la transición de flanco (subida, bajada o ambos) en un pin externo.
  - Usado para medir con resolución de microsegundos periodos de señal, tiempos en alto, frecuencias y decodificación de señales PPM/sensores ultrasónicos (HC-SR04).

# Arquitectura y Manejo de Interrupciones

## Comparativa: Sondeo (Polling) vs. Interrupciones (Interrupts)
- **Sondeo (Polling):** La CPU consulta repetidamente el estado de un flag de hardware; genera desperdicio de ciclos de CPU y latencia dependiente de la longitud del bucle de ejecución.
- **Interrupciones (Interrupts):** El evento de hardware suspende asíncronamente el flujo de ejecución normal para atender la rutina de servicio correspondiente; optimiza el consumo de energía permitiendo modos de suspensión (Sleep/WFI).

## Componentes del Sistema de Interrupción
- **Líneas de Solicitud de Interrupción (IRQ):** Líneas físicas dedicadas que conectan periféricos con el controlador de interrupciones.
- **Controlador de Interrupciones (NVIC / PIC / GIC):** Circuito en chip que administra prioridades, enmascaramiento y anidamiento.
- **Tabla de Vectores de Interrupción (IVT):** Bloque de memoria fija que contiene los punteros a las direcciones de inicio de cada rutina de servicio (ISR).

## Anatomía y Ciclo de Vida de una Interrupción
1. **Detección del evento:** El hardware periférico establece el flag de estado y emite la señal de IRQ.
2. **Priorización:** El controlador evalúa si la interrupción está habilitada global e individualmente y si su prioridad supera a la tarea actual.
3. **Guardado de contexto (Context Stacking):** Se almacenan automáticamente en el Stack los registros del procesador (en ARM Cortex-M: R0-R3, R12, LR, PC, xPSR).
4. **Ejecución de la ISR:** El vector salta a la rutina de interrupción correspondiente.
5. **Limpieza de flag:** La ISR debe limpiar el flag de interrupción en el periférico para evitar reinvocaciones recursivas indeseadas.
6. **Restauración de contexto (Unstacking):** La instrucción de retorno de excepción restaura los registros y reanuda el programa principal.

## Latencia de Interrupción y Jitter
- **Latencia de interrupción:** Intervalo de tiempo transcurrido entre la ocurrencia física del evento de hardware y la ejecución de la primera instrucción dentro de la ISR.
- **Factores de jitter:**
  - Finalización de instrucciones no interrumpibles o de ciclo múltiple.
  - Estado de secciones críticas con interrupciones deshabilitadas globalmente (`cli()` / `__disable_irq()`).
  - Preempción por interrupciones de mayor prioridad concurrentes.

# Aplicaciones y Mejores Prácticas en Sistemas Embebidos

- **Regla fundamental de ISR:** Mantener las rutinas de servicio breves, no bloqueantes y deterministas. Nunca invocar funciones de retardo (`delay()`, `sleep()`), operaciones I/O lentas ni reservas dinámicas de memoria dentro de una ISR.
- **Comunicación entre ISR y Bucle Principal:** Utilizar variables compartidas calificadas con `volatile` o buffers circulares / colas atómicas.
- **Antirrebote (Debounce) de botones:** Utilizar un temporizador periódico (10 ms - 20 ms) para muestrear niveles estables en lugar de conectar botones mecánicos directamente a interrupciones externas por flanco.

# Limitaciones y Advertencias

- **Desbordamiento de pila (Stack Overflow):** Interrupciones excesivamente anidadas o variables locales pesadas en ISRs pueden agotar la memoria SRAM de la pila en microcontroladores con recursos limitados.
- **Condiciones de carrera (Race Conditions):** El acceso a datos de múltiples bytes (ej. enteros de 32 bits en AVR de 8 bits) compartido entre una ISR y el bucle principal requiere deshabilitar interrupciones durante la lectura/escritura (sección crítica).
"""

L6_TIMERS_JSON = {
  "file_name": "L6-Timers-and-Interrupts.pdf",
  "processed_file": "data/processed/electronica/L6-Timers-and-Interrupts.md",
  "source_path": "data/raw/Microcontroladores_RAG_Documentacion/Electronica/L6-Timers-and-Interrupts.pdf",
  "category": "Electronica",
  "type": "Lecture Notes / Academic Guide",
  "component": "Embedded Timers & Interrupt Systems",
  "manufacturer": "Carnegie Mellon University (ECE 18-349)",
  "family": "Embedded Systems Fundamentals",
  "interfaces": [
    "PWM",
    "GPIO"
  ],
  "voltage": {
    "logic_levels": "Depende de la arquitectura del microcontrolador anfitrión (3.3V / 5V)"
  },
  "temperature_range": {
    "min": "unknown",
    "max": "unknown"
  },
  "topics": [
    "Arquitectura de temporizadores: prescaler, contador y registro de recarga automática (ARR)",
    "Generación de PWM alineado al borde y centrado con cálculo de ciclo de trabajo",
    "Captura de entrada para medición de frecuencia y ancho de pulso",
    "Comparación de salida para temporización determinista",
    "Mecanismos de interrupción frente a sondeo (polling)",
    "Tabla de vectores de interrupción (IVT), guardado y restauración de contexto",
    "Latencia de interrupción, jitter y secciones críticas con variables volatile"
  ],
  "critical_params": {
    "timer_types": "Prescaled, Auto-reload, Input Capture, Output Compare, PWM",
    "isr_design_rule": "Non-blocking, minimal latency, volatile flags",
    "pwm_modes": "Edge-aligned, Center-aligned",
    "context_switching": "Hardware register stacking/unstacking"
  },
  "keywords": [
    "Timers",
    "Interrupts",
    "ISR",
    "PWM",
    "Prescaler",
    "Auto-reload",
    "Input Capture",
    "Output Compare",
    "NVIC",
    "Latency",
    "Jitter",
    "Volatile"
  ],
  "issues_found": [
    "Documento de diapositivas académicas de CMU; condensado en especificación técnica estructurada preservando fórmulas de temporización y reglas de diseño."
  ]
}

NOTE_ADC_DAC_MD = """# Información general

- **Nombre del componente:** ADC & DAC Data Acquisition Systems
- **Documento:** SIC1203 Measurements & Instrumentation - Unit V: Data Acquisition
- **Autor / Institución:** Ms. D. Jamuna Rani, Ms. S. Celin - Sathyabama University
- **Familia:** Instrumentation and Electronics / Mixed-Signal Systems
- **Tipo de documento:** Course Notes / Technical Reference Guide
- **Enfoque técnico:** Principios de conversión analógico-digital (ADC) y digital-analógica (DAC), arquitecturas de circuito, parámetros de rendimiento y sistemas de adquisición de datos (DAS)

# Estructura del Sistema de Adquisición de Datos (DAS)

Un sistema de adquisición de datos para instrumentación y sistemas embebidos se compone de las siguientes etapas en cascada:
1. **Transductores / Sensores:** Convierten variables físicas (temperatura, presión, desplazamiento) en señales eléctricas de voltaje o corriente.
2. **Acondicionamiento de Señal:** Amplificación (amplificadores de instrumentación), filtrado analógico paso-bajo (antialiasing) y aislamiento galvánico.
3. **Multiplexor Analógico (MUX):** Conmuta múltiples canales de entrada hacia una única etapa de conversión.
4. **Circuito de Muestreo y Retención (Sample and Hold - S/H):** Mantiene constante el voltaje analógico durante el intervalo de conversión del ADC para evitar errores de apertura.
5. **Convertidor Analógico a Digital (ADC):** Cuantifica y codifica la señal analógica muestreada en una palabra binaria.
6. **Procesador Digital / Microcontrolador:** Procesa, almacena o transmite los datos.
7. **Convertidor Digital a Analógico (DAC):** Reconstruye señales analógicas para control de actuadores.

# Convertidores Analógico-Digitales (ADC)

## Parámetros Fundamentales de Desempeño
- **Resolución:** Número de bits ($n$) que cuantifican el rango de voltaje de entrada. El paso mínimo cuantificado (Voltaje del LSB) es:
  $$V_{\\text{LSB}} = \\frac{V_{\\text{ref}}}{2^n}$$
- **Error de Cuantificación:** Incertidumbre inherente al proceso de redondeo discreto, acotada en:
  $$\\text{Error de cuantificación} = \\pm \\frac{1}{2} V_{\\text{LSB}}$$
- **Tiempo de Conversión:** Duración requerida desde el pulso de inicio de conversión (Start of Conversion - SOC) hasta la activación de la señal de fin de conversión (End of Conversion - EOC).
- **Linealidad:**
  - **DNL (Differential Non-Linearity):** Desviación del ancho de un paso real respecto al paso ideal de 1 LSB. Si $\\text{DNL} < -1\\text{ LSB}$, el ADC pierde monotonicidad (códigos faltantes).
  - **INL (Integral Non-Linearity):** Desviación máxima de la curva de transferencia real respecto a la línea recta ideal.

## Arquitecturas Principales de ADC
### 1. Flash ADC (Comparadores en Paralelo)
- **Principio:** Utiliza una red divisora resistiva de referencia y $2^n - 1$ comparadores que operan simultáneamente, seguidos de un decodificador de prioridad.
- **Ventaja:** Velocidad máxima (conversión en un solo ciclo de reloj, tiempos en nanosegundos).
- **Desventaja:** Alta disipación de potencia y complejidad exponencial; limitado típicamente a resoluciones de 6 a 8 bits.

### 2. ADC de Aproximaciones Sucesivas (SAR)
- **Principio:** Utiliza un comparador, un registro SAR y un DAC interno. Realiza una búsqueda binaria bit por bit desde el MSB hasta el LSB.
- **Tiempo de conversión:** Fijo a $n$ ciclos de reloj para $n$ bits de resolución.
- **Ventaja:** Excelente equilibrio entre velocidad moderada/alta (hasta varios MSps), bajo consumo y resoluciones típicas de 10, 12 a 16 bits. Es la arquitectura estándar en ATmega328P, STM32 y ESP32.

### 3. ADC de Doble Rampa (Dual-Slope Integrating)
- **Principio:** Integra la señal de entrada analógica durante un tiempo fijo $T_1$, y luego descarga el integrador con una referencia conocida inversa midiendo el tiempo $T_2$ requerido para cruzar cero.
- **Ventaja:** Rechazo intrínseco de ruido de red (50/60 Hz) y alta inmunidad a derivas de componentes.
- **Desventaja:** Conversión muy lenta (decenas de milisegundos). Ideal para multímetros digitales e instrumentación de precisión lenta.

### 4. ADC Sigma-Delta ($\Sigma\Delta$)
- **Principio:** Modulación de sobremuestreo a alta frecuencia de un solo bit combinada con modelado de ruido (Noise Shaping) y filtrado digital diezmador.
- **Ventaja:** Resoluciones ultra altas (16 a 24 bits) con alto rango dinámico y bajo costo.

# Convertidores Digital-Analógicos (DAC)

## 1. DAC de Resistencias Ponderadas Binarias (Binary-Weighted DAC)
- Utiliza resistencias con valores escalados en potencias de 2 ($R, 2R, 4R, 8R, \\dots, 2^{n-1}R$) conectadas al nodo inversor de un amplificador operacional.
- Limitación: Dificultad para mantener tolerancias estrictas en un rango amplio de valores resistivos en circuitos integrados de alta resolución.

## 2. DAC en Escalera R-2R (R-2R Ladder Network)
- Utiliza únicamente dos valores de resistencia: $R$ y $2R$.
- La corriente se divide binariamente en cada nodo de la escalera hacia la tierra virtual del amplificador operacional.
- Ventaja: Fácil fabricación y ajuste térmico idéntico en silicio; arquitectura estándar para DACs de alta resolución.

# Teorema del Muestreo y Filtro Antialiasing

- **Criterio de Nyquist-Shannon:** Para reconstruir sin ambigüedad una señal analógica de banda limitada con frecuencia máxima $f_{\\text{max}}$, la tasa de muestreo $f_s$ debe cumplir:
  $$f_s \\ge 2 \\times f_{\\text{max}}$$
- **Filtro Antialiasing:** Filtro paso-bajo analógico colocado antes de la etapa de muestreo para eliminar componentes de frecuencia superiores a $f_s / 2$, previniendo el solapamiento de frecuencias (aliasing).

# Aplicaciones

- Interfaces de sensores analógicos en microcontroladores (temperatura, fotoceldas, potenciómetros, transductores de corriente).
- Generación de formas de onda arbitrarias y control analógico de referencia mediante DAC.
- Osciloscopios digitales y registradores de datos industriales.
- Sistemas de audio digital y procesamiento digital de señales (DSP).

# Limitaciones y Advertencias

- **Impedancia de entrada del ADC:** Fuentes de señal con impedancia superior a la especificada por el fabricante (ej. > 10 kΩ en ATmega328P) aumentan el tiempo de carga del capacitor de muestreo y degradan severamente la precisión.
- **Ruido en líneas de referencia:** Cualquier fluctuación o rizado en el pin de voltaje de referencia ($V_{\\text{ref}}$) se traduce directamente en error proporcional en todos los códigos convertidos.
"""

NOTE_ADC_DAC_JSON = {
  "file_name": "note_1474198148.pdf",
  "processed_file": "data/processed/electronica/note_1474198148.md",
  "source_path": "data/raw/Microcontroladores_RAG_Documentacion/Electronica/note_1474198148.pdf",
  "category": "Electronica",
  "type": "Course Notes / Technical Reference Guide",
  "component": "ADC & DAC Data Acquisition Systems (SIC1203)",
  "manufacturer": "Sathyabama University / Academic",
  "family": "Instrumentation and Electronics",
  "interfaces": [
    "ADC",
    "DAC"
  ],
  "voltage": {
    "vref": "Voltaje de referencia configurable según circuito"
  },
  "temperature_range": {
    "min": "unknown",
    "max": "unknown"
  },
  "topics": [
    "Etapas del sistema de adquisición de datos (DAS): acondicionamiento, MUX, S/H, ADC, DAC",
    "Parámetros métricos: resolución, V_LSB, error de cuantificación, tiempo de conversión, DNL e INL",
    "Arquitecturas de ADC: Flash, Aproximaciones Sucesivas (SAR), Doble Rampa y Sigma-Delta",
    "Arquitecturas de DAC: Resistencias ponderadas binarias y red en escalera R-2R",
    "Teorema del muestreo de Nyquist-Shannon y filtros analógicos antialiasing",
    "Efecto de la impedancia de fuente y ruido de referencia en la precisión de conversión"
  ],
  "critical_params": {
    "adc_architectures": "Flash, SAR, Dual Slope, Sigma-Delta",
    "dac_architectures": "Binary Weighted, R-2R Ladder",
    "sampling_condition": "fs >= 2 * fmax",
    "quantization_uncertainty": "+/- 0.5 LSB"
  },
  "keywords": [
    "ADC",
    "DAC",
    "SAR",
    "Flash ADC",
    "Dual Slope",
    "Sigma Delta",
    "R-2R Ladder",
    "Quantization Error",
    "Nyquist",
    "Resolution",
    "INL",
    "DNL"
  ],
  "issues_found": [
    "Documento de notas de cátedra universitaria sobre instrumentación; procesado y estructurado según especificación técnica formal."
  ]
}

TL5001A_MD = """# Información general

- **Nombre del componente:** TL5001A-Q1
- **Fabricante:** Texas Instruments
- **Familia:** Automotive Power Management / PWM Controllers
- **Tipo de dispositivo:** Circuito integrado de control modulador por ancho de pulsos (PWM) para fuentes conmutadas
- **Calificación:** Calificado para aplicaciones automotrices bajo estándar AEC-Q100 Grado 1
- **Rango de tensión de alimentación (VCC):** 3.6 V a 40 V
- **Frecuencia de oscilación:** 20 kHz a 500 kHz (ajustable mediante componentes pasivos externos)
- **Tensión de referencia de precisión:** 1.0 V ± 1.5% a 25 °C (± 2.5% en todo el rango térmico)
- **Encapsulado:** 8-pin SOIC (D) y 8-pin TSSOP (PW)

# Características eléctricas

## Valores Máximos Absolutos
- **Tensión de alimentación (VCC):** 41 V
- **Tensión en pin de salida (OUT):** 41 V
- **Corriente de salida en colector de salida:** 21 mA
- **Corriente pico de salida:** 50 mA
- **Rango de temperatura de operación en unión (TJ):** -40 °C a 125 °C
- **Temperatura de almacenamiento:** -65 °C a 150 °C

## Condiciones Recomendadas de Operación
- **Tensión de alimentación (VCC):** 3.6 V a 40 V
- **Frecuencia de oscilador:** 20 kHz a 500 kHz
- **Resistencia de temporización (RT):** 10 kΩ a 250 kΩ
- **Capacitancia de temporización (CT):** 100 pF a 10,000 pF
- **Temperatura de operación ambiente:** -40 °C a 125 °C

## Especificaciones Eléctricas Clave (a 25 °C, VCC = 6 V, f_osc = 100 kHz)
- **Tensión de referencia (Vref):** 1.000 V (mín: 0.985 V, máx: 1.015 V)
- **Variación de referencia por línea (Line Regulation):** 2 mV típico (3.6 V ≤ VCC ≤ 40 V)
- **Corriente de polarización del amplificador de error:** 0.1 µA típico
- **Ganancia en lazo abierto del amplificador de error:** 80 dB típico
- **Umbral de bloqueo por subtensión (UVLO):** 2.7 V típico (histéresis de 0.1 V)
- **Umbral de protección contra cortocircuitos (SCP):** 1.0 V

# Interfaces y Periféricos

- **Oscilador Integrado:** Genera la rampa de diente de sierra mediante la carga y descarga lineal del capacitor externo `CT` gobernada por la resistencia `RT`:
  $$f_{\\text{osc}} \\approx \\frac{1}{R_T \\times C_T}$$
- **Amplificador de Error:** Amplificador diferencial con entrada no inversora interna conectada a la referencia de 1.0 V y entrada inversora accesible en pin `FB`.
- **Comparador PWM:** Compara la salida del amplificador de error (`COMP`) con la señal de rampa del oscilador para modular el ancho del pulso de salida.
- **Control de Tiempo Muerto (Dead-Time Control - DTC):** Permite fijar un límite máximo al ciclo de trabajo para evitar la saturación de transformadores o la conducción simultánea en topologías push-pull.
- **Arranque Suave (Soft-Start) y Protección contra Cortocircuito (SCP):** Pin compartido `DTC/SCP` que permite elevar gradualmente el ciclo de trabajo en el arranque y apagar el convertidor si la sobrecarga persiste.
- **Etapa de Salida:** Transistor bipolar con salida de colector abierto que puede conectarse directamente a la base de transistores bipolares de potencia o al gate de MOSFETs de canal P o canal N (con circuito inversor/driver).

# Pines importantes y Descripción Funcional

### Mapeo de Pines (Encapsulado SOIC 8 pines)
| Pin | Nombre | Tipo | Descripción Funcional |
|---|---|---|---|
| 1 | OUT | Salida | Salida PWM a colector abierto para excitación de etapa de potencia |
| 2 | VCC | Alimentación | Entrada de alimentación positiva del circuito integrado (3.6 V a 40 V) |
| 3 | COMP | Entrada/Salida | Salida del amplificador de error y entrada del comparador PWM; nodo para red de compensación |
| 4 | FB | Entrada | Entrada inversora del amplificador de error para lazo de realimentación de tensión |
| 5 | GND | Masa | Conexión de referencia y tierra del circuito integrado |
| 6 | RT | Entrada analógica | Resistencia externa de temporización a GND que fija la corriente de oscilación |
| 7 | CT | Entrada analógica | Capacitor externo de temporización a GND que fija la frecuencia del oscilador |
| 8 | DTC/SCP | Entrada analógica | Control de tiempo muerto, arranque suave y temporizador de retardo de protección contra cortocircuito |

# Aplicaciones

- Fuentes conmutadas automotrices DC-DC elevadoras (Boost), reductoras (Buck) e inversoras (Inverting/Flyback).
- Controladores PWM para retroiluminación LCD y balastos en tableros de instrumentos vehiculares.
- Reguladores de tensión auxiliares en sistemas de control de transmisión y gestión de batería (BMS).
- Fuentes de alimentación industriales aisladas de amplio rango de entrada.

# Limitaciones y Advertencias

- **Tensión de referencia baja:** Dado que Vref interna es de 1.0 V, los divisores resistivos de realimentación deben dimensionarse con resistencias de precisión para no degradar la relación señal/ruido.
- **Corriente de salida máxima limitada:** La corriente de salida continua es de 21 mA; no conectar directamente gates de MOSFETs de gran capacitancia sin un buffer o driver push-pull intermedio en frecuencias superiores a 100 kHz.
- **Disipación térmica:** El encapsulado SOIC-8 disipa típicamente hasta 700 mW a 25 °C con degradación térmica de 5.8 mW/°C para temperaturas superiores.
"""

TL5001A_JSON = {
  "file_name": "tl5001a-q1.pdf",
  "processed_file": "data/processed/electronica/tl5001a-q1.md",
  "source_path": "data/raw/Microcontroladores_RAG_Documentacion/Electronica/tl5001a-q1.pdf",
  "category": "Electronica",
  "type": "Datasheet",
  "component": "TL5001A-Q1",
  "manufacturer": "Texas Instruments",
  "family": "Automotive Power Management / PWM Controllers",
  "interfaces": [
    "PWM"
  ],
  "voltage": {
    "vcc_range": "3.6V - 40V",
    "vref": "1.0V +/- 1.5%",
    "abs_max_vcc": "41V"
  },
  "temperature_range": {
    "min": "-40 °C",
    "max": "125 °C"
  },
  "topics": [
    "Controlador PWM para fuentes conmutadas DC-DC automotrices",
    "Tensión de operación de 3.6 V a 40 V y frecuencia de 20 kHz a 500 kHz",
    "Oscilador temporizado por resistencia RT y capacitor CT",
    "Lazo de control con amplificador de error y referencia interna de 1.0 V",
    "Arranque suave, control de tiempo muerto (DTC) y protección contra cortocircuito (SCP)",
    "Bloqueo por subtensión (UVLO) a 2.7 V",
    "Distribución de pines en encapsulados SOIC-8 y TSSOP-8"
  ],
  "critical_params": {
    "vcc_min": "3.6 V",
    "vcc_max": "40 V",
    "vref_v": 1.0,
    "osc_freq_min_khz": 20,
    "osc_freq_max_khz": 500,
    "max_collector_current_ma": 21,
    "uvlo_threshold_v": 2.7
  },
  "keywords": [
    "TL5001A",
    "TL5001A-Q1",
    "Texas Instruments",
    "PWM Controller",
    "AEC-Q100",
    "DC-DC",
    "Buck",
    "Boost",
    "Flyback",
    "UVLO",
    "Dead Time Control",
    "Soft Start"
  ],
  "issues_found": [
    "Datasheet técnico de componentes analógicos de TI; procesado y normalizado conforme a las habilidades datasheet-analyzer y technical-document-cleaner."
  ]
}

def write_electronica_docs():
    p_proc = Path("data/processed/electronica")
    p_meta = Path("data/metadata/electronica")
    p_proc.mkdir(parents=True, exist_ok=True)
    p_meta.mkdir(parents=True, exist_ok=True)

    # 1. L6-Timers
    (p_proc / "L6-Timers-and-Interrupts.md").write_text(L6_TIMERS_MD, encoding="utf-8")
    with open(p_meta / "L6-Timers-and-Interrupts.json", "w", encoding="utf-8") as f:
        json.dump(L6_TIMERS_JSON, f, indent=2, ensure_ascii=False)
    print("Wrote L6-Timers-and-Interrupts.md and json")

    # 2. Note ADC DAC
    (p_proc / "note_1474198148.md").write_text(NOTE_ADC_DAC_MD, encoding="utf-8")
    with open(p_meta / "note_1474198148.json", "w", encoding="utf-8") as f:
        json.dump(NOTE_ADC_DAC_JSON, f, indent=2, ensure_ascii=False)
    print("Wrote note_1474198148.md and json")

    # 3. TL5001A
    (p_proc / "tl5001a-q1.md").write_text(TL5001A_MD, encoding="utf-8")
    with open(p_meta / "tl5001a-q1.json", "w", encoding="utf-8") as f:
        json.dump(TL5001A_JSON, f, indent=2, ensure_ascii=False)
    print("Wrote tl5001a-q1.md and json")

if __name__ == "__main__":
    write_electronica_docs()
