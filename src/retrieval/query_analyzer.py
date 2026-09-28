"""Módulo de análisis de intención y extracción de entidades técnicas para consultas RAG."""
import re
from typing import Dict, Any, Optional


class QueryAnalyzer:
    """Analiza consultas técnicas en lenguaje natural y extrae entidades para recuperación restringida.

    Responsabilidad:
    - Analizar la intención técnica de la consulta.
    - Extraer entidades clave (familia de hardware, placa, componentes, interfaces, fabricante, dominio).
    - Proponer candidatos de filtros sin interactuar con ChromaDB ni generar embeddings.
    """

    # Reglas para identificar familia y placas de hardware
    HARDWARE_PATTERNS = [
        # Arduino / AVR
        (r'\barduino\s+uno\b|\batmega328p?\b', {"hardware_family": "Arduino", "board": "UNO"}),
        (r'\barduino\s+mega\b|\batmega2560\b|\batmega1280\b', {"hardware_family": "Arduino", "board": "Mega"}),
        (r'\barduino\b', {"hardware_family": "Arduino"}),
        (r'\bavr\b|\bmegaavr\b', {"hardware_family": "Arduino"}),

        # ESP32 / Espressif
        (r'\besp32-?pico\b', {"hardware_family": "ESP32", "board": "PICO"}),
        (r'\besp32\b|\bxtensa\b|\bespressif\b', {"hardware_family": "ESP32"}),

        # Raspberry Pi / RP2040
        (r'\braspberry\s+pi\s+pico\b|\braspberry\s+pico\b|\bpico\b', {"hardware_family": "Raspberry Pi", "board": "Pico"}),
        (r'\brp2040\b|\braspberry\s+pi\b', {"hardware_family": "Raspberry Pi"}),

        # Texas Instruments / Controladores
        (r'\btl5001a?(?:-q1)?\b', {"hardware_family": "Texas Instruments", "component": "TL5001A-Q1"}),
    ]

    # Reglas para periféricos e interfaces técnicas
    INTERFACE_PATTERNS = [
        (r'\buart\b|\busart\b', "UART"),
        (r'\bspi\b', "SPI"),
        (r'\bi2c\b|\btwi\b', "I2C"),
        (r'\bcan(?:\s+bus)?\b|\biso\s*11898\b', "CAN"),
        (r'\bmodbus\b', "MODBUS"),
        (r'\badc\b|\banal[oó]gic[oa]\b|\bsar\b', "ADC"),
        (r'\bdac\b', "DAC"),
        (r'\bpwm\b', "PWM"),
        (r'\bgpio\b|\bpines\s+digitales\b', "GPIO"),
        (r'\btimer[s]?\b|\btemporizador(?:es)?\b|\bprescaler\b', "Timers"),
    ]

    # Reglas para dominios técnicos
    DOMAIN_PATTERNS = [
        (r'\bcomunicaci[oó]n\b|\bprotocolo[s]?\b|\btransmisi[oó]n\b', "Communication"),
        (r'\balimentaci[oó]n\b|\bvoltaje\b|\bpower\b|\bvsys\b|\bvin\b|\bconsumo\b', "Power"),
        (r'\bmemoria\b|\bflash\b|\bsram\b|\beeprom\b', "Memory"),
        (r'\bcripto|\bseguridad\b|\baes\b|\baccelerador\b', "Security"),
    ]

    def analyze(self, query: str) -> Dict[str, Any]:
        """Extrae entidades estructuradas a partir del texto de consulta.

        Devuelve un diccionario con las entidades detectadas o {} si la consulta
        no contiene referencias técnicas identificables.
        """
        if not query or not query.strip():
            return {}

        text = query.strip()
        entities: Dict[str, Any] = {}

        # 1. Extracción de hardware y fabricante
        for pattern, hw_data in self.HARDWARE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                for k, v in hw_data.items():
                    if k not in entities:
                        entities[k] = v
                break

        # 2. Extracción de periféricos / componentes
        for pattern, iface in self.INTERFACE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                # Si no se ha asignado un componente específico, asignar el periférico
                if "component" not in entities:
                    entities["component"] = iface
                break

        # 3. Extracción de dominio funcional
        for pattern, domain in self.DOMAIN_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                entities["domain"] = domain
                break

        # 4. Inferencia de dominio para protocolos independientes si no hay hardware asignado
        if "hardware_family" not in entities:
            if entities.get("component") in ["CAN", "MODBUS", "I2C", "SPI"]:
                entities["domain"] = "Communication"
            elif entities.get("component") in ["ADC", "DAC", "Timers"]:
                entities["domain"] = "Electronics"

        return entities
