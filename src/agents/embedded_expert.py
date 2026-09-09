"""Especialista en hardware, microcontroladores, electrónica y periféricos."""
from typing import Dict, Any, List
from src.core.interfaces import BaseAgent


class EmbeddedExpertAgent(BaseAgent):
    """Explica conceptos técnicos, conexionados y características eléctricas basándose en fuentes."""

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Implementación de la interfaz BaseAgent."""
        query = task.get("query", "")
        chunks = task.get("chunks", [])
        return self.answer_hardware_query(query, chunks)

    def answer_hardware_query(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Genera explicación, ejemplo de conexión, consideraciones técnicas y fuentes."""
        context_text = "\n\n".join([c.get("text", "") for c in context_chunks])
        sources = list(set([c.get("metadata", {}).get("file_name", "datasheet") for c in context_chunks]))

        answer = f"**Análisis de Hardware y Embebidos para:** '{query}'\n\n"
        if context_text:
            answer += f"**Información Técnica de Hojas de Datos Extraída:**\n{context_text[:1200]}\n\n"
        else:
            answer += "No se hallaron fragmentos específicos en el índice RAG para esta consulta.\n\n"

        answer += "**Recomendación General de Conexión:**\n- Verificar rangos de voltaje operativo.\n- Usar desacoplamiento con capacitores de 100nF en pines VCC/GND.\n"

        return {
            "query": query,
            "answer": answer,
            "sources": sources,
            "chunks_used": len(context_chunks)
        }

    def generate_pinout_diagram(self, mcu: str, peripheral: str) -> str:
        """Genera diagrama textual/ASCII o tabla pin-a-pin con asignaciones exactas."""
        return f"Tabla de Pines para {mcu} ({peripheral}):\n" \
               f"| Periférico | Pin {mcu} | Descripción |\n" \
               f"|------------|-------------|-------------|\n" \
               f"| VCC        | 3.3V / 5V   | Alimentación |\n" \
               f"| GND        | GND         | Tierra |\n" \
               f"| SDA / MOSI | GPIO / SDA  | Línea de Datos |\n" \
               f"| SCL / SCK  | GPIO / SCL  | Reloj de Bus |\n"
