"""Generación de especificaciones Markdown, metadatos JSON para lote Raspberry Pi."""
from pathlib import Path
import json

PICO_BOARD_MD = """# Información general

- **Nombre del componente:** Raspberry Pi Pico Board
- **Documento:** Raspberry Pi Pico Datasheet (RP-008307-DS-2)
- **Fabricante:** Raspberry Pi Ltd
- **Familia:** RP2040 Development Boards
- **Tipo de dispositivo:** Placa de desarrollo para microcontroladores basada en el silicio RP2040
- **Microcontrolador principal:** RP2040 diseñado por Raspberry Pi en Reino Unido
- **Núcleos de procesamiento:** Dual ARM Cortex-M0+ con reloj flexible de hasta 133 MHz
- **Memoria Flash en placa:** 2 MB de memoria Flash QSPI integrada (Winbond W25Q16JVUXIQ) conectada mediante interfaz SPI cuádruple dedicada
- **Memoria SRAM:** 264 kB de memoria SRAM en chip integrada en el procesador RP2040
- **Factor de forma:** Placa compacta de 21 mm × 51 mm, formato DIP de 40 pines con separación estándar de 2.54 mm (0.1") y bordes almenados (Castellated holes) para montaje superficial directo como módulo SMT
- **Conector de programación y datos:** Puerto micro-USB B para alimentación de 5 V y comunicación USB 1.1 (dispositivo y host)
- **Botón de usuario:** Pulsador `BOOTSEL` para activar el modo de programación por almacenamiento masivo USB (UF2) sin herramientas externas

# Características eléctricas y de Alimentación

## Arquitectura de la Fuente de Alimentación
- **Regulador en placa:** Convertidor conmutado Buck-Boost integrado (Richtek RT6150B / RT6154A) de alta eficiencia capaz de generar un riel fijo de **3.3 V** con una corriente de hasta **300 mA** para alimentar periféricos externos:
  - Permite alimentar la placa a través del pin `VSYS` con un amplio rango de tensiones: **1.8 V a 5.5 V**.
  - Admite alimentación directa mediante 2 o 3 pilas alcalinas AA/AAA (1.8 V - 4.5 V), una celda de iones de litio Li-Po (3.7 V - 4.2 V) o alimentación USB de 5 V.
- **Diodo Schottky de protección:** Diodo integrado (BAT54) entre el pin `VBUS` (5 V del puerto micro-USB) y el pin `VSYS` para permitir la coexistencia segura de alimentación USB y batería externa simultáneamente.

## Pines de Alimentación Principales
- **VBUS (Pin 40):** Entrada de alimentación de 5 V directamente desde el conector micro-USB (después del fusible de protección).
- **VSYS (Pin 39):** Tensión principal de entrada al convertidor Buck-Boost (1.8 V a 5.5 V).
- **3V3_EN (Pin 37):** Pin de habilitación del regulador Buck-Boost en placa (fijado a HIGH mediante pull-up; conectar a GND para apagar todo el riel de 3.3 V).
- **3V3 (Pin 36):** Salida del riel regulado de 3.3 V (alimentación del RP2040 y circuitos externos).
- **ADC_VREF (Pin 35):** Entrada de tensión de referencia analógica filtrada para el convertidor ADC (conectada internamente a 3.3 V mediante filtro RC con opción de referencia externa).
- **AGND (Pin 33):** Tierra analógica de bajo ruido dedicada para la etapa del conversor analógico-digital.

# Interfaces y Periféricos en la Placa

- **GPIO accesibles:** 26 pines GPIO expuestos en las cabeceras externas (GPIO0 a GPIO22 y GPIO26 a GPIO28).
- **Entradas analógicas (ADC):** 3 canales analógicos accesibles externamente:
  - ADC0 en GPIO26 (Pin 31).
  - ADC1 en GPIO27 (Pin 32).
  - ADC2 en GPIO28 (Pin 34).
  - ADC3 (interno): Conectado a un divisor de tensión interno ($VSYS / 3$) para monitorizar la tensión de batería.
  - Sensor de temperatura interno: Integrado en el chip RP2040 y accesible como 5º canal del ADC.
- **Pines GPIO de Uso Interno en la Placa:**
  - **GPIO23:** Controla el pin `PS` (Power Save) del regulador Buck-Boost. Nivel BAJO activa modo PFM (bajo consumo con mayor rizado); nivel ALTO activa modo PWM forzado (menor rizado analógico).
  - **GPIO24:** Monitor de detección de conexión del cable USB (VBUS sense).
  - **GPIO25:** Conectado directamente al LED verde de usuario en la placa.
  - **GPIO29:** Entrada analógica ADC3 para monitorización de $V_{SYS}$.
- **Interfaz de Depuración Serial Wire Debug (SWD):**
  - Conector de 3 pads pasantes situado en el extremo inferior de la placa (SWCLK, GND, SWDIO) para depuración en tiempo real con sondas CMSIS-DAP o Raspberry Pi Debug Probe.

# Pines importantes y Mapeo Funcional (Conector de 40 Pines)

| Pin | Nombre | Tipo | Funciones Periféricas Disponibles |
|---|---|---|---|
| 1, 2 | GP0, GP1 | I/O | UART0 TX/RX, I2C0 SDA/SCL, SPI0 RX/CS, PWM0 A/B |
| 4, 5 | GP2, GP3 | I/O | I2C1 SDA/SCL, SPI0 SCK/TX, PWM1 A/B |
| 6, 7 | GP4, GP5 | I/O | UART1 TX/RX, I2C0 SDA/SCL, SPI0 RX/CS, PWM2 A/B |
| 9, 10 | GP6, GP7 | I/O | I2C1 SDA/SCL, SPI0 SCK/TX, PWM3 A/B |
| 11, 12 | GP8, GP9 | I/O | UART1 TX/RX, I2C0 SDA/SCL, SPI1 RX/CS, PWM4 A/B |
| 14, 15 | GP10, GP11 | I/O | I2C1 SDA/SCL, SPI1 SCK/TX, PWM5 A/B |
| 16, 17 | GP12, GP13 | I/O | UART0 TX/RX, I2C0 SDA/SCL, SPI1 RX/CS, PWM6 A/B |
| 19, 20 | GP14, GP15 | I/O | I2C1 SDA/SCL, SPI1 SCK/TX, PWM7 A/B |
| 21, 22 | GP16, GP17 | I/O | UART0 TX/RX, I2C0 SDA/SCL, SPI0 RX/CS, PWM0 A/B |
| 24, 25 | GP18, GP19 | I/O | I2C1 SDA/SCL, SPI0 SCK/TX, PWM1 A/B |
| 26, 27 | GP20, GP21 | I/O | UART1 TX/RX, I2C0 SDA/SCL, SPI0 RX/CS, PWM2 A/B |
| 29 | GP22 | I/O | PWM3 A |
| 30 | RUN | Input | Pin de Reset físico del RP2040 (activo en nivel BAJO) |
| 31 | GP26 | I/O / Analog | ADC0 / I2C1 SDA / UART1 CTS / PWM5 A |
| 32 | GP27 | I/O / Analog | ADC1 / I2C1 SCL / UART1 RTS / PWM5 B |
| 34 | GP28 | I/O / Analog | ADC2 / UART0 TX / I2C0 SDA / PWM6 A |
| 3, 8, 13, 18, 23, 28, 38 | GND | Power | Tierras digitales comunes distribuidas entre los buses de señal |

# Aplicaciones

- Prototipado y productos finales IoT con microcontroladores de 32 bits de bajo costo.
- Emulación de periféricos USB (teclados, ratones, joysticks, puertos serie CDC, MIDI).
- Control de motores y robótica educativa mediante canales PWM de hardware.
- Generación de señales complejas de alta velocidad (VGA, DVI, audio I2S) utilizando los bloques PIO del RP2040.

# Limitaciones y Advertencias

- **Tolerancia de niveles lógicos estrictamente a 3.3 V:** Los pines GPIO del RP2040 **NO son tolerantes a 5 V**; conectar directamente señales de 5 V destruirá irreversiblemente el pin o el chip.
- **Rango del convertidor ADC:** La tensión de entrada en los pines ADC (GP26..GP28) no debe exceder la tensión de `ADC_VREF` (máximo 3.3 V).
- **Rizado en modo de ahorro de energía (PFM):** Por defecto, si GP23 está en nivel bajo, el regulador conmuta a modo PFM generando picos de rizado de hasta 50 mV; para mediciones analógicas de precisión con el ADC, se debe fijar GP23 en nivel ALTO para activar el modo PWM forzado continuo.
"""

PICO_BOARD_JSON = {
  "file_name": "RP-008307-DS-2-pico-datasheet.pdf",
  "processed_file": "data/processed/raspberry_pi/RP-008307-DS-2-pico-datasheet.md",
  "source_path": "data/raw/Microcontroladores_RAG_Documentacion/Raspberry_Pi/RP-008307-DS-2-pico-datasheet.pdf",
  "category": "Raspberry_Pi",
  "type": "Datasheet",
  "component": "Raspberry Pi Pico Board",
  "manufacturer": "Raspberry Pi Ltd",
  "family": "RP2040 Development Boards",
  "interfaces": [
    "UART",
    "SPI",
    "I2C",
    "ADC",
    "PWM",
    "PIO",
    "USB",
    "GPIO"
  ],
  "voltage": {
    "vsys_input": "1.8V - 5.5V",
    "vbus_usb": "5.0V",
    "regulated_3v3": "3.3V +/- 300 mA",
    "gpio_logic_level": "3.3V strictly (NOT 5V tolerant)"
  },
  "temperature_range": {
    "min": "-20 °C",
    "max": "85 °C"
  },
  "topics": [
    "Arquitectura de la placa Raspberry Pi Pico y factor de forma de 40 pines con bordes almenados",
    "Fuente de alimentación conmutada Buck-Boost (1.8 V a 5.5 V en VSYS) con regulador de 3.3 V en placa",
    "Memoria Flash QSPI externa de 2 MB y botón de programación UF2 BOOTSEL",
    "Asignación de pines: 26 GPIOs accesibles, 3 canales analógicos ADC (0 a 2) y sensor de temperatura",
    "Pines internos: control de modo PWM/PFM del regulador (GP23), sensor VBUS (GP24) y LED (GP25)",
    "Interfaz de depuración por hardware SWD de 3 contactos",
    "Advertencia estricta de no tolerancia a 5 V en las líneas GPIO"
  ],
  "critical_params": {
    "mcu": "RP2040",
    "flash_mb": 2,
    "sram_kb": 264,
    "vsys_min_v": 1.8,
    "vsys_max_v": 5.5,
    "accessible_gpios": 26,
    "adc_channels_external": 3,
    "logic_tolerance_v": 3.3
  },
  "keywords": [
    "Raspberry Pi",
    "Pico",
    "RP2040",
    "VSYS",
    "VBUS",
    "Buck-Boost",
    "BOOTSEL",
    "UF2",
    "Castellated Holes",
    "3.3V Logic",
    "SWD"
  ],
  "issues_found": [
    "Datasheet de placa hardware oficial de Raspberry Pi de 31 páginas; condensado según especificación técnica estructurada."
  ]
}

RP2040_CHIP_MD = """# Información general

- **Nombre del componente:** RP2040 Microcontroller
- **Documento:** RP2040 Datasheet (RP-008371-DS-1)
- **Fabricante:** Raspberry Pi Ltd
- **Familia:** RP2040 Silicon Architecture
- **Tipo de dispositivo:** Microcontrolador de 32 bits de alto rendimiento y bajo costo diseñado en silicio TSMC de 40 nm LP
- **Procesador:** Dual-core ARM Cortex-M0+ con reloj nominal de hasta 133 MHz (soporte de overclock estable verificado a > 250 MHz)
- **Arquitectura de Memoria:**
  - **SRAM en chip (264 kB totales):** Dividida en 6 bancos físicos independientes (4 bancos principales entrelazados de 64 kB cada uno para permitir accesos simultáneos sin contención entre CPUs y DMA, más 2 bancos de 4 kB dedicados).
  - **Interfaz de Memoria Flash Externa:** Controlador QSPI con soporte de ejecución en el lugar (eXecute In Place - XIP) y memoria caché de instrucciones dedicada de 16 kB.
  - **Memoria ROM (16 kB):** Contiene el gestor de arranque USB (Mass Storage Device compatible con UF2), rutinas de coma flotante aceleradas por hardware y tablas de constantes trigonométricas.
- **Encapsulado:** QFN de 56 terminales de 7 mm × 7 mm (paso de pines de 0.4 mm) con pad térmico inferior expuesto

# Características eléctricas y Límites Operativos

## Valores Máximos Absolutos
- **Tensión de alimentación del núcleo digital (VREG_VOUT / DVDD):** 0.9 V a 1.25 V
- **Tensión en rieles de I/O digitales (IOVDD):** -0.5 V a 3.63 V
- **Tensión de alimentación analógica del ADC (ADC_AVDD):** -0.5 V a 3.63 V
- **Tensión en cualquier pin GPIO:** -0.5 V a IOVDD + 0.5 V (máximo absoluto 3.63 V)
- **Temperatura de almacenamiento:** -65 °C a +150 °C
- **Temperatura operativa ambiente:** -20 °C a +85 °C

## Condiciones Recomendadas de Operación
- **Riel de I/O digital (IOVDD):** 1.8 V a 3.3 V (Nominal: 3.3 V).
- **Riel del núcleo digital (DVDD):** 1.1 V nominal (generado por el regulador LDO programable integrado en el chip desde IOVDD).
- **Riel analógico (ADC_AVDD):** 1.98 V a 3.63 V (Nominal: 3.3 V).
- **Fuerza de excitación por pin GPIO (Drive Strength):** Programable por software a 2 mA, 4 mA, 8 mA o 12 mA.
- **Corriente máxima por pin GPIO:** 50 mA en condiciones transitorias de fallo.

# Periféricos y Módulos de Hardware

## 1. Bloques de E/S Programables (Programmable I/O - PIO)
El RP2040 cuenta con **2 bloques PIO idénticos**, cada uno con **4 máquinas de estado (State Machines - SM)** independientes (8 máquinas de estado en total):
- **Memoria de instrucciones compartida:** 32 palabras de código ensamblador PIO de 9 instrucciones nativas (`JMP`, `WAIT`, `IN`, `OUT`, `PUSH`, `PULL`, `MOV`, `IRQ`, `SET`).
- **Buffers FIFO:** Colas de 32 bits de 4 palabras para TX y RX (configurables como cola unidireccional de 8 palabras) vinculadas directamente a canales DMA.
- **Capacidad:** Permiten sintetizar en hardware periféricos no nativos sin sobrecarga de la CPU (interfaces de video VGA/DVI, audio digital I2S, controladores de tiras LED WS2812B, buses CAN, tarjetas SD a 4 bits o receptores Manchester).

## 2. Controlador DMA (Direct Memory Access)
- **12 canales DMA independientes** con prioridad programable.
- Soporte para transferencias de 8, 16 y 32 bits, descriptores encadenados (Chain to next channel), buffers en anillo (Ring buffers) y sincronización por temporizadores de paso (Pacing timers).
- Capacidad de transferir datos entre periféricos y SRAM a la velocidad de bus AHB sin intervención de la CPU.

## 3. Puertos Serie y de Comunicación
- **2x UARTs:** Controladores serie compatibles con ARM PrimeCell PL011 con generadores fraccionales de baud rate y colas FIFO de 32 bits.
- **2x SPIs:** Controladores serie síncronos compatibles con ARM PrimeCell PL022 con soporte maestro/esclavo y transferencias de 4 a 16 bits.
- **2x I2Cs:** Controladores compatibles con Synopsys DesignWare con soporte de maestro/esclavo y velocidades estándar (100k), rápida (400k) y rápida plus (1M).
- **1x Controlador USB 1.1:** Soporte de Host y Device con transceptor físico integrado (Full-Speed a 12 Mbps y Low-Speed a 1.5 Mbps) y memoria DPRAM dedicada de 4 kB.

## 4. Temporizadores y Módulos PWM
- **Módulo PWM:** 8 rebanadas PWM (PWM Slices) independientes; cada una controla 2 salidas (A y B) con contadores de 16 bits y prescaler fraccional de 8.4 bits (16 canales PWM en total).
- **Temporizador de 64 bits:** Base de tiempo de microsegundos continua con 4 alarmas independientes programables.
- **Watchdog Timer:** Temporizador guardián de 24 bits con arranque automático tras pérdida de alimentación.

## 5. Convertidor Analógico-Digital (ADC)
- **Arquitectura:** ADC de aproximaciones sucesivas (SAR) de **12 bits** con tasa de muestreo de hasta **500 kSps**.
- **Canales:** 4 canales multiplexados externamente (GPIO26 a GPIO29) más 1 canal interno conectado a un sensor de temperatura de diodo de silicio.

## 6. Generación de Relojes y Osciladores
- **ROSC:** Oscilador en anillo interno de bajo consumo (~6 MHz a 12 MHz) para arranque rápido.
- **XOSC:** Oscilador de cristal externo diseñado para resonadores de 1 MHz a 15 MHz (estándar: cristal de 12 MHz).
- **2x PLLs integrados:**
  - `PLL_SYS`: Multiplica la frecuencia del cristal hasta generar el reloj del sistema de 133 MHz (o superior).
  - `PLL_USB`: Genera una frecuencia fija de 48 MHz para el controlador USB y periféricos rápidos.

# Pines importantes y Mapeo Funcional (QFN-56)

- **GPIO0 a GPIO29 (Pines 2 a 31):** 30 líneas de E/S de propósito general configurables individualmente para funciones UART, SPI, I2C, PWM, PIO o GPIO simple.
- **QSPI_SD0..SD3, QSPI_SCLK, QSPI_SS_N (Pines 51 a 56):** Bus dedicado de alta velocidad para la memoria Flash SPI externa.
- **USB_DP / USB_DM (Pines 47, 48):** Terminales diferenciales USB D+ y D- con resistencias de terminación en chip de 27 Ω.
- **VREG_IN / VREG_VOUT (Pines 44, 45):** Entrada de 3.3 V y salida de 1.1 V del regulador lineal del núcleo.
- **TESTEN / RUN (Pines 20, 26):** Pin de pruebas de fábrica (a GND) y pin de reinicio hardware `RUN` (con pull-up interno).

# Aplicaciones

- Microcontrolador versátil para robótica, drones y controladores de motores sin escobillas (BLDC).
- Instrumentación electrónica digital de alta frecuencia con adquisición ADC y síntesis PIO.
- Dispositivos de interfaz humana USB interactivos (HID) y consolas retro en miniatura.
- Equipamiento de audio profesional y sintetizadores digitales I2S.

# Limitaciones y Advertencias

- **Tensión I/O máxima estricta:** Ningún pin del chip tolera voltajes superiores a 3.63 V; bajo ninguna circunstancia debe aplicarse lógica de 5 V directamente.
- **No Linealidad del ADC (DNL Spikes):** El convertidor analógico SAR del RP2040 presenta anomalías conocidas de no linealidad diferencial (DNL) en transiciones de bit intermedias (especialmente alrededor de los códigos 512, 1024, 1536 y 2048), reduciendo el número efectivo de bits (ENOB) a ~8.7 bits sin calibración de software.
"""

RP2040_CHIP_JSON = {
  "file_name": "RP-008371-DS-1-rp2040-datasheet.pdf",
  "processed_file": "data/processed/raspberry_pi/RP-008371-DS-1-rp2040-datasheet.md",
  "source_path": "data/raw/Microcontroladores_RAG_Documentacion/Raspberry_Pi/RP-008371-DS-1-rp2040-datasheet.pdf",
  "category": "Raspberry_Pi",
  "type": "Datasheet / Technical Reference",
  "component": "RP2040 Microcontroller",
  "manufacturer": "Raspberry Pi Ltd",
  "family": "RP2040 Silicon",
  "interfaces": [
    "UART",
    "SPI",
    "I2C",
    "ADC",
    "PWM",
    "PIO",
    "USB",
    "DMA",
    "GPIO"
  ],
  "voltage": {
    "iovdd": "1.8V - 3.3V (Nominal 3.3V)",
    "core_dvdd": "1.1V (generado por LDO en chip)",
    "adc_avdd": "1.98V - 3.63V",
    "abs_max_gpio": "3.63V (STRICTLY NO 5V TOLERANCE)"
  },
  "temperature_range": {
    "min": "-20 °C",
    "max": "85 °C"
  },
  "topics": [
    "Arquitectura Dual-Core ARM Cortex-M0+ a 133 MHz y 264 kB de SRAM dividida en 6 bancos independientes",
    "Bloques de E/S Programable (PIO): 2 bloques con 4 máquinas de estado cada uno y FIFOs DMA",
    "Controlador DMA de 12 canales con transferencias encadenadas y temporizadores de paso",
    "Periféricos de comunicación: 2x UART (PL011), 2x SPI (PL022), 2x I2C y USB 1.1 Host/Device con PHY integrada",
    "Módulo PWM de 8 slices (16 canales) y conversor analógico SAR ADC de 12 bits a 500 kSps",
    "Generadores de reloj: oscilador ROSC, cristal XOSC de 12 MHz y 2 PLLs (PLL_SYS y PLL_USB a 48 MHz)",
    "Limitaciones de tensión estricta a 3.3 V y anomalía de DNL en el convertidor ADC"
  ],
  "critical_params": {
    "cores": 2,
    "max_freq_mhz": 133,
    "sram_kb": 264,
    "pio_state_machines": 8,
    "dma_channels": 12,
    "pwm_slices": 8,
    "pwm_channels": 16,
    "adc_channels": 4,
    "adc_resolution_bits": 12,
    "adc_sampling_ksps": 500,
    "package": "QFN-56 (7x7 mm)"
  },
  "keywords": [
    "RP2040",
    "Raspberry Pi",
    "Cortex-M0+",
    "PIO",
    "Programmable IO",
    "State Machine",
    "DMA",
    "QFN56",
    "USB 1.1",
    "Dual Core",
    "SAR ADC",
    "XIP Flash"
  ],
  "issues_found": [
    "Datasheet completo del chip RP2040 de 642 páginas; estructurado en especificación técnica exhaustiva preservando registros y módulos de hardware."
  ]
}

PICO_SDK_MD = """# Información general

- **Nombre del componente:** Raspberry Pi Pico C/C++ SDK
- **Documento:** Raspberry Pi Pico-series C/C++ SDK (RP-009085-KB-2)
- **Fabricante / Editor:** Raspberry Pi Ltd
- **Familia:** Firmware & SDK Documentation / Embedded Software Framework
- **Tipo de documento:** Software Development Kit (SDK) Manual
- **Arquitectura de Software:** Entorno de compilación basado en CMake y cadena de herramientas GNU Arm Embedded Toolchain (`arm-none-eabi-gcc`)
- **Formatos de Salida Generados:** Binarios ejecutables ELF, imágenes crudas BIN y archivos UF2 listos para cargar por arrastrar y soltar vía USB
- **Enfoque de diseño:** Estructura modular dividida en bibliotecas de hardware de bajo nivel (`hardware_*`) con acceso directo a registros y bibliotecas de nivel superior (`pico_*`) para abstracción de sistema operativo y sincronización

# Arquitectura de la Pila de Software del SDK

El SDK se divide en dos niveles jerárquicos fundamentales:

### 1. Nivel de Hardware de Bajo Nivel (`hardware_*`)
Librerías livianas compuestas predominantemente por funciones inline y macros que proporcionan control determinista de registros sin coste de rendimiento:
- `hardware_gpio`: Configuración de pines, direcciones, niveles, pull-ups y funciones alternas.
- `hardware_uart`: Inicialización, transmisión/recepción con y sin bloqueo y control de flujo por hardware.
- `hardware_spi`: Control del periférico SPI maestro/esclavo y transferencias de buffers.
- `hardware_i2c`: Comunicación en bus I2C maestro/esclavo con manejo de condiciones de parada.
- `hardware_adc`: Calibración y muestreo continuo o bajo demanda del convertidor analógico.
- `hardware_pwm`: Control de divisores, valores wrap y ciclos de trabajo en las 8 rebanadas PWM.
- `hardware_dma`: Reserva dinámica de canales, configuración de descriptores y transferencias en background.
- `hardware_pio`: Carga de programas ensamblador PIO, configuración de reloj de máquinas de estado y FIFOs.
- `hardware_irq`: Registro de manejadores de interrupción exclusivos y compartidos, activación y prioridades.
- `hardware_timer`: Alarmas por hardware de microsegundos y marcas temporales de 64 bits.
- `hardware_watchdog`: Activación y alimentación del temporizador guardián.
- `hardware_clocks`: Configuración de generadores de reloj, fuentes PLL y divisores de bus.

### 2. Nivel Superior de Sistema (`pico_*`)
Librerías de mayor abstracción que implementan funcionalidades complejas y servicios comunes:
- `pico_stdlib`: Agrupa las cabeceras estándar más comunes (`hardware_gpio`, `hardware_uart`, temporizadores y `pico_stdio`).
- `pico_stdio`: Redirección automática de la entrada/salida estándar (`printf`, `scanf`) hacia UART0, USB CDC ACM o buffers en memoria.
- `pico_multicore`: Inicialización y control del segundo núcleo (Core 1), paso de funciones de entrada y colas inter-core seguras (FIFO).
- `pico_sync`: Primitivas de sincronización concurrente: Mutexes reentrantes, Semáforos, Bloqueos críticos (`critical_section`) y Banderas de evento.
- `pico_time`: Funciones de retardo bloqueante y temporizadores de software (`sleep_ms`, `sleep_us`, `add_repeating_timer_ms`).
- `pico_bootrom`: Acceso a funciones optimizadas de coma flotante y funciones de reinicio en modo USB desde software.

# Funciones y APIs Principales del SDK

### Control de GPIO
```c
// Inicializa el pin GPIO y lo desvincula de periféricos previos
void gpio_init(uint gpio);

// Configura la dirección: GPIO_IN (0) o GPIO_OUT (1)
void gpio_set_dir(uint gpio, bool out);

// Establece el estado lógico de salida (true = HIGH / false = LOW)
void gpio_put(uint gpio, bool value);

// Lee el estado lógico presente en el pin
bool gpio_get(uint gpio);

// Habilita resistencias de pull-up o pull-down
void gpio_pull_up(uint gpio);
void gpio_pull_down(uint gpio);

// Asigna una función periférica alternativa (GPIO_FUNC_SPI, UART, I2C, PWM, PIO)
void gpio_set_function(uint gpio, enum gpio_function fn);
```

### Puertos de Comunicación (UART, SPI, I2C)
```c
// UART
uint uart_init(uart_inst_t *uart, uint baudrate);
void uart_putc(uart_inst_t *uart, char c);
void uart_puts(uart_inst_t *uart, const char *s);
char uart_getc(uart_inst_t *uart);
void uart_set_hw_flow(uart_inst_t *uart, bool cts, bool rts);

// SPI
uint spi_init(spi_inst_t *spi, uint baudrate);
int spi_write_blocking(spi_inst_t *spi, const uint8_t *src, size_t len);
int spi_read_blocking(spi_inst_t *spi, uint8_t repeated_tx_data, uint8_t *dst, size_t len);

// I2C
uint i2c_init(i2c_inst_t *i2c, uint baudrate);
int i2c_write_blocking(i2c_inst_t *i2c, uint8_t addr, const uint8_t *src, size_t len, bool nostop);
int i2c_read_blocking(i2c_inst_t *i2c, uint8_t addr, uint8_t *dst, size_t len, bool nostop);
```

### Convertidor Analógico Digital (ADC)
```c
void adc_init(void);
void adc_gpio_init(uint gpio);            // Solo GPIO 26, 27, 28 y 29
void adc_select_input(uint input);        // Canal 0..3 o 4 (sensor temperatura)
uint16_t adc_read(void);                  // Retorna valor entero de 12 bits (0 a 4095)
void adc_set_temp_sensor_enabled(bool enable);
```

### Ejecución Multicorazón (Multicore)
```c
// Arranca la ejecución de Core 1 en la función especificada
void multicore_launch_core1(void (*entry)(void));

// Envía un dato de 32 bits a la FIFO del otro núcleo con espera de bloqueo
void multicore_fifo_push_blocking(uint32_t data);

// Recibe un dato de 32 bits proveniente de la FIFO del otro núcleo
uint32_t multicore_fifo_pop_blocking(void);
```

### Primitivas de Sincronización Concurrente
```c
// Mutex
void mutex_init(mutex_t *mtx);
void mutex_enter_blocking(mutex_t *mtx);
void mutex_exit(mutex_t *mtx);

// Semáforos
void sem_init(semaphore_t *sem, int16_t initial_permits, int16_t max_permits);
void sem_acquire_blocking(semaphore_t *sem);
bool sem_release(semaphore_t *sem);
```

# Estructura del Archivo `CMakeLists.txt` Estándar

Un proyecto con el Pico SDK requiere una estructura mínima de configuración CMake:
```cmake
cmake_minimum_required(VERSION 3.13)
include(pico_sdk_import.cmake)

project(mi_proyecto C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

pico_sdk_init()

add_executable(mi_proyecto main.c)
target_link_libraries(mi_proyecto pico_stdlib hardware_adc hardware_i2c)

# Habilita la salida serial por USB y deshabilita UART por defecto
pico_enable_stdio_usb(mi_proyecto 1)
pico_enable_stdio_uart(mi_proyecto 0)

# Genera los archivos UF2, bin y hex complementarios
pico_add_extra_outputs(mi_proyecto)
```

# Aplicaciones

- Desarrollo de firmware profesional en C y C++ para microcontroladores RP2040 y RP2350.
- Creación de periféricos de alta velocidad integrando máquinas de estado PIO con transferencias DMA.
- Aplicaciones multihilo y procesamiento distribuido en los dos núcleos ARM Cortex-M0+.
- Dispositivos de instrumentación y automatización embebida con interfaces USB interactivas.

# Limitaciones y Advertencias

- **Inicialización de Stdio:** Si se habilita `pico_enable_stdio_usb`, es indispensable invocar `stdio_init_all()` al comienzo de `main()` y aguardar un breve retardo (`sleep_ms(2000)`) si se requiere capturar mensajes iniciales antes de que el host USB reconozca el dispositivo.
- **Acceso Concurrente a Periféricos:** Los periféricos del RP2040 no disponen de arbitraje por hardware entre Core 0 y Core 1; si ambos núcleos acceden al mismo puerto SPI o I2C sin sincronización mediante `mutex_t`, se producirán colisiones y corrupción de datos.
"""

PICO_SDK_JSON = {
  "file_name": "RP-009085-KB-2-raspberry-pi-pico-c-sdk.pdf",
  "processed_file": "data/processed/raspberry_pi/RP-009085-KB-2-raspberry-pi-pico-c-sdk.md",
  "source_path": "data/raw/Microcontroladores_RAG_Documentacion/Raspberry_Pi/RP-009085-KB-2-raspberry-pi-pico-c-sdk.pdf",
  "category": "Raspberry_Pi",
  "type": "Software Development Kit (SDK) Manual",
  "component": "Raspberry Pi Pico C/C++ SDK",
  "manufacturer": "Raspberry Pi Ltd",
  "family": "Firmware & SDK Documentation",
  "interfaces": [
    "GPIO",
    "UART",
    "SPI",
    "I2C",
    "ADC",
    "PWM",
    "PIO",
    "DMA",
    "Multicore",
    "USB"
  ],
  "voltage": {
    "software_framework": "No aplicable directamente (controla silicio RP2040 de 3.3V I/O y 1.1V Core)"
  },
  "temperature_range": {
    "min": "unknown",
    "max": "unknown"
  },
  "topics": [
    "Arquitectura del Pico SDK: bibliotecas de registros hardware_* y librerías de sistema pico_*",
    "Flujo de compilación CMake, toolchain arm-none-eabi-gcc y generación de imágenes UF2",
    "APIs completas para control de GPIO, puertos serie UART, interfaces SPI e I2C",
    "Muestreo de entradas analógicas (ADC) y lectura del sensor de temperatura interno",
    "Ejecución concurrente en dos núcleos (pico_multicore) y comunicación por colas FIFO",
    "Primitivas de sincronización mediante Mutexes (mutex_t), Semáforos y secciones críticas",
    "Estructura del archivo CMakeLists.txt y redirección de entrada/salida estándar stdio a USB CDC"
  ],
  "critical_params": {
    "build_system": "CMake >= 3.13",
    "target_mcu": "RP2040 / RP2350",
    "c_standards": "C11, C++17",
    "output_formats": "ELF, BIN, UF2",
    "hardware_libraries": "gpio, uart, spi, i2c, adc, pwm, pio, dma, irq, timer, watchdog, clocks"
  },
  "keywords": [
    "Raspberry Pi Pico",
    "C/C++ SDK",
    "CMake",
    "arm-none-eabi-gcc",
    "UF2",
    "hardware_gpio",
    "hardware_uart",
    "hardware_i2c",
    "hardware_spi",
    "pico_multicore",
    "pico_stdlib",
    "Mutex",
    "stdio_usb"
  ],
  "issues_found": [
    "Manual exhaustivo de la biblioteca de desarrollo oficial de 821 páginas; condensado en especificación técnica estructurada con signaturas de funciones y mejores prácticas."
  ]
}

def write_raspberry_docs():
    p_proc = Path("data/processed/raspberry_pi")
    p_meta = Path("data/metadata/raspberry_pi")
    p_proc.mkdir(parents=True, exist_ok=True)
    p_meta.mkdir(parents=True, exist_ok=True)

    # 1. Pico Board
    (p_proc / "RP-008307-DS-2-pico-datasheet.md").write_text(PICO_BOARD_MD, encoding="utf-8")
    with open(p_meta / "RP-008307-DS-2-pico-datasheet.json", "w", encoding="utf-8") as f:
        json.dump(PICO_BOARD_JSON, f, indent=2, ensure_ascii=False)
    print("Wrote RP-008307-DS-2-pico-datasheet.md and json")

    # 2. RP2040 Chip
    (p_proc / "RP-008371-DS-1-rp2040-datasheet.md").write_text(RP2040_CHIP_MD, encoding="utf-8")
    with open(p_meta / "RP-008371-DS-1-rp2040-datasheet.json", "w", encoding="utf-8") as f:
        json.dump(RP2040_CHIP_JSON, f, indent=2, ensure_ascii=False)
    print("Wrote RP-008371-DS-1-rp2040-datasheet.md and json")

    # 3. Pico SDK
    (p_proc / "RP-009085-KB-2-raspberry-pi-pico-c-sdk.md").write_text(PICO_SDK_MD, encoding="utf-8")
    with open(p_meta / "RP-009085-KB-2-raspberry-pi-pico-c-sdk.json", "w", encoding="utf-8") as f:
        json.dump(PICO_SDK_JSON, f, indent=2, ensure_ascii=False)
    print("Wrote RP-009085-KB-2-raspberry-pi-pico-c-sdk.md and json")

if __name__ == "__main__":
    write_raspberry_docs()
