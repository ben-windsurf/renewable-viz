"""
Filtering utilities for power plants data
"""
import pandas as pd
import geopandas as gpd
from typing import List, Optional, Union, Dict, Any
from shapely.geometry import Polygon, Point
import logging

from models import PowerPlant, EnergyType, SectorType

logger = logging.getLogger(__name__)


class PowerPlantFilter:
    """Utility class for filtering power plants data"""
    
    @staticmethod
    def filter_by_capacity_range(
        plants: List[PowerPlant],
        min_capacity: Optional[float] = None,
        max_capacity: Optional[float] = None,
        capacity_type: str = 'total_mw'
    ) -> List[PowerPlant]:
        """
        Filter plants by capacity range
        
        Args:
            plants: List of PowerPlant objects
            min_capacity: Minimum capacity in MW
            max_capacity: Maximum capacity in MW
            capacity_type: Type of capacity to filter by
            
        Returns:
            Filtered list of PowerPlant objects
        """
        filtered = []
        
        for plant in plants:
            capacity_value = getattr(plant.capacity, capacity_type, None)
            
            if capacity_value is None:
                continue
                
            if min_capacity is not None and capacity_value < min_capacity:
                continue
                
            if max_capacity is not None and capacity_value > max_capacity:
                continue
                
            filtered.append(plant)
        
        return filtered
    
    @staticmethod
    def filter_by_energy_types(
        plants: List[PowerPlant],
        energy_types: List[EnergyType]
    ) -> List[PowerPlant]:
        """
        Filter plants by multiple energy types
        
        Args:
            plants: List of PowerPlant objects
            energy_types: List of energy types to include
            
        Returns:
            Filtered list of PowerPlant objects
        """
        return [
            plant for plant in plants 
            if plant.primary_energy_type in energy_types
        ]
    
    @staticmethod
    def filter_by_states(
        plants: List[PowerPlant],
        states: List[str]
    ) -> List[PowerPlant]:
        """
        Filter plants by states
        
        Args:
            plants: List of PowerPlant objects
            states: List of state names or abbreviations
            
        Returns:
            Filtered list of PowerPlant objects
        """
        states_lower = [state.lower() for state in states]
        return [
            plant for plant in plants 
            if plant.location.state.lower() in states_lower
        ]
    
    @staticmethod
    def filter_by_sector_types(
        plants: List[PowerPlant],
        sector_types: List[str]
    ) -> List[PowerPlant]:
        """
        Filter plants by sector types
        
        Args:
            plants: List of PowerPlant objects
            sector_types: List of sector type names
            
        Returns:
            Filtered list of PowerPlant objects
        """
        return [
            plant for plant in plants 
            if plant.sector_name in sector_types
        ]
    
    @staticmethod
    def filter_renewable_only(plants: List[PowerPlant]) -> List[PowerPlant]:
        """
        Filter to include only renewable energy plants
        
        Args:
            plants: List of PowerPlant objects
            
        Returns:
            Filtered list of renewable PowerPlant objects
        """
        return [plant for plant in plants if plant.is_renewable]
    
    @staticmethod
    def filter_by_bounding_box(
        plants: List[PowerPlant],
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float
    ) -> List[PowerPlant]:
        """
        Filter plants by geographic bounding box
        
        Args:
            plants: List of PowerPlant objects
            min_lat: Minimum latitude
            max_lat: Maximum latitude
            min_lon: Minimum longitude
            max_lon: Maximum longitude
            
        Returns:
            Filtered list of PowerPlant objects
        """
        return [
            plant for plant in plants
            if (min_lat <= plant.location.latitude <= max_lat and
                min_lon <= plant.location.longitude <= max_lon)
        ]
    
    @staticmethod
    def filter_by_polygon(
        plants: List[PowerPlant],
        polygon: Polygon
    ) -> List[PowerPlant]:
        """
        Filter plants by geographic polygon
        
        Args:
            plants: List of PowerPlant objects
            polygon: Shapely Polygon object
            
        Returns:
            Filtered list of PowerPlant objects
        """
        filtered = []
        for plant in plants:
            point = Point(plant.location.longitude, plant.location.latitude)
            if polygon.contains(point):
                filtered.append(plant)
        
        return filtered
    
    @staticmethod
    def filter_by_data_period(
        plants: List[PowerPlant],
        min_year: Optional[int] = None,
        max_year: Optional[int] = None,
        min_period: Optional[int] = None,
        max_period: Optional[int] = None
    ) -> List[PowerPlant]:
        """
        Filter plants by data period (year or specific period)
        
        Args:
            plants: List of PowerPlant objects
            min_year: Minimum year (e.g., 2024)
            max_year: Maximum year (e.g., 2025)
            min_period: Minimum period in YYYYMM format (e.g., 202401)
            max_period: Maximum period in YYYYMM format (e.g., 202412)
            
        Returns:
            Filtered list of PowerPlant objects
        """
        filtered = []
        
        for plant in plants:
            if plant.data_period is None:
                continue
            
            # Extract year from period (first 4 digits)
            try:
                period_year = int(str(plant.data_period)[:4])
            except (ValueError, TypeError):
                continue
            
            # Check year-based filters
            if min_year is not None and period_year < min_year:
                continue
            if max_year is not None and period_year > max_year:
                continue
            
            # Check period-based filters
            if min_period is not None and plant.data_period < min_period:
                continue
            if max_period is not None and plant.data_period > max_period:
                continue
            
            filtered.append(plant)
        
        return filtered
    
    @staticmethod
    def filter_after_2024(plants: List[PowerPlant]) -> List[PowerPlant]:
        """
        Convenience method to filter plants with data from 2024 onwards
        
        Args:
            plants: List of PowerPlant objects
            
        Returns:
            Filtered list of PowerPlant objects from 2024+
        """
        return PowerPlantFilter.filter_by_data_period(plants, min_year=2024)
    
    @staticmethod
    def filter_dataframe_by_capacity_range(
        df: pd.DataFrame,
        min_capacity: Optional[float] = None,
        max_capacity: Optional[float] = None,
        capacity_column: str = 'total_mw'
    ) -> pd.DataFrame:
        """
        Filter DataFrame by capacity range
        
        Args:
            df: DataFrame with power plants data
            min_capacity: Minimum capacity in MW
            max_capacity: Maximum capacity in MW
            capacity_column: Column name for capacity values
            
        Returns:
            Filtered DataFrame
        """
        filtered_df = df.copy()
        
        if min_capacity is not None:
            filtered_df = filtered_df[
                filtered_df[capacity_column] >= min_capacity
            ]
        
        if max_capacity is not None:
            filtered_df = filtered_df[
                filtered_df[capacity_column] <= max_capacity
            ]
        
        return filtered_df
    
    @staticmethod
    def filter_dataframe_by_energy_types(
        df: pd.DataFrame,
        energy_types: List[str],
        energy_type_column: str = 'primary_energy_type'
    ) -> pd.DataFrame:
        """
        Filter DataFrame by energy types
        
        Args:
            df: DataFrame with power plants data
            energy_types: List of energy type names
            energy_type_column: Column name for energy type
            
        Returns:
            Filtered DataFrame
        """
        return df[df[energy_type_column].isin(energy_types)]
    
    @staticmethod
    def filter_dataframe_by_states(
        df: pd.DataFrame,
        states: List[str],
        state_column: str = 'state'
    ) -> pd.DataFrame:
        """
        Filter DataFrame by states
        
        Args:
            df: DataFrame with power plants data
            states: List of state names
            state_column: Column name for state
            
        Returns:
            Filtered DataFrame
        """
        return df[df[state_column].isin(states)]
    
    @staticmethod
    def get_capacity_summary_by_state(
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Get capacity summary grouped by state
        
        Args:
            df: DataFrame with power plants data
            
        Returns:
            DataFrame with capacity summary by state
        """
        capacity_columns = [
            'total_mw', 'coal_mw', 'natural_gas_mw', 'nuclear_mw',
            'hydro_mw', 'solar_mw', 'wind_mw', 'geothermal_mw',
            'biomass_mw', 'battery_mw', 'renewable_capacity_mw'
        ]
        
        # Filter to only existing columns
        existing_columns = [col for col in capacity_columns if col in df.columns]
        
        summary = df.groupby('state')[existing_columns].sum().reset_index()
        summary['plant_count'] = df.groupby('state').size().reset_index(drop=True)
        
        return summary
    
    @staticmethod
    def get_capacity_summary_by_energy_type(
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Get capacity summary grouped by energy type
        
        Args:
            df: DataFrame with power plants data
            
        Returns:
            DataFrame with capacity summary by energy type
        """
        summary = df.groupby('primary_energy_type').agg({
            'total_mw': ['sum', 'mean', 'count'],
            'plant_name': 'count'
        }).reset_index()
        
        # Flatten column names
        summary.columns = [
            'energy_type', 'total_capacity_mw', 'avg_capacity_mw', 
            'capacity_count', 'plant_count'
        ]
        
        return summary.sort_values('total_capacity_mw', ascending=False)
    
    @staticmethod
    def filter_dataframe_by_data_period(
        df: pd.DataFrame,
        min_year: Optional[int] = None,
        max_year: Optional[int] = None,
        min_period: Optional[int] = None,
        max_period: Optional[int] = None,
        period_column: str = 'data_period'
    ) -> pd.DataFrame:
        """
        Filter DataFrame by data period
        
        Args:
            df: DataFrame with power plants data
            min_year: Minimum year (e.g., 2024)
            max_year: Maximum year (e.g., 2025)
            min_period: Minimum period in YYYYMM format (e.g., 202401)
            max_period: Maximum period in YYYYMM format (e.g., 202412)
            period_column: Column name for data period
            
        Returns:
            Filtered DataFrame
        """
        filtered_df = df.copy()
        
        # Remove rows with null periods
        filtered_df = filtered_df[filtered_df[period_column].notna()]
        
        if min_year is not None or max_year is not None:
            # Extract year from period
            filtered_df['period_year'] = filtered_df[period_column].astype(str).str[:4].astype(int)
            
            if min_year is not None:
                filtered_df = filtered_df[filtered_df['period_year'] >= min_year]
            if max_year is not None:
                filtered_df = filtered_df[filtered_df['period_year'] <= max_year]
            
            # Drop the temporary column
            filtered_df = filtered_df.drop('period_year', axis=1)
        
        if min_period is not None:
            filtered_df = filtered_df[filtered_df[period_column] >= min_period]
        if max_period is not None:
            filtered_df = filtered_df[filtered_df[period_column] <= max_period]
        
        return filtered_df
    
    @staticmethod
    def filter_dataframe_after_2024(
        df: pd.DataFrame,
        period_column: str = 'data_period'
    ) -> pd.DataFrame:
        """
        Convenience method to filter DataFrame to 2024+ data
        
        Args:
            df: DataFrame with power plants data
            period_column: Column name for data period
            
        Returns:
            Filtered DataFrame with 2024+ data
        """
        return PowerPlantFilter.filter_dataframe_by_data_period(
            df, min_year=2024, period_column=period_column
        )


class DataAggregator:
    """Utility class for aggregating power plants data"""
    
    @staticmethod
    def aggregate_by_state_and_type(
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Aggregate capacity data by state and energy type
        
        Args:
            df: DataFrame with power plants data
            
        Returns:
            Aggregated DataFrame
        """
        return df.groupby(['state', 'primary_energy_type']).agg({
            'total_mw': 'sum',
            'plant_name': 'count',
            'renewable_capacity_mw': 'sum'
        }).reset_index().rename(columns={'plant_name': 'plant_count'})
    
    @staticmethod
    def create_capacity_pivot_table(
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Create pivot table with states as rows and energy types as columns
        
        Args:
            df: DataFrame with power plants data
            
        Returns:
            Pivot table DataFrame
        """
        return df.pivot_table(
            index='state',
            columns='primary_energy_type',
            values='total_mw',
            aggfunc='sum',
            fill_value=0
        ).reset_index()
    
    @staticmethod
    def calculate_renewable_percentage(
        df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calculate renewable energy percentage by state
        
        Args:
            df: DataFrame with power plants data
            
        Returns:
            DataFrame with renewable percentages
        """
        state_summary = df.groupby('state').agg({
            'total_mw': 'sum',
            'renewable_capacity_mw': 'sum'
        }).reset_index()
        
        state_summary['renewable_percentage'] = (
            state_summary['renewable_capacity_mw'] / 
            state_summary['total_mw'] * 100
        ).round(2)
        
        return state_summary.sort_values('renewable_percentage', ascending=False)
