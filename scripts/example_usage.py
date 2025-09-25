"""
Example usage of the EIA Atlas Power Plants data layer
"""
import pandas as pd
import geopandas as gpd
import logging
from src.data import (
    EIAAtlasClient, 
    EnergyType, 
    PowerPlantFilter, 
    DataAggregator
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Main example function demonstrating the data layer usage"""
    
    # Initialize the client
    logger.info("Initializing EIA Atlas client...")
    client = EIAAtlasClient()
    
    # Example 1: Get all renewable energy plants (limited sample)
    logger.info("Fetching renewable energy plants...")
    renewable_plants = client.get_renewable_plants(limit=100)
    logger.info(f"Found {len(renewable_plants)} renewable plants")
    
    # Convert to DataFrame
    renewable_df = client.to_dataframe(renewable_plants)
    print("\nRenewable Plants Sample:")
    print(renewable_df[['plant_name', 'state', 'primary_energy_type', 'total_mw']].head())
    
    # Example 2: Get solar plants in California
    logger.info("Fetching solar plants in California...")
    ca_solar_plants = client.get_plants_by_state('California', energy_type=EnergyType.SOLAR, limit=50)
    ca_solar_df = client.to_dataframe(ca_solar_plants)
    
    print(f"\nCalifornia Solar Plants: {len(ca_solar_plants)} found")
    print(ca_solar_df[['plant_name', 'city', 'solar_mw', 'total_mw']].head())
    
    # Example 3: Filter by capacity range
    logger.info("Filtering plants by capacity...")
    large_plants = PowerPlantFilter.filter_by_capacity_range(
        renewable_plants, 
        min_capacity=50.0  # Plants with at least 50 MW
    )
    
    print(f"\nLarge renewable plants (>50 MW): {len(large_plants)} found")
    
    # Example 4: Get capacity summary by state
    logger.info("Creating capacity summary by state...")
    state_summary = PowerPlantFilter.get_capacity_summary_by_state(renewable_df)
    print("\nRenewable Capacity by State (Top 10):")
    print(state_summary.nlargest(10, 'renewable_capacity_mw')[
        ['state', 'renewable_capacity_mw', 'plant_count']
    ])
    
    # Example 5: Get capacity summary by energy type
    logger.info("Creating capacity summary by energy type...")
    type_summary = PowerPlantFilter.get_capacity_summary_by_energy_type(renewable_df)
    print("\nCapacity by Energy Type:")
    print(type_summary)
    
    # Example 6: Create pivot table
    logger.info("Creating capacity pivot table...")
    pivot_table = DataAggregator.create_capacity_pivot_table(renewable_df)
    print("\nCapacity Pivot Table (States x Energy Types):")
    print(pivot_table.head())
    
    # Example 7: Calculate renewable percentage by state
    logger.info("Calculating renewable percentages...")
    
    # Get a broader sample for better percentage calculation
    all_plants_sample = client.get_power_plants('all_plants', limit=500)
    all_plants_df = client.to_dataframe(all_plants_sample)
    
    renewable_pct = DataAggregator.calculate_renewable_percentage(all_plants_df)
    print("\nRenewable Percentage by State (Top 10):")
    print(renewable_pct.head(10)[['state', 'total_mw', 'renewable_capacity_mw', 'renewable_percentage']])
    
    # Example 8: Create GeoDataFrame for mapping
    logger.info("Creating GeoDataFrame...")
    renewable_gdf = client.to_geodataframe(renewable_plants)
    print(f"\nGeoDataFrame created with {len(renewable_gdf)} plants")
    print("Geometry sample:")
    print(renewable_gdf[['plant_name', 'state', 'geometry']].head())
    
    # Example 9: Filter by bounding box (e.g., Western US)
    logger.info("Filtering by geographic bounding box...")
    western_plants = PowerPlantFilter.filter_by_bounding_box(
        renewable_plants,
        min_lat=32.0,  # Southern border
        max_lat=49.0,  # Northern border  
        min_lon=-125.0,  # Western border
        max_lon=-100.0   # Eastern border
    )
    
    print(f"\nWestern US renewable plants: {len(western_plants)} found")
    
    # Example 10: Export data
    logger.info("Exporting data to files...")
    
    # Export to CSV
    renewable_df.to_csv('renewable_plants_sample.csv', index=False)
    logger.info("Exported renewable_plants_sample.csv")
    
    # Export GeoDataFrame to GeoJSON
    renewable_gdf.to_file('renewable_plants_sample.geojson', driver='GeoJSON')
    logger.info("Exported renewable_plants_sample.geojson")
    
    # Export state summary
    state_summary.to_csv('renewable_capacity_by_state.csv', index=False)
    logger.info("Exported renewable_capacity_by_state.csv")
    
    logger.info("Example completed successfully!")


if __name__ == "__main__":
    main()
