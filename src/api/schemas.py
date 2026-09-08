"""Esquemas de datos Pydantic para peticiones y respuestas."""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Petición de usuario al Asistente RAG."""
    query: str = Field(..., description="Pregunta técnica o requerimiento de conexión/código")
    target_mcu: Optional[str] = Field(None, description="Ej. ESP32, Arduino UNO, RP2040")
    framework: Optional[str] = Field(None, description="Ej. Arduino C++, ESP-IDF, MicroPython")


class SourceCitation(BaseModel):
    """Detalle de atribución de fuente verificada."""
    document: str
    section: Optional[str] = None
    page: Optional[int] = None
    excerpt: str
    confidence_score: float


class QueryResponse(BaseModel):
    """Estructura de respuesta final del sistema."""
    answer: str
    explanation: str
    sources: List[SourceCitation]
    hardware_considerations: List[str]
    pinout_mapping: Optional[Dict[str, str]] = None


class HardwareVerificationResponse(BaseModel):
    """Respuesta del validador de límites eléctricos."""
    is_safe: bool
    warnings: List[str]
    max_ratings_checked: Dict[str, Any]
