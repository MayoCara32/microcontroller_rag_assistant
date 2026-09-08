"""Configuración de logging estructurado para el sistema."""
import logging
import sys


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Configura el logger base del proyecto."""
    logger = logging.getLogger("MicrocontrollersRAG")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    return logger
