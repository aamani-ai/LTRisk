"""
STEP 1B: Severe Climate Variability Rating (SCVR) Calculation Module

This module calculates SCVR metrics for various climate variables by measuring
the increase in area under exceedance curves compared to historical baseline.

Functions:
    - calculate_heat_waves: Identify heat wave events
    - calculate_cold_waves: Identify cold wave events
    - calculate_freeze_events: Count frost and icing days
    - calculate_extreme_precipitation: Measure extreme rainfall
    - calculate_dry_spells: Identify drought periods
    - calculate_wind_extremes: Measure extreme wind events
    - calculate_energy_droughts: Identify low generation periods
    - calculate_fire_weather_index: Compute wildfire risk proxy
    - calculate_scvr: Compute SCVR for all variables

Author: Climate Risk Assessment Team
Date: 2025
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, Tuple, List
from scipy import stats
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SCVRCalculator:
    """
    Calculates Severe Climate Variability Ratings for climate variables.
    
    SCVR quantifies the increase in extreme events by comparing future
    climate scenarios against historical baselines using exceedance curves.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize SCVR calculator.
        
        Args:
            config: Configuration dictionary with SCVR thresholds and parameters
        """
        self.config = config
        self.thresholds = config['SCVR_THRESHOLDS']
        self.fwi_params = config['FWI_PARAMS']
        
        logger.info("SCVR Calculator initialized")
    
    def calculate_heat_waves(
        self,
        tmax: pd.Series,
        tmin: pd.Series,
        dates: pd.Series,
        baseline_tmax: pd.Series,
        baseline_tmin: pd.Series
    ) -> Tuple[int, pd.DataFrame]:
        """
        Calculate heat wave events based on temperature exceedance.
        
        A heat wave is defined as 3+ consecutive days where both T_max and T_min
        exceed the 90th percentile of the historical baseline.
        
        Args:
            tmax: Daily maximum temperature (°C)
            tmin: Daily minimum temperature (°C)
            dates: Date index
            baseline_tmax: Historical T_max for percentile calculation
            baseline_tmin: Historical T_min for percentile calculation
        
        Returns:
            Tuple of (number of heat wave events, DataFrame with event details)
        """
        params = self.thresholds['heat_wave']
        min_days = params['min_consecutive_days']
        
        # Calculate percentile thresholds
        tmax_threshold = np.percentile(baseline_tmax, params['percentile_tmax'])
        tmin_threshold = np.percentile(baseline_tmin, params['percentile_tmin'])
        
        # Identify days exceeding both thresholds
        exceed_both = (tmax > tmax_threshold) & (tmin > tmin_threshold)
        
        # Find consecutive sequences
        events = self._find_consecutive_events(exceed_both, dates, min_days)
        
        logger.info(f"Identified {len(events)} heat wave events")
        
        return len(events), events
    
    def calculate_cold_waves(
        self,
        tmax: pd.Series,
        tmin: pd.Series,
        dates: pd.Series,
        baseline_tmax: pd.Series,
        baseline_tmin: pd.Series
    ) -> Tuple[int, pd.DataFrame]:
        """
        Calculate cold wave events.
        
        A cold wave is defined as 3+ consecutive days where both T_max and T_min
        fall below the 10th percentile of the historical baseline.
        
        Args:
            tmax: Daily maximum temperature (°C)
            tmin: Daily minimum temperature (°C)
            dates: Date index
            baseline_tmax: Historical T_max for percentile calculation
            baseline_tmin: Historical T_min for percentile calculation
        
        Returns:
            Tuple of (number of cold wave events, DataFrame with event details)
        """
        params = self.thresholds['cold_wave']
        min_days = params['min_consecutive_days']
        
        # Calculate percentile thresholds
        tmax_threshold = np.percentile(baseline_tmax, params['percentile_tmax'])
        tmin_threshold = np.percentile(baseline_tmin, params['percentile_tmin'])
        
        # Identify days below both thresholds
        below_both = (tmax < tmax_threshold) & (tmin < tmin_threshold)
        
        # Find consecutive sequences
        events = self._find_consecutive_events(below_both, dates, min_days)
        
        logger.info(f"Identified {len(events)} cold wave events")
        
        return len(events), events
    
    def calculate_freeze_events(
        self,
        tmax: pd.Series,
        tmin: pd.Series,
        dates: pd.Series
    ) -> Dict[str, int]:
        """
        Calculate freeze and frost events.
        
        - Frost Days: T_min < 0°C
        - Icing Days: T_max < 0°C (more severe)
        
        Args:
            tmax: Daily maximum temperature (°C)
            tmin: Daily minimum temperature (°C)
            dates: Date index
        
        Returns:
            Dictionary with frost day count, icing day count, and details
        """
        params = self.thresholds['freeze_frost']
        
        frost_days = (tmin < params['frost_threshold_c']).sum()
        icing_days = (tmax < params['icing_threshold_c']).sum()
        
        logger.info(f"Frost days: {frost_days}, Icing days: {icing_days}")
        
        return {
            'frost_days': frost_days,
            'icing_days': icing_days,
            'frost_fraction': frost_days / len(dates),
            'icing_fraction': icing_days / len(dates)
        }
    
    def calculate_extreme_precipitation(
        self,
        precipitation: pd.Series,
        dates: pd.Series
    ) -> Dict[str, float]:
        """
        Calculate extreme precipitation metrics.
        
        Uses 5-day maximum rolling precipitation sums as indicator of
        extreme rainfall events that can cause flooding.
        
        Args:
            precipitation: Daily precipitation (mm)
            dates: Date index
        
        Returns:
            Dictionary with extreme precipitation metrics
        """
        params = self.thresholds['extreme_precipitation']
        window = params['rolling_window_days']
        
        # Calculate rolling sum
        rolling_sum = precipitation.rolling(window=window).sum()
        
        # Get annual maximum 5-day precipitation
        df = pd.DataFrame({'precip': rolling_sum, 'year': dates.dt.year})
        annual_max = df.groupby('year')['precip'].max()
        
        logger.info(f"Extreme precipitation - Mean annual max: {annual_max.mean():.1f} mm")
        
        return {
            'mean_annual_max_5day': annual_max.mean(),
            'max_5day_overall': rolling_sum.max(),
            'p95_5day': np.percentile(rolling_sum.dropna(), 95),
            'p99_5day': np.percentile(rolling_sum.dropna(), 99)
        }
    
    def calculate_dry_spells(
        self,
        precipitation: pd.Series,
        dates: pd.Series
    ) -> Dict[str, float]:
        """
        Calculate dry spell metrics.
        
        Dry spells are periods of consecutive days with zero precipitation,
        which increase wildfire risk and solar panel soiling.
        
        Args:
            precipitation: Daily precipitation (mm)
            dates: Date index
        
        Returns:
            Dictionary with dry spell statistics
        """
        params = self.thresholds['dry_spell']
        threshold = params['precipitation_threshold_mm']
        
        # Identify dry days
        dry_days = (precipitation <= threshold)
        
        # Find consecutive dry periods
        events = self._find_consecutive_events(dry_days, dates, min_length=1)
        
        if len(events) > 0:
            max_dry_spell = events['duration'].max()
            mean_dry_spell = events['duration'].mean()
            n_dry_spells_7plus = (events['duration'] >= 7).sum()
        else:
            max_dry_spell = 0
            mean_dry_spell = 0
            n_dry_spells_7plus = 0
        
        logger.info(f"Max dry spell: {max_dry_spell} days")
        
        return {
            'max_consecutive_dry_days': max_dry_spell,
            'mean_dry_spell_length': mean_dry_spell,
            'n_dry_spells_7plus_days': n_dry_spells_7plus,
            'total_dry_days': dry_days.sum()
        }
    
    def calculate_wind_extremes(
        self,
        wind_speed: pd.Series,
        dates: pd.Series
    ) -> Dict[str, float]:
        """
        Calculate wind extreme metrics.
        
        Tracks high wind speeds for:
        - Storm intensity (proxy using daily mean wind)
        - Turbine cut-out events (wind > 25 m/s)
        
        Args:
            wind_speed: Daily mean wind speed (m/s)
            dates: Date index
        
        Returns:
            Dictionary with wind extreme statistics
        """
        params = self.thresholds['wind_extreme']
        cutout_speed = params['cut_out_speed_ms']
        
        # Count cut-out events (wind > 25 m/s)
        cutout_days = (wind_speed > cutout_speed).sum()
        
        # Calculate percentiles
        p95_wind = np.percentile(wind_speed, 95)
        p99_wind = np.percentile(wind_speed, 99)
        max_wind = wind_speed.max()
        
        logger.info(f"Cut-out events: {cutout_days} days, Max wind: {max_wind:.1f} m/s")
        
        return {
            'cutout_days': cutout_days,
            'cutout_fraction': cutout_days / len(dates),
            'p95_wind': p95_wind,
            'p99_wind': p99_wind,
            'max_wind': max_wind
        }
    
    def calculate_energy_droughts(
        self,
        generation: pd.Series,
        dates: pd.Series,
        historical_avg: float
    ) -> Dict[str, float]:
        """
        Calculate energy drought periods.
        
        Energy droughts are multi-week periods where generation falls below
        50% of historical average, indicating sustained low resource availability.
        
        Args:
            generation: Daily generation (MWh) or resource proxy
            dates: Date index
            historical_avg: Historical average daily generation
        
        Returns:
            Dictionary with energy drought statistics
        """
        params = self.thresholds['energy_drought']
        threshold_pct = params['threshold_pct']
        min_duration = params['min_duration_days']
        
        # Identify low generation days
        threshold_value = historical_avg * (threshold_pct / 100)
        low_gen_days = (generation < threshold_value)
        
        # Find consecutive low generation periods
        events = self._find_consecutive_events(low_gen_days, dates, min_duration)
        
        logger.info(f"Identified {len(events)} energy drought events")
        
        return {
            'n_energy_droughts': len(events),
            'total_drought_days': events['duration'].sum() if len(events) > 0 else 0,
            'max_drought_duration': events['duration'].max() if len(events) > 0 else 0,
            'mean_drought_duration': events['duration'].mean() if len(events) > 0 else 0
        }
    
    def calculate_fire_weather_index(
        self,
        tmax: pd.Series,
        humidity: pd.Series,
        wind_speed: pd.Series,
        precipitation: pd.Series
    ) -> pd.Series:
        """
        Calculate Fire Weather Index as wildfire risk proxy.
        
        FWI is a weighted combination of:
        - High temperature (increases fire risk)
        - Low humidity (increases fire risk)
        - High wind (increases fire spread)
        - Low precipitation (increases fuel dryness)
        
        Args:
            tmax: Daily maximum temperature (°C)
            humidity: Relative humidity (%)
            wind_speed: Wind speed (m/s)
            precipitation: Daily precipitation (mm)
        
        Returns:
            Series with daily FWI values
        """
        # Normalize each component to 0-1 scale
        temp_norm = (tmax - tmax.min()) / (tmax.max() - tmax.min())
        hum_norm = 1 - ((humidity - humidity.min()) / (humidity.max() - humidity.min()))  # Inverted
        wind_norm = (wind_speed - wind_speed.min()) / (wind_speed.max() - wind_speed.min())
        precip_norm = 1 - ((precipitation - precipitation.min()) / (precipitation.max() - precipitation.min()))  # Inverted
        
        # Weighted combination
        fwi = (
            self.fwi_params['temperature_weight'] * temp_norm +
            self.fwi_params['humidity_weight'] * hum_norm +
            self.fwi_params['wind_weight'] * wind_norm +
            self.fwi_params['precipitation_weight'] * precip_norm
        )
        
        logger.info(f"FWI calculated - Mean: {fwi.mean():.3f}, Max: {fwi.max():.3f}")
        
        return fwi
    
    def calculate_scvr(
        self,
        future_data: pd.DataFrame,
        baseline_data: pd.DataFrame,
        variable: str
    ) -> float:
        """
        Calculate SCVR (Severe Climate Variability Rating).
        
        SCVR measures the increase in area under the exceedance curve
        for extreme events, quantifying the change in climate variability.
        
        Args:
            future_data: Future climate scenario data
            baseline_data: Historical baseline data
            variable: Climate variable name
        
        Returns:
            SCVR value (ratio of future to baseline exceedance area)
        """
        # Calculate exceedance curves
        future_sorted = np.sort(future_data)[::-1]  # Descending order
        baseline_sorted = np.sort(baseline_data)[::-1]
        
        # Normalize to same length for comparison
        n_points = min(len(future_sorted), len(baseline_sorted))
        future_sorted = future_sorted[:n_points]
        baseline_sorted = baseline_sorted[:n_points]
        
        # Calculate area under exceedance curves (using trapezoidal rule)
        exceedance_probs = np.linspace(0, 1, n_points)
        # trapezoid is the modern name; trapz was removed in NumPy 2.0
        _trapz = getattr(np, "trapezoid", getattr(np, "trapz", None))
        if _trapz is None:
            raise RuntimeError("NumPy trapezoid or trapz required; upgrade numpy.")
        area_future = _trapz(future_sorted, exceedance_probs)
        area_baseline = _trapz(baseline_sorted, exceedance_probs)
        
        # SCVR is the ratio of areas
        if area_baseline > 0:
            scvr = area_future / area_baseline
        else:
            scvr = 1.0
        
        logger.info(f"SCVR for {variable}: {scvr:.3f}")
        
        return scvr
    
    def _find_consecutive_events(
        self,
        condition: pd.Series,
        dates: pd.Series,
        min_length: int = 3
    ) -> pd.DataFrame:
        """
        Helper function to find consecutive events meeting a condition.
        
        Args:
            condition: Boolean series indicating condition met
            dates: Date series
            min_length: Minimum consecutive days to count as event
        
        Returns:
            DataFrame with event start dates, end dates, and duration
        """
        # Identify sequences
        condition_int = condition.astype(int)
        groups = (condition_int != condition_int.shift()).cumsum()
        
        events_list = []
        for group_id, group_data in condition.groupby(groups):
            if group_data.iloc[0]:  # Only positive events
                duration = len(group_data)
                if duration >= min_length:
                    start_idx = group_data.index[0]
                    end_idx = group_data.index[-1]
                    events_list.append({
                        'start_date': dates.iloc[start_idx],
                        'end_date': dates.iloc[end_idx],
                        'duration': duration
                    })
        
        return pd.DataFrame(events_list)
    
    def generate_scvr_tables(
        self,
        climate_data: pd.DataFrame,
        baseline_data: pd.DataFrame,
        scenarios: List[str],
        years: List[int]
    ) -> pd.DataFrame:
        """
        Generate complete SCVR tables for all scenarios and years.
        
        Args:
            climate_data: Combined climate projection data
            baseline_data: Historical baseline data
            scenarios: List of scenarios to analyze
            years: List of years to calculate SCVR
        
        Returns:
            DataFrame with SCVR values by scenario, year, and variable
        """
        logger.info("Generating SCVR tables for all scenarios and years")
        
        scvr_results = []
        
        for scenario in scenarios:
            scenario_data = climate_data[climate_data['scenario'] == scenario]
            
            for year in years:
                year_data = scenario_data[scenario_data['year'] == year]
                
                # Calculate SCVR for each climate variable
                for variable in year_data['variable'].unique():
                    var_future = year_data[year_data['variable'] == variable]['value']
                    var_baseline = baseline_data[baseline_data['variable'] == variable]['value']
                    
                    scvr = self.calculate_scvr(var_future, var_baseline, variable)
                    
                    scvr_results.append({
                        'scenario': scenario,
                        'year': year,
                        'variable': variable,
                        'scvr': scvr
                    })
        
        scvr_df = pd.DataFrame(scvr_results)
        
        logger.info(f"Generated SCVR table with {len(scvr_df)} entries")
        
        return scvr_df


def main():
    """
    Test the SCVR calculator.
    """
    from config.config import SCVR_THRESHOLDS, FWI_PARAMS
    
    config = {
        'SCVR_THRESHOLDS': SCVR_THRESHOLDS,
        'FWI_PARAMS': FWI_PARAMS
    }
    
    calculator = SCVRCalculator(config)
    
    # Generate synthetic test data
    n_days = 365 * 5
    dates = pd.date_range('2025-01-01', periods=n_days, freq='D')
    
    tmax = 25 + 10 * np.sin(2 * np.pi * np.arange(n_days) / 365) + np.random.normal(0, 3, n_days)
    tmin = 15 + 8 * np.sin(2 * np.pi * np.arange(n_days) / 365) + np.random.normal(0, 2, n_days)
    precip = np.maximum(0, 2 + np.random.gamma(2, 1, n_days))
    wind = np.maximum(0, 5 + np.random.normal(0, 1.5, n_days))
    humidity = np.clip(60 + 15 * np.sin(2 * np.pi * np.arange(n_days) / 365) + np.random.normal(0, 10, n_days), 0, 100)
    
    # Historical baseline
    tmax_baseline = 23 + 9 * np.sin(2 * np.pi * np.arange(n_days) / 365) + np.random.normal(0, 2.5, n_days)
    tmin_baseline = 13 + 7 * np.sin(2 * np.pi * np.arange(n_days) / 365) + np.random.normal(0, 2, n_days)
    
    # Test calculations
    n_heat_waves, hw_events = calculator.calculate_heat_waves(tmax, tmin, dates, tmax_baseline, tmin_baseline)
    print(f"Heat waves: {n_heat_waves}")
    
    freeze_metrics = calculator.calculate_freeze_events(tmax, tmin, dates)
    print(f"Freeze events: {freeze_metrics}")
    
    precip_metrics = calculator.calculate_extreme_precipitation(precip, dates)
    print(f"Extreme precipitation: {precip_metrics}")
    
    fwi = calculator.calculate_fire_weather_index(tmax, humidity, wind, precip)
    print(f"FWI range: {fwi.min():.3f} - {fwi.max():.3f}")


if __name__ == "__main__":
    main()
