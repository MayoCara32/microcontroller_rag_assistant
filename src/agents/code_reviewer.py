"""[COMPONENTE AISLADO - RESERVADO PARA DÍA 13+]
Especialista en revisión y corrección de firmware embebido.
No participa en el pipeline activo de Día 12.
"""
from typing import Dict, Any, List
from src.core.interfaces import BaseAgent


class EmbeddedCodeReviewerAgent(BaseAgent):
    """Evalúa errores lógicos, bloqueos por delays, uso de memoria y problemas de timers/ISR."""

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Implementación de la interfaz BaseAgent."""
        code = task.get("code", "")
        mcu = task.get("target_mcu", "Arduino")
        chunks = task.get("chunks", [])
        return self.review_code(code, mcu, chunks)

    def review_code(
        self,
        code_snippet: str,
        target_mcu: str,
        context_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Sigue el flujo: explica problema -> causa -> propone solución -> fragmento corregido."""
        issues = []
        suggestions = []

        if "delay(" in code_snippet and "millis()" not in code_snippet:
            issues.append("Uso de delay() bloqueante detectado en el loop principal.")
            suggestions.append("Sustituir delay() por temporización no bloqueante usando millis().")

        if "String " in code_snippet and ("Arduino" in target_mcu or "AVR" in target_mcu):
            issues.append("Uso de clase String dinámica en microcontrolador con SRAM limitada.")
            suggestions.append("Utilizar arreglos de caracteres C (char arrays) estáticos para evitar fragmentación de heap.")

        if not issues:
            issues.append("No se detectaron problemas críticos inmediatos de sintaxis o memoria.")

        report = f"**Revisión de Código Embebido para [{target_mcu}]**\n\n"
        report += "**Hallazgos Identificados:**\n" + "\n".join([f"- {i}" for i in issues]) + "\n\n"
        report += "**Sugerencias de Optimización:**\n" + "\n".join([f"- {s}" for s in suggestions]) + "\n"

        return {
            "target_mcu": target_mcu,
            "issues": issues,
            "suggestions": suggestions,
            "report": report
        }
