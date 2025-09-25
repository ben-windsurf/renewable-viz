"""
EIA Atlas API Client for Power Plants Data
"""
import requests
import pandas as pd
import geopandas as gpd
from typing import List, Optional, Dict, Any, Union
from shapely.geometry import Point
import logging
from urllib.parse import urljoin

from models import (
    PowerPlant, PowerPlantLocation, PowerPlantCapacity, 
    PowerPlantQueryParams, EIAAtlasResponse, EnergyType, SectorType
)


logger = logging.getLogger(__name__)


class EIAAtlasClient:
    """Client for accessing EIA Atlas Power Plants data via ArcGIS REST API"""
    
    BASE_URL = "https://services7.arcgis.com/FGr1D95XCGALKXqM/ArcGIS/rest/services"
    
    # Available power plant services
    SERVICES = {
        'all_plants': 'ElectricPowerPlants/FeatureServer/0',
        'coal_plants': 'Coal_Power_Plants/FeatureServer/0',
        'natural_gas_plants': 'Natural_Gas_Power_Plants/FeatureServer/0',
        'nuclear_plants': 'Nuclear_Power_Plants/FeatureServer/0',
        'hydro_plants': 'Hydroelectric_Power_Plants/FeatureServer/0',
        'hydro_pumped_plants': 'Hydro_Pumped_Storage_Power_Plants/FeatureServer/0',
        'solar_plants': 'Solar_Power_Plants/FeatureServer/0',
        'wind_plants': 'Wind_Power_Plants/FeatureServer/0',
        'geothermal_plants': 'Geothermal_Power_Plants/FeatureServer/0',
        'battery_plants': 'Battery_Storage_Plants/FeatureServer/0',
        'petroleum_plants': 'Petroleum_Power_Plants/FeatureServer/0',
        'other_plants': 'Other_Power_Plants/FeatureServer/0'
    }
    
    def __init__(self, timeout: int = 30):
        """
        Initialize the EIA Atlas client
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'EIA-Atlas-Python-Client/1.0'
        })
    
    def _build_url(self, service_path: str) -> str:
        """Build full URL for API endpoint"""
        return f"{self.BASE_URL}/{service_path}/query"
    
    def _make_request(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make HTTP request to API endpoint
        
        Args:
            url: API endpoint URL
            params: Query parameters
            
        Returns:
            JSON response data
            
        Raises:
            requests.RequestException: If request fails
        """
        try:
            logger.debug(f"Making request to {url} with params: {params}")
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API errors
            if 'error' in data:
                error_msg = data['error'].get('message', 'Unknown API error')
                raise requests.RequestException(f"API Error: {error_msg}")
                
            return data
            
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise
        except ValueError as e:
            logger.error(f"JSON decode error: {e}")
            raise requests.RequestException(f"Invalid JSON response: {e}")
    
    def _parse_feature_to_power_plant(self, feature: Dict[str, Any]) -> PowerPlant:
        """
        Parse a feature from API response to PowerPlant object
        
        Args:
            feature: Feature dictionary from API response
            
        Returns:
            PowerPlant object
        """
        attrs = feature.get('attributes', {})
        geom = feature.get('geometry', {})
        
        # Parse location
        location = PowerPlantLocation(
            latitude=geom.get('y', attrs.get('Latitude', 0.0)),
            longitude=geom.get('x', attrs.get('Longitude', 0.0)),
            city=attrs.get('City', ''),
            county=attrs.get('County', ''),
            state=attrs.get('StateName', ''),
            zip_code=attrs.get('Zip'),
            street_address=attrs.get('Street_Address')
        )
        
        # Parse capacity information
        capacity = PowerPlantCapacity(
            total_mw=attrs.get('Total_MW'),
            install_mw=attrs.get('Install_MW'),
            coal_mw=attrs.get('Coal_MW'),
            natural_gas_mw=attrs.get('NG_MW'),
            nuclear_mw=attrs.get('Nuclear_MW'),
            hydro_mw=attrs.get('Hydro_MW'),
            hydro_pumped_mw=attrs.get('HydroPS_MW'),
            solar_mw=attrs.get('Solar_MW'),
            wind_mw=attrs.get('Wind_MW'),
            geothermal_mw=attrs.get('Geo_MW'),
            biomass_mw=attrs.get('Bio_MW'),
            battery_mw=attrs.get('Bat_MW'),
            crude_oil_mw=attrs.get('Crude_MW'),
            other_mw=attrs.get('Other_MW')
        )
        
        return PowerPlant(
            object_id=attrs.get('OBJECTID', 0),
            plant_code=attrs.get('Plant_Code', 0),
            plant_name=attrs.get('Plant_Name', ''),
            utility_name=attrs.get('Utility_Name', ''),
            utility_id=attrs.get('Utility_ID', 0),
            sector_name=attrs.get('Sector_Name', ''),
            primary_source=attrs.get('PrimSource', ''),
            location=location,
            capacity=capacity,
            tech_desc=attrs.get('tech_desc'),
            source_desc=attrs.get('Source_Desc'),
            data_period=attrs.get('Period'),
            source=attrs.get('Source')
        )
    
    def get_power_plants(
        self,
        service: str = 'all_plants',
        query_params: Optional[PowerPlantQueryParams] = None,
        limit: Optional[int] = None
    ) -> List[PowerPlant]:
        """
        Fetch power plants data from specified service
        
        Args:
            service: Service name from SERVICES dict
            query_params: Query parameters for filtering
            limit: Maximum number of records to return
            
        Returns:
            List of PowerPlant objects
        """
        if service not in self.SERVICES:
            raise ValueError(f"Unknown service: {service}. Available: {list(self.SERVICES.keys())}")
        
        if query_params is None:
            query_params = PowerPlantQueryParams()
        
        if limit:
            query_params.result_record_count = limit
        
        url = self._build_url(self.SERVICES[service])
        params = query_params.to_dict()
        
        all_plants = []
        offset = 0
        batch_size = query_params.result_record_count or 1000
        
        while True:
            # Set offset for pagination
            current_params = params.copy()
            current_params['resultOffset'] = offset
            if 'resultRecordCount' not in current_params:
                current_params['resultRecordCount'] = batch_size
            
            data = self._make_request(url, current_params)
            response = EIAAtlasResponse.from_dict(data)
            
            if not response.features:
                break
            
            # Parse features to PowerPlant objects
            batch_plants = [
                self._parse_feature_to_power_plant(feature) 
                for feature in response.features
            ]
            all_plants.extend(batch_plants)
            
            # Check if we've reached the limit or if there are no more records
            if limit and len(all_plants) >= limit:
                all_plants = all_plants[:limit]
                break
            
            if len(response.features) < batch_size or response.exceeded_transfer_limit:
                break
            
            offset += len(response.features)
            logger.info(f"Fetched {len(all_plants)} plants so far...")
        
        logger.info(f"Total plants fetched: {len(all_plants)}")
        return all_plants
    
    def get_plants_by_energy_type(
        self,
        energy_type: EnergyType,
        limit: Optional[int] = None
    ) -> List[PowerPlant]:
        """
        Get power plants filtered by energy type
        
        Args:
            energy_type: Type of energy to filter by
            limit: Maximum number of records to return
            
        Returns:
            List of PowerPlant objects
        """
        # Map energy types to services where possible
        service_mapping = {
            EnergyType.COAL: 'coal_plants',
            EnergyType.NATURAL_GAS: 'natural_gas_plants',
            EnergyType.NUCLEAR: 'nuclear_plants',
            EnergyType.HYDRO: 'hydro_plants',
            EnergyType.SOLAR: 'solar_plants',
            EnergyType.WIND: 'wind_plants',
            EnergyType.GEOTHERMAL: 'geothermal_plants',
            EnergyType.BATTERY: 'battery_plants',
            EnergyType.CRUDE_OIL: 'petroleum_plants',
            EnergyType.OTHER: 'other_plants'
        }
        
        if energy_type in service_mapping:
            return self.get_power_plants(service_mapping[energy_type], limit=limit)
        else:
            # For types without dedicated services, filter from all plants
            all_plants = self.get_power_plants('all_plants', limit=limit)
            return [plant for plant in all_plants if plant.primary_energy_type == energy_type]
    
    def get_plants_by_state(
        self,
        state: str,
        energy_type: Optional[EnergyType] = None,
        limit: Optional[int] = None
    ) -> List[PowerPlant]:
        """
        Get power plants filtered by state
        
        Args:
            state: State name or abbreviation
            energy_type: Optional energy type filter
            limit: Maximum number of records to return
            
        Returns:
            List of PowerPlant objects
        """
        where_clause = f"StateName = '{state}' OR StateName LIKE '%{state}%'"
        query_params = PowerPlantQueryParams(where_clause=where_clause)
        
        service = 'all_plants'
        if energy_type:
            service_mapping = {
                EnergyType.COAL: 'coal_plants',
                EnergyType.NATURAL_GAS: 'natural_gas_plants',
                EnergyType.NUCLEAR: 'nuclear_plants',
                EnergyType.HYDRO: 'hydro_plants',
                EnergyType.SOLAR: 'solar_plants',
                EnergyType.WIND: 'wind_plants',
                EnergyType.GEOTHERMAL: 'geothermal_plants',
                EnergyType.BATTERY: 'battery_plants',
                EnergyType.CRUDE_OIL: 'petroleum_plants',
                EnergyType.OTHER: 'other_plants'
            }
            service = service_mapping.get(energy_type, 'all_plants')
        
        return self.get_power_plants(service, query_params, limit)
    
    def get_renewable_plants(self, limit: Optional[int] = None) -> List[PowerPlant]:
        """
        Get all renewable energy power plants
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of PowerPlant objects for renewable plants
        """
        renewable_types = [
            EnergyType.SOLAR,
            EnergyType.WIND,
            EnergyType.HYDRO,
            EnergyType.GEOTHERMAL,
            EnergyType.BIOMASS
        ]
        
        all_renewable = []
        for energy_type in renewable_types:
            plants = self.get_plants_by_energy_type(energy_type)
            all_renewable.extend(plants)
            
            if limit and len(all_renewable) >= limit:
                break
        
        if limit:
            all_renewable = all_renewable[:limit]
        
        return all_renewable
    
    def to_dataframe(self, plants: List[PowerPlant]) -> pd.DataFrame:
        """
        Convert list of PowerPlant objects to pandas DataFrame
        
        Args:
            plants: List of PowerPlant objects
            
        Returns:
            pandas DataFrame with flattened plant data
        """
        if not plants:
            return pd.DataFrame()
        
        records = []
        for plant in plants:
            record = {
                'object_id': plant.object_id,
                'plant_code': plant.plant_code,
                'plant_name': plant.plant_name,
                'utility_name': plant.utility_name,
                'utility_id': plant.utility_id,
                'sector_name': plant.sector_name,
                'primary_source': plant.primary_source,
                'primary_energy_type': plant.primary_energy_type.value,
                'is_renewable': plant.is_renewable,
                
                # Location fields
                'latitude': plant.location.latitude,
                'longitude': plant.location.longitude,
                'city': plant.location.city,
                'county': plant.location.county,
                'state': plant.location.state,
                'zip_code': plant.location.zip_code,
                'street_address': plant.location.street_address,
                
                # Capacity fields
                'total_mw': plant.capacity.total_mw,
                'install_mw': plant.capacity.install_mw,
                'coal_mw': plant.capacity.coal_mw,
                'natural_gas_mw': plant.capacity.natural_gas_mw,
                'nuclear_mw': plant.capacity.nuclear_mw,
                'hydro_mw': plant.capacity.hydro_mw,
                'hydro_pumped_mw': plant.capacity.hydro_pumped_mw,
                'solar_mw': plant.capacity.solar_mw,
                'wind_mw': plant.capacity.wind_mw,
                'geothermal_mw': plant.capacity.geothermal_mw,
                'biomass_mw': plant.capacity.biomass_mw,
                'battery_mw': plant.capacity.battery_mw,
                'crude_oil_mw': plant.capacity.crude_oil_mw,
                'other_mw': plant.capacity.other_mw,
                'renewable_capacity_mw': plant.capacity.get_renewable_capacity(),
                
                # Additional fields
                'tech_desc': plant.tech_desc,
                'source_desc': plant.source_desc,
                'data_period': plant.data_period,
                'source': plant.source
            }
            records.append(record)
        
        return pd.DataFrame(records)
    
    def to_geodataframe(self, plants: List[PowerPlant]) -> gpd.GeoDataFrame:
        """
        Convert list of PowerPlant objects to GeoPandas GeoDataFrame
        
        Args:
            plants: List of PowerPlant objects
            
        Returns:
            GeoPandas GeoDataFrame with geometry column
        """
        df = self.to_dataframe(plants)
        if df.empty:
            return gpd.GeoDataFrame()
        
        # Create geometry points
        geometry = [
            Point(row['longitude'], row['latitude']) 
            for _, row in df.iterrows()
        ]
        
        # Remove lat/lon columns since they're now in geometry
        df = df.drop(['latitude', 'longitude'], axis=1)
        
        return gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
