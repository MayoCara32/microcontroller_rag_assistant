"""Generación de especificaciones Markdown, metadatos JSON para lote Protocolos."""
from pathlib import Path
import json

UM10204_MD = """# Información general

- **Nombre del componente:** I2C-bus Specification and User Manual
- **Documento:** UM10204 Rev. 7.0 (NXP Semiconductors)
- **Fabricante / Organización:** NXP Semiconductors (originalmente Philips Semiconductors)
- **Familia:** Serial Communication Protocols / Two-Wire Bus Architecture
- **Tipo de documento:** Specification and User Manual (Estándar Oficial)
- **Topología física:** Bus serie bidireccional síncrono de 2 hilos con líneas a colector/drenador abierto (Open-drain / Open-collector)
- **Líneas del bus:**
  - **SDA (Serial Data Line):** Línea de datos serie bidireccional.
  - **SCL (Serial Clock Line):** Línea de reloj serie síncrono generada por el maestro (con soporte de estiramiento por el esclavo).
- **Resistencias de pull-up (Rp):** Cada línea debe conectarse a la tensión de alimentación positiva ($V_{DD}$) mediante una resistencia pull-up externa.

# Modos de Velocidad y Características Eléctricas

| Modo de Operación | Velocidad Máxima | Sentido de Transmisión | Carga Capacitiva Máxima (Cb) | Supresión de Picos (Glitch Filter) |
|---|---|---|---|---|
| Standard-mode (Sm) | Hasta 100 kbit/s | Bidireccional | 400 pF | No obligatoria |
| Fast-mode (Fm) | Hasta 400 kbit/s | Bidireccional | 400 pF | 50 ns supresión en chip |
| Fast-mode Plus (Fm+) | Hasta 1 Mbit/s | Bidireccional | 550 pF | 50 ns supresión en chip |
| High-speed mode (Hs-mode) | Hasta 3.4 Mbit/s | Bidireccional | 100 pF (a 3.4 Mbps) / 400 pF (a 1.7 Mbps) | 10 ns supresión en chip |
| Ultra Fast-mode (UFm) | Hasta 5 Mbit/s | Unidireccional (Push-pull) | 400 pF | No aplicable |

## Rangos de Tensión y Niveles Lógicos
- **Tensión de alimentación típica (VDD):** 1.8 V, 2.5 V, 3.3 V o 5.0 V.
- **Tensión de entrada en nivel bajo (VIL):** Máximo $0.3 \\times V_{DD}$.
- **Tensión de entrada en nivel alto (VIH):** Mínimo $0.7 \\times V_{DD}$.
- **Tensión de salida en nivel bajo (VOL):** Máximo $0.4\\ \\text{V}$ a corriente de drenador especificada ($3\\ \\text{mA}$ para Sm/Fm; $20\\ \\text{mA}$ para Fm+).

## Cálculo de Resistencias de Pull-Up (Rp)
- **Resistencia mínima ($R_{p(\\text{min})}$):** Limitada por la corriente máxima admisible que pueden drenar los transistores del bus ($I_{OL}$):
  $$R_{p(\\text{min})} = \\frac{V_{DD} - V_{OL(\\text{max})}}{I_{OL}}$$
  *(Para $V_{DD} = 5\\ \\text{V}$, $V_{OL} = 0.4\\ \\text{V}$ e $I_{OL} = 3\\ \\text{mA}$: $R_{p(\\text{min})} \\approx 1.53\\ \\text{k}\\Omega$)*.
- **Resistencia máxima ($R_{p(\\text{max})}$):** Limitada por el tiempo de subida admisible ($t_r$) y la capacitancia total del bus ($C_b$):
  $$R_{p(\\text{max})} = \\frac{t_r}{0.8473 \\times C_b}$$
  *(Para Standard-mode con $t_r = 1000\\ \\text{ns}$ y $C_b = 400\\ \\text{pF}$: $R_{p(\\text{max})} \\approx 2.95\\ \\text{k}\\Omega$)*.

# Protocolo y Formato de Tramas

## Condiciones de Señalización en el Bus
- **Bus Libre (Bus Free):** Ambas líneas SDA y SCL permanecen en nivel alto (HIGH).
- **Condición de INICIO (START - S):** Transición de nivel ALTO a BAJO en la línea SDA mientras SCL permanece en ALTO.
- **Condición de PARADA (STOP - P):** Transición de nivel BAJO a ALTO en la línea SDA mientras SCL permanece en ALTO.
- **INICIO Repetido (Repeated START - Sr):** Generación de una nueva condición de START sin haber emitido previamente un STOP; permite encadenar transacciones manteniendo el control del bus.
- **Validez de los Datos:** Durante la transmisión de bits, el nivel en SDA debe permanecer completamente estable durante todo el pulso en ALTO de SCL. Los cambios de estado en SDA solo están permitidos cuando SCL se encuentra en nivel BAJO.

## Formato del Byte y Reconocimiento (ACK / NACK)
- Cada byte transferido en el bus consta de **8 bits de datos** seguidos por **1 bit de confirmación (Acknowledge - ACK)** en el 9º pulso de reloj.
- Durante el pulso de reloj de ACK:
  - El transmisor libera la línea SDA (la deja flotar a HIGH mediante la resistencia de pull-up).
  - El receptor debe forzar activamente SDA a nivel BAJO (**ACK = 0**).
  - Si el receptor deja SDA en nivel ALTO (**NACK = 1**), indica condición de no reconocimiento (fin de lectura, esclavo ocupado o dirección inexistente).

## Esquemas de Direccionamiento
### Direccionamiento de 7 bits
- El primer byte tras la condición de START contiene los 7 bits de dirección del esclavo (MSB primero) y el bit 8 que indica el sentido de operación:
  - **R/W = 0:** Operación de Escritura (Maestro transmite hacia el esclavo).
  - **R/W = 1:** Operación de Lectura (Maestro recibe datos del esclavo).
- **Direcciones reservadas de 7 bits:**
  - `0000 000 0`: Llamada general (General Call reset/reconfiguración).
  - `0000 000 1`: Byte de inicio (Start byte).
  - `1111 0xx x`: Cabecera de direccionamiento de 10 bits.
  - `1111 1xx x`: Identificador de dispositivo (Device ID).

### Direccionamiento de 10 bits
- Utiliza dos bytes de cabecera: el primer byte contiene el prefijo `1111 0` seguido de los dos bits más significativos de la dirección y el bit R/W; el segundo byte transporta los 8 bits restantes de la dirección.

# Sincronización, Arbitraje y Estiramiento de Reloj

- **Estiramiento de Reloj (Clock Stretching):** Si un dispositivo esclavo necesita tiempo adicional para procesar un byte recibido o atender una interrupción interna, puede forzar y retener la línea SCL en nivel BAJO. El maestro detecta esta condición y suspende la generación de pulsos de reloj hasta que el esclavo libera SCL.
- **Arbitraje Multimaestro No Destructivo:** Si dos maestros inician simultáneamente una transmisión, monitorizan la línea SDA bit a bit. Dado que el bus funciona por lógica cableada (Wired-AND), el primer maestro que intenta emitir un '1' (deja flotar SDA) pero detecta un '0' en la línea (forzado por el otro maestro) pierde el arbitraje de inmediato, apaga sus drivers y pasa a modo de escucha sin corromper la trama.

# Aplicaciones

- Comunicación con sensores de bajo y medio ancho de banda (acelerómetros, sensores ambientales I2C como BME280/MPU6050).
- Chips de memoria EEPROM serie (ej. familia 24LCxx) y relojes de tiempo real (RTC DS1307/DS3231).
- Expansores de puertos GPIO (PCF8574, MCP23017) y controladores de pantallas OLED (SSD1306).

# Limitaciones y Advertencias

- **Capacitancia del bus:** La longitud física del bus I2C está severamente limitada por la capacitancia acumulada en los cables ($C_b > 400\\ \\text{pF}$ provoca distorsión en los tiempos de subida); no utilizar cables largos no apantallados sin buffers o transceptores diferenciales dedicados (PCA9615).
- **Bloqueo del bus (I2C Bus Lockup):** Si el maestro se reinicia o se cuelga en medio de una lectura mientras el esclavo está transmitiendo un bit '0', la línea SDA queda bloqueada en nivel bajo indefinidamente. Procedimiento de recuperación: El maestro debe generar manualmente 9 pulsos en SCL seguidos de una condición de STOP.
"""

UM10204_JSON = {
  "file_name": "UM10204.pdf",
  "processed_file": "data/processed/protocolos/UM10204.md",
  "source_path": "data/raw/Microcontroladores_RAG_Documentacion/Protocolos/UM10204.pdf",
  "category": "Protocolos",
  "type": "Specification and User Manual",
  "component": "I2C-bus Specification (UM10204)",
  "manufacturer": "NXP Semiconductors",
  "family": "Serial Communication Protocols",
  "interfaces": [
    "I2C"
  ],
  "voltage": {
    "standard_vdd": "1.8V, 2.5V, 3.3V, 5.0V",
    "vol_max": "0.4V a 3 mA (Sm/Fm) o 20 mA (Fm+)"
  },
  "temperature_range": {
    "min": "unknown",
    "max": "unknown"
  },
  "topics": [
    "Especificación oficial del protocolo I2C y modos de velocidad (Sm 100k, Fm 400k, Fm+ 1M, Hs 3.4M)",
    "Líneas SDA y SCL a drenador abierto y cálculo formal de resistencias pull-up (Rp_min y Rp_max)",
    "Condiciones de señalización: START, STOP, Repeated START y ventana de estabilidad de datos",
    "Formato de trama de 8 bits con confirmación ACK/NACK en el noveno ciclo",
    "Direccionamiento estándar de 7 bits, direcciones reservadas y direccionamiento extendido de 10 bits",
    "Sincronización por estiramiento de reloj (Clock Stretching) y arbitraje multimaestro sin colisión",
    "Problema del bloqueo de bus (Bus Lockup) y secuencia de recuperación mediante 9 pulsos SCL"
  ],
  "critical_params": {
    "max_speed_standard_kbps": 100,
    "max_speed_fast_kbps": 400,
    "max_speed_fast_plus_kbps": 1000,
    "max_bus_capacitance_pf": 400,
    "addressing_modes": "7-bit, 10-bit",
    "lines": "SDA (Serial Data), SCL (Serial Clock)"
  },
  "keywords": [
    "I2C",
    "I2C-bus",
    "UM10204",
    "NXP",
    "SDA",
    "SCL",
    "Pull-up",
    "Open-Drain",
    "Clock Stretching",
    "Arbitration",
    "ACK",
    "NACK",
    "Fast-Mode"
  ],
  "issues_found": [
    "Manual de especificación técnica oficial de NXP (62 páginas); estructurado rigurosamente para el sistema RAG técnico."
  ]
}

MODBUS_MD = """# Información general

- **Nombre del componente:** MODBUS Application Protocol Specification
- **Documento:** MODBUS Application Protocol Specification V1.1b3
- **Organización / Fabricante:** Modbus Organization (Modbus-IDA)
- **Familia:** Industrial Communication Protocols / Fieldbus Architecture
- **Tipo de documento:** Protocol Specification (Estándar Abierto)
- **Capa del modelo OSI:** Nivel 7 (Capa de Aplicación)
- **Modelo de comunicación:** Cliente / Servidor (históricamente Maestro / Esclavo) mediante esquema de solicitud-respuesta (Request / Response)
- **Pila de comunicación:**
  - MODBUS sobre líneas serie (TIA/EIA-485, TIA/EIA-232) en modos **RTU** (binario con verificación CRC-16) o **ASCII** (con verificación LRC).
  - MODBUS sobre TCP/IP (puerto estándar IANA: **502**).

# Estructura del Protocolo y Tramas

## Unidades de Datos (PDU vs. ADU)
- **PDU (Protocol Data Unit):** Estructura independiente de la capa física de transporte:
  $$\\text{PDU} = [\\text{Function Code (1 byte)}] + [\\text{Data (variable)}]$$
- **ADU (Application Data Unit):** PDU encapsulada con direccionamiento y suma de verificación específica del medio:
  $$\\text{ADU Serial} = [\\text{Address (1 byte)}] + [\\text{PDU}] + [\\text{Error Check (2 bytes CRC o 1 byte LRC)}]$$
  $$\\text{ADU TCP/IP} = [\\text{MBAP Header (7 bytes)}] + [\\text{PDU}]$$

## Cabecera MBAP (Modbus TCP)
Consta de 7 bytes prefijados a la PDU:
1. **Transaction Identifier (2 bytes):** Identificador para emparejar solicitudes y respuestas concurrentes.
2. **Protocol Identifier (2 bytes):** Siempre `0x0000` para protocolo Modbus.
3. **Length (2 bytes):** Conteo de bytes restantes en la trama (incluyendo el Unit Identifier y la PDU).
4. **Unit Identifier (1 byte):** Dirección del dispositivo esclavo para pasarelas serie o puenteo (`0xFF` o `0x01` por defecto).

# Modelo de Datos Modbus

El protocolo define 4 bloques lógicos de datos con rangos de direccionamiento de 1 a 65536 (mapeados internamente de `0x0000` a `0xFFFF` en la trama):

| Tipo de Objeto | Tamaño | Acceso | Rango Clásico de Registro | Rango de Dirección en Trama |
|---|---|---|---|---|
| Discretes Input (Entradas Discretas) | 1 bit | Solo Lectura (Read-Only) | 10001 - 19999 | `0x0000` - `0xFFFF` |
| Coils (Bobinas de Relé) | 1 bit | Lectura y Escritura (Read-Write) | 00001 - 09999 | `0x0000` - `0xFFFF` |
| Input Registers (Registros de Entrada) | 16 bits (Palabra) | Solo Lectura (Read-Only) | 30001 - 39999 | `0x0000` - `0xFFFF` |
| Holding Registers (Registros de Retención) | 16 bits (Palabra) | Lectura y Escritura (Read-Write) | 40001 - 49999 | `0x0000` - `0xFFFF` |

# Códigos de Función Principales (Function Codes)

| Código (Dec) | Código (Hex) | Nombre del Servicio | Descripción Técnica |
|---|---|---|---|
| **01** | `0x01` | Read Coils | Lee estado ON/OFF de bobinas contiguas (1 a 2000 bobinas por trama) |
| **02** | `0x02` | Read Discrete Inputs | Lee estado de entradas digitales físicas (1 a 2000 entradas) |
| **03** | `0x03` | Read Holding Registers | Lee contenido de bloques de registros de retención de 16 bits (1 a 125 registros) |
| **04** | `0x04` | Read Input Registers | Lee valores de registros de entrada analógicos/sensores (1 a 125 registros) |
| **05** | `0x05` | Write Single Coil | Fuerza el estado de una sola bobina (`0xFF00` = ON; `0x0000` = OFF) |
| **06** | `0x06` | Write Single Register | Escribe un valor de 16 bits en un solo registro de retención |
| **15** | `0x0F` | Write Multiple Coils | Modifica un bloque de bobinas contiguas (1 a 1968 bobinas) |
| **16** | `0x10` | Write Multiple Registers | Escribe un bloque de registros de 16 bits contiguos (1 a 123 registros) |
| **23** | `0x17` | Read/Write Multiple Registers | Ejecuta una lectura y una escritura combinadas en una sola transacción |

# Gestión de Excepciones

Si un servidor/esclavo recibe una solicitud válida pero no puede ejecutar la operación requerida, devuelve una **Respuesta de Excepción**:
- El código de función devuelto se modifica sumándole `0x80` (se activa el bit más significativo MSB).
- Se anexa un byte con el **Código de Excepción**:

| Código de Excepción | Nombre de la Excepción | Causa Raíz |
|---|---|---|
| `0x01` | ILLEGAL FUNCTION | El código de función no está implementado o no está admitido en el servidor |
| `0x02` | ILLEGAL DATA ADDRESS | La dirección de registro o bobina no existe o está fuera del rango permitido |
| `0x03` | ILLEGAL DATA VALUE | La cantidad de registros solicitada excede el límite de la trama o el valor escrito es inválido |
| `0x04` | SLAVE DEVICE FAILURE | Ocurrió un error irrecuperable en el servidor mientras intentaba ejecutar la acción |
| `0x05` | ACKNOWLEDGE | El servidor aceptó la solicitud pero requiere tiempo prolongado para completarla |
| `0x06` | SLAVE DEVICE BUSY | El servidor está ejecutando un comando de larga duración; el cliente debe reintentar |

# Aplicaciones

- Comunicación con autómatas programables (PLCs) en líneas de fabricación industrial.
- Lectura de transductores de potencia, analizadores de red y medidores de energía eléctrica trifásica.
- Control de variadores de frecuencia (VFD) y servomotores industriales.
- Sistemas de monitorización SCADA y pasarelas de telemetría IoT industrial.

# Limitaciones y Advertencias

- **Seguridad en Modbus Clásico:** El protocolo Modbus estándar carece de autenticación, cifrado o verificación de integridad criptográfica; cualquier nodo en la red puede inyectar tramas maliciosas si no se implementa una capa TLS externa (Modbus Security).
- **Representación de datos superiores a 16 bits (Float y 32-bit int):** El protocolo solo define palabras de 16 bits. La transmisión de flotantes IEEE 754 de 32 bits requiere 2 registros consecutivos y depende del orden de bytes y palabras configurado por el fabricante (Big-endian, Little-endian, Word-swapped).
"""

MODBUS_JSON = {
  "file_name": "modbusprotocolspecification.pdf",
  "processed_file": "data/processed/protocolos/modbusprotocolspecification.md",
  "source_path": "data/raw/Microcontroladores_RAG_Documentacion/Protocolos/modbusprotocolspecification.pdf",
  "category": "Protocolos",
  "type": "Protocol Specification",
  "component": "MODBUS Application Protocol V1.1b3",
  "manufacturer": "Modbus Organization (Modbus-IDA)",
  "family": "Industrial Communication Protocols",
  "interfaces": [
    "Modbus",
    "UART",
    "RS-485",
    "TCP/IP"
  ],
  "voltage": {
    "physical_layer": "Dependiente del medio (RS-485 diferencial: +/- 1.5V a +/- 5V; RS-232: +/- 12V)"
  },
  "temperature_range": {
    "min": "unknown",
    "max": "unknown"
  },
  "topics": [
    "Arquitectura Modbus en capa de aplicación: cliente/servidor y estructura PDU/ADU",
    "Modelo de datos de 4 bloques: Coils (0x), Discrete Inputs (1x), Input Registers (3x) y Holding Registers (4x)",
    "Códigos de función estándar: 01, 02, 03, 04, 05, 06, 15 (0x0F) y 16 (0x10)",
    "Formato de cabecera MBAP para Modbus TCP sobre puerto 502",
    "Mecanismo de respuesta de excepción con bit MSB activado y códigos 01 a 06",
    "Compatibilidad serie RTU con CRC-16 y ASCII con LRC",
    "Problemática de ordenamiento de bytes en datos flotantes de 32 bits y ausencia de seguridad nativa"
  ],
  "critical_params": {
    "standard_tcp_port": 502,
    "function_codes": "01, 02, 03, 04, 05, 06, 15, 16",
    "pdu_structure": "Function Code (1 byte) + Data",
    "max_read_registers": 125,
    "max_write_registers": 123
  },
  "keywords": [
    "Modbus",
    "Modbus-IDA",
    "PDU",
    "ADU",
    "MBAP",
    "Holding Registers",
    "Coils",
    "Input Registers",
    "Discrete Inputs",
    "CRC-16",
    "RS-485",
    "Industrial Ethernet"
  ],
  "issues_found": [
    "Especificación de protocolo industrial oficial de 50 páginas; normalizada conforme a los estándares de catalogación y diseño de chunks."
  ]
}

SBOA621_MD = """# Información general

- **Nombre del componente:** SPI Bus Protocol (SBOA621)
- **Documento:** Understanding the SPI Bus (Application Brief SBOA621)
- **Autor / Fabricante:** Younghua Pan, Texas Instruments
- **Familia:** Synchronous Serial Communication Protocols
- **Tipo de documento:** Application Brief / Technical Guide
- **Topología física:** Bus serie síncrono maestro/esclavo (Controller / Peripheral) de 4 hilos en modo dúplex completo (Full-Duplex)
- **Líneas del bus:**
  - **SCLK:** Serial Clock (reloj serie generado por el controlador maestro).
  - **MOSI / SIMO:** Master Out Slave In / Controller Out Peripheral In (línea de datos del maestro al periférico).
  - **MISO / SOMI:** Master In Slave Out / Controller In Peripheral Out (línea de datos del periférico al maestro).
  - **CS / SS:** Chip Select / Slave Select (línea de selección de periférico, activa en nivel BAJO).

# Modos de Operación SPI (Polaridad y Fase de Reloj)

La relación de fase y sincronización entre el reloj SCLK y los datos transmitidos se define mediante dos parámetros de configuración:
- **CPOL (Clock Polarity):** Determina el estado lógico de la línea SCLK cuando el bus está en reposo (Idle).
  - `CPOL = 0`: Reloj en reposo en nivel BAJO (LOW).
  - `CPOL = 1`: Reloj en reposo en nivel ALTO (HIGH).
- **CPHA (Clock Phase):** Determina qué flanco del reloj se utiliza para muestrear (capturar) el dato y cuál para desplazarlo (conmutar).
  - `CPHA = 0`: El dato se muestrea en el **primer flanco** de SCLK y se desplaza en el segundo flanco.
  - `CPHA = 1`: El dato se desplaza en el primer flanco de SCLK y se muestrea en el **segundo flanco**.

### Matriz de los 4 Modos SPI
| Modo SPI | CPOL | CPHA | Estado de Reposo SCLK | Flanco de Muestreo (Sample Edge) | Flanco de Conmutación (Shift Edge) |
|---|---|---|---|---|---|
| **Modo 0** | 0 | 0 | LOW | Primer flanco (Subida / Rising) | Segundo flanco (Bajada / Falling) |
| **Modo 1** | 0 | 1 | LOW | Segundo flanco (Bajada / Falling) | Primer flanco (Subida / Rising) |
| **Modo 2** | 1 | 0 | HIGH | Primer flanco (Bajada / Falling) | Segundo flanco (Subida / Rising) |
| **Modo 3** | 1 | 1 | HIGH | Segundo flanco (Subida / Rising) | Primer flanco (Bajada / Falling) |

> **Nota práctica:** El **Modo 0 (0,0)** y el **Modo 3 (1,1)** son los esquemas más comunes en memorias Flash SPI, sensores analógicos y pantallas.

# Topologías de Conexión Multi-Esclavo

### 1. Topología en Estrella con Líneas de Chip Select Independientes
- Se comparte una única línea de SCLK, MOSI y MISO entre todos los periféricos.
- El maestro dedica una línea de selección independiente ($\overline{\\text{CS}}_1, \\overline{\\text{CS}}_2, \\dots, \\overline{\\text{CS}}_n$) para cada esclavo.
- Ventaja: Permite comunicarse de forma aislada y flexible con cada esclavo sin interferencia de datos.
- Desventaja: Requiere $N$ líneas GPIO adicionales en el microcontrolador controlador.

### 2. Topología en Cadena (Daisy-Chain)
- Se utiliza una única línea de $\overline{\\text{CS}}$ común para todos los esclavos.
- La salida MISO del Esclavo 1 se conecta a la entrada MOSI del Esclavo 2, encadenándose sucesivamente hasta retornar al MISO del maestro.
- Los dispositivos actúan como un único registro de desplazamiento gigante en anillo.
- Ventaja: Solo requiere 4 líneas físicas independientemente del número de periféricos.
- Desventaja: Todos los dispositivos deben soportar topología daisy-chain y la latencia de actualización se multiplica por el número de nodos.

# Parámetros Temporales Críticos

- **Tiempo de establecimiento de datos (Setup Time - t_SU):** Intervalo mínimo de tiempo que el dato en MOSI/MISO debe permanecer estable antes del flanco activo de muestreo de SCLK.
- **Tiempo de retención de datos (Hold Time - t_H):** Intervalo de tiempo que el dato debe mantenerse estable tras el flanco activo de reloj.
- **Tiempo de retardo de activación (CS to SCLK Delay):** Tiempo requerido desde la caída a nivel bajo de $\overline{\\text{CS}}$ hasta la emisión del primer flanco de reloj para permitir que el periférico active sus buffers de salida.

# Comparativa Técnica: SPI vs. I2C vs. UART

| Característica | SPI | I2C | UART |
|---|---|---|---|
| Número de hilos | 4 (SCLK, MOSI, MISO, CS) | 2 (SDA, SCL) | 2 (TX, RX) |
| Sincronización | Síncrono (reloj explícito) | Síncrono (reloj explícito) | Asíncrono (baud rate preacordado) |
| Modo de transmisión | Dúplex completo (Full-Duplex) | Semidúplex (Half-Duplex) | Dúplex completo (Full-Duplex) |
| Velocidad típica | Muy alta (10 MHz a 80+ MHz) | Media (100 kHz a 1 MHz) | Baja/Media (9600 bps a 921600 bps) |
| Resistencias pull-up | No requeridas (Push-pull) | Obligatorias (Open-drain) | No requeridas |
| Control de flujo / ACK | No tiene (debe gestionarse en software) | Bit de ACK/NACK nativo | Por hardware opcional (RTS/CTS) |

# Aplicaciones

- Interfaces con memorias Flash SPI de alta velocidad (W25Qxx) y memorias EEPROM.
- Control de pantallas gráficas TFT / LCD (controladores ST7789, ILI9341).
- Lectura de convertidores analógico-digitales (ADC) y control de DACs de precisión de alta tasa de muestreo.
- Módulos de comunicación de radiofrecuencia (NRF24L01, transceptores LoRa SX1276).

# Limitaciones y Advertencias

- **Ausencia de control de flujo por hardware nativo:** No existe mecanismo de señalización de ACK/NACK a nivel de protocolo físico; si el esclavo no puede procesar los datos a la velocidad del reloj maestro, se produce pérdida silenciosa de información.
- **Integridad de señal a alta velocidad:** A frecuencias superiores a 20 MHz, las reflexiones y el desacoplamiento de impedancia en pistas largas de PCB pueden causar falsos flancos de reloj; se recomienda colocar resistencias de amortiguación en serie (22 Ω a 33 Ω) en la línea SCLK cerca del maestro.
"""

SBOA621_JSON = {
  "file_name": "sboa621.pdf",
  "processed_file": "data/processed/protocolos/sboa621.md",
  "source_path": "data/raw/Microcontroladores_RAG_Documentacion/Protocolos/sboa621.pdf",
  "category": "Protocolos",
  "type": "Application Brief",
  "component": "SPI Bus Protocol (SBOA621)",
  "manufacturer": "Texas Instruments",
  "family": "Synchronous Serial Communication",
  "interfaces": [
    "SPI"
  ],
  "voltage": {
    "logic_levels": "Configurable según el estándar del controlador (1.8V, 3.3V, 5.0V push-pull)"
  },
  "temperature_range": {
    "min": "unknown",
    "max": "unknown"
  },
  "topics": [
    "Arquitectura síncrona full-duplex de 4 hilos: SCLK, MOSI, MISO y CS",
    "Definición detallada de los 4 modos SPI según polaridad (CPOL) y fase (CPHA)",
    "Topología en estrella con líneas CS dedicadas frente a topología en cadena Daisy-Chain",
    "Requisitos temporales: Setup Time, Hold Time y CS to SCLK Delay",
    "Tabla comparativa exhaustiva entre interfaces SPI, I2C y UART",
    "Consideraciones de integridad de señal y resistencias serie de amortiguación a frecuencias elevadas"
  ],
  "critical_params": {
    "lines_count": 4,
    "spi_modes": "Mode 0 (0,0), Mode 1 (0,1), Mode 2 (1,0), Mode 3 (1,1)",
    "duplex": "Full-Duplex",
    "speed_range": "1 MHz to > 50 MHz"
  },
  "keywords": [
    "SPI",
    "Serial Peripheral Interface",
    "SBOA621",
    "Texas Instruments",
    "CPOL",
    "CPHA",
    "Full-Duplex",
    "Daisy-Chain",
    "Chip Select",
    "MOSI",
    "MISO",
    "SCLK"
  ],
  "issues_found": [
    "Resumen de aplicación conciso de 5 páginas de Texas Instruments; condensado con alta densidad de especificación técnica."
  ]
}

SPRUGP1_MD = """# Información general

- **Nombre del componente:** KeyStone Architecture UART Peripheral
- **Documento:** Universal Asynchronous Receiver/Transmitter (UART) User Guide (Literature Number: SPRUGP1)
- **Fabricante:** Texas Instruments
- **Familia:** Embedded Peripherals / UART Architecture
- **Tipo de documento:** User Guide / Architecture Manual
- **Compatibilidad:** Conforme con el estándar industrial TL16C550 / 16550 UART
- **Modos de operación:** Transmisión y recepción asíncrona dúplex completa (Full-Duplex)
- **Topología física:** 2 hilos básicos (TXD, RXD) con líneas de control de flujo por hardware opcionales (RTS, CTS)

# Estructura del Generador de Baudios y Formato de Carácter

## Generador de Tasa de Baudios (Baud Rate Generator)
- Divisor de frecuencia programable de 16 bits dividido en dos registros de 8 bits: `DLL` (Divisor Latch Low) y `DLH` (Divisor Latch High).
- **Relación de sobremuestreo:** El periférico utiliza sobremuestreo de 16x (o 13x seleccionable en modo de alta velocidad) para centrar la toma de muestras en el pulso de bit y rechazar ruido de transición.
- **Fórmula de cálculo de Baud Rate:**
  $$\\text{Baud Rate} = \\frac{f_{\\text{UARTCLK}}}{16 \\times (\\text{Divisor})}$$
  $$\\text{Divisor} = \\frac{f_{\\text{UARTCLK}}}{16 \\times \\text{Baud Rate}}$$
  donde $\\text{Divisor} = (\\text{DLH} \\times 256) + \\text{DLL}$.

## Formato del Carácter y Trama Asíncrona
Una trama UART asíncrona se compone secuencialmente de:
1. **Bit de Inicio (Start Bit):** Nivel BAJO ('0') que señaliza el comienzo de la trama.
2. **Bits de Datos:** 5, 6, 7 u 8 bits de datos programables (transmitidos comenzando por el LSB).
3. **Bit de Paridad (Opcional):**
   - Sin paridad (None).
   - Paridad Par (Even): El bit se ajusta para que la suma de unos sea par.
   - Paridad Impar (Odd): El bit se ajusta para que la suma de unos sea impar.
   - Paridad Fija (Stick Parity): Bit fijado permanentemente en '1' (Mark) o '0' (Space).
4. **Bits de Parada (Stop Bits):** 1, 1.5 o 2 bits en nivel ALTO ('1') que restauran la línea al estado de reposo.

# Buffers FIFO y Control de Flujo por Hardware

## Colas FIFO de 16 Bytes
- **FIFO de Transmisión (TX FIFO):** Buffer de 16 bytes que almacena caracteres pendientes de envío, reduciendo la carga de interrupciones sobre la CPU.
- **FIFO de Recepción (RX FIFO):** Buffer de 16 bytes con niveles de disparo (Trigger Levels) programables a 1, 4, 8 o 14 bytes para disparar la interrupción de datos disponibles.

## Control de Flujo por Hardware Automático (Auto-RTS / Auto-CTS)
- **Auto-RTS:** El hardware UART fuerza automáticamente la línea `RTS` a nivel ALTO cuando la FIFO de recepción alcanza el umbral de disparo configurado, indicando al transmisor remoto que suspenda el envío. Cuando la CPU vacía la FIFO por debajo del umbral, el hardware vuelve a poner `RTS` en nivel BAJO de forma transparente.
- **Auto-CTS:** El transmisor suspende el envío del siguiente carácter si detecta la línea `CTS` en nivel ALTO, evitando desbordamientos de buffer (Receiver Overrun).

# Registros de Control y Estado del Periférico

| Registro | Mnemónico | Tipo | Descripción Funcional |
|---|---|---|---|
| Receiver Buffer Register | `RBR` | Read-only | Lee el byte superior recibido de la FIFO de recepción (DLAB = 0) |
| Transmitter Holding Register | `THR` | Write-only | Escribe el siguiente byte a transmitir en la FIFO de transmisión (DLAB = 0) |
| Interrupt Enable Register | `IER` | Read/Write | Habilita interrupciones de datos recibidos (ERBI), transmisor vacío (ETBEI) y estado de línea (ELSI) |
| Interrupt Identification Register | `IIR` | Read-only | Identifica la prioridad y la causa activa de la interrupción |
| FIFO Control Register | `FCR` | Write-only | Habilita/deshabilita colas FIFO, limpia buffers (TXFRST/RXFRST) y selecciona trigger levels |
| Line Control Register | `LCR` | Read/Write | Configura longitud de palabra (WLS), bits de parada, tipo de paridad y bit de acceso DLAB |
| Modem Control Register | `MCR` | Read/Write | Control de líneas RTS, DTR, modo bucle local (Loopback) y habilitación de autoflujo (AFE) |
| Line Status Register | `LSR` | Read-only | Flags de estado: Data Ready (DR), Overrun Error (OE), Parity Error (PE), Framing Error (FE), Break Interrupt (BI), THRE y TEMT |
| Modem Status Register | `MSR` | Read-only | Estado de las líneas externas CTS, DSR, RI y CD |
| Divisor Latch LSB / MSB | `DLL` / `DLH` | Read/Write | Registros de 8 bits para configurar el divisor de velocidad de baudios (accesibles cuando DLAB = 1 en LCR) |
| Power and Emulation Mgmt | `PWREMU_MGMT` | Read/Write | Control de suspensión por ahorro de energía y modo Free-run para depuración |

# Manejo de Errores de Recepción

- **Overrun Error (OE):** Ocurre cuando se recibe un nuevo carácter pero la FIFO de recepción o el registro RBR ya estaban llenos, provocando la pérdida de datos.
- **Parity Error (PE):** El bit de paridad recibido no coincide con el algoritmo par/impar configurado.
- **Framing Error (FE):** El receptor no detectó el bit de parada en nivel alto esperado al finalizar el intervalo de tiempo del carácter.
- **Break Interrupt (BI):** La línea de recepción RXD permaneció en nivel bajo continuo durante un tiempo superior a la longitud total de una trama completa.

# Aplicaciones

- Consola serie interactiva de depuración y logging en microcontroladores y SoCs.
- Comunicación con módems celulares (comandos AT con control de flujo por hardware RTS/CTS).
- Conexión a transceptores RS-485 para redes industriales en distancias de hasta 1200 metros.
- Enlace punto a punto con módulos GPS/GNSS y sensores analítico-químicos.

# Limitaciones y Advertencias

- **Tolerancia de reloj en comunicación asíncrona:** Al no compartir una línea de reloj explícita, la desviación de frecuencia entre el transmisor y el receptor no debe exceder el **2.5% a 3%**; desviaciones mayores causan errores sistemáticos de framing hacia los últimos bits de la trama.
- **Bit DLAB en registro LCR:** Para programar los divisores de baudios `DLL` y `DLH`, es obligatorio fijar primero el bit `DLAB` en 1 en el registro `LCR`, y volver a ponerlo en 0 al finalizar para restaurar el acceso a los registros normales de datos `RBR` y `THR`.
"""

SPRUGP1_JSON = {
  "file_name": "sprugp1.pdf",
  "processed_file": "data/processed/protocolos/sprugp1.md",
  "source_path": "data/raw/Microcontroladores_RAG_Documentacion/Protocolos/sprugp1.pdf",
  "category": "Protocolos",
  "type": "User Guide / Architecture Manual",
  "component": "KeyStone Architecture UART Peripheral (SPRUGP1)",
  "manufacturer": "Texas Instruments",
  "family": "Embedded Peripherals / UART",
  "interfaces": [
    "UART",
    "RS-232",
    "RS-485"
  ],
  "voltage": {
    "interface_levels": "Niveles lógicos TTL/CMOS del SoC (1.8V / 3.3V) conectables a transceptores externos"
  },
  "temperature_range": {
    "min": "unknown",
    "max": "unknown"
  },
  "topics": [
    "Controlador UART compatible 16550 con colas FIFO de 16 bytes para TX y RX",
    "Generador de baudios fraccional con divisor de 16 bits (DLL/DLH) y sobremuestreo de 16x",
    "Formato de trama: 5 a 8 bits de datos, 1/1.5/2 stop bits y paridad configurable",
    "Control de flujo por hardware automático Auto-RTS y Auto-CTS con umbrales de trigger",
    "Mapa exhaustivo de registros: RBR, THR, IER, IIR, FCR, LCR, MCR, LSR, MSR, DLL, DLH",
    "Detección y flags de errores: Overrun (OE), Parity (PE), Framing (FE) y Break (BI)",
    "Restricción de desviación máxima de reloj (2.5% - 3%) y uso del bit DLAB"
  ],
  "critical_params": {
    "compatibility": "TL16C550 / 16550",
    "fifo_depth_bytes": 16,
    "oversampling_factor": 16,
    "divisor_bits": 16,
    "max_clock_drift_percent": 2.5
  },
  "keywords": [
    "UART",
    "Texas Instruments",
    "SPRUGP1",
    "16550",
    "Baud Rate",
    "DLL",
    "DLH",
    "DLAB",
    "Auto-RTS",
    "Auto-CTS",
    "FIFO",
    "Framing Error",
    "Overrun"
  ],
  "issues_found": [
    "Manual de arquitectura de periférico UART de Texas Instruments de 51 páginas; procesado y catalogado para indexación técnica."
  ]
}

def write_protocolos_docs():
    p_proc = Path("data/processed/protocolos")
    p_meta = Path("data/metadata/protocolos")
    p_proc.mkdir(parents=True, exist_ok=True)
    p_meta.mkdir(parents=True, exist_ok=True)

    # 1. UM10204 (I2C)
    (p_proc / "UM10204.md").write_text(UM10204_MD, encoding="utf-8")
    with open(p_meta / "UM10204.json", "w", encoding="utf-8") as f:
        json.dump(UM10204_JSON, f, indent=2, ensure_ascii=False)
    print("Wrote UM10204.md and json")

    # 2. Modbus
    (p_proc / "modbusprotocolspecification.md").write_text(MODBUS_MD, encoding="utf-8")
    with open(p_meta / "modbusprotocolspecification.json", "w", encoding="utf-8") as f:
        json.dump(MODBUS_JSON, f, indent=2, ensure_ascii=False)
    print("Wrote modbusprotocolspecification.md and json")

    # 3. SPI (SBOA621)
    (p_proc / "sboa621.md").write_text(SBOA621_MD, encoding="utf-8")
    with open(p_meta / "sboa621.json", "w", encoding="utf-8") as f:
        json.dump(SBOA621_JSON, f, indent=2, ensure_ascii=False)
    print("Wrote sboa621.md and json")

    # 4. UART (SPRUGP1)
    (p_proc / "sprugp1.md").write_text(SPRUGP1_MD, encoding="utf-8")
    with open(p_meta / "sprugp1.json", "w", encoding="utf-8") as f:
        json.dump(SPRUGP1_JSON, f, indent=2, ensure_ascii=False)
    print("Wrote sprugp1.md and json")

if __name__ == "__main__":
    write_protocolos_docs()
