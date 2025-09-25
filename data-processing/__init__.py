"""
EIA Atlas Power Plants Data Layer

This module provides a comprehensive data layer for accessing and processing
US power plants data from the EIA Atlas API.
"""

from .models import (
    PowerPlant,
    PowerPlantLocation,
    PowerPlantCapacity,
    PowerPlantQueryParams,
    EIAAtlasResponse,
    EnergyType,
    SectorType
)

from .eia_atlas_client import EIAAtlasClient

from .filters import (
    PowerPlantFilter,
    DataAggregator
)

__version__ = "1.0.0"

__all__ = [
    # Models
    'PowerPlant',
    'PowerPlantLocation', 
    'PowerPlantCapacity',
    'PowerPlantQueryParams',
    'EIAAtlasResponse',
    'EnergyType',
    'SectorType',
    
    # Client
    'EIAAtlasClient',
    
    # Filters and utilities
    'PowerPlantFilter',
    'DataAggregator'
]