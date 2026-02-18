"""
STEP 1A: Climate Scenario Data Acquisition Module

This module handles the acquisition and validation of CMIP6 climate projection data
from the World Bank Climate Knowledge Portal and NOAA ground stations.

Functions:
    - fetch_cmip6_data: Download CMIP6 ensemble data
    - fetch_noaa_validation_data: Download historical ground station data
    - validate_climate_data: Cross-validate model outputs against observations
    - downscale_climate_data: Apply statistical downscaling to asset locations

Author: Climate Risk Assessment Team
Date: 2025
"""

import logging
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import warnings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CMIP6DataAcquisition:
    """
    Handles acquisition of CMIP6 climate projection data from multiple sources.
    
    The class provides methods to download, process, and validate climate data
    for the specified asset locations and time periods.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the data acquisition module.
        
        Args:
            config: Configuration dictionary containing API endpoints, variables,
                   asset locations, and temporal parameters
        """
        self.config = config
        self.data_dir = Path(config['DATA_DIR'])
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for different data types
        self.cmip6_dir = self.data_dir / 'cmip6'
        self.noaa_dir = self.data_dir / 'noaa'
        self.processed_dir = self.data_dir / 'processed'
        
        for dir_path in [self.cmip6_dir, self.noaa_dir, self.processed_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        logger.info("CMIP6 Data Acquisition module initialized")
    
    def fetch_cmip6_data(
        self,
        scenario: str,
        variable: str,
        latitude: float,
        longitude: float,
        start_year: int,
        end_year: int
    ) -> pd.DataFrame:
        """
        Fetch CMIP6 climate projection data from World Bank API.
        
        This function downloads ensemble climate data for a specific scenario,
        variable, and location. It handles multi-model ensemble data and
        returns a structured DataFrame.
        
        Args:
            scenario: Climate scenario (e.g., 'rcp45', 'rcp85')
            variable: Climate variable code (e.g., 'tas', 'pr', 'sfcWind')
            latitude: Latitude of location
            longitude: Longitude of location
            start_year: Start year for data extraction
            end_year: End year for data extraction
        
        Returns:
            DataFrame with columns: [year, month, variable_value, model, scenario]
        
        Note:
            This is a placeholder implementation. The actual World Bank API
            endpoints and request structure need to be configured based on
            their current API documentation.
        """
        logger.info(f"Fetching CMIP6 data: {scenario}, {variable}, "
                   f"lat={latitude}, lon={longitude}, {start_year}-{end_year}")
        
        # Placeholder URL structure (to be updated with actual API)
        # base_url = self.config['WORLD_BANK_API']['base_url']
        # url = f"{base_url}/data/{scenario}/{variable}"
        
        # ==================================================================
        # PLACEHOLDER: Replace with actual API call
        # ==================================================================
        # The actual implementation should:
        # 1. Construct proper API request with authentication if needed
        # 2. Handle pagination for large datasets
        # 3. Parse response format (JSON/NetCDF/CSV)
        # 4. Extract ensemble member data
        # 5. Handle missing data and quality flags
        
        # For now, generate synthetic data structure
        logger.warning("Using placeholder data - replace with actual World Bank API call")
        
        dates = pd.date_range(
            start=f'{start_year}-01-01',
            end=f'{end_year}-12-31',
            freq='D'  # Daily frequency
        )
        
        # Simulate ensemble of 10 climate models
        models = [f'model_{i:02d}' for i in range(1, 11)]
        
        data_list = []
        for model in models:
            # Generate synthetic data with seasonal patterns
            n_days = len(dates)
            
            if variable in ['tas', 'tasmax', 'tasmin']:
                # Temperature (°C) with seasonal cycle
                base_temp = 20 + 10 * np.sin(2 * np.pi * np.arange(n_days) / 365.25)
                noise = np.random.normal(0, 3, n_days)
                values = base_temp + noise
                
            elif variable == 'pr':
                # Precipitation (mm/day)
                base_pr = 2 + 1 * np.sin(2 * np.pi * np.arange(n_days) / 365.25)
                values = np.maximum(0, base_pr + np.random.gamma(2, 1, n_days))
                
            elif variable == 'sfcWind':
                # Wind speed (m/s)
                base_wind = 5 + 2 * np.sin(2 * np.pi * np.arange(n_days) / 365.25)
                values = np.maximum(0, base_wind + np.random.normal(0, 1.5, n_days))
                
            elif variable == 'hurs':
                # Relative humidity (%)
                base_hurs = 60 + 15 * np.sin(2 * np.pi * np.arange(n_days) / 365.25)
                values = np.clip(base_hurs + np.random.normal(0, 10, n_days), 0, 100)
            
            else:
                values = np.random.normal(0, 1, n_days)
            
            df_model = pd.DataFrame({
                'date': dates,
                'year': dates.year,
                'month': dates.month,
                'day': dates.day,
                'value': values,
                'variable': variable,
                'model': model,
                'scenario': scenario
            })
            
            data_list.append(df_model)
        
        df_combined = pd.concat(data_list, ignore_index=True)
        
        # Save to disk
        output_file = self.cmip6_dir / f'{scenario}_{variable}_lat{latitude}_lon{longitude}.csv'
        df_combined.to_csv(output_file, index=False)
        logger.info(f"Saved CMIP6 data to {output_file}")
        
        return df_combined
    
    def fetch_noaa_validation_data(
        self,
        station_id: str,
        start_year: int,
        end_year: int
    ) -> pd.DataFrame:
        """
        Fetch historical weather data from NOAA ground stations for validation.
        
        Args:
            station_id: NOAA station identifier
            start_year: Start year for historical data
            end_year: End year for historical data
        
        Returns:
            DataFrame with historical observations
        
        Note:
            Requires NOAA API token. Replace with actual API implementation.
        """
        logger.info(f"Fetching NOAA validation data: {station_id}, {start_year}-{end_year}")
        
        # ==================================================================
        # PLACEHOLDER: Replace with actual NOAA API call
        # ==================================================================
        # Actual implementation should use NOAA Climate Data Online (CDO) API:
        # https://www.ncdc.noaa.gov/cdo-web/webservices/v2
        
        logger.warning("Using placeholder data - replace with actual NOAA API call")
        
        dates = pd.date_range(
            start=f'{start_year}-01-01',
            end=f'{end_year}-12-31',
            freq='D'
        )
        
        # Generate synthetic historical data
        n_days = len(dates)
        df_noaa = pd.DataFrame({
            'date': dates,
            'year': dates.year,
            'month': dates.month,
            'tmax': 25 + 10 * np.sin(2 * np.pi * np.arange(n_days) / 365.25) + np.random.normal(0, 3, n_days),
            'tmin': 15 + 8 * np.sin(2 * np.pi * np.arange(n_days) / 365.25) + np.random.normal(0, 2.5, n_days),
            'precipitation': np.maximum(0, 2 + np.random.gamma(2, 1, n_days)),
            'wind_speed': np.maximum(0, 5 + np.random.normal(0, 1.5, n_days)),
            'station_id': station_id
        })
        
        # Save to disk
        output_file = self.noaa_dir / f'{station_id}_{start_year}_{end_year}.csv'
        df_noaa.to_csv(output_file, index=False)
        logger.info(f"Saved NOAA data to {output_file}")
        
        return df_noaa
    
    def validate_climate_data(
        self,
        cmip6_data: pd.DataFrame,
        noaa_data: pd.DataFrame,
        variable_mapping: Dict[str, str]
    ) -> Dict[str, float]:
        """
        Cross-validate CMIP6 model outputs against NOAA ground observations.
        
        Computes validation metrics including bias, RMSE, and correlation
        between modeled and observed climate variables.
        
        Args:
            cmip6_data: CMIP6 projection data
            noaa_data: NOAA historical observations
            variable_mapping: Mapping between CMIP6 and NOAA variable names
        
        Returns:
            Dictionary of validation metrics
        """
        logger.info("Validating CMIP6 data against NOAA observations")
        
        validation_metrics = {}
        
        for cmip6_var, noaa_var in variable_mapping.items():
            # Filter CMIP6 data for this variable
            cmip6_subset = cmip6_data[cmip6_data['variable'] == cmip6_var].copy()
            
            # Aggregate across ensemble members (take mean)
            cmip6_daily = cmip6_subset.groupby('date')['value'].mean().reset_index()
            cmip6_daily.columns = ['date', 'cmip6_value']
            
            # Merge with NOAA data
            noaa_subset = noaa_data[['date', noaa_var]].copy()
            noaa_subset.columns = ['date', 'noaa_value']
            
            merged = pd.merge(cmip6_daily, noaa_subset, on='date', how='inner')
            
            if len(merged) == 0:
                logger.warning(f"No overlapping data for {cmip6_var}/{noaa_var}")
                continue
            
            # Calculate validation metrics
            bias = (merged['cmip6_value'] - merged['noaa_value']).mean()
            rmse = np.sqrt(((merged['cmip6_value'] - merged['noaa_value']) ** 2).mean())
            correlation = merged[['cmip6_value', 'noaa_value']].corr().iloc[0, 1]
            
            validation_metrics[cmip6_var] = {
                'bias': bias,
                'rmse': rmse,
                'correlation': correlation,
                'n_obs': len(merged)
            }
            
            logger.info(f"{cmip6_var}: Bias={bias:.2f}, RMSE={rmse:.2f}, R={correlation:.3f}")
        
        return validation_metrics
    
    def downscale_climate_data(
        self,
        raw_data: pd.DataFrame,
        target_lat: float,
        target_lon: float,
        method: str = 'random_forest'
    ) -> pd.DataFrame:
        """
        Apply statistical downscaling to climate data for asset location.
        
        Uses perfect-prognosis statistical downscaling with Random Forest
        or Quantile Regression Forest to refine coarse GCM outputs to
        site-specific conditions.
        
        Args:
            raw_data: Raw CMIP6 data at coarse resolution
            target_lat: Target latitude for downscaling
            target_lon: Target longitude for downscaling
            method: Downscaling method ('random_forest' or 'quantile_regression')
        
        Returns:
            Downscaled climate data at target location
        
        Note:
            This is a simplified placeholder. Full implementation requires:
            - Training predictors from historical high-res data
            - Accounting for topography and local features
            - Bias correction using observations
        """
        logger.info(f"Downscaling climate data to lat={target_lat}, lon={target_lon}")
        
        # ==================================================================
        # PLACEHOLDER: Simplified downscaling
        # ==================================================================
        # Actual implementation should:
        # 1. Extract large-scale predictors from GCM
        # 2. Train statistical model on historical high-res observations
        # 3. Apply trained model to future GCM projections
        # 4. Include elevation, land-sea contrast, and local circulations
        
        logger.warning("Using simplified downscaling - implement full RF/QRF method")
        
        # For now, apply simple bias correction
        downscaled = raw_data.copy()
        
        # Add small-scale variability
        if method == 'random_forest':
            # Simulate local-scale variations
            downscaled['value'] = downscaled['value'] + np.random.normal(0, 0.5, len(downscaled))
        
        logger.info("Downscaling complete")
        return downscaled
    
    def aggregate_to_monthly(self, daily_data: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate daily data to monthly resolution for Years 1-5.
        
        Args:
            daily_data: Daily climate data
        
        Returns:
            Monthly aggregated data
        """
        logger.info("Aggregating data to monthly resolution")
        
        # Group by year, month, model, scenario, variable
        monthly = daily_data.groupby(
            ['year', 'month', 'model', 'scenario', 'variable']
        ).agg({
            'value': ['mean', 'min', 'max', 'std']
        }).reset_index()
        
        monthly.columns = ['year', 'month', 'model', 'scenario', 'variable',
                          'mean', 'min', 'max', 'std']
        
        return monthly
    
    def aggregate_to_annual(self, daily_data: pd.DataFrame) -> pd.DataFrame:
        """
        Aggregate daily data to annual resolution for Years 6-50.
        
        Args:
            daily_data: Daily climate data
        
        Returns:
            Annual aggregated data
        """
        logger.info("Aggregating data to annual resolution")
        
        # Group by year, model, scenario, variable
        annual = daily_data.groupby(
            ['year', 'model', 'scenario', 'variable']
        ).agg({
            'value': ['mean', 'min', 'max', 'std']
        }).reset_index()
        
        annual.columns = ['year', 'model', 'scenario', 'variable',
                         'mean', 'min', 'max', 'std']
        
        return annual


def main():
    """
    Test the data acquisition module.
    """
    from config.config import (
        ASSETS, CLIMATE_SCENARIOS, DATA_DIR,
        ANALYSIS_START_YEAR, ANALYSIS_END_YEAR,
        HISTORICAL_START_YEAR, HISTORICAL_END_YEAR,
        WORLD_BANK_API, NOAA_STATIONS
    )
    
    config = {
        'DATA_DIR': DATA_DIR,
        'WORLD_BANK_API': WORLD_BANK_API,
        'NOAA_STATIONS': NOAA_STATIONS
    }
    
    acquisition = CMIP6DataAcquisition(config)
    
    # Example: Fetch data for Hayhurst Solar
    asset = ASSETS['hayhurst_solar']
    lat = asset['location']['latitude']
    lon = asset['location']['longitude']
    
    # Fetch CMIP6 data for both scenarios
    for scenario in ['rcp45', 'rcp85']:
        for variable in ['tas', 'tasmax', 'tasmin', 'pr']:
            data = acquisition.fetch_cmip6_data(
                scenario=scenario,
                variable=variable,
                latitude=lat,
                longitude=lon,
                start_year=ANALYSIS_START_YEAR,
                end_year=ANALYSIS_END_YEAR
            )
            print(f"Fetched {len(data)} records for {scenario}/{variable}")
    
    # Fetch NOAA validation data
    station_id = NOAA_STATIONS['culberson']['station_id']
    noaa_data = acquisition.fetch_noaa_validation_data(
        station_id=station_id,
        start_year=HISTORICAL_START_YEAR,
        end_year=HISTORICAL_END_YEAR
    )
    
    print(f"\nNOAA validation data: {len(noaa_data)} records")


if __name__ == "__main__":
    main()
