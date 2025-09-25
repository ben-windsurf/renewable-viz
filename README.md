# Renewable Energy Visualization Dashboard

A comprehensive dashboard for visualizing renewable energy data across the United States, combining a robust Python data layer for accessing US Energy Atlas API data with a modern TypeScript/React frontend for interactive visualization.

## Features

- **Comprehensive Data Access**: Access to all power plant types (coal, natural gas, nuclear, renewable, etc.)
- **Interactive Visualization**: Modern TypeScript/React frontend with Mapbox GL integration
- **Energy Type Filtering**: Filter plants by specific energy types (solar, wind, hydro, etc.)
- **Geographic Filtering**: Filter by state, bounding box, or custom polygons
- **Capacity Analysis**: Analyze generation capacity by various dimensions
- **DataFrame Integration**: Seamless conversion to pandas DataFrames and GeoPandas GeoDataFrames
- **Renewable Energy Focus**: Built-in support for renewable energy analysis
- **Data Export**: Export to CSV, GeoJSON, and other formats
- **Design System**: Comprehensive styling with enforced color palette

## Installation

1. Clone or download this repository
2. Install the required dependencies:

**Python Dependencies:**
```bash
pip3 install -r requirements.txt
```

**Node.js Dependencies:**
```bash
npm install
```

## Quick Start

### Python Data Layer

```python
from src.data import EIAAtlasClient, EnergyType

# Initialize the client
client = EIAAtlasClient()

# Get all renewable energy plants
renewable_plants = client.get_renewable_plants(limit=100)

# Convert to DataFrame
df = client.to_dataframe(renewable_plants)
print(df.head())

# Get solar plants in California
ca_solar = client.get_plants_by_state('California', energy_type=EnergyType.SOLAR)

# Create GeoDataFrame for mapping
gdf = client.to_geodataframe(ca_solar)
```

### Frontend Development

```bash
# Start development server
npm run dev

# Build for production
npm run build
```

## Available Energy Types

The library supports the following energy types:

- **Coal**: Coal-fired power plants
- **Natural Gas**: Natural gas power plants  
- **Nuclear**: Nuclear power plants
- **Hydro**: Hydroelectric power plants
- **Hydro Pumped Storage**: Pumped storage hydroelectric plants
- **Solar**: Solar photovoltaic and thermal plants
- **Wind**: Wind power plants
- **Geothermal**: Geothermal power plants
- **Biomass**: Biomass and biogas plants
- **Battery**: Battery storage systems
- **Other**: Other energy sources
- **Crude Oil**: Oil-fired power plants

## Data Sources

The library accesses the following EIA Atlas services:

- `ElectricPowerPlants`: Comprehensive dataset with all plant types
- `Solar_Power_Plants`: Solar-specific plants
- `Wind_Power_Plants`: Wind-specific plants
- `Hydroelectric_Power_Plants`: Hydroelectric plants
- `Nuclear_Power_Plants`: Nuclear plants
- `Coal_Power_Plants`: Coal plants
- `Natural_Gas_Power_Plants`: Natural gas plants
- `Geothermal_Power_Plants`: Geothermal plants
- `Battery_Storage_Plants`: Battery storage systems

## Core Classes

### EIAAtlasClient

Main client class for accessing the EIA Atlas API.

```python
client = EIAAtlasClient(timeout=30)

# Get plants by service type
plants = client.get_power_plants('solar_plants', limit=100)

# Get plants by energy type
solar_plants = client.get_plants_by_energy_type(EnergyType.SOLAR)

# Get plants by state
ca_plants = client.get_plants_by_state('California')

# Get only renewable plants
renewable_plants = client.get_renewable_plants()
```

### PowerPlantFilter

Utility class for filtering power plants data.

```python
from src.data import PowerPlantFilter

# Filter by capacity range
large_plants = PowerPlantFilter.filter_by_capacity_range(
    plants, min_capacity=100.0
)

# Filter by multiple energy types
renewable_types = [EnergyType.SOLAR, EnergyType.WIND, EnergyType.HYDRO]
filtered_plants = PowerPlantFilter.filter_by_energy_types(plants, renewable_types)

# Filter by geographic bounding box
western_plants = PowerPlantFilter.filter_by_bounding_box(
    plants, min_lat=32.0, max_lat=49.0, min_lon=-125.0, max_lon=-100.0
)

# Get capacity summaries
state_summary = PowerPlantFilter.get_capacity_summary_by_state(df)
type_summary = PowerPlantFilter.get_capacity_summary_by_energy_type(df)
```

### DataAggregator

Utility class for aggregating and analyzing power plants data.

```python
from src.data import DataAggregator

# Aggregate by state and energy type
aggregated = DataAggregator.aggregate_by_state_and_type(df)

# Create pivot table
pivot = DataAggregator.create_capacity_pivot_table(df)

# Calculate renewable percentages
renewable_pct = DataAggregator.calculate_renewable_percentage(df)
```

## Data Structure

Each power plant record includes:

### Location Information
- Latitude/Longitude coordinates
- City, County, State
- Street address and ZIP code

### Capacity Information (in MW)
- Total installed capacity
- Capacity by energy type (coal, natural gas, solar, wind, etc.)
- Renewable capacity calculation

### Plant Details
- Plant name and code
- Utility name and ID
- Sector type (Electric Utility, IPP, etc.)
- Primary energy source
- Technology description

### Metadata
- Data period
- Source information
- Object ID for tracking

## Example Use Cases

### 1. Renewable Energy Analysis

```python
# Get all renewable plants
renewable_plants = client.get_renewable_plants()
df = client.to_dataframe(renewable_plants)

# Calculate renewable capacity by state
state_renewable = df.groupby('state')['renewable_capacity_mw'].sum().sort_values(ascending=False)
print("Top 10 states by renewable capacity:")
print(state_renewable.head(10))
```

### 2. Solar Plant Mapping

```python
# Get solar plants
solar_plants = client.get_plants_by_energy_type(EnergyType.SOLAR, limit=500)
solar_gdf = client.to_geodataframe(solar_plants)

# Filter large solar installations
large_solar = solar_gdf[solar_gdf['solar_mw'] >= 100]

# Export for mapping
large_solar.to_file('large_solar_plants.geojson', driver='GeoJSON')
```

### 3. State Energy Profile

```python
# Get all plants in Texas
texas_plants = client.get_plants_by_state('Texas', limit=1000)
texas_df = client.to_dataframe(texas_plants)

# Create energy mix summary
energy_mix = texas_df.groupby('primary_energy_type')['total_mw'].sum().sort_values(ascending=False)
print("Texas Energy Mix:")
print(energy_mix)
```

### 4. Capacity Trend Analysis

```python
# Get plants with data period information
plants = client.get_power_plants('all_plants', limit=1000)
df = client.to_dataframe(plants)

# Analyze by data period
period_analysis = df.groupby(['data_period', 'primary_energy_type'])['total_mw'].sum().unstack(fill_value=0)
print("Capacity trends by period and energy type:")
print(period_analysis)
```

## Filtering and Analysis

### Geographic Filtering

```python
# Filter by bounding box (e.g., Northeast US)
northeast_plants = PowerPlantFilter.filter_by_bounding_box(
    plants,
    min_lat=40.0, max_lat=47.0,
    min_lon=-80.0, max_lon=-67.0
)

# Filter by multiple states
target_states = ['California', 'Texas', 'Florida', 'New York']
multi_state_plants = PowerPlantFilter.filter_by_states(plants, target_states)
```

### Capacity Filtering

```python
# Large installations only
large_plants = PowerPlantFilter.filter_by_capacity_range(
    plants, min_capacity=500.0
)

# Medium-sized renewable plants
medium_renewable = PowerPlantFilter.filter_by_capacity_range(
    renewable_plants, min_capacity=10.0, max_capacity=100.0
)
```

### Data Export

```python
# Export to various formats
df.to_csv('power_plants.csv', index=False)
df.to_excel('power_plants.xlsx', index=False)

# Export GeoDataFrame
gdf.to_file('power_plants.geojson', driver='GeoJSON')
gdf.to_file('power_plants.shp', driver='ESRI Shapefile')
```

## Frontend Architecture

The frontend is built with:

- **Vite + React + TypeScript**: Modern development stack
- **Mapbox GL**: Hardware-accelerated mapping visualization
- **Design System**: Enforced color palette (#4a98d2, #92c362, #292929)
- **Responsive Design**: Mobile-friendly UI with accessibility support

## Error Handling

The library includes comprehensive error handling:

```python
try:
    plants = client.get_power_plants('invalid_service')
except ValueError as e:
    print(f"Invalid service: {e}")

try:
    plants = client.get_plants_by_state('California', limit=10000)
except requests.RequestException as e:
    print(f"API request failed: {e}")
```

## Performance Considerations

- The API supports pagination for large datasets
- Use `limit` parameter to control memory usage
- Consider filtering at the API level when possible
- Large queries may take several minutes to complete
- Mapbox GL provides hardware-accelerated rendering

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## License

This project is open source and available under the MIT License.

## Data Attribution

Data is sourced from the U.S. Energy Information Administration (EIA) Atlas. Please refer to EIA's terms of use and data attribution requirements when using this data in publications or applications.

## Support

For questions or issues, please create an issue in the repository or contact the maintainers.
