"""
Export power plants data for TypeScript frontend
"""
import json
import logging
from pathlib import Path
import sys
import os
import pandas as pd
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'data-processing'))
from eia_atlas_client import EIAAtlasClient
from filters import PowerPlantFilter, EnergyType

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def export_power_plants_data():
    """Export power plants data to JSON for frontend consumption"""
    
    # Initialize client
    client = EIAAtlasClient()
    
    try:
        # Get a reasonable sample of data (adjust limit as needed)
        logger.info("Fetching power plants data...")
        plants = client.get_power_plants('all_plants', limit=5000)
        
        # Don't filter by date initially - get all available data
        logger.info("Processing all available data...")
        
        # Convert to DataFrame for easier processing
        df = client.to_dataframe(plants)
        
        # Filter to more recent data (2020+ instead of 2024+ for more data)
        if not df.empty and 'data_period' in df.columns:
            logger.info("Filtering to 2020+ data...")
            df = df[df['data_period'].notna()]
            df['period_year'] = df['data_period'].astype(str).str[:4].astype(int)
            df = df[df['period_year'] >= 2020]
            df = df.drop('period_year', axis=1)
        else:
            logger.info("Using all available data (no date filtering)")
        
        # Convert to records for JSON export
        if not df.empty:
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
        else:
            logger.warning("No data found after filtering to 2024+")
            cleaned_records = []
        
        # Create output directory
        output_dir = Path('public/data')
        output_dir.mkdir(exist_ok=True)
        
        # Export main dataset
        output_file = output_dir / 'power_plants_comprehensive.json'
        with open(output_file, 'w') as f:
            json.dump(cleaned_records, f, indent=2, default=str)
        
        logger.info(f"Exported {len(cleaned_records)} plants to {output_file}")
        
        # Export summary statistics
        summary = {
            'total_plants': len(cleaned_records),
            'energy_types': df['primary_energy_type'].value_counts().to_dict(),
            'states': df['state'].value_counts().head(10).to_dict(),
            'capacity_stats': {
                'total_mw': float(df['total_mw'].sum()) if not df['total_mw'].isna().all() else 0,
                'renewable_mw': float(df['renewable_capacity_mw'].sum()) if not df['renewable_capacity_mw'].isna().all() else 0,
                'avg_capacity': float(df['total_mw'].mean()) if not df['total_mw'].isna().all() else 0,
                'max_capacity': float(df['total_mw'].max()) if not df['total_mw'].isna().all() else 0,
            },
            'data_periods': df['data_period'].value_counts().to_dict() if 'data_period' in df.columns else {}
        }
        
        summary_file = output_dir / 'summary_stats.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        logger.info(f"Exported summary statistics to {summary_file}")
        
        # Export renewable plants separately
        renewable_plants = [
            record for record in cleaned_records 
            if record.get('is_renewable', False)
        ]
        
        renewable_file = output_dir / 'renewable_plants_2024.json'
        with open(renewable_file, 'w') as f:
            json.dump(renewable_plants, f, indent=2, default=str)
        
        logger.info(f"Exported {len(renewable_plants)} renewable plants to {renewable_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"Data export failed: {e}")
        return False


def export_sample_data():
    """Export a smaller sample for development/testing"""
    
    client = EIAAtlasClient()
    
    try:
        # Get samples from different energy types
        logger.info("Fetching sample data for development...")
        
        sample_data = []
        energy_types = [EnergyType.SOLAR, EnergyType.WIND, EnergyType.HYDRO, EnergyType.NUCLEAR]
        
        for energy_type in energy_types:
            plants = client.get_plants_by_energy_type(energy_type, limit=50)
            recent_plants = PowerPlantFilter.filter_after_2024(plants)
            df = client.to_dataframe(recent_plants)
            
            if not df.empty:
                records = df.to_dict('records')
                sample_data.extend(records[:25])  # Take up to 25 from each type
        
        # Clean up the data
        cleaned_sample = []
        for record in sample_data:
            cleaned_record = {}
            for key, value in record.items():
                if pd.isna(value):
                    cleaned_record[key] = None
                else:
                    cleaned_record[key] = value
            cleaned_sample.append(cleaned_record)
        
        # Export sample
        output_dir = Path('public/data')
        output_dir.mkdir(exist_ok=True)
        
        sample_file = output_dir / 'sample_plants.json'
        with open(sample_file, 'w') as f:
            json.dump(cleaned_sample, f, indent=2, default=str)
        
        logger.info(f"Exported {len(cleaned_sample)} sample plants to {sample_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"Sample data export failed: {e}")
        return False


if __name__ == "__main__":
    
    logger.info("Starting data export...")
    
    # Export sample data first (faster for development)
    if export_sample_data():
        logger.info("✓ Sample data export completed")
    else:
        logger.error("✗ Sample data export failed")
    
    # Export full dataset
    if export_power_plants_data():
        logger.info("✓ Full data export completed")
    else:
        logger.error("✗ Full data export failed")
    
    logger.info("Data export process completed")
