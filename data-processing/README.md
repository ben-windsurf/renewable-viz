# Data Processing Directory

This directory contains Python modules for data processing and API clients.

## Files

- `__init__.py` - Package initialization with utility functions
- `eia_atlas_client.py` - EIA Atlas API client for fetching renewable energy data
- `filters.py` - Data filtering and processing functions
- `models.py` - Data models and structures for renewable energy data
- `exported/` - Directory containing exported data files

## Usage

These modules are imported and used by scripts in the `scripts/` directory.

```python
from data_processing.eia_atlas_client import EIAAtlasClient
from data_processing.models import PowerPlant
from data_processing.filters import filter_by_technology
```
