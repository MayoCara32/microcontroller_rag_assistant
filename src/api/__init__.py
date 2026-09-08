"""Módulo de interfaces y comunicación externa."""
from .schemas import QueryRequest, QueryResponse, HardwareVerificationResponse
from .cli import run_cli

__all__ = [
    "QueryRequest",
    "QueryResponse",
    "HardwareVerificationResponse",
    "run_cli"
]
