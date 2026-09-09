"""Comprobaciones deterministas de límites eléctricos y riesgos físicos de hardware."""
import re
from typing import Dict, Any, List


class ElectricalSafetyGuardrails:
    """Detecta inconsistencias peligrosas (p. ej. inyectar 5V en GPIOs de 3.3V no tolerantes)."""

    def check_voltage_compatibility(self, mcu_pin_voltage: float, peripheral_voltage: float) -> bool:
        """Verifica compatibilidad lógica y advierte si se requiere cambiador de nivel (level shifter)."""
        return not (mcu_pin_voltage <= 3.3 and peripheral_voltage >= 4.5)

    def audit_hardware_plan(self, text_or_plan: str) -> List[str]:
        """Devuelve una lista de advertencias de seguridad física sobre el plan o texto generado."""
        warnings = []
        text = str(text_or_plan)

        # Regla 1: Inyección de 5V en ESP32 / Raspberry Pi Pico
        if re.search(r'\b(esp32|rp2040|pico)\b', text, re.IGNORECASE) and re.search(r'\b5v\b', text, re.IGNORECASE):
            if re.search(r'\b(gpio|pin|Entrada)\b', text, re.IGNORECASE) and not re.search(r'\b(level shifter|divisor|optocoplador|3\.3v)\b', text, re.IGNORECASE):
                warnings.append("ADVERTENCIA DE VOLTAJE: Los GPIO de ESP32 y RP2040 operan a 3.3V y NO son tolerantes a 5V. Inyectar 5V directamente puede destruir el microcontrolador. Se recomienda un Level Shifter bidireccional o un divisor de tensión.")

        # Regla 2: Corriente máxima de pines Arduino AVR
        if re.search(r'\barduino\b|\batmega328p\b', text, re.IGNORECASE) and re.search(r'\b(led|relé|rele|motor)\b', text, re.IGNORECASE):
            if not re.search(r'\b(resistencia|transistor|mosfet|driver|uln2003)\b', text, re.IGNORECASE):
                warnings.append("ADVERTENCIA DE CORRIENTE: La corriente máxima sostenida por pin I/O en procesadores AVR (ATmega328P/2560) es de 40mA. Para cargas inductivas (motores, relés) o LEDs de alta potencia, utilice un transistor, MOSFET o módulo driver dedicado.")

        # Regla 3: Pull-ups I2C
        if re.search(r'\bi2c\b', text, re.IGNORECASE) and not re.search(r'\b(pull-up|pullup|resistencia de elevación)\b', text, re.IGNORECASE):
            warnings.append("ADVERTENCIA DE BUS DE COMUNICACIÓN: El bus I2C requiere resistencias de pull-up (típicamente 4.7kΩ a 3.3V/5V) en las líneas SDA y SCL para operar correctamente.")

        return warnings
