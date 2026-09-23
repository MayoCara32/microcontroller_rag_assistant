"""Generación de especificaciones Markdown, metadatos JSON e indexación vectorial para lote Arduino."""
from pathlib import Path
import json
import time

ATMEGA328DS_MD = """# Información general

- **Nombre del componente:** ATmega328 / ATmega328P
- **Fabricante:** Atmel / Microchip Technology
- **Familia:** megaAVR 8-bit
- **Tipo de dispositivo:** Microcontrolador de 8 bits de alto rendimiento y bajo consumo
- **Arquitectura:** AVR RISC avanzada con 131 instrucciones (la mayoría de ejecución en un solo ciclo de reloj)
- **Registros de trabajo:** 32 registros de 8 bits de propósito general directamente conectados a la ALU
- **Rendimiento:** Hasta 20 MIPS a 20 MHz
- **Multiplicador integrado:** Multiplicador en chip de 2 ciclos de reloj
- **Memoria de programa:** 32 kB de Flash autorreprogramable en sistema (10,000 ciclos de escritura/borrado)
- **Memoria de datos EEPROM:** 1 kB de EEPROM en chip (100,000 ciclos de escritura/borrado)
- **Memoria de datos SRAM:** 2 kB de SRAM interna
- **Retención de datos:** 20 años a 85 °C / 100 años a 25 °C
- **Encapsulados:** 28-pin PDIP, 28-pad QFN/MLF, 32-lead TQFP, 32-pad QFN/MLF

# Características eléctricas

## Valores Máximos Absolutos
- **Tensión en cualquier pin (excepto RESET) respecto a GND:** -0.5 V a VCC + 0.5 V
- **Tensión en pin RESET respecto a GND:** -0.5 V a +13.0 V
- **Tensión máxima de operación (VCC):** 6.0 V
- **Corriente continua máxima por pin de I/O:** 40.0 mA
- **Corriente continua total en pines VCC y GND:** 200.0 mA
- **Temperatura de almacenamiento:** -65 °C a +150 °C

## Rangos Operativos Recomendados
- **Tensión de alimentación (ATmega328P estándar):** 1.8 V a 5.5 V
- **Grados de velocidad según tensión:**
  - 0 a 4 MHz a 1.8 V - 5.5 V
  - 0 a 10 MHz a 2.7 V - 5.5 V
  - 0 a 20 MHz a 4.5 V - 5.5 V
- **Rango de temperatura operativa:**
  - Rango industrial: -40 °C a +85 °C
  - Rango extendido: -40 °C a +105 °C / +125 °C (según calificación automotriz)

## Consumo de Corriente (Modo Activo a 1 MHz, 1.8 V, 25 °C)
- Modo activo: 0.2 mA
- Modo Power-down: 0.1 µA a 1.8 V
- Modo Power-save: 0.75 µA a 1.8 V (incluyendo oscilador RTC de 32 kHz)

# Interfaces y Periféricos

- **GPIO:** 23 líneas de E/S programables (28 en encapsulado TQFP/QFN con ADC6 y ADC7 dedicados).
- **Temporizadores y Contadores:**
  - Timer0: Contador/Temporizador de 8 bits con prescaler independiente y dos canales PWM (OC0A, OC0B).
  - Timer1: Contador/Temporizador de 16 bits de alta resolución con prescaler independiente, registro de captura de entrada (ICR1) y dos canales PWM (OC1A, OC1B).
  - Timer2: Contador/Temporizador de 8 bits con prescaler independiente y capacidad de oscilador asíncrono en tiempo real (TOSC1/TOSC2 para cristal de 32.768 kHz).
- **Canales PWM:** 6 canales modulados por ancho de pulso en total.
- **Convertidor Analógico-Digital (ADC):**
  - Resolución: 10 bits.
  - Canales: 8 canales multiplexados en encapsulado TQFP/QFN; 6 canales en encapsulado PDIP.
  - Tensión de referencia: Referencia interna de 1.1 V estabilizada, tensión AVCC o pin AREF externo.
  - Tiempo de conversión: 13 a 260 µs (frecuencia de reloj ADC de 50 kHz a 200 kHz).
- **USART:** 1x USART serie programable con generador de tasa de baudios fraccional, detección de trama e interrupciones independientes de transmisión y recepción.
- **SPI (Serial Peripheral Interface):** 1x interfaz maestro/esclavo con operación síncrona de 3 y 4 hilos, soporte de doble velocidad (SPI2X).
- **I2C / TWI (Two-Wire Interface):** 1x bus serie compatible con protocolo I2C de 2 hilos, velocidad estándar (100 kHz) y rápida (400 kHz) con soporte multimaestro y detección de colisiones.
- **Comparador Analógico:** Comparador analógico en chip en pines AIN0 (PD6) y AIN1 (PD7), multiplexable a canales ADC.
- **Watchdog Timer:** Temporizador Guardián programable con oscilador en chip independiente de baja potencia.
- **Interrupciones externas:** Interrupciones por flanco y nivel en INT0 (PD2) e INT1 (PD3), e interrupciones por cambio de pin (PCINT0 a PCINT23) en las 24 líneas I/O.

# Pines importantes y Registros

### Registros Principales de Control
| Registro | Función | Descripción técnica |
|---|---|---|
| DDRB / DDRC / DDRD | Dirección I/O | Bits en 1 configuran pines como salida; bits en 0 como entrada |
| PORTB / PORTC / PORTD | Datos de Salida | Escribe nivel HIGH/LOW en salida; activa pull-up interno en entrada |
| PINB / PINC / PIND | Datos de Entrada | Lectura de niveles lógicos presentes en los pines físicos |
| ADMUX | Selección Multiplexor ADC | Configura referencia de tensión (REFS1:0), ajuste izquierda (ADLAR) y canal (MUX3:0) |
| ADCSRA | Control y Estado ADC | Habilita ADC (ADEN), inicia conversión (ADSC), auto-trigger (ADATE) y prescaler (ADPS2:0) |
| TCCR1A / TCCR1B | Control Timer1 (16-bit) | Configura modo de operación PWM (WGM13:0), compare match (COM1A/B) y prescaler (CS12:0) |
| UCSR0A / UCSR0B / UCSR0C | Control USART0 | Flags de recepción (RXC0), transmisión (TXC0), habilitación (RXEN0, TXEN0) y formato de trama |
| UBRR0H / UBRR0L | Baud Rate USART0 | Registro de 12 bits para divisor de velocidad serie: BAUD = F_CPU / (16 * (UBRR + 1)) |
| SPCR / SPSR / SPDR | Control/Estado/Dato SPI | Habilita SPI (SPE), maestro/esclavo (MSTR), polaridad (CPOL), fase (CPHA) y velocidad (SPR1:0) |
| TWCR / TWSR / TWBR | Control/Estado/Baud TWI | Controla inicio (TWSTA), parada (TWSTO), interrupción (TWINT) y prescaler de bus I2C |

### Distribución de Pines (Encapsulado PDIP 28 pines)
| Pin | Nombre | Tipo | Funciones Alternativas |
|---|---|---|---|
| 1 | PC6 | I/O | RESET / PCINT14 |
| 2 | PD0 | I/O | RXD (Entrada de datos USART) / PCINT16 |
| 3 | PD1 | I/O | TXD (Salida de datos USART) / PCINT17 |
| 4 | PD2 | I/O | INT0 (Interrupción Externa 0) / PCINT18 |
| 5 | PD3 | I/O | INT1 (Interrupción Externa 1) / OC2B (Salida PWM Timer2) / PCINT19 |
| 6 | PD4 | I/O | XCK (Reloj USART) / T0 (Entrada externa Timer0) / PCINT20 |
| 7 | VCC | Power | Alimentación digital principal |
| 8 | GND | Power | Tierra digital |
| 9 | PB6 | I/O | XTAL1 (Oscilador a cristal) / TOSC1 (Oscilador RTC) / PCINT6 |
| 10 | PB7 | I/O | XTAL2 (Oscilador a cristal) / TOSC2 (Oscilador RTC) / PCINT7 |
| 11 | PD5 | I/O | T1 (Entrada externa Timer1) / OC0B (Salida PWM Timer0) / PCINT21 |
| 12 | PD6 | I/O | AIN0 (Entrada + Comparador) / OC0A (Salida PWM Timer0) / PCINT22 |
| 13 | PD7 | I/O | AIN1 (Entrada - Comparador) / PCINT23 |
| 14 | PB0 | I/O | ICP1 (Captura de entrada Timer1) / CLKO / PCINT0 |
| 15 | PB1 | I/O | OC1A (Salida PWM Timer1 Canal A) / PCINT1 |
| 16 | PB2 | I/O | SS (Selección de esclavo SPI) / OC1B (Salida PWM Timer1) / PCINT2 |
| 17 | PB3 | I/O | MOSI (Salida Maestro/Entrada Esclavo SPI) / OC2A / PCINT3 |
| 18 | PB4 | I/O | MISO (Entrada Maestro/Salida Esclavo SPI) / PCINT4 |
| 19 | PB5 | I/O | SCK (Reloj serie SPI) / LED en placas Arduino / PCINT5 |
| 20 | AVCC | Power | Alimentación para convertidor ADC (debe desacoplarse con filtro LC de VCC) |
| 21 | AREF | Analog | Pin de referencia de tensión externa para convertidor ADC |
| 22 | GND | Power | Tierra analógica/digital |
| 23 | PC0 | I/O | ADC0 (Entrada analógica 0) / PCINT8 |
| 24 | PC1 | I/O | ADC1 (Entrada analógica 1) / PCINT9 |
| 25 | PC2 | I/O | ADC2 (Entrada analógica 2) / PCINT10 |
| 26 | PC3 | I/O | ADC3 (Entrada analógica 3) / PCINT11 |
| 27 | PC4 | I/O | ADC4 (Entrada analógica 4) / SDA (Línea de datos I2C) / PCINT12 |
| 28 | PC5 | I/O | ADC5 (Entrada analógica 5) / SCL (Línea de reloj I2C) / PCINT13 |

# Aplicaciones

- Microcontrolador central de la placa Arduino UNO R3 y Arduino Nano.
- Sistemas embebidos industriales y controladores de automatización compactos.
- Adquisición de datos mediante sensores analógicos y digitales I2C/SPI.
- Control de motores mediante señales PWM de alta velocidad y modulación de ciclo.
- Dispositivos IoT de bajo consumo con modos Power-down activados por interrupción externa.

# Limitaciones y Advertencias

- **Tolerancia de niveles lógicos:** Los pines no toleran voltajes superiores a VCC + 0.5 V; operar a 3.3 V requiere convertidores de nivel bidireccionales para comunicarse con periféricos de 5 V.
- **Corriente máxima por puerto:** La suma de corrientes de todos los pines de salida no debe superar los 150 mA en los puertos B y C, ni 150 mA en el puerto D.
- **Alimentación de AVCC:** AVCC no debe diferir de VCC en más de ±0.3 V; conectar siempre AVCC a VCC mediante inductancia de 10 µH y capacitor de 100 nF si se requiere precisión ADC.
- **Frecuencia vs Voltaje:** Operar a 16 MHz o 20 MHz requiere al menos 4.5 V; operar a 3.3 V con cristal de 16 MHz viola las especificaciones de temporización garantizadas por el fabricante.
"""

ATMEGA328DS_JSON = {
  "file_name": "atmega328ds.pdf",
  "processed_file": "data/processed/arduino/atmega328ds.md",
  "source_path": "data/raw/Microcontroladores_RAG_Documentacion/Arduino/atmega328ds.pdf",
  "category": "Arduino",
  "type": "Datasheet (Complete)",
  "component": "ATmega328 / ATmega328P",
  "manufacturer": "Atmel / Microchip",
  "family": "megaAVR 8-bit",
  "interfaces": [
    "UART",
    "USART",
    "SPI",
    "I2C",
    "ADC",
    "PWM",
    "GPIO"
  ],
  "voltage": {
    "operating_range": "1.8V - 5.5V",
    "operating_at_20mhz": "4.5V - 5.5V",
    "operating_at_10mhz": "2.7V - 5.5V",
    "operating_at_4mhz": "1.8V - 5.5V",
    "abs_max_vcc": "6.0V"
  },
  "temperature_range": {
    "min": "-40 °C",
    "max": "85 °C / 125 °C"
  },
  "topics": [
    "Arquitectura AVR RISC y banco de registros de 8 bits",
    "Mapa de memoria Flash (32 kB), SRAM (2 kB) y EEPROM (1 kB)",
    "Configuración y registros de Timer0, Timer1 (16 bits) y Timer2",
    "Conversor Analógico Digital ADC de 10 bits y referencia interna de 1.1 V",
    "Módulos de comunicación serie USART, SPI y TWI/I2C",
    "Interrupciones externas (INT0, INT1) e interrupciones por cambio de pin (PCINT)",
    "Límites eléctricos absolutos y curvas de frecuencia respecto al voltaje"
  ],
  "critical_params": {
    "max_frequency_mhz": 20,
    "flash_kb": 32,
    "sram_kb": 2,
    "eeprom_kb": 1,
    "gpio_count": 23,
    "pwm_channels": 6,
    "adc_channels": 8,
    "adc_resolution_bits": 10,
    "max_current_per_io_pin_ma": 40,
    "max_total_current_vcc_gnd_ma": 200
  },
  "keywords": [
    "ATmega328P",
    "ATmega328",
    "AVR",
    "Arduino UNO",
    "Microchip",
    "Atmel",
    "8-bit",
    "PWM",
    "ADC",
    "USART",
    "SPI",
    "I2C",
    "TWI"
  ],
  "issues_found": [
    "Documento extenso de 448 páginas con topología condensada en especificación estructurada respetando tablas de registros principales y límites de corriente."
  ]
}

ATMEGA2560_MD = """# Información general

- **Nombre del componente:** ATmega640 / ATmega1280 / ATmega1281 / ATmega2560 / ATmega2561
- **Fabricante:** Atmel / Microchip Technology
- **Familia:** megaAVR 8-bit de alta capacidad
- **Tipo de dispositivo:** Microcontrolador de 8 bits con amplio número de pines y memoria expandida
- **Arquitectura:** AVR RISC avanzada con 135 instrucciones
- **Registros de trabajo:** 32 registros de 8 bits de propósito general
- **Rendimiento:** Hasta 16 MIPS a 16 MHz
- **Capacidades de Memoria por Variante:**
  - ATmega640: 64 kB Flash, 8 kB SRAM, 4 kB EEPROM
  - ATmega1280 / ATmega1281: 128 kB Flash, 8 kB SRAM, 4 kB EEPROM
  - ATmega2560 / ATmega2561: 256 kB Flash, 8 kB SRAM, 4 kB EEPROM
- **Soporte de Memoria Externa:** Interfaz de bus externa direccionable hasta 64 kB de espacio de datos
- **Encapsulados:** 100-pin TQFP y 100-ball CBGA (ATmega640/1280/2560); 64-pin TQFP y 64-pad QFN (ATmega1281/2561)

# Características eléctricas

## Valores Máximos Absolutos
- **Tensión en cualquier pin (excepto RESET) respecto a GND:** -0.5 V a VCC + 0.5 V
- **Tensión en pin RESET respecto a GND:** -0.5 V a +13.0 V
- **Tensión de alimentación máxima (VCC):** 6.0 V
- **Corriente continua máxima por pin de I/O:** 40.0 mA
- **Corriente continua total en pines VCC y GND:** 200.0 mA (encapsulado 64 pines) / 400.0 mA (encapsulado 100 pines)
- **Temperatura de almacenamiento:** -65 °C a +150 °C

## Rangos Operativos Recomendados
- **Tensión de alimentación:**
  - ATmega2560V (bajo voltaje): 1.8 V a 5.5 V (0-4 MHz a 1.8V-5.5V, 0-8 MHz a 2.7V-5.5V)
  - ATmega2560 estándar: 4.5 V a 5.5 V para operación a 16 MHz (2.7V-5.5V para 0-8 MHz)
- **Rango de temperatura operativa:** -40 °C a +85 °C (Industrial)

# Interfaces y Periféricos

- **GPIO:**
  - Dispositivos de 100 pines (ATmega2560): 86 líneas I/O bidireccionales con resistencias pull-up configurables.
  - Dispositivos de 64 pines (ATmega2561): 54 líneas I/O bidireccionales.
- **Temporizadores y Contadores:**
  - 2x Temporizadores/Contadores de 8 bits con prescalers independientes y modo compare (Timer0, Timer2).
  - 4x Temporizadores/Contadores de 16 bits (Timer1, Timer3, Timer4, Timer5 en modelos de 100 pines) con captura de entrada y múltiples canales compare.
  - Timer2 con capacidad de reloj asíncrono para RTC de 32.768 kHz.
- **Canales PWM:** Hasta 16 canales PWM con resolución programable de 2 a 16 bits (12 canales en encapsulado de 64 pines).
- **Convertidor Analógico-Digital (ADC):**
  - Resolución: 10 bits.
  - Canales: 16 canales multiplexados en encapsulado de 100 pines; 8 canales en encapsulado de 64 pines.
  - Entradas diferenciales con ganancia programable de 10x y 200x.
  - Referencias de tensión: Interna seleccionable (1.1 V y 2.56 V), AVCC o pin AREF externo.
- **Puertos USART:** 4x USARTs serie independientes totalmente programables con soporte para modo SPI maestro e interrupciones de buffer vacío y recepción completa.
- **SPI (Serial Peripheral Interface):** Interfaz SPI maestro/esclavo por hardware de alta velocidad.
- **I2C / TWI:** Interfaz serie de dos hilos compatible con I2C hasta 400 kHz con reconocimiento de direcciones de esclavo de 7 bits.
- **Interfaz JTAG:** Conforme a norma IEEE 1149.1 para depuración en chip (On-chip Debug), escaneo de límites (Boundary-scan) y programación.

# Pines importantes y Registros

### Registros Clave de Periféricos
| Periférico | Registros principales | Descripción técnica |
|---|---|---|
| Puertos I/O | DDRA..DDRL, PORTA..PORTL, PINA..PINL | Configuración de dirección, salida y lectura de los puertos de 8 bits A a L |
| USART0..3 | UCSRnA, UCSRnB, UCSRnC, UBRRnH/L, UDRn | Control, habilitación y divisores de baud rate para los 4 puertos serie (n = 0, 1, 2, 3) |
| Timers 1, 3, 4, 5 | TCCRnA, TCCRnB, TCCRnC, TCNTn, OCRnA/B/C, ICRn | Temporizadores de 16 bits con hasta 3 canales compare independientes por timer |
| ADC Multicanal | ADMUX, ADCSRA, ADCSRB, ADCH/ADCL, DIDR0, DIDR2 | Control de conversión, selección de canal (MUX5:0) y deshabilitación de buffers digitales |
| Interrupciones | EICRA, EICRB, EIMSK, EIFR, PCICR, PCMSK0..2 | Configuración de interrupciones externas INT0..INT7 y cambio de pin PCINT0..23 |

### Mapeo de Puertos y Funciones en Placas Arduino Mega 2560
- **Puerto E (PE0, PE1):** USART0 RX0 y TX0 (comunicación con coprocesador USB ATmega16U2).
- **Puerto D (PD2, PD3):** USART1 RX1 y TX1 (Pines digitales D19 y D18).
- **Puerto H (PH0, PH1):** USART2 RX2 y TX2 (Pines digitales D17 y D16).
- **Puerto J (PJ0, PJ1):** USART3 RX3 y TX3 (Pines digitales D15 y D14).
- **Puerto B (PB0..PB3):** SPI (PB0=SS, PB1=SCK, PB2=MOSI, PB3=MISO en conector ICSP central).
- **Puerto D (PD1, PD0):** Bus I2C / TWI (PD1=SDA, PD0=SCL en pines D20 y D21).
- **Puerto F / Puerto K:** Entradas analógicas ADC0..ADC7 (Puerto F) y ADC8..ADC15 (Puerto K).

# Aplicaciones

- Procesador principal de la placa de desarrollo Arduino Mega 2560 Rev3.
- Controladores de impresoras 3D multieje (ej. firmware Marlin / placas RAMPS).
- Robótica avanzada que requiere múltiples sensores analógicos y servos PWM concurrentes.
- Sistemas de pasarela de comunicación con traducción entre múltiples buses serie UART/I2C/SPI.
- Control numérico computarizado (CNC) e instrumentación de laboratorio.

# Limitaciones y Advertencias

- **Nivel de tensión lógica:** La lógica I/O es estrictamente referenciada a VCC (típicamente 5 V en placas estándar); no es tolerante a 5 V si el microcontrolador se alimenta a 3.3 V.
- **Límites de disipación de corriente:** Aunque el encapsulado tolera 400 mA combinados, ningún puerto individual debe exceder 100 mA de corriente acumulada.
- **Tensión de AVCC:** AVCC debe mantenerse dentro del rango VCC ± 0.3 V.
- **Reloj a 16 MHz:** Requiere alimentación superior a 4.5 V para garantizar estabilidad de frecuencia.
"""

ATMEGA2560_JSON = {
  "file_name": "atmel-2549-8-bit-avr-microcontroller-atmega640-1280-1281-2560-2561_datasheet.pdf",
  "processed_file": "data/processed/arduino/atmel-2549-8-bit-avr-microcontroller-atmega640-1280-1281-2560-2561_datasheet.md",
  "source_path": "data/raw/Microcontroladores_RAG_Documentacion/Arduino/atmel-2549-8-bit-avr-microcontroller-atmega640-1280-1281-2560-2561_datasheet.pdf",
  "category": "Arduino",
  "type": "Datasheet (Complete)",
  "component": "ATmega640 / ATmega1280 / ATmega1281 / ATmega2560 / ATmega2561",
  "manufacturer": "Atmel / Microchip",
  "family": "megaAVR 8-bit",
  "interfaces": [
    "UART",
    "USART",
    "SPI",
    "I2C",
    "ADC",
    "PWM",
    "JTAG",
    "GPIO"
  ],
  "voltage": {
    "operating_range": "1.8V - 5.5V (versión V) / 4.5V - 5.5V a 16 MHz",
    "operating_at_16mhz": "4.5V - 5.5V",
    "operating_at_8mhz": "2.7V - 5.5V",
    "abs_max_vcc": "6.0V"
  },
  "temperature_range": {
    "min": "-40 °C",
    "max": "85 °C"
  },
  "topics": [
    "Arquitectura AVR mega de alta capacidad y mapa de registros extendido",
    "Memoria Flash de 256 kB con direccionamiento de 16 bits y tabla IVT",
    "Configuración de los 4 puertos USART integrados",
    "Módulos Timer/Counter de 16 bits (Timer 1, 3, 4, 5) y 16 canales PWM",
    "Conversor ADC de 16 canales y 10 bits con etapas diferenciales y ganancia programable",
    "Interfaz de memoria externa y depuración por bus JTAG",
    "Límites absolutos y distribución de pines en encapsulado de 100 terminales"
  ],
  "critical_params": {
    "max_frequency_mhz": 16,
    "flash_kb": 256,
    "sram_kb": 8,
    "eeprom_kb": 4,
    "gpio_count": 86,
    "hardware_uarts": 4,
    "pwm_channels": 16,
    "adc_channels": 16,
    "adc_resolution_bits": 10,
    "max_current_per_io_pin_ma": 40,
    "max_total_current_vcc_gnd_ma": 400
  },
  "keywords": [
    "ATmega2560",
    "ATmega1280",
    "ATmega640",
    "Arduino Mega",
    "Microchip",
    "Atmel",
    "AVR",
    "8-bit",
    "4x USART",
    "16x PWM",
    "16x ADC",
    "JTAG"
  ],
  "issues_found": [
    "Datasheet completo de 435 páginas; condensado en especificación estructurada según habilidades datasheet-analyzer y technical-document-cleaner."
  ]
}

def write_arduino_docs():
    p_proc = Path("data/processed/arduino")
    p_meta = Path("data/metadata/arduino")
    p_proc.mkdir(parents=True, exist_ok=True)
    p_meta.mkdir(parents=True, exist_ok=True)

    # 1. ATmega328ds
    (p_proc / "atmega328ds.md").write_text(ATMEGA328DS_MD, encoding="utf-8")
    with open(p_meta / "atmega328ds.json", "w", encoding="utf-8") as f:
        json.dump(ATMEGA328DS_JSON, f, indent=2, ensure_ascii=False)
    print("Wrote atmega328ds.md and atmega328ds.json")

    # 2. ATmega2560
    f_md = "atmel-2549-8-bit-avr-microcontroller-atmega640-1280-1281-2560-2561_datasheet.md"
    f_json = "atmel-2549-8-bit-avr-microcontroller-atmega640-1280-1281-2560-2561_datasheet.json"
    (p_proc / f_md).write_text(ATMEGA2560_MD, encoding="utf-8")
    with open(p_meta / f_json, "w", encoding="utf-8") as f:
        json.dump(ATMEGA2560_JSON, f, indent=2, ensure_ascii=False)
    print(f"Wrote {f_md} and {f_json}")

if __name__ == "__main__":
    write_arduino_docs()
