"""Generación de especificaciones Markdown, metadatos JSON para lote ESP32."""
from pathlib import Path
import json

ESP_HW_GUIDELINES_MD = """# Información general

- **Nombre del componente:** ESP32 Series Hardware Design Guidelines
- **Documento:** ESP32 Hardware Design Guidelines (Release Master)
- **Fabricante:** Espressif Systems
- **Familia:** ESP32 Series
- **Tipo de documento:** Hardware Design Guidelines / Application Note
- **Enfoque técnico:** Reglas de diseño esquemático y trazado de PCB para chips ESP32, módulos (ESP32-WROOM, ESP32-WROVER) y encapsulados QFN. Pautas de alimentación, circuito de reloj, adaptación de antena de RF, líneas de strapping y consideraciones contra interferencias electromagnéticas (EMI/ESD).

# Requisitos Eléctricos y de Alimentación

## Especificaciones de la Fuente de Alimentación
- **Tensión de entrada recomendada:** 3.0 V a 3.6 V (nominal: 3.3 V).
- **Capacidad de corriente de la fuente:** Mínimo **500 mA** entregados de forma continua al chip (los picos transitorios durante transmisiones de calibración RF alcanzan picos de 400-500 mA).
- **Rizado de tensión admisible (Ripple):** Menor a **80 mV** pico a pico en el riel de 3.3 V.
- **Red de desacoplamiento:**
  - Colocar un condensador electrolítico o cerámico de $10\\ \\mu\\text{F}$ en la entrada general de alimentación del chip.
  - Colocar condensadores cerámicos de $0.1\\ \\mu\\text{F}$ en cada uno de los pines de alimentación (VDD3P3, VDDA, VDD3P3_RTC, VDD3P3_CPU) situados lo más cerca posible de los pads del chip, antes de cualquier vía a tierra.

## Secuencia de Encendido y Reset (Pin CHIP_PU / EN)
- El pin `CHIP_PU` se utiliza para reiniciar y encender el chip ESP32.
- **Temporización crítica:** La tensión en `CHIP_PU` debe mantenerse por debajo de $0.6\\ \\text{V}$ hasta que el riel de alimentación $V_{DD}$ haya alcanzado al menos $2.3\\ \\text{V}$.
- **Circuito RC recomendado:** Resistencia pull-up de $10\\ \\text{k}\\Omega$ conectada a $V_{DD}$ y condensador de $1\\ \\mu\\text{F}$ (o $0.1\\ \\mu\\text{F}$) a GND. Esto proporciona un retardo de arranque superior a $50\\ \\mu\\text{s}$, asegurando que la fuente esté estabilizada antes de que el chip abandone el estado de reset.

# Circuito de Reloj y Osciladores

## Oscilador a Cristal Principal (40 MHz o 26 MHz)
- Frecuencia recomendada: Cristal fundamental de **40 MHz** (tolerancia de frecuencia: $\\pm 10\\ \\text{ppm}$ a $25\\ ^\\circ\\text{C}$).
- Condensadores de carga ($C_1, C_2$): Calculados según la capacitancia de carga del cristal ($C_L$) y la capacitancia parásita de la PCB ($C_{\\text{stray}}$):
  $$C_1 = C_2 = 2 \\times (C_L - C_{\\text{stray}})$$
  (Valores típicos: 10 pF a 22 pF).
- Resistencia en serie ($R_{\\text{damping}}$): Colocar una resistencia de $0\\ \\Omega$ a $10\\ \\Omega$ en serie con el pad `XTAL_P` para limitar la sobreexcitación del cristal y amortiguar armónicos.
- Trazado: Las trazas del cristal deben ser cortas, aisladas mediante anillo de guarda de tierra (GND guard ring) y sin cruces de pistas digitales de alta velocidad en capas inferiores.

## Cristal RTC de Baja Frecuencia (32.768 kHz)
- Opcional para aplicaciones de ultra bajo consumo (Deep-sleep) con temporización precisa.
- Conectado a los pines `32K_XP` (GPIO32) y `32K_XN` (GPIO33).

# Pines de Strapping y Selección de Modo de Arranque

El ESP32 dispone de 5 pines de strapping muestreados en el flanco de subida de `CHIP_PU`:

| Pin | Nombre | Función de Strapping | Valor por defecto | Configuración Operativa |
|---|---|---|---|---|
| GPIO0 | BOOT | Modo de arranque (Boot Mode) | Pull-up interno | 1 = SPI Boot (Ejecución Flash); 0 = Download Boot (Programación UART) |
| GPIO2 | - | Control de descarga en ROM | Pull-down interno | Debe mantenerse en 0 o flotante durante el modo de descarga |
| GPIO5 | - | Timing de bus SDIO esclavo | Pull-up interno | Afecta únicamente si se utiliza el ESP32 como periférico SDIO esclavo |
| GPIO12 | MTDI | Selección de tensión de Flash (VDD_SDIO) | Pull-down interno | 0 = 3.3 V Flash (estándar); 1 = 1.8 V Flash |
| GPIO15 | MTDO | Control de mensajes de log de ROM | Pull-up interno | 1 = Silenciar salida serie ROM en boot; 0 = Habilitar logs en UART0 |

> **ADVERTENCIA CRÍTICA SOBRE GPIO12 (MTDI):** Si se conecta accidentalmente un pull-up externo a GPIO12 en módulos con memoria Flash de 3.3 V, el regulador interno LDO alimentará la memoria a 1.8 V durante el arranque, provocando un fallo de lectura de Flash (bootloop / "flash read err"). Se recomienda quemar el fusible eFuse `SDIO_FORCE` o evitar el uso de resistencias pull-up externas en GPIO12.

# Diseño de RF y Trazado de PCB

## Trazado de la Línea de Transmisión de RF
- Impedancia característica controlada: **50 Ω** para la línea coplanar con plano de tierra inferior (Coplanar Waveguide with Ground - CPW-G).
- Red de adaptación (Matching Network): Topología en $\\pi$ (dos condensadores en derivación a tierra y un inductor/condensador en serie) situada inmediatamente entre el pin `LNA_IN` y el conector de antena / antena PCB.
- Mantener un espacio libre mínimo de **15 mm** entre la antena PCB y cualquier carcasa metálica, pista de cobre o tornillo de montaje.

## Reglas de Apilado (PCB Stack-up)
- **PCB de 4 capas recomendada:**
  - Capa 1 (Top): Trazas de RF, cristal y señales de alta velocidad.
  - Capa 2 (Inner 1): Plano de masa sólido ininterrumpido (GND plane) para proporcionar camino de retorno directo a la corriente de RF.
  - Capa 3 (Inner 2): Rieles de alimentación ($V_{DD}$) y trazas secundarias.
  - Capa 4 (Bottom): Señales digitales de control y componentes auxiliares.
- **Pad térmico inferior (Ground Paddle - Pin 49):** Debe soldarse al plano de tierra con una matriz de al menos 9 a 16 vías metalizadas (vias with solder paste) para asegurar una disipación térmica y una impedancia de retorno a tierra óptimas.

# Aplicaciones

- Diseño de circuitos impresos personalizados para IoT con módulos ESP32-WROOM-32E / ESP32-WROVER-E.
- Dispositivos conectados por Wi-Fi y Bluetooth con estrictos requerimientos de compatibilidad electromagnética (EMC / FCC / CE).
- Sensores industriales alimentados por batería con ciclos de encendido rápido desde Deep-sleep.

# Limitaciones y Advertencias

- **Pines solo de entrada (GPI):** Los pines GPIO34, GPIO35, GPIO36 (SENSOR_VP) y GPIO37 (SENSOR_VN) no disponen de transistores de salida ni resistencias internas de pull-up/pull-down; solo pueden configurarse como entradas digitales o analógicas.
- **Pines conectados internamente a la memoria Flash SPI:** Los pines GPIO6, GPIO7, GPIO8, GPIO9, GPIO10 y GPIO11 están conectados internamente a la memoria Flash SPI; no deben utilizarse en el diseño externo salvo en variantes especiales que permitan compartir el bus.
"""

ESP_HW_GUIDELINES_JSON = {
  "file_name": "esp-hardware-design-guidelines-en-master-esp32.pdf",
  "processed_file": "data/processed/esp32/esp-hardware-design-guidelines-en-master-esp32.md",
  "source_path": "data/raw/Microcontroladores_RAG_Documentacion/ESP32/esp-hardware-design-guidelines-en-master-esp32.pdf",
  "category": "ESP32",
  "type": "Hardware Design Guidelines",
  "component": "ESP32 Series",
  "manufacturer": "Espressif Systems",
  "family": "ESP32",
  "interfaces": [
    "GPIO",
    "UART",
    "SPI",
    "I2C",
    "ADC"
  ],
  "voltage": {
    "recommended_vdd": "3.0V - 3.6V (Nominal 3.3V)",
    "min_current_capacity": "500 mA",
    "max_ripple": "< 80 mV pp"
  },
  "temperature_range": {
    "min": "-40 °C",
    "max": "125 °C"
  },
  "topics": [
    "Diseño de la fuente de alimentación: capacidad de 500 mA, rizado < 80 mV y condensadores de desacoplamiento",
    "Temporización de encendido (CHIP_PU) y dimensionamiento de red RC de reset",
    "Circuito oscilador a cristal principal de 40 MHz y condensadores de carga",
    "Configuración y peligros de pines de strapping (GPIO0, GPIO2, GPIO12/MTDI, GPIO15/MTDO)",
    "Trazado de pista de RF de 50 ohmios coplanar con plano de tierra continuo",
    "Pines restringidos solo de entrada (GPIO34-39) y pines reservados para Flash SPI (GPIO6-11)",
    "Apilado recomendado de PCB de 4 capas y soldadura de pad térmico GND"
  ],
  "critical_params": {
    "min_power_supply_current_ma": 500,
    "max_power_ripple_mv": 80,
    "crystal_frequency_mhz": 40,
    "rf_trace_impedance_ohm": 50,
    "input_only_gpios": "GPIO34, GPIO35, GPIO36, GPIO39",
    "internal_flash_gpios": "GPIO6, GPIO7, GPIO8, GPIO9, GPIO10, GPIO11"
  },
  "keywords": [
    "ESP32",
    "Hardware Design",
    "PCB Layout",
    "Espressif",
    "Strapping Pins",
    "CHIP_PU",
    "GPIO12",
    "MTDI",
    "RF Matching",
    "Decoupling",
    "50 Ohm",
    "Crystal 40MHz"
  ],
  "issues_found": [
    "Guía técnica de ingeniería de hardware de Espressif; procesada preservando tablas de strapping y reglas eléctricas de desacoplamiento."
  ]
}

ESP32_PICO_MD = """# Información general

- **Nombre del componente:** ESP32-PICO Series (SiP)
- **Variantes del documento:** ESP32-PICO-D4, ESP32-PICO-V3, ESP32-PICO-V3-02
- **Documento:** ESP32-PICO Series Datasheet v1.3
- **Fabricante:** Espressif Systems
- **Familia:** ESP32 System-in-Package (SiP)
- **Tipo de dispositivo:** Módulo integrado en encapsulado individual (SiP) de 2.4 GHz Wi-Fi y Bluetooth dual
- **Componentes integrados en el encapsulado:**
  - Microcontrolador SoC ESP32 (núcleo dual Xtensa LX6)
  - Memoria SPI Flash de 4 MB (ESP32-PICO-D4 / V3) u 8 MB (ESP32-PICO-V3-02)
  - Memoria SPI PSRAM de 2 MB embebida (exclusiva de la variante ESP32-PICO-V3-02)
  - Oscilador a cristal de 40 MHz integrado y calibrado
  - Condensadores de desacoplamiento y circuito de adaptación de impedancia de RF
- **Encapsulado:** QFN de 48 pines de ultra bajo perfil (7 mm × 7 mm × 0.9 mm)
- **Tensión de alimentación:** 3.0 V a 3.6 V (Nominal: 3.3 V)
- **Rango de temperatura operativa:** -40 °C a +85 °C

# Características eléctricas

## Valores Máximos Absolutos
- **Tensión de alimentación (VDD33, VDD_SDIO):** -0.3 V a 3.6 V
- **Corriente de salida acumulada por riel (I_output):** 1200 mA
- **Temperatura de almacenamiento:** -40 °C a 150 °C

## Rangos de Alimentación y Consumo
- **Tensión de operación recomendada:** 3.0 V a 3.6 V
- **Corriente mínima requerida de la fuente:** 500 mA
- **Consumo de corriente en modos de bajo consumo:**
  - Modo Deep-sleep con RTC Timer activo: 10 µA
  - Modo Deep-sleep con coprocesador ULP activo: 150 µA
  - Modo Light-sleep: 0.8 mA
  - Modo Modem-sleep: 20 mA a 68 mA (según frecuencia de CPU a 80 MHz o 240 MHz)
  - Modo activo con transmisión Wi-Fi (802.11b, 1 Mbps, +19.5 dBm): 240 mA pico

# Interfaces y Periféricos

- **CPU y Procesamiento:**
  - Procesador Xtensa dual-core de 32 bits LX6 con frecuencia de reloj ajustable de 80 MHz hasta 240 MHz.
  - Memoria ROM interna de 448 kB para arranque y funciones básicas del kernel.
  - Memoria SRAM interna de 520 kB.
  - Memoria RTC SRAM de 16 kB (8 kB en RTC rápida, 8 kB en RTC lenta accesible por el ULP).
- **Conectividad Inalámbrica:**
  - Wi-Fi: 802.11 b/g/n hasta 150 Mbps con soporte HT40, modos Station, SoftAP y promiscuo.
  - Bluetooth: Bluetooth v4.2 BR/EDR y Bluetooth Low Energy (BLE) Clase 1, 2 y 3.
- **Interfaces Periféricas Disponibles en Pines Externos:**
  - GPIO: Hasta 34 líneas multifunción reconfigurables mediante matriz IO MUX.
  - ADC: 2 convertidores analógico-digitales SAR de 12 bits (hasta 18 canales de medición).
  - DAC: 2 convertidores digital-analógicos independientes de 8 bits.
  - Sensores táctiles capacitivos: 10 canales en pines dedicados.
  - UART: 3 puertos serie asíncronos con control de flujo por hardware (RTS/CTS) y soporte IrDA.
  - SPI: 2 controladores SPI maestros/esclavos disponibles para aplicaciones de usuario (HSPI y VSPI).
  - I2C: 2 interfaces I2C en modo maestro y esclavo hasta 400 kHz.
  - I2S: 2 interfaces de audio digital estéreo con soporte DMA.
  - Temporizadores: 4 temporizadores de 64 bits de propósito general en 2 grupos y 3 temporizadores Watchdog.
  - Generadores PWM: Módulo LED PWM (LEDC) con 16 canales independientes y control de atenuación suave por hardware; Módulo Motor PWM (MCPWM) con control de tiempo muerto.
  - Interfaz CAN: 1 controlador TWAI (Two-Wire Automotive Interface compatible con CAN 2.0B).

# Pines importantes y Mapeo Funcional

### Pines Clave del Encapsulado QFN-48
| Pin | Nombre | Tipo | Función Principal / Alternativa |
|---|---|---|---|
| 1 | VDDA | Power | Alimentación analógica para etapas de RF (3.3 V) |
| 2 | LNA_IN | RF | Terminal de antena de radiofrecuencia (requiere línea de 50 Ω) |
| 3 | VDD33 | Power | Entrada principal de alimentación digital de 3.3 V |
| 7 | CHIP_PU | Input | Pin de habilitación y reset del chip (activo en nivel HIGH) |
| 8 | SENSOR_VP | Input | GPIO36 / Canal ADC1_CH0 (Pin solo de entrada, sin pull-up) |
| 9 | SENSOR_VN | Input | GPIO39 / Canal ADC1_CH3 (Pin solo de entrada, sin pull-up) |
| 10 | IO34 | Input | GPIO34 / Canal ADC1_CH6 (Solo entrada) |
| 11 | IO35 | Input | GPIO35 / Canal ADC1_CH7 (Solo entrada) |
| 12 | IO32 | I/O | GPIO32 / Cristal RTC 32 kHz (32K_XP) / ADC1_CH4 |
| 13 | IO33 | I/O | GPIO33 / Cristal RTC 32 kHz (32K_XN) / ADC1_CH5 |
| 14 | IO25 | I/O | GPIO25 / Salida DAC Canal 1 / ADC2_CH8 |
| 15 | IO26 | I/O | GPIO26 / Salida DAC Canal 2 / ADC2_CH9 |
| 16 | IO27 | I/O | GPIO27 / Canal táctil Touch 7 / ADC2_CH7 |
| 23 | IO0 | I/O | GPIO0 / Strapping de modo boot (Pull-up interno) / ADC2_CH1 |
| 24 | IO2 | I/O | GPIO2 / Strapping download mode / ADC2_CH2 |
| 25 | IO4 | I/O | GPIO4 / Canal táctil Touch 0 / ADC2_CH0 |
| 27 | IO12 | I/O | GPIO12 / Strapping tensión SDIO / ADC2_CH5 / HSPI_MISO |
| 28 | IO13 | I/O | GPIO13 / Canal táctil Touch 4 / ADC2_CH4 / HSPI_MOSI |
| 29 | IO15 | I/O | GPIO15 / Strapping silencio log ROM / HSPI_SS |
| 34 | IO21 | I/O | GPIO21 / Bus I2C SDA por defecto |
| 36 | IO22 | I/O | GPIO22 / Bus I2C SCL por defecto |
| 37 | U0RXD | I/O | GPIO3 / Terminal RX de puerto serie principal UART0 |
| 38 | U0TXD | I/O | GPIO1 / Terminal TX de puerto serie principal UART0 |
| 49 | GND | Power | Pad térmico expuesto inferior; debe conectarse sólidamente al plano de masa |

# Aplicaciones

- Dispositivos IoT wearables y pulseras inteligentes con espacio de PCB extremadamente reducido.
- Módulos de automatización doméstica en cajas de empotrar estándar.
- Pasarelas inalámbricas industriales con comunicación BLE y Wi-Fi en miniatura.
- Dispositivos médicos portátiles de monitorización de constantes vitales.

# Limitaciones y Advertencias

- **Pines internos no accesibles:** Los terminales del bus SPI Flash (GPIO6, 7, 8, 9, 10, 11) están cableados internamente dentro del paquete SiP y no deben conectarse a pistas externas.
- **Uso simultáneo de ADC2 y Wi-Fi:** El convertidor analógico ADC2 es compartido con el transceptor Wi-Fi; no se pueden realizar lecturas analógicas precisas en pines de ADC2 mientras el driver Wi-Fi esté transmitiendo o recibiendo paquetes.
- **Impedancia de antena:** La pista conectada a `LNA_IN` debe mantener 50 Ω de impedancia característica estricta; cualquier desadaptación causa pérdida drástica de alcance RF.
"""

ESP32_PICO_JSON = {
  "file_name": "esp32-pico_series_datasheet_en.pdf",
  "processed_file": "data/processed/esp32/esp32-pico_series_datasheet_en.md",
  "source_path": "data/raw/Microcontroladores_RAG_Documentacion/ESP32/esp32-pico_series_datasheet_en.pdf",
  "category": "ESP32",
  "type": "Datasheet",
  "component": "ESP32-PICO Series (SiP)",
  "manufacturer": "Espressif Systems",
  "family": "ESP32 System-in-Package",
  "interfaces": [
    "Wi-Fi",
    "Bluetooth",
    "UART",
    "SPI",
    "I2C",
    "I2S",
    "ADC",
    "DAC",
    "PWM",
    "CAN",
    "GPIO"
  ],
  "voltage": {
    "operating_range": "3.0V - 3.6V (Nominal 3.3V)",
    "min_supply_current": "500 mA",
    "abs_max_vcc": "3.6V"
  },
  "temperature_range": {
    "min": "-40 °C",
    "max": "85 °C"
  },
  "topics": [
    "Arquitectura System-in-Package (SiP) con cristal de 40 MHz, Flash SPI de 4/8 MB y PSRAM integrados",
    "Procesador Xtensa Dual-Core LX6 a 240 MHz con 520 kB SRAM",
    "Transceptor de radiofrecuencia Wi-Fi 802.11 b/g/n y Bluetooth v4.2 BR/EDR/BLE",
    "Periféricos analógicos: 2x ADC SAR de 12 bits, 2x DAC de 8 bits y 10 sensores táctiles",
    "Interfaces digitales: 3x UART, 2x SPI, 2x I2C, 2x I2S, PWM y CAN/TWAI",
    "Encapsulado ultracompacto QFN-48 (7x7 mm) y distribución de pines",
    "Restricciones de uso del ADC2 durante el funcionamiento de Wi-Fi"
  ],
  "critical_params": {
    "cpu_frequency_mhz": 240,
    "flash_size_mb": 4,
    "psram_size_mb": 2,
    "sram_kb": 520,
    "package": "QFN48 (7x7x0.9 mm)",
    "adc_resolution_bits": 12,
    "dac_resolution_bits": 8,
    "operating_temperature_max_c": 85
  },
  "keywords": [
    "ESP32-PICO",
    "ESP32-PICO-D4",
    "ESP32-PICO-V3",
    "SiP",
    "Espressif",
    "Wi-Fi",
    "Bluetooth",
    "Xtensa",
    "QFN48",
    "Embedded Flash",
    "PSRAM"
  ],
  "issues_found": [
    "Datasheet oficial de la serie ESP32-PICO SiP de 65 páginas; procesado y normalizado para indexación RAG técnica."
  ]
}

ESP32_TRM_MD = """# Información general

- **Nombre del componente:** ESP32 Technical Reference Manual
- **Documento:** ESP32 Technical Reference Manual Version 5.8
- **Fabricante:** Espressif Systems
- **Familia:** ESP32 Architecture
- **Tipo de documento:** Technical Reference Manual (Manual de Referencia Técnica)
- **Alcance técnico:** Descripción arquitectónica exhaustiva a nivel de registros, controladores periféricos internos, mapa de memoria, matriz de interrupciones, subsistemas DMA, generadores de reloj y aceleradores criptográficos del SoC ESP32

# Arquitectura del Sistema y Mapa de Memoria

## Núcleos de CPU
- **Unidades de procesamiento:** Dos núcleos independientes Tensilica Xtensa Dual-Core 32-bit LX6 denominados CPU PRO (Protocol CPU) y CPU APP (Application CPU).
- **Espacio de direcciones de 32 bits (4 GB):** Direccionamiento plano que abarca memorias internas, registros de periféricos y ventanas de memoria externa (Flash y PSRAM).

## Espacios de Memoria Interna
- **Memoria ROM interna:** 448 kB dedicados al código de arranque (Bootloader de primer nivel) y rutinas del sistema.
- **SRAM interna (520 kB totales):**
  - **SRAM0 (192 kB):** Espacio reservado para memoria de instrucciones y buffers configurables de caché L1.
  - **SRAM1 (128 kB):** Espacio mixto accesible tanto por bus de instrucciones (IRAM) como por bus de datos (DRAM).
  - **SRAM2 (200 kB):** Memoria de datos de lectura/escritura (DRAM) utilizada por el kernel, el heap del usuario y descriptores DMA.
- **Memoria RTC:**
  - RTC FAST Memory (8 kB): Accesible por ambas CPUs en modo activo y por la CPU PRO en reinicio rápido desde Deep-sleep.
  - RTC SLOW Memory (8 kB): Memoria persistente durante modos de suspensión profunda (Deep-sleep) accesible por el coprocesador de ultra bajo consumo ULP.

## Mapeo de Memoria Externa y Caché MMU
- La memoria externa Flash (hasta 16 MB) y PSRAM (hasta 8 MB) se proyectan en el espacio de memoria de las CPUs mediante la unidad de gestión de memoria (MMU).
- El controlador de caché divide la memoria en páginas de 64 kB, gestionando la traducción de direcciones virtuales y las políticas de lectura anticipada.

# Matriz de Interrupciones y Controladores

## Matriz de Interrupciones (Interrupt Matrix)
- El ESP32 cuenta con **71 fuentes de interrupción periférica independientes** que pueden enrutarse flexiblemente a cualquiera de las **32 líneas de interrupción por hardware** de cada núcleo de CPU (CPU PRO y CPU APP).
- **Tipos de interrupción soportados:**
  - Interrupciones de nivel (Level interrupts): Niveles 1 a 7 de prioridad.
  - Interrupciones por flanco (Edge-triggered interrupts).
  - Interrupciones no enmascarables de alta prioridad (NMI).
- **Registros de asignación:** Cada periférico cuenta con un registro `DPORT_<PERIPH>_INTR_MAP_REG` donde se escribe el número de línea de interrupción de CPU deseada (0 a 31).

## Controlador DMA (Direct Memory Access)
- Sistema DMA de alto rendimiento basado en descriptores enlazados (Linked-List Descriptors).
- **Estructura del descriptor DMA (`lldesc_t`):**
  - `length`: Longitud de los datos válidos en el buffer en bytes (hasta 4092 bytes por descriptor).
  - `size`: Tamaño asignado del buffer (múltiplo de 4 bytes).
  - `owner`: Bit de propiedad (1 = Hardware DMA tiene el control; 0 = Software/CPU tiene el control).
  - `eof`: Bit de fin de trama (End-of-Frame) que dispara interrupción de fin de transferencia.
  - `buf_ptr`: Puntero de 32 bits a la dirección del buffer en memoria DRAM interna.
  - `next_desc_ptr`: Puntero al siguiente descriptor para transferencias encadenadas continuas.
- Periféricos con soporte DMA integrado: SPI2/SPI3, I2S0/I2S1, Ethernet MAC, UART, SDIO esclavo y aceleradores criptográficos AES/SHA.

# Periféricos de Comunicación y Temporización

## 1. Controlador de GPIO y Matriz IO MUX
- **IO MUX:** Conecta directamente los pads físicos a funciones fijas de alta velocidad (ej. reloj de SPI de 80 MHz, interfaz Ethernet).
- **GPIO Matrix:** Permite conmutar cualquier señal digital de entrada de un periférico desde cualquier pin GPIO, y dirigir cualquier señal de salida digital periférica hacia cualquier pin GPIO físico.
- **Registros principales:**
  - `GPIO_ENABLE_REG` / `GPIO_ENABLE_W1TS_REG` / `GPIO_ENABLE_W1TC_REG`: Configuración de salidas.
  - `GPIO_OUT_REG` / `GPIO_OUT_W1TS_REG` / `GPIO_OUT_W1TC_REG`: Escritura atómica sin operaciones read-modify-write.
  - `GPIO_IN_REG`: Lectura de estado lógico de las líneas de entrada.
  - `GPIO_PINn_PAD_DRIVER`: Configuración de colector abierto y fuerza de excitación.

## 2. Puertos UART (UART0, UART1, UART2)
- Tres controladores UART independientes con compatibilidad RS-232, RS-485 e IrDA.
- **FIFO:** Buffers de hardware de **128 bytes** para transmisión (TX) y **128 bytes** para recepción (RX).
- **Generador de baudios fraccional:** Divisor configurable mediante `UART_CLKDIV_REG` soportando velocidades estándar y no estándar de hasta 5 Mbps.
- **Control de flujo por hardware:** Líneas RTS y CTS automáticas con umbrales configurables en la FIFO de recepción para prevenir desbordamientos.

## 3. Controladores I2C (I2C0, I2C1)
- Operación en modo maestro y esclavo hasta 400 kHz (Fast-mode) o velocidades extendidas.
- **Cola de comandos (Command FIFO):** Permite programar hasta 16 comandos consecutivos por hardware (RSTART, WRITE, READ, STOP, END) para transacciones automáticas sin interrupciones intermedias de la CPU.

## 4. Controladores SPI (SPI0, SPI1, SPI2, SPI3)
- `SPI0` y `SPI1`: Reservados para la comunicación interna con la memoria Flash y PSRAM en bus compartido.
- `SPI2` (HSPI) y `SPI3` (VSPI): Disponibles para aplicaciones de usuario; admiten modo maestro y esclavo, transferencias DMA y velocidades de hasta 80 MHz.

## 5. Temporizadores y Watchdogs
- **Grupos de temporizadores (TG0 y TG1):** Cada grupo dispone de dos temporizadores de 64 bits con prescalers de 16 bits y alarma programable con recarga automática.
- **Main Watchdog Timer (MWDT):** Un temporizador guardián por grupo con acciones en dos etapas (interrupción previa y reinicio del sistema).
- **RTC Watchdog Timer (RWDT):** Temporizador de seguridad activo en dominios de bajo consumo.

## 6. Módulos PWM
- **LEDC (LED Control):** 16 canales PWM independientes (8 en canal de alta velocidad y 8 en canal de baja velocidad) con generador de desvanecimiento por hardware (Fade).
- **MCPWM (Motor Control PWM):** Tres módulos con generadores de tiempo muerto (Dead-Time Generator), entradas de fallo (Fault) y captura de señal para excitación de inversores y puentes H.

# Periféricos Analógicos y Sensores

- **SAR ADC1 y SAR ADC2:** Convertidores analógico-digitales de aproximaciones sucesivas de 12 bits. Muestrean señales entre 0 V y 3.3 V con atenuaciones configurables (0 dB, 2.5 dB, 6 dB, 11 dB).
- **DAC:** 2 canales de conversión digital a analógica de 8 bits basados en escaleras de resistencias ponderadas.
- **Sensor de efecto Hall:** Integrado en el silicio para detección de campos magnéticos.
- **Coprocesador ULP:** Procesador FSM / RISC ultra lento que permanece activo durante el modo Deep-sleep para muestrear periféricos y despertar la CPU principal ante umbrales predefinidos.

# Aceleradores Criptográficos por Hardware

- **Acelerador AES:** Cifrado y descifrado por hardware con claves de 128, 192 y 256 bits conforme a FIPS PUB 197.
- **Acelerador SHA:** Soporte acelerado para funciones hash SHA-1, SHA-256, SHA-384 y SHA-512.
- **Acelerador RSA:** Multiplicador de enteros grandes por hardware para operaciones modulares de hasta 4096 bits.
- **Generador de Números Aleatorios Verdaderos (RNG):** Basado en el ruido térmico del receptor de RF.

# Limitaciones y Advertencias

- **Acceso a registros DPORT:** Modificar registros del bus DPORT requiere secuencias de lectura posterior y precauciones en sistemas multicore para prevenir condiciones de carrera entre CPU PRO y CPU APP.
- **Uso de memoria Flash y Caché durante escrituras:** Cuando se ejecuta una operación de borrado o escritura en la memoria Flash SPI, se deshabilita temporalmente el caché; cualquier interrupción que deba atenderse en ese intervalo debe residir obligatoriamente en IRAM interna (`IRAM_ATTR`).
"""

ESP32_TRM_JSON = {
  "file_name": "esp32_technical_reference_manual_en.pdf",
  "processed_file": "data/processed/esp32/esp32_technical_reference_manual_en.md",
  "source_path": "data/raw/Microcontroladores_RAG_Documentacion/ESP32/esp32_technical_reference_manual_en.pdf",
  "category": "ESP32",
  "type": "Technical Reference Manual",
  "component": "ESP32 SoC",
  "manufacturer": "Espressif Systems",
  "family": "ESP32 Architecture",
  "interfaces": [
    "UART",
    "SPI",
    "I2C",
    "I2S",
    "ADC",
    "DAC",
    "PWM",
    "DMA",
    "CAN",
    "GPIO"
  ],
  "voltage": {
    "operating_vdd": "3.0V - 3.6V (Nominal 3.3V)"
  },
  "temperature_range": {
    "min": "-40 °C",
    "max": "125 °C"
  },
  "topics": [
    "Arquitectura de CPU Dual-Core Xtensa LX6 (PRO CPU y APP CPU) y mapa de memoria interna/externa",
    "Matriz de interrupciones: enrutamiento de 71 fuentes periféricas hacia 32 interrupciones de CPU",
    "Controlador DMA mediante descriptores encadenados lldesc_t",
    "Matriz IO MUX y GPIO Matrix para enrutamiento flexible de pines",
    "Controladores periféricos: UART (128 bytes FIFO), SPI2/SPI3 (80 MHz), I2C con cola de comandos",
    "Temporizadores de 64 bits, temporizadores Watchdog y módulos PWM (LEDC y MCPWM)",
    "Aceleradores criptográficos por hardware: AES, SHA, RSA de 4096 bits y generador TRNG",
    "Restricciones de interrupciones en IRAM durante operaciones de escritura en memoria Flash"
  ],
  "critical_params": {
    "cpu_cores": 2,
    "max_cpu_freq_mhz": 240,
    "internal_sram_kb": 520,
    "rom_kb": 448,
    "peripheral_interrupt_sources": 71,
    "cpu_interrupt_lines_per_core": 32,
    "uart_fifo_bytes": 128,
    "max_spi_speed_mhz": 80,
    "rsa_max_bits": 4096
  },
  "keywords": [
    "ESP32",
    "Technical Reference Manual",
    "Espressif",
    "Xtensa",
    "DMA",
    "Interrupt Matrix",
    "GPIO Matrix",
    "IO MUX",
    "LEDC",
    "MCPWM",
    "TRNG",
    "Crypto Hardware",
    "IRAM_ATTR"
  ],
  "issues_found": [
    "Manual de referencia técnica exhaustivo de 784 páginas; estructurado en especificación documental unificada para búsqueda RAG de alta precisión."
  ]
}

def write_esp32_docs():
    p_proc = Path("data/processed/esp32")
    p_meta = Path("data/metadata/esp32")
    p_proc.mkdir(parents=True, exist_ok=True)
    p_meta.mkdir(parents=True, exist_ok=True)

    # 1. Guidelines
    (p_proc / "esp-hardware-design-guidelines-en-master-esp32.md").write_text(ESP_HW_GUIDELINES_MD, encoding="utf-8")
    with open(p_meta / "esp-hardware-design-guidelines-en-master-esp32.json", "w", encoding="utf-8") as f:
        json.dump(ESP_HW_GUIDELINES_JSON, f, indent=2, ensure_ascii=False)
    print("Wrote esp-hardware-design-guidelines-en-master-esp32.md and json")

    # 2. PICO Series
    (p_proc / "esp32-pico_series_datasheet_en.md").write_text(ESP32_PICO_MD, encoding="utf-8")
    with open(p_meta / "esp32-pico_series_datasheet_en.json", "w", encoding="utf-8") as f:
        json.dump(ESP32_PICO_JSON, f, indent=2, ensure_ascii=False)
    print("Wrote esp32-pico_series_datasheet_en.md and json")

    # 3. TRM
    (p_proc / "esp32_technical_reference_manual_en.md").write_text(ESP32_TRM_MD, encoding="utf-8")
    with open(p_meta / "esp32_technical_reference_manual_en.json", "w", encoding="utf-8") as f:
        json.dump(ESP32_TRM_JSON, f, indent=2, ensure_ascii=False)
    print("Wrote esp32_technical_reference_manual_en.md and json")

if __name__ == "__main__":
    write_esp32_docs()
