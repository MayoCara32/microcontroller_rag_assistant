"""Constructor y validador de filtros de metadatos compatibles con ChromaDB."""
from typing import Dict, Any, Optional, List


class MetadataFilterBuilder:
    """Convierte entidades técnicas extraídas de consultas en filtros nativos `where` de ChromaDB.

    Responsabilidad:
    - Mapear nombres de entidades lógicas (hardware_family, domain, board) a campos reales de ChromaDB.
    - Validar que los campos y valores existan en el corpus indexado.
    - Prevenir filtros contradictorios o imposibles que destruirían el Recall.
    - Estructurar operadores lógicos ($and) exigidos por ChromaDB.
    """

    # Esquema estricto de campos reales almacenados en ChromaDB
    VALID_CHROMA_FIELDS = {
        "category",
        "component",
        "family",
        "manufacturer",
        "file_name",
        "interfaces",
        "document_type",
        "sku"
    }

    # Valores canónicos reales en la colección ChromaDB (286 chunks)
    VALID_CATEGORIES = {
        "Arduino",
        "ESP32",
        "Raspberry_Pi",
        "Protocolos",
        "Electronica",
        "General Embebidos"
    }

    VALID_MANUFACTURERS = {
        "Arduino S.r.l",
        "Arduino S.r.l.",
        "Espressif Systems",
        "Atmel / Microchip",
        "Texas Instruments",
        "Raspberry Pi Ltd",
        "NXP Semiconductors",
        "Modbus Organization (Modbus-IDA)"
    }

    # Mapeo de familias de hardware a categorías reales en ChromaDB
    HARDWARE_TO_CATEGORY = {
        "Arduino": "Arduino",
        "AVR": "Arduino",
        "ESP32": "ESP32",
        "Raspberry Pi": "Raspberry_Pi",
        "Raspberry": "Raspberry_Pi",
        "RP2040": "Raspberry_Pi",
        "Texas Instruments": "Electronica",
    }

    # Protocolos independientes asignados a categoría 'Protocolos'
    STANDALONE_PROTOCOLS = {"CAN", "MODBUS", "I2C", "SPI"}

    # Componentes de electrónica analógica / drivers
    ELECTRONICS_COMPONENTS = {"ADC", "DAC", "TIMERS", "TL5001A-Q1"}

    @classmethod
    def build_from_analysis(cls, analysis_data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Construye un filtro ChromaDB a partir de la salida de QueryAnalyzer."""
        if not analysis_data or not isinstance(analysis_data, dict):
            return None

        conditions: List[Dict[str, Any]] = []

        hw_family = analysis_data.get("hardware_family")
        comp = analysis_data.get("component")
        domain = analysis_data.get("domain")

        # 1. Mapeo de Categoría Principal
        target_category: Optional[str] = None
        if hw_family in cls.HARDWARE_TO_CATEGORY:
            target_category = cls.HARDWARE_TO_CATEGORY[hw_family]
        elif domain == "Communication" or (comp and comp.upper() in cls.STANDALONE_PROTOCOLS):
            target_category = "Protocolos"
        elif domain in ["Electronics", "Power"] or (comp and comp.upper() in cls.ELECTRONICS_COMPONENTS and not hw_family):
            target_category = "Electronica"

        if target_category and target_category in cls.VALID_CATEGORIES:
            conditions.append({"category": target_category})

        # 2. Filtrado específico por fabricante si está explícito
        manufacturer = analysis_data.get("manufacturer")
        if manufacturer and manufacturer in cls.VALID_MANUFACTURERS:
            conditions.append({"manufacturer": manufacturer})

        # 3. Componentes específicos conocidos en ChromaDB (solo cuando delimitan exactamente un documento sin riesgo de falso negativo)
        if comp == "TL5001A-Q1":
            conditions.append({"component": "TL5001A-Q1"})

        # Ensamblar según formato exigido por ChromaDB
        if not conditions:
            return None
        if len(conditions) == 1:
            return conditions[0]
        return {"$and": conditions}

    @classmethod
    def build_filter(
        cls,
        microcontroller: Optional[str] = None,
        family: Optional[str] = None,
        interface: Optional[str] = None,
        document_type: Optional[str] = None,
        category: Optional[str] = None,
        component: Optional[str] = None,
        manufacturer: Optional[str] = None,
        file_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Genera un filtro estructurado a partir de parámetros explícitos (retrocompatible)."""
        conditions: List[Dict[str, Any]] = []

        # Normalizar y validar categoría
        raw_cat = category or microcontroller or family
        if raw_cat:
            cat_resolved = cls.HARDWARE_TO_CATEGORY.get(raw_cat, raw_cat)
            if cat_resolved in cls.VALID_CATEGORIES:
                conditions.append({"category": cat_resolved})

        if component:
            conditions.append({"component": component})

        if manufacturer and manufacturer in cls.VALID_MANUFACTURERS:
            conditions.append({"manufacturer": manufacturer})

        if file_name:
            conditions.append({"file_name": file_name})

        if document_type:
            conditions.append({"document_type": document_type})

        if not conditions:
            return None
        if len(conditions) == 1:
            return conditions[0]
        return {"$and": conditions}
