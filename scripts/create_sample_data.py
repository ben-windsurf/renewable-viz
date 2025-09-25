"""
Create sample data for development and testing
"""
import json
import os
import sys
from pathlib import Path
sys.path.append('../data-processing')
from eia_atlas_client import EIAAtlasClient
from filters import PowerPlantFilter, EnergyTypeFilter

def create_sample_data():
    """Create sample power plant data for development"""
    
    sample_data = [
        {
            "object_id": 1,
            "plant_code": 1001,
            "plant_name": "Ivanpah Solar Power Facility",
            "utility_name": "NRG Energy Inc",
            "utility_id": 1001,
            "sector_name": "IPP Non-CHP",
            "primary_source": "solar",
            "primary_energy_type": "Solar",
            "is_renewable": True,
            "latitude": 35.5556,
            "longitude": -115.4689,
            "city": "Primm",
            "county": "San Bernardino",
            "state": "California",
            "zip_code": None,
            "street_address": None,
            "total_mw": 392.0,
            "install_mw": 392.0,
            "coal_mw": None,
            "natural_gas_mw": None,
            "nuclear_mw": None,
            "hydro_mw": None,
            "hydro_pumped_mw": None,
            "solar_mw": 392.0,
            "wind_mw": None,
            "geothermal_mw": None,
            "biomass_mw": None,
            "battery_mw": None,
            "crude_oil_mw": None,
            "other_mw": None,
            "renewable_capacity_mw": 392.0,
            "tech_desc": "Solar Thermal",
            "source_desc": "Solar = 392 MW",
            "data_period": 202401,
            "source": "EIA-860, EIA-860M and EIA-923"
        },
        {
            "object_id": 2,
            "plant_code": 1002,
            "plant_name": "Alta Wind Energy Center",
            "utility_name": "Terra-Gen Power LLC",
            "utility_id": 1002,
            "sector_name": "IPP Non-CHP",
            "primary_source": "wind",
            "primary_energy_type": "Wind",
            "is_renewable": True,
            "latitude": 34.6037,
            "longitude": -118.3406,
            "city": "Tehachapi",
            "county": "Kern",
            "state": "California",
            "zip_code": 93561,
            "street_address": "20000 Tehachapi Willow Springs Rd",
            "total_mw": 1548.0,
            "install_mw": 1548.0,
            "coal_mw": None,
            "natural_gas_mw": None,
            "nuclear_mw": None,
            "hydro_mw": None,
            "hydro_pumped_mw": None,
            "solar_mw": None,
            "wind_mw": 1548.0,
            "geothermal_mw": None,
            "biomass_mw": None,
            "battery_mw": None,
            "crude_oil_mw": None,
            "other_mw": None,
            "renewable_capacity_mw": 1548.0,
            "tech_desc": "Onshore Wind Turbine",
            "source_desc": "Wind = 1548 MW",
            "data_period": 202401,
            "source": "EIA-860, EIA-860M and EIA-923"
        },
        {
            "object_id": 3,
            "plant_code": 1003,
            "plant_name": "Grand Coulee Dam",
            "utility_name": "Bureau of Reclamation",
            "utility_id": 1003,
            "sector_name": "Electric Utility",
            "primary_source": "hydro",
            "primary_energy_type": "Hydroelectric",
            "is_renewable": True,
            "latitude": 47.9648,
            "longitude": -118.9816,
            "city": "Grand Coulee",
            "county": "Grant",
            "state": "Washington",
            "zip_code": 99133,
            "street_address": "Grand Coulee Dam",
            "total_mw": 6809.0,
            "install_mw": 6809.0,
            "coal_mw": None,
            "natural_gas_mw": None,
            "nuclear_mw": None,
            "hydro_mw": 6809.0,
            "hydro_pumped_mw": None,
            "solar_mw": None,
            "wind_mw": None,
            "geothermal_mw": None,
            "biomass_mw": None,
            "battery_mw": None,
            "crude_oil_mw": None,
            "other_mw": None,
            "renewable_capacity_mw": 6809.0,
            "tech_desc": "Conventional Hydroelectric",
            "source_desc": "Hydro = 6809 MW",
            "data_period": 202401,
            "source": "EIA-860, EIA-860M and EIA-923"
        },
        {
            "object_id": 4,
            "plant_code": 1004,
            "plant_name": "Palo Verde Nuclear Station",
            "utility_name": "Arizona Public Service Co",
            "utility_id": 1004,
            "sector_name": "Electric Utility",
            "primary_source": "nuclear",
            "primary_energy_type": "Nuclear",
            "is_renewable": False,
            "latitude": 33.3881,
            "longitude": -112.8642,
            "city": "Wintersburg",
            "county": "Maricopa",
            "state": "Arizona",
            "zip_code": 85358,
            "street_address": "5801 S Wintersburg Rd",
            "total_mw": 3937.0,
            "install_mw": 3937.0,
            "coal_mw": None,
            "natural_gas_mw": None,
            "nuclear_mw": 3937.0,
            "hydro_mw": None,
            "hydro_pumped_mw": None,
            "solar_mw": None,
            "wind_mw": None,
            "geothermal_mw": None,
            "biomass_mw": None,
            "battery_mw": None,
            "crude_oil_mw": None,
            "other_mw": None,
            "renewable_capacity_mw": 0.0,
            "tech_desc": "Nuclear",
            "source_desc": "Nuclear = 3937 MW",
            "data_period": 202401,
            "source": "EIA-860, EIA-860M and EIA-923"
        },
        {
            "object_id": 5,
            "plant_code": 1005,
            "plant_name": "The Geysers",
            "utility_name": "Calpine Corp",
            "utility_id": 1005,
            "sector_name": "IPP Non-CHP",
            "primary_source": "geothermal",
            "primary_energy_type": "Geothermal",
            "is_renewable": True,
            "latitude": 38.7756,
            "longitude": -122.7575,
            "city": "Geyserville",
            "county": "Sonoma",
            "state": "California",
            "zip_code": 95441,
            "street_address": "The Geysers",
            "total_mw": 725.0,
            "install_mw": 725.0,
            "coal_mw": None,
            "natural_gas_mw": None,
            "nuclear_mw": None,
            "hydro_mw": None,
            "hydro_pumped_mw": None,
            "solar_mw": None,
            "wind_mw": None,
            "geothermal_mw": 725.0,
            "biomass_mw": None,
            "battery_mw": None,
            "crude_oil_mw": None,
            "other_mw": None,
            "renewable_capacity_mw": 725.0,
            "tech_desc": "Geothermal",
            "source_desc": "Geothermal = 725 MW",
            "data_period": 202401,
            "source": "EIA-860, EIA-860M and EIA-923"
        },
        {
            "object_id": 6,
            "plant_code": 1006,
            "plant_name": "W A Parish Electric Generating Station",
            "utility_name": "NRG Texas Power LLC",
            "utility_id": 1006,
            "sector_name": "IPP Non-CHP",
            "primary_source": "natural gas",
            "primary_energy_type": "Natural Gas",
            "is_renewable": False,
            "latitude": 29.4833,
            "longitude": -95.6389,
            "city": "Thompsons",
            "county": "Fort Bend",
            "state": "Texas",
            "zip_code": 77481,
            "street_address": "16403 Crabb River Rd",
            "total_mw": 3653.0,
            "install_mw": 3653.0,
            "coal_mw": None,
            "natural_gas_mw": 3653.0,
            "nuclear_mw": None,
            "hydro_mw": None,
            "hydro_pumped_mw": None,
            "solar_mw": None,
            "wind_mw": None,
            "geothermal_mw": None,
            "biomass_mw": None,
            "battery_mw": None,
            "crude_oil_mw": None,
            "other_mw": None,
            "renewable_capacity_mw": 0.0,
            "tech_desc": "Natural Gas Fired Combined Cycle",
            "source_desc": "Natural Gas = 3653 MW",
            "data_period": 202401,
            "source": "EIA-860, EIA-860M and EIA-923"
        },
        {
            "object_id": 7,
            "plant_code": 1007,
            "plant_name": "Hornsdale Power Reserve",
            "utility_name": "Tesla Inc",
            "utility_id": 1007,
            "sector_name": "IPP Non-CHP",
            "primary_source": "batteries",
            "primary_energy_type": "Battery Storage",
            "is_renewable": False,
            "latitude": 33.7490,
            "longitude": -116.2023,
            "city": "Desert Center",
            "county": "Riverside",
            "state": "California",
            "zip_code": 92239,
            "street_address": None,
            "total_mw": 150.0,
            "install_mw": 150.0,
            "coal_mw": None,
            "natural_gas_mw": None,
            "nuclear_mw": None,
            "hydro_mw": None,
            "hydro_pumped_mw": None,
            "solar_mw": None,
            "wind_mw": None,
            "geothermal_mw": None,
            "biomass_mw": None,
            "battery_mw": 150.0,
            "crude_oil_mw": None,
            "other_mw": None,
            "renewable_capacity_mw": 0.0,
            "tech_desc": "Batteries",
            "source_desc": "Battery = 150 MW",
            "data_period": 202401,
            "source": "EIA-860, EIA-860M and EIA-923"
        }
    ]
    
    # Create output directory
    output_dir = Path('public/data')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Export sample data
    sample_file = output_dir / 'sample_plants.json'
    with open(sample_file, 'w') as f:
        json.dump(sample_data, f, indent=2)
    
    print(f"Created sample data with {len(sample_data)} plants at {sample_file}")
    
    # Create summary stats
    summary = {
        "total_plants": len(sample_data),
        "energy_types": {},
        "states": {},
        "capacity_stats": {
            "total_mw": sum(plant.get("total_mw", 0) or 0 for plant in sample_data),
            "renewable_mw": sum(plant.get("renewable_capacity_mw", 0) or 0 for plant in sample_data),
            "avg_capacity": sum(plant.get("total_mw", 0) or 0 for plant in sample_data) / len(sample_data),
            "max_capacity": max(plant.get("total_mw", 0) or 0 for plant in sample_data)
        },
        "data_periods": {"202401": len(sample_data)}
    }
    
    # Count energy types and states
    for plant in sample_data:
        energy_type = plant.get("primary_energy_type", "Unknown")
        state = plant.get("state", "Unknown")
        
        summary["energy_types"][energy_type] = summary["energy_types"].get(energy_type, 0) + 1
        summary["states"][state] = summary["states"].get(state, 0) + 1
    
    # Export summary
    summary_file = output_dir / 'summary_stats.json'
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Created summary statistics at {summary_file}")
    
    return True

if __name__ == "__main__":
    create_sample_data()
