# Climate Risk Framework - Quick Start Guide

## Installation (5 minutes)

```bash
# 1. Extract the archive
tar -xzf climate_risk_framework.tar.gz
cd climate_risk_framework

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

## Critical Integration Points

### 1. InfraSure Performance Model Integration

**File:** `modules/step2_asset_performance.py`
**Line:** ~45

**What to do:**
```python
def call_infrasure_performance(self, asset_id, climate_data, scenario):
    # REPLACE THIS PLACEHOLDER:
    
    # Step 1: Import your actual InfraSure module
    from infrasure.performance import calculate_asset_performance
    
    # Step 2: Call with properly formatted inputs
    results = calculate_asset_performance(
        asset_id=asset_id,
        climate_data=climate_data,  # Format as InfraSure expects
        scenario=scenario
    )
    
    # Step 3: Return DataFrame with columns:
    # ['date', 'year', 'month', 'generation_mwh', 'capacity_factor']
    return results
```

### 2. InfraSure BI Model Integration

**File:** `modules/step3_4_5_integrated.py`
**Line:** ~55

**What to do:**
```python
def call_infrasure_bi(self, asset_id, scenario):
    # REPLACE THIS PLACEHOLDER:
    
    # Step 1: Import your actual InfraSure BI module
    from infrasure.business_interruption import calculate_bi_losses
    
    # Step 2: Call with parameters
    results = calculate_bi_losses(
        asset_id=asset_id,
        scenario=scenario
    )
    
    # Step 3: Return DataFrame with columns:
    # ['year', 'asset_id', 'scenario', 'bi_base_loss_mwh']
    # NOTE: InfraSure BI should already be scaled by SCVR
    return results
```

### 3. Update Configuration

**File:** `config/config.py`
**Lines:** ~230-245

**What to do:**
```python
INFRASURE_CONFIG = {
    "performance_model": {
        "module_name": "infrasure.performance",  # UPDATE: your module path
        "function_name": "calculate_asset_performance",  # UPDATE: your function name
    },
    "bi_model": {
        "module_name": "infrasure.business_interruption",  # UPDATE: your module path
        "function_name": "calculate_bi_losses",  # UPDATE: your function name
    }
}
```

## Running the Framework (First Time)

```bash
# Test with solar asset, RCP 4.5 scenario
python main.py --asset hayhurst_solar --scenario rcp45

# This will:
# - Download placeholder climate data (replace with real API later)
# - Calculate SCVR for all variables
# - Call InfraSure models (using placeholders until you integrate)
# - Calculate BI losses with HCR tables
# - Model equipment degradation
# - Compute NAV impairment with Monte Carlo
# - Save all results to outputs/ directory
```

## Viewing Results

```bash
# Launch interactive dashboard
python dashboard/dashboard.py

# Open browser to: http://127.0.0.1:8050
```

## Data API Updates (After Testing)

### World Bank Climate API

**File:** `modules/step1_data_acquisition.py`
**Line:** ~90

**Current:** Uses placeholder synthetic data
**TODO:** Replace with actual World Bank Climate Knowledge Portal API calls

```python
def fetch_cmip6_data(self, ...):
    # Replace placeholder with:
    base_url = "https://climateknowledgeportal.worldbank.org/api"
    endpoint = f"{base_url}/data/{scenario}/{variable}"
    
    response = requests.get(endpoint, params={
        'lat': latitude,
        'lon': longitude,
        'start': start_year,
        'end': end_year
    })
    
    data = response.json()
    # Parse response into DataFrame...
```

### NOAA Ground Station Data

**File:** `modules/step1_data_acquisition.py`
**Line:** ~145

**Current:** Uses placeholder synthetic data
**TODO:** Replace with NOAA Climate Data Online (CDO) API

```python
def fetch_noaa_validation_data(self, ...):
    # Replace placeholder with:
    base_url = "https://www.ncdc.noaa.gov/cdo-web/api/v2"
    
    # Requires NOAA API token
    headers = {'token': 'YOUR_NOAA_TOKEN'}
    
    response = requests.get(
        f"{base_url}/data",
        headers=headers,
        params={
            'datasetid': 'GHCND',
            'stationid': station_id,
            'startdate': f'{start_year}-01-01',
            'enddate': f'{end_year}-12-31'
        }
    )
    # Parse response...
```

## Testing Checklist

- [ ] Install all dependencies successfully
- [ ] Run main.py without errors
- [ ] Output files appear in outputs/ directory
- [ ] Dashboard launches and shows placeholder data
- [ ] InfraSure performance model integrated
- [ ] InfraSure BI model integrated
- [ ] Real CMIP6 data acquisition working
- [ ] NOAA validation data working
- [ ] Results validated against known benchmarks

## File Structure After Installation

```
climate_risk_framework/
├── config/
│   ├── __init__.py
│   └── config.py                 ← UPDATE InfraSure settings here
│
├── modules/
│   ├── __init__.py
│   ├── step1_data_acquisition.py  ← UPDATE World Bank/NOAA API here
│   ├── step1b_scvr_calculation.py
│   ├── step2_asset_performance.py ← UPDATE InfraSure Performance here
│   └── step3_4_5_integrated.py    ← UPDATE InfraSure BI here
│
├── dashboard/
│   ├── __init__.py
│   └── dashboard.py
│
├── data/                         ← Climate data downloaded here
├── outputs/                      ← Results saved here
├── main.py                       ← Run this
├── requirements.txt
└── README.md                     ← Full documentation
```

## Common Issues & Solutions

**"ModuleNotFoundError: No module named 'config'"**
→ Make sure you're in the climate_risk_framework directory
→ Run: `export PYTHONPATH="${PYTHONPATH}:$(pwd)"`

**"InfraSure module not found"**
→ Normal! Replace placeholders with your actual InfraSure module paths

**"Dashboard not loading"**
→ Check if port 8050 is available
→ Try: `python dashboard/dashboard.py --port 8051`

**"Data download slow/failing"**
→ Placeholder uses synthetic data (fast)
→ Real API will take longer on first run
→ Data is cached after first download

## Next Steps After Integration

1. **Validate with Known Data**
   - Compare Year 1-3 projections with actual asset performance
   - Check degradation rates against NREL benchmarks

2. **Calibrate HCR/EFR Tables**
   - Review literature for your specific asset types
   - Adjust multipliers in config.py based on research

3. **Run Sensitivity Analysis**
   - Test WACC at 8%, 10%, 12%
   - Vary HCR/EFR ranges
   - Check impact on NAV ratio

4. **Generate Reports**
   - All outputs are in CSV format
   - Easy to import into Excel/Power BI
   - Dashboard provides interactive exploration

## Support

For questions about:
- **Framework logic:** See README.md and code docstrings
- **InfraSure integration:** Contact your InfraSure team
- **Scientific methodology:** See framework document Appendix
- **Code issues:** Check inline comments and function documentation

---

**Last Updated:** 2025-02-13
**Version:** 1.0
