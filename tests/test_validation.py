"""Pruebas unitarias para los validadores de citas y reglas de seguridad eléctrica."""
from src.validation.safety_guardrails import ElectricalSafetyGuardrails
from src.validation.citation_validator import CitationSourceValidator


def test_electrical_safety_voltage_warning():
    guardrails = ElectricalSafetyGuardrails()
    warnings = guardrails.audit_hardware_plan("Conectar sensor con salida de 5V al GPIO de la placa ESP32 directamente en la entrada digital.")
    assert len(warnings) > 0
    assert "ADVERTENCIA DE VOLTAJE" in warnings[0]


def test_electrical_safety_safe():
    guardrails = ElectricalSafetyGuardrails()
    is_safe = guardrails.check_voltage_compatibility(3.3, 3.3)
    assert is_safe is True


def test_citation_source_validator():
    validator = CitationSourceValidator()
    chunks = [{"text": "Sample text", "metadata": {"file_name": "A000067-datasheet.pdf"}}]
    result = validator.validate_citations("Explicación de prueba", chunks)
    assert result["valid"] is True
    assert "A000067-datasheet.pdf" in result["validated_response"]
