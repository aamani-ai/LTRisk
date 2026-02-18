"""
Configuration file for Climate Risk Assessment Framework

This module contains all configuration parameters for the NAV impairment analysis
including asset specifications, climate scenarios, model parameters, and file paths.

Author: Climate Risk Assessment Team
Date: 2025
"""

from datetime import datetime
from pathlib import Path

# ============================================================================
# PROJECT STRUCTURE
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
DASHBOARD_DIR = PROJECT_ROOT / "dashboard"

# Create directories if they don't exist
for dir_path in [DATA_DIR, OUTPUT_DIR, DASHBOARD_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# ============================================================================
# ASSET SPECIFICATIONS
# ============================================================================

ASSETS = {
    "hayhurst_solar": {
        "name": "Hayhurst Texas Solar",
        "type": "solar_pv",
        "location": {
            "county": "Culberson",
            "state": "TX",
            "latitude": 31.815992,
            "longitude": -104.0853,
            "climate_zone": "arid_desert"
        },
        "capacity_mw": 24.8,
        "eul_years": 25,  # Expected Useful Life
        "technology": "crystalline_silicon",
        "installation_year": 2020
    },
    "maverick_wind": {
        "name": "Maverick Creek Wind",
        "type": "wind_turbine",
        "location": {
            "county": "Concho",
            "state": "TX",
            "latitude": 31.262546,
            "longitude": -99.84396,
            "climate_zone": "semi_arid"
        },
        "capacity_mw": 491.6,
        "eul_years": 35,  # Expected Useful Life
        "technology": "horizontal_axis",
        "hub_height_m": 80,
        "rotor_diameter_m": 90
    }
}

# ============================================================================
# CLIMATE SCENARIOS
# ============================================================================

CLIMATE_SCENARIOS = {
    "rcp45": {
        "name": "RCP 4.5",
        "description": "Moderate emissions pathway",
        "emission_level": "medium"
    },
    "rcp85": {
        "name": "RCP 8.5",
        "description": "High emissions pathway",
        "emission_level": "high"
    }
}

# ============================================================================
# TEMPORAL PARAMETERS
# ============================================================================

ANALYSIS_START_YEAR = 2025
ANALYSIS_END_YEAR = 2050
TOTAL_YEARS = ANALYSIS_END_YEAR - ANALYSIS_START_YEAR + 1

# High resolution period (monthly) for validation
HIGH_RES_START_YEAR = 2025
HIGH_RES_END_YEAR = 2029
HIGH_RES_YEARS = HIGH_RES_END_YEAR - HIGH_RES_START_YEAR + 1

# Annual resolution period
ANNUAL_START_YEAR = 2030
ANNUAL_END_YEAR = 2050

# Historical validation period
HISTORICAL_START_YEAR = 2000
HISTORICAL_END_YEAR = 2024

# ============================================================================
# FINANCIAL PARAMETERS
# ============================================================================

# Weighted Average Cost of Capital
WACC_BASE = 0.10  # 10%
WACC_SENSITIVITY = [0.08, 0.10, 0.12]  # For sensitivity analysis

# NPV discount rate (same as WACC for base case)
DISCOUNT_RATE = WACC_BASE

# ============================================================================
# CLIMATE DATA SOURCES
# ============================================================================

# World Bank Climate Knowledge Portal API
WORLD_BANK_API = {
    "base_url": "https://climateknowledgeportal.worldbank.org/api",
    "variables": [
        "tas",      # Near-surface air temperature
        "tasmax",   # Maximum temperature
        "tasmin",   # Minimum temperature
        "pr",       # Precipitation
        "sfcWind",  # Near-surface wind speed
        "hurs",     # Near-surface relative humidity
    ]
}

# LLNL AIMS Portal (alternative source)
LLNL_AIMS = {
    "base_url": "https://aims2.llnl.gov/search",
    "project": "CMIP6"
}

# NOAA Ground Stations for Validation
NOAA_STATIONS = {
    "culberson": {
        "station_id": "USC00412019",  # Example ID
        "name": "Culberson County",
        "latitude": 31.82,
        "longitude": -104.09
    },
    "concho": {
        "station_id": "USC00411962",  # Example ID
        "name": "Concho County",
        "latitude": 31.26,
        "longitude": -99.84
    }
}

# ============================================================================
# SEVERE CLIMATE VARIABILITY RATING (SCVR) PARAMETERS
# ============================================================================

SCVR_THRESHOLDS = {
    "heat_wave": {
        "min_consecutive_days": 3,
        "percentile_tmax": 90,
        "percentile_tmin": 90
    },
    "cold_wave": {
        "min_consecutive_days": 3,
        "percentile_tmax": 10,
        "percentile_tmin": 10
    },
    "freeze_frost": {
        "frost_threshold_c": 0,   # T_min < 0°C
        "icing_threshold_c": 0    # T_max < 0°C
    },
    "extreme_precipitation": {
        "rolling_window_days": 5
    },
    "dry_spell": {
        "precipitation_threshold_mm": 0,  # Consecutive days with P = 0
    },
    "wind_extreme": {
        "cut_out_speed_ms": 25  # Wind turbine cut-out speed
    },
    "energy_drought": {
        "threshold_pct": 50,  # % of historical average
        "min_duration_days": 14  # Multi-week period
    }
}

# Fire Weather Index parameters
FWI_PARAMS = {
    "temperature_weight": 0.3,
    "humidity_weight": 0.3,
    "wind_weight": 0.2,
    "precipitation_weight": 0.2
}

# ============================================================================
# HAZARD CHANGE RATIO (HCR) PARAMETERS
# ============================================================================

# Base HCR multipliers (will be calibrated based on literature)
HCR_BASE = {
    "pluvial_flood": {
        "scvr_dependency": ["precipitation"],
        "base_multiplier": 1.0,
        "impact_level": "moderate"
    },
    "hail": {
        "scvr_dependency": ["temperature", "wind"],
        "base_multiplier": 1.0,
        "impact_level": "high"
    },
    "icing_rime": {
        "scvr_dependency": ["freeze", "humidity"],
        "base_multiplier": 1.0,
        "power_loss_pct": [20, 40],
        "impact_level": "moderate"
    },
    "icing_glaze": {
        "scvr_dependency": ["freeze", "precipitation"],
        "base_multiplier": 1.0,
        "power_loss_pct": [40, 80],
        "impact_level": "high"
    },
    "dust_storm": {
        "scvr_dependency": ["dry_spell", "wind"],
        "base_multiplier": 1.0,
        "impact_level": "moderate"
    },
    "wildfire": {
        "scvr_dependency": ["fire_weather_index"],
        "base_multiplier": 1.0,
        "impact_level": "variable",
        "proximity_buffer_km": [1, 5]
    }
}

# ============================================================================
# CATASTROPHIC EVENT PARAMETERS
# ============================================================================

CATASTROPHIC_EVENTS = {
    "hurricane": {
        "historical_frequency_per_year": 0.05,  # 1 in 20 years for Texas
        "scvr_multiplier_var": "wind",
        "duration_days": [3, 7],
        "severity_range": [0.6, 1.0]  # Fraction of capacity affected
    },
    "extreme_ice_storm": {
        "historical_frequency_per_year": 0.10,  # 1 in 10 years (Texas 2021 analog)
        "scvr_multiplier_var": "cold_wave",
        "duration_days": [7, 14],
        "recovery_days": [30, 60],
        "severity_range": [0.7, 1.0]
    },
    "wildfire": {
        "proximity_dependent": True,
        "buffer_zones_km": [1, 5, 10],
        "severity_by_zone": [0.9, 0.5, 0.2]
    }
}

# ============================================================================
# EQUIPMENT FAILURE RATIO (EFR) PARAMETERS - SOLAR PV
# ============================================================================

SOLAR_DEGRADATION = {
    "temperature_coefficient": {
        "gamma_per_c": -0.0045,  # Power coefficient per °C
        "reference_temp_c": 25,
        "model": "linear"
    },
    "humidity_heat_aging": {
        "model": "pecks",
        "gamma_0": 0.0,  # To be calibrated
        "gamma_1": 0.0,  # To be calibrated
        "gamma_2": 0.0,  # To be calibrated
        "climate_zone_factor": {
            "arid_desert": 0.7,  # Lower humidity dampens effect
            "semi_arid": 0.85,
            "humid": 1.2
        }
    },
    "freeze_thaw": {
        "model": "coffin_manson",
        "constant_c": 1.0,  # To be calibrated
        "exponent_k": 2.0,
        "impact_level": "moderate"
    },
    "uv_heat": {
        "base_rate_pct_year": 0.1,
        "climate_zone_factor": {
            "arid_desert": 2.5,  # High UV in desert
            "semi_arid": 1.5,
            "humid": 1.0
        }
    },
    "soiling": {
        "dry_spell_coefficient": 0.001,  # Loss per dry spell day
        "wind_speed_coefficient": 0.0005,
        "cleaning_frequency_days": 30,
        "climate_zone_factor": {
            "arid_desert": 2.0,  # High dust in West Texas
            "semi_arid": 1.3,
            "humid": 0.8
        }
    },
    "composite_degradation": {
        "typical_pct_year": [0.5, 0.8],
        "arid_projected_pct_year": [1.2, 1.8]
    }
}

# ============================================================================
# EQUIPMENT FAILURE RATIO (EFR) PARAMETERS - WIND TURBINE
# ============================================================================

WIND_DEGRADATION = {
    "rime_icing": {
        "temperature_threshold_c": 0,
        "humidity_threshold_pct": 75,
        "power_loss_pct": [20, 40],
        "typical_duration_hours": [4, 12]
    },
    "glaze_icing": {
        "temperature_threshold_c": 0,
        "precipitation_required": True,
        "power_loss_pct": [40, 80],
        "typical_duration_days": [1, 3],
        "texas_2021_analog": True
    },
    "blade_erosion": {
        "annual_aep_loss_pct": 0.25,  # 5-7% over 20 years
        "cumulative_20yr_loss_pct": [5, 7],
        "progressive": True
    },
    "structural_fatigue": {
        "model": "palmgren_miner",
        "failure_threshold": 1.0,
        "wind_variability_multiplier": 1.2
    },
    "extreme_wind_cutout": {
        "cutout_speed_ms": 25,
        "increasing_frequency": True
    }
}

# ============================================================================
# UNCERTAINTY QUANTIFICATION PARAMETERS
# ============================================================================

MONTE_CARLO = {
    "n_iterations": 1000,
    "random_seed": 42,
    "confidence_intervals": [10, 50, 90],  # P10, P50, P90
    "parameter_ranges": {
        "hcr_variation_pct": 20,
        "efr_variation_pct": 15,
        "cat_event_freq_variation_pct": 30
    }
}

# ============================================================================
# INFRASURE MODEL INTEGRATION (PLACEHOLDERS)
# ============================================================================

INFRASURE_CONFIG = {
    "performance_model": {
        "module_name": "infrasure.performance",  # TO BE UPDATED
        "function_name": "calculate_asset_performance",  # TO BE UPDATED
        "parameters": {
            "ensemble_size": 10,
            "time_resolution": "hourly",
            "include_weather_data": True
        }
    },
    "bi_model": {
        "module_name": "infrasure.business_interruption",  # TO BE UPDATED
        "function_name": "calculate_bi_losses",  # TO BE UPDATED
        "parameters": {
            "scvr_scaled": True,  # InfraSure BI already includes SCVR scaling
            "include_recovery": False
        }
    }
}

# ============================================================================
# VISUALIZATION PARAMETERS
# ============================================================================

VISUALIZATION = {
    "color_scheme": {
        "rcp45": "#4472C4",
        "rcp85": "#C55A11",
        "base": "#70AD47",
        "degradation": "#FFC000"
    },
    "figure_size": (12, 8),
    "dpi": 150,
    "style": "seaborn-v0_8-darkgrid"
}

# ============================================================================
# DASHBOARD CONFIGURATION
# ============================================================================

DASHBOARD_CONFIG = {
    "port": 8050,
    "host": "127.0.0.1",
    "debug": True,
    "title": "Climate Risk Assessment Dashboard",
    "update_interval_ms": 5000
}

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOGGING = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": OUTPUT_DIR / f"climate_risk_{datetime.now().strftime('%Y%m%d')}.log"
}
