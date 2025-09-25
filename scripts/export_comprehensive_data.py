"""
Export comprehensive power plants data from multiple EIA Atlas services
"""
import json
import logging
from pathlib import Path
import sys
sys.path.append('../data-processing')
from eia_atlas_client import EIAAtlasClient
from filters import PowerPlantFilter, EnergyType
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def export_comprehensive_data():
    """Export comprehensive power plant data from all available services"""
    
    # Initialize client
    client = EIAAtlasClient()
    
    all_plants = []
    
    # Services to fetch from
    services_to_fetch = [
        ('all_plants', 'All Plants'),
        ('solar_plants', 'Solar Plants'),
        ('wind_plants', 'Wind Plants'),
        ('hydro_plants', 'Hydro Plants'),
        ('nuclear_plants', 'Nuclear Plants'),
        ('natural_gas_plants', 'Natural Gas Plants'),
        ('coal_plants', 'Coal Plants'),
        ('geothermal_plants', 'Geothermal Plants'),
        ('battery_plants', 'Battery Storage'),
    ]
    
    try:
        for service_key, service_name in services_to_fetch:
            try:
                logger.info(f"Fetching data from {service_name}...")
                plants = client.get_power_plants(service_key, limit=1000)
                
                if plants:
                    logger.info(f"Retrieved {len(plants)} plants from {service_name}")
                    all_plants.extend(plants)
                else:
                    logger.warning(f"No plants found in {service_name}")
                    
            except Exception as e:
                logger.warning(f"Failed to fetch from {service_name}: {e}")
                continue
        
        # Remove duplicates based on plant_code
        logger.info("Removing duplicates...")
        unique_plants = {}
        for plant in all_plants:
            plant_code = plant.plant_code
            if plant_code not in unique_plants:
                unique_plants[plant_code] = plant
        
        final_plants = list(unique_plants.values())
        logger.info(f"Total unique plants: {len(final_plants)}")
        
        # Convert to DataFrame
        df = client.to_dataframe(final_plants)
        
        if df.empty:
            logger.error("No data to export")
            return False
        
        # Convert to records for JSON export
        records = df.to_dict('records')
        
        # Clean up the data for frontend
        cleaned_records = []
        for record in records:
            # Convert NaN values to None
            cleaned_record = {}
            for key, value in record.items():
                if pd.isna(value):
                    cleaned_record[key] = None
                else:
                    cleaned_record[key] = value
            cleaned_records.append(cleaned_record)
        
        # Create output directory
        output_dir = Path('public/data')
        output_dir.mkdir(exist_ok=True)
        
        # Export comprehensive dataset
        output_file = output_dir / 'power_plants_comprehensive.json'
        with open(output_file, 'w') as f:
            json.dump(cleaned_records, f, indent=2, default=str)
        
        logger.info(f"Exported {len(cleaned_records)} comprehensive plants to {output_file}")
        
        # Export by energy type
        energy_type_data = {}
        for record in cleaned_records:
            energy_type = record.get('primary_energy_type', 'Unknown')
            if energy_type not in energy_type_data:
                energy_type_data[energy_type] = []
            energy_type_data[energy_type].append(record)
        
        # Export renewable plants separately
        renewable_plants = []
        for record in cleaned_records:
            if record.get('is_renewable', False):
                renewable_plants.append(record)
        
        renewable_file = output_dir / 'renewable_plants_comprehensive.json'
        with open(renewable_file, 'w') as f:
            json.dump(renewable_plants, f, indent=2, default=str)
        
        logger.info(f"Exported {len(renewable_plants)} renewable plants to {renewable_file}")
        
        # Export summary statistics
        summary = {
            'total_plants': len(cleaned_records),
            'renewable_plants': len(renewable_plants),
            'energy_types': {},
            'states': {},
            'capacity_stats': {
                'total_mw': float(df['total_mw'].sum()) if not df['total_mw'].isna().all() else 0,
                'renewable_mw': float(df['renewable_capacity_mw'].sum()) if not df['renewable_capacity_mw'].isna().all() else 0,
                'avg_capacity': float(df['total_mw'].mean()) if not df['total_mw'].isna().all() else 0,
                'max_capacity': float(df['total_mw'].max()) if not df['total_mw'].isna().all() else 0,
            },
            'data_periods': df['data_period'].value_counts().to_dict() if 'data_period' in df.columns else {},
            'by_energy_type': {k: len(v) for k, v in energy_type_data.items()}
        }
        
        # Count by energy type and state
        if 'primary_energy_type' in df.columns:
            summary['energy_types'] = df['primary_energy_type'].value_counts().to_dict()
        if 'state' in df.columns:
            summary['states'] = df['state'].value_counts().head(15).to_dict()
        
        summary_file = output_dir / 'comprehensive_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        logger.info(f"Exported comprehensive summary to {summary_file}")
        
        # Print summary
        print("\n" + "="*60)
        print("COMPREHENSIVE DATA EXPORT SUMMARY")
        print("="*60)
        print(f"Total Plants: {summary['total_plants']:,}")
        print(f"Renewable Plants: {summary['renewable_plants']:,}")
        print(f"Total Capacity: {summary['capacity_stats']['total_mw']:,.0f} MW")
        print(f"Renewable Capacity: {summary['capacity_stats']['renewable_mw']:,.0f} MW")
        print(f"Average Plant Size: {summary['capacity_stats']['avg_capacity']:.1f} MW")
        print(f"Largest Plant: {summary['capacity_stats']['max_capacity']:,.0f} MW")
        
        print(f"\nTop Energy Types:")
        for energy_type, count in list(summary['energy_types'].items())[:8]:
            print(f"  {energy_type}: {count} plants")
        
        print(f"\nTop States:")
        for state, count in list(summary['states'].items())[:10]:
            print(f"  {state}: {count} plants")
        
        return True
        
    except Exception as e:
        logger.error(f"Comprehensive data export failed: {e}")
        return False


if __name__ == "__main__":
    logger.info("Starting comprehensive data export...")
    
    if export_comprehensive_data():
        logger.info("✓ Comprehensive data export completed successfully!")
    else:
        logger.error("✗ Comprehensive data export failed")
