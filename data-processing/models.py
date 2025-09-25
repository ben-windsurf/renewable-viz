"""
Data models for EIA Atlas Power Plants API
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from enum import Enum


class EnergyType(Enum):
    """Enumeration of energy types available in the power plants data"""
    COAL = "Coal"
    NATURAL_GAS = "Natural Gas"
    NUCLEAR = "Nuclear"
    HYDRO = "Hydroelectric"
    HYDRO_PUMPED = "Hydro Pumped Storage"
    SOLAR = "Solar"
    WIND = "Wind"
    GEOTHERMAL = "Geothermal"
    BIOMASS = "Biomass"
    BATTERY = "Battery Storage"
    OTHER = "Other"
    CRUDE_OIL = "Crude Oil"


class SectorType(Enum):
    """Enumeration of utility sector types"""
    ELECTRIC_UTILITY = "Electric Utility"
    IPP_NON_CHP = "IPP Non-CHP"
    IPP_CHP = "IPP CHP"
    COMBINED_HEAT_POWER = "Combined Heat and Power"


@dataclass
class PowerPlantLocation:
    """Geographic location information for a power plant"""
    latitude: float
    longitude: float
    city: str
    county: str
    state: str
    zip_code: Optional[int] = None
    street_address: Optional[str] = None


@dataclass
class PowerPlantCapacity:
    """Capacity information by energy type (in MW)"""
    total_mw: Optional[float] = None
    install_mw: Optional[float] = None
    coal_mw: Optional[float] = None
    natural_gas_mw: Optional[float] = None
    nuclear_mw: Optional[float] = None
    hydro_mw: Optional[float] = None
    hydro_pumped_mw: Optional[float] = None
    solar_mw: Optional[float] = None
    wind_mw: Optional[float] = None
    geothermal_mw: Optional[float] = None
    biomass_mw: Optional[float] = None
    battery_mw: Optional[float] = None
    crude_oil_mw: Optional[float] = None
    other_mw: Optional[float] = None

    def get_renewable_capacity(self) -> float:
        """Calculate total renewable energy capacity"""
        renewable_sources = [
            self.solar_mw or 0,
            self.wind_mw or 0,
            self.hydro_mw or 0,
            self.geothermal_mw or 0,
            self.biomass_mw or 0
        ]
        return sum(renewable_sources)

    def get_capacity_by_type(self, energy_type: EnergyType) -> Optional[float]:
        """Get capacity for a specific energy type"""
        mapping = {
            EnergyType.COAL: self.coal_mw,
            EnergyType.NATURAL_GAS: self.natural_gas_mw,
            EnergyType.NUCLEAR: self.nuclear_mw,
            EnergyType.HYDRO: self.hydro_mw,
            EnergyType.HYDRO_PUMPED: self.hydro_pumped_mw,
            EnergyType.SOLAR: self.solar_mw,
            EnergyType.WIND: self.wind_mw,
            EnergyType.GEOTHERMAL: self.geothermal_mw,
            EnergyType.BIOMASS: self.biomass_mw,
            EnergyType.BATTERY: self.battery_mw,
            EnergyType.CRUDE_OIL: self.crude_oil_mw,
            EnergyType.OTHER: self.other_mw
        }
        return mapping.get(energy_type)


@dataclass
class PowerPlant:
    """Complete power plant information"""
    object_id: int
    plant_code: int
    plant_name: str
    utility_name: str
    utility_id: int
    sector_name: str
    primary_source: str
    location: PowerPlantLocation
    capacity: PowerPlantCapacity
    tech_desc: Optional[str] = None
    source_desc: Optional[str] = None
    data_period: Optional[int] = None
    source: Optional[str] = None

    @property
    def primary_energy_type(self) -> EnergyType:
        """Determine the primary energy type based on primary_source"""
        source_mapping = {
            'coal': EnergyType.COAL,
            'natural gas': EnergyType.NATURAL_GAS,
            'nuclear': EnergyType.NUCLEAR,
            'hydro': EnergyType.HYDRO,
            'hydroelectric': EnergyType.HYDRO,
            'solar': EnergyType.SOLAR,
            'wind': EnergyType.WIND,
            'geothermal': EnergyType.GEOTHERMAL,
            'biomass': EnergyType.BIOMASS,
            'batteries': EnergyType.BATTERY,
            'battery': EnergyType.BATTERY,
            'crude oil': EnergyType.CRUDE_OIL,
            'petroleum': EnergyType.CRUDE_OIL,
        }
        
        source_lower = self.primary_source.lower()
        for key, energy_type in source_mapping.items():
            if key in source_lower:
                return energy_type
        
        return EnergyType.OTHER

    @property
    def is_renewable(self) -> bool:
        """Check if the plant is primarily renewable energy"""
        renewable_types = {
            EnergyType.SOLAR,
            EnergyType.WIND,
            EnergyType.HYDRO,
            EnergyType.GEOTHERMAL,
            EnergyType.BIOMASS
        }
        return self.primary_energy_type in renewable_types


@dataclass
class PowerPlantQueryParams:
    """Parameters for querying power plants data"""
    where_clause: str = "1=1"
    out_fields: str = "*"
    out_sr: int = 4326
    result_record_count: Optional[int] = None
    result_offset: Optional[int] = None
    order_by_fields: Optional[str] = None
    return_geometry: bool = True
    f: str = "json"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request"""
        params = {
            'where': self.where_clause,
            'outFields': self.out_fields,
            'outSR': self.out_sr,
            'returnGeometry': str(self.return_geometry).lower(),
            'f': self.f
        }
        
        if self.result_record_count is not None:
            params['resultRecordCount'] = self.result_record_count
        if self.result_offset is not None:
            params['resultOffset'] = self.result_offset
        if self.order_by_fields is not None:
            params['orderByFields'] = self.order_by_fields
            
        return params


@dataclass
class EIAAtlasResponse:
    """Response from EIA Atlas API"""
    object_id_field_name: str
    geometry_type: str
    spatial_reference: Dict[str, Any]
    fields: List[Dict[str, Any]]
    features: List[Dict[str, Any]]
    exceeded_transfer_limit: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EIAAtlasResponse':
        """Create instance from API response dictionary"""
        return cls(
            object_id_field_name=data.get('objectIdFieldName', ''),
            geometry_type=data.get('geometryType', ''),
            spatial_reference=data.get('spatialReference', {}),
            fields=data.get('fields', []),
            features=data.get('features', []),
            exceeded_transfer_limit=data.get('exceededTransferLimit', False)
        )
