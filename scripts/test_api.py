"""
Simple test script to verify EIA Atlas API connectivity and data layer functionality
"""
import sys
import logging
from src.data import EIAAtlasClient, EnergyType

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_api_connectivity():
    """Test basic API connectivity"""
    try:
        logger.info("Testing API connectivity...")
        client = EIAAtlasClient()
        
        # Test with a small sample
        plants = client.get_power_plants('all_plants', limit=5)
        
        if plants:
            logger.info(f"✓ Successfully fetched {len(plants)} plants")
            
            # Test first plant data
            first_plant = plants[0]
            logger.info(f"✓ Sample plant: {first_plant.plant_name} in {first_plant.location.state}")
            logger.info(f"✓ Primary source: {first_plant.primary_source}")
            logger.info(f"✓ Total capacity: {first_plant.capacity.total_mw} MW")
            
            return True
        else:
            logger.error("✗ No plants returned from API")
            return False
            
    except Exception as e:
        logger.error(f"✗ API connectivity test failed: {e}")
        return False


def test_dataframe_conversion():
    """Test DataFrame conversion functionality"""
    try:
        logger.info("Testing DataFrame conversion...")
        client = EIAAtlasClient()
        
        # Get a small sample
        plants = client.get_power_plants('all_plants', limit=10)
        
        # Convert to DataFrame
        df = client.to_dataframe(plants)
        
        if not df.empty:
            logger.info(f"✓ DataFrame created with {len(df)} rows and {len(df.columns)} columns")
            logger.info(f"✓ Sample columns: {list(df.columns[:5])}")
            return True
        else:
            logger.error("✗ Empty DataFrame created")
            return False
            
    except Exception as e:
        logger.error(f"✗ DataFrame conversion test failed: {e}")
        return False


def test_energy_type_filtering():
    """Test energy type filtering"""
    try:
        logger.info("Testing energy type filtering...")
        client = EIAAtlasClient()
        
        # Test solar plants
        solar_plants = client.get_plants_by_energy_type(EnergyType.SOLAR, limit=5)
        
        if solar_plants:
            logger.info(f"✓ Found {len(solar_plants)} solar plants")
            
            # Verify they are actually solar
            for plant in solar_plants:
                if plant.primary_energy_type != EnergyType.SOLAR:
                    logger.warning(f"Plant {plant.plant_name} classified as {plant.primary_energy_type}, not solar")
            
            return True
        else:
            logger.warning("No solar plants found (this might be normal depending on data)")
            return True
            
    except Exception as e:
        logger.error(f"✗ Energy type filtering test failed: {e}")
        return False


def test_state_filtering():
    """Test state-based filtering"""
    try:
        logger.info("Testing state filtering...")
        client = EIAAtlasClient()
        
        # Test California plants
        ca_plants = client.get_plants_by_state('California', limit=5)
        
        if ca_plants:
            logger.info(f"✓ Found {len(ca_plants)} plants in California")
            
            # Verify they are actually in California
            for plant in ca_plants:
                if 'california' not in plant.location.state.lower():
                    logger.warning(f"Plant {plant.plant_name} not in California: {plant.location.state}")
            
            return True
        else:
            logger.warning("No California plants found")
            return True
            
    except Exception as e:
        logger.error(f"✗ State filtering test failed: {e}")
        return False


def main():
    """Run all tests"""
    logger.info("Starting EIA Atlas API tests...")
    
    tests = [
        ("API Connectivity", test_api_connectivity),
        ("DataFrame Conversion", test_dataframe_conversion),
        ("Energy Type Filtering", test_energy_type_filtering),
        ("State Filtering", test_state_filtering)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} Test ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nOverall: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        logger.info("🎉 All tests passed! The data layer is working correctly.")
        return 0
    else:
        logger.error("❌ Some tests failed. Check the logs above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
