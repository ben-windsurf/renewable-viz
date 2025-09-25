"""
Export mixed energy type data for better visualization
"""
import json
import logging
from pathlib import Path
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data-processing'))
from eia_atlas_client import EIAAtlasClient
from filters import PowerPlantFilter, EnergyType
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def export_mixed_data():
    """Export a balanced mix of different energy types"""
    
    # Initialize client
    client = EIAAtlasClient()
    
    all_plants = []
    
    # Fetch smaller samples from each service to get variety
    services_config = [
        ('solar_plants', 'Solar Plants', 200),
        ('wind_plants', 'Wind Plants', 200),
        ('hydro_plants', 'Hydro Plants', 200),
        ('nuclear_plants', 'Nuclear Plants', 50),  # Fewer nuclear plants exist
        ('natural_gas_plants', 'Natural Gas Plants', 200),
        ('coal_plants', 'Coal Plants', 100),
        ('geothermal_plants', 'Geothermal Plants', 50),
        ('battery_plants', 'Battery Storage', 100),
    ]
    
    try:
        for service_key, service_name, limit in services_config:
            try:
                logger.info(f"Fetching {limit} plants from {service_name}...")
                plants = client.get_power_plants(service_key, limit=limit)
                
                if plants:
                    logger.info(f"Retrieved {len(plants)} plants from {service_name}")
                    all_plants.extend(plants)
                else:
                    logger.warning(f"No plants found in {service_name}")
                    
            except Exception as e:
                logger.warning(f"Failed to fetch from {service_name}: {e}")
                continue
        
        logger.info(f"Total plants collected: {len(all_plants)}")
        
        # Convert to DataFrame without deduplication first to see what we have
        df = client.to_dataframe(all_plants)
        
        if df.empty:
            logger.error("No data to export")
            return False
        
        logger.info(f"DataFrame shape: {df.shape}")
        logger.info(f"Energy types in DataFrame: {df['primary_energy_type'].value_counts().to_dict()}")
        
        # Now remove duplicates based on plant_code
        logger.info("Removing duplicates...")
        df_unique = df.drop_duplicates(subset=['plant_code'], keep='first')
        logger.info(f"After deduplication: {len(df_unique)} plants")
        
        # Convert to records for JSON export
        records = df_unique.to_dict('records')
        
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
        
        # Export mixed dataset
        output_file = output_dir / 'power_plants_mixed.json'
        with open(output_file, 'w') as f:
            json.dump(cleaned_records, f, indent=2, default=str)
        
        logger.info(f"Exported {len(cleaned_records)} mixed plants to {output_file}")
        
        # Export summary statistics
        energy_type_counts = {}
        state_counts = {}
        
        for record in cleaned_records:
            # Energy type counts
            energy_type = record.get('primary_energy_type', 'Unknown')
            energy_type_counts[energy_type] = energy_type_counts.get(energy_type, 0) + 1
            
            # State counts
            state = record.get('state', 'Unknown')
            state_counts[state] = state_counts.get(state, 0) + 1
        
        summary = {
            'total_plants': len(cleaned_records),
            'energy_types': energy_type_counts,
            'states': dict(sorted(state_counts.items(), key=lambda x: x[1], reverse=True)[:15]),
            'capacity_stats': {
                'total_mw': float(df_unique['total_mw'].sum()) if not df_unique['total_mw'].isna().all() else 0,
                'renewable_mw': float(df_unique['renewable_capacity_mw'].sum()) if not df_unique['renewable_capacity_mw'].isna().all() else 0,
                'avg_capacity': float(df_unique['total_mw'].mean()) if not df_unique['total_mw'].isna().all() else 0,
                'max_capacity': float(df_unique['total_mw'].max()) if not df_unique['total_mw'].isna().all() else 0,
            }
        }
        
        summary_file = output_dir / 'mixed_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        logger.info(f"Exported mixed summary to {summary_file}")
        
        # Print summary
        print("\n" + "="*60)
        print("MIXED DATA EXPORT SUMMARY")
        print("="*60)
        print(f"Total Plants: {summary['total_plants']:,}")
        print(f"Total Capacity: {summary['capacity_stats']['total_mw']:,.0f} MW")
        print(f"Renewable Capacity: {summary['capacity_stats']['renewable_mw']:,.0f} MW")
        print(f"Average Plant Size: {summary['capacity_stats']['avg_capacity']:.1f} MW")
        print(f"Largest Plant: {summary['capacity_stats']['max_capacity']:,.0f} MW")
        
        print(f"\nEnergy Types:")
        for energy_type, count in summary['energy_types'].items():
            print(f"  {energy_type}: {count} plants")
        
        print(f"\nTop States:")
        for state, count in list(summary['states'].items())[:10]:
            print(f"  {state}: {count} plants")
        
        return True
        
    except Exception as e:
        logger.error(f"Mixed data export failed: {e}")
        return False


if __name__ == "__main__":
    logger.info("Starting mixed data export...")
    
    if export_mixed_data():
        logger.info("✓ Mixed data export completed successfully!")
    else:
        logger.error("✗ Mixed data export failed")
