"""EuroMCM 2026 Problem Alpha research package."""

from .allocation import (
    AllocationResult,
    allocate_resources,
    allocate_resources_priority,
)
from .historical import HistoricalParameters, HistoricalSimulation, simulate_historical
from .rsi import RSIParameters, RSISimulation, simulate_rsi
from .viability import ViabilityCertificate, viability_certificate

__all__ = [
    "AllocationResult",
    "allocate_resources",
    "allocate_resources_priority",
    "HistoricalParameters",
    "HistoricalSimulation",
    "simulate_historical",
    "RSIParameters",
    "RSISimulation",
    "simulate_rsi",
    "ViabilityCertificate",
    "viability_certificate",
]
