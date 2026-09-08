"""Comprobaciones deterministas de límites eléctricos y riesgos físicos de hardware."""
from typing import Dict, Any, List


class ElectricalSafetyGuardrails:
    """Detecta inconsistencias peligrosas (p. ej. inyectar 5V en GPIOs de 3.3V no tolerantes)."""

    def __init__(self):
        pass

    def check_voltage_compatibility(self, mcu_pin_voltage: float, peripheral_voltage: float) -> bool:
        """Verifica compatibilidad lógica y advierte si se requiere cambiador de nivel (level shifter)."""
        raise NotImplementedError("Estructura inicial: función aún no implementada.")

    def audit_hardware_plan(self, generated_plan: Dict[str, Any]) -> List[str]:
        """Devuelve una lista de advertencias de seguridad física sobre el plan generado."""
        raise NotImplementedError("Estructura inicial: función aún no implementada.")
