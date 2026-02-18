"""
Main Orchestration Script for Climate Risk Assessment Framework

This script executes the complete 3-week analysis workflow:
- Week 1: Climate data acquisition and SCVR calculation
- Week 2: Asset performance and risk modeling
- Week 3: Equipment degradation and NAV analysis

Usage:
    python main.py --asset hayhurst_solar --scenario rcp45
    python main.py --asset maverick_wind --scenario rcp85 --monte-carlo

Author: Climate Risk Assessment Team
Date: 2025
"""

import argparse
import gc
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Import configuration
from config.config import *

# Import modules
from modules.step1_data_acquisition import CMIP6DataAcquisition
from modules.step1b_scvr_calculation import SCVRCalculator
from modules.step2_asset_performance import AssetPerformanceModel
from modules.step3_4_5_integrated import (
    BusinessInterruptionModel,
    EquipmentDegradationModel,
    NAVCalculator
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGGING['file']),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ClimateRiskFramework:
    """
    Main orchestrator for climate risk assessment workflow.
    """
    
    def __init__(self, asset_id: str, scenario: str):
        """
        Initialize framework.
        
        Args:
            asset_id: Asset identifier (e.g., 'hayhurst_solar')
            scenario: Climate scenario (e.g., 'rcp45', 'rcp85')
        """
        self.asset_id = asset_id
        self.scenario = scenario
        self.asset = ASSETS[asset_id]
        
        # Initialize all modules
        self.data_acquisition = CMIP6DataAcquisition({
            'DATA_DIR': DATA_DIR,
            'WORLD_BANK_API': WORLD_BANK_API,
            'NOAA_STATIONS': NOAA_STATIONS
        })
        
        self.scvr_calculator = SCVRCalculator({
            'SCVR_THRESHOLDS': SCVR_THRESHOLDS,
            'FWI_PARAMS': FWI_PARAMS
        })
        
        self.performance_model = AssetPerformanceModel({
            'ASSETS': ASSETS,
            'INFRASURE_CONFIG': INFRASURE_CONFIG,
            'SOLAR_DEGRADATION': SOLAR_DEGRADATION,
            'WIND_DEGRADATION': WIND_DEGRADATION
        })
        
        self.bi_model = BusinessInterruptionModel({
            'HCR_BASE': HCR_BASE,
            'CATASTROPHIC_EVENTS': CATASTROPHIC_EVENTS,
            'INFRASURE_CONFIG': INFRASURE_CONFIG
        })
        
        self.degradation_model = EquipmentDegradationModel({
            'SOLAR_DEGRADATION': SOLAR_DEGRADATION,
            'WIND_DEGRADATION': WIND_DEGRADATION
        })
        
        self.nav_calculator = NAVCalculator({
            'WACC_BASE': WACC_BASE,
            'MONTE_CARLO': MONTE_CARLO
        })
        
        logger.info(f"Framework initialized for {asset_id}, scenario: {scenario}")
    
    def run_week1_climate_analysis(self):
        """
        WEEK 1: Climate Data & Variability Analysis
        """
        logger.info("="*60)
        logger.info("WEEK 1: Climate Data & Variability Analysis")
        logger.info("="*60)
        
        lat = self.asset['location']['latitude']
        lon = self.asset['location']['longitude']
        
        # Step 1A: Acquire CMIP6 data
        logger.info("Step 1A: Acquiring CMIP6 data...")
        
        climate_vars = ['tas', 'tasmax', 'tasmin', 'pr', 'sfcWind', 'hurs']
        climate_data_list = []
        
        for var in climate_vars:
            data = self.data_acquisition.fetch_cmip6_data(
                scenario=self.scenario,
                variable=var,
                latitude=lat,
                longitude=lon,
                start_year=ANALYSIS_START_YEAR,
                end_year=ANALYSIS_END_YEAR
            )
            climate_data_list.append(data)
        
        climate_data = pd.concat(climate_data_list, ignore_index=True)
        
        # Fetch NOAA validation data
        station_key = 'culberson' if 'solar' in self.asset_id else 'concho'
        station_id = NOAA_STATIONS[station_key]['station_id']
        
        noaa_data = self.data_acquisition.fetch_noaa_validation_data(
            station_id=station_id,
            start_year=HISTORICAL_START_YEAR,
            end_year=HISTORICAL_END_YEAR
        )
        
        # Validate
        validation_metrics = self.data_acquisition.validate_climate_data(
            cmip6_data=climate_data,
            noaa_data=noaa_data,
            variable_mapping={
                'tasmax': 'tmax',
                'tasmin': 'tmin',
                'pr': 'precipitation'
            }
        )
        
        # Step 1B: Calculate SCVR
        logger.info("Step 1B: Calculating SCVR...")
        
        # Convert NOAA data (wide: tmax, tmin, etc.) to long format with 'variable' and 'value'
        # so it matches what generate_scvr_tables expects (same variable names as CMIP6).
        noaa_to_cmip6 = {
            'tmax': 'tasmax',
            'tmin': 'tasmin',
            'precipitation': 'pr',
            'wind_speed': 'sfcWind',
        }
        baseline_list = []
        for noaa_col, cmip6_var in noaa_to_cmip6.items():
            if noaa_col in noaa_data.columns:
                baseline_list.append(noaa_data[['date', 'year']].assign(
                    variable=cmip6_var,
                    value=noaa_data[noaa_col].values
                ))
        if 'tmax' in noaa_data.columns and 'tmin' in noaa_data.columns:
            baseline_list.append(noaa_data[['date', 'year']].assign(
                variable='tas',
                value=((noaa_data['tmax'] + noaa_data['tmin']) / 2).values
            ))
        # Placeholder for hurs (NOAA often has no humidity); use constant 60
        baseline_list.append(noaa_data[['date', 'year']].assign(
            variable='hurs',
            value=60.0
        ))
        baseline_data = pd.concat(baseline_list, ignore_index=True)
        
        scvr_table = self.scvr_calculator.generate_scvr_tables(
            climate_data=climate_data,
            baseline_data=baseline_data,
            scenarios=[self.scenario],
            years=list(range(ANALYSIS_START_YEAR, ANALYSIS_END_YEAR + 1))
        )
        
        # Save results
        scvr_table.to_csv(OUTPUT_DIR / f'{self.asset_id}_{self.scenario}_scvr.csv', index=False)
        
        logger.info(f"Week 1 complete. SCVR table saved with {len(scvr_table)} entries")
        
        # Free large intermediates to lower RAM spike (helps avoid Colab killing the run)
        del climate_data_list, noaa_data, baseline_data, baseline_list
        gc.collect()
        return climate_data, scvr_table
    
    def run_week2_performance_modeling(self, climate_data, scvr_table):
        """
        WEEK 2: Asset Performance & Risk Modeling
        """
        logger.info("="*60)
        logger.info("WEEK 2: Asset Performance & Risk Modeling")
        logger.info("="*60)
        
        # Step 2: Asset Performance
        logger.info("Step 2: Modeling asset performance...")
        
        performance = self.performance_model.call_infrasure_performance(
            asset_id=self.asset_id,
            climate_data=climate_data,
            scenario=self.scenario
        )
        
        # Apply climate zone factors
        performance_adjusted = self.performance_model.apply_climate_zone_factors(
            performance=performance,
            asset_id=self.asset_id,
            scvr_data=scvr_table
        )
        
        # Calculate revenue
        revenue = self.performance_model.calculate_revenue_projections(
            generation=performance_adjusted,
            ppa_price_mwh=50.0
        )
        
        # Step 3: Business Interruption
        logger.info("Step 3: Calculating business interruption...")
        
        # Develop HCR tables
        hcr_table = self.bi_model.develop_hcr_tables(scvr_table)
        
        # Get InfraSure BI estimates
        infrasure_bi = self.bi_model.call_infrasure_bi(
            asset_id=self.asset_id,
            scenario=self.scenario
        )
        
        # Calculate BI losses
        bi_losses = self.bi_model.calculate_bi_losses(
            infrasure_bi=infrasure_bi,
            hcr_table=hcr_table
        )
        
        # Model catastrophic events
        cat_losses = self.bi_model.model_catastrophic_events(scvr_table)
        
        # Save results
        revenue.to_csv(OUTPUT_DIR / f'{self.asset_id}_{self.scenario}_revenue.csv', index=False)
        bi_losses.to_csv(OUTPUT_DIR / f'{self.asset_id}_{self.scenario}_bi_losses.csv', index=False)
        
        logger.info("Week 2 complete. Performance and BI models executed")
        
        return revenue, bi_losses, cat_losses
    
    def run_week3_degradation_nav(self, revenue, bi_losses, cat_losses, scvr_table):
        """
        WEEK 3: Equipment Degradation & NAV Analysis
        """
        logger.info("="*60)
        logger.info("WEEK 3: Equipment Degradation & NAV Analysis")
        logger.info("="*60)
        
        # Step 4: Equipment Degradation
        logger.info("Step 4: Modeling equipment degradation...")
        
        asset_type = self.asset['type']
        
        # Develop EFR tables
        efr_table = self.degradation_model.develop_efr_tables(
            scvr_data=scvr_table,
            asset_type=asset_type
        )
        
        # Calculate degradation losses
        degradation_losses = self.degradation_model.calculate_degradation_losses(
            revenue_base=revenue,
            efr_table=efr_table
        )
        
        # Calculate IUL
        eul = self.asset['eul_years']
        iul = self.degradation_model.calculate_impaired_useful_life(
            eul=eul,
            efr_table=efr_table,
            cat_damage_factor=0.05  # 5% from catastrophic events
        )
        
        # Step 5: NAV Calculation
        logger.info("Step 5: Calculating NAV impairment...")
        
        # Calculate climate-adjusted asset performance
        ap_climate = self.nav_calculator.calculate_asset_performance_climate(
            revenue_base=revenue,
            bi_losses=bi_losses,
            cat_losses=cat_losses,
            degradation_losses=degradation_losses
        )
        
        # Calculate NPVs
        # Base scenario (first IUL years)
        revenue_base = revenue[revenue['year'] <= (ANALYSIS_START_YEAR + eul - 1)]
        npv_base = self.nav_calculator.calculate_npv(
            cash_flows=revenue_base['revenue_usd']
        )
        
        # Climate scenario (first IUL years)
        ap_climate_subset = ap_climate[ap_climate['year'] <= (ANALYSIS_START_YEAR + iul - 1)]
        npv_climate = self.nav_calculator.calculate_npv(
            cash_flows=ap_climate_subset['asset_performance_climate']
        )
        
        # Calculate NAV Impairment Ratio
        nav_ratio = self.nav_calculator.calculate_nav_impairment_ratio(
            npv_climate=npv_climate,
            npv_base=npv_base
        )
        
        # Run Monte Carlo
        logger.info("Running Monte Carlo simulations...")
        mc_results = self.nav_calculator.run_monte_carlo(
            base_scenario={
                'npv_base': npv_base,
                'npv_climate': npv_climate
            }
        )
        
        # Calculate confidence intervals
        p10 = mc_results['nav_ratio'].quantile(0.10)
        p50 = mc_results['nav_ratio'].quantile(0.50)
        p90 = mc_results['nav_ratio'].quantile(0.90)
        
        # Compile final results
        final_results = {
            'asset_id': self.asset_id,
            'scenario': self.scenario,
            'eul_years': eul,
            'iul_years': iul,
            'npv_base': npv_base,
            'npv_climate': npv_climate,
            'nav_impairment_ratio': nav_ratio,
            'nav_ratio_p10': p10,
            'nav_ratio_p50': p50,
            'nav_ratio_p90': p90
        }
        
        # Save results
        results_df = pd.DataFrame([final_results])
        results_df.to_csv(OUTPUT_DIR / f'{self.asset_id}_{self.scenario}_final_results.csv', index=False)
        mc_results.to_csv(OUTPUT_DIR / f'{self.asset_id}_{self.scenario}_monte_carlo.csv', index=False)
        
        logger.info("Week 3 complete. NAV impairment analysis finished")
        logger.info(f"NAV Impairment Ratio: {nav_ratio:.4f} (P10: {p10:.4f}, P50: {p50:.4f}, P90: {p90:.4f})")
        
        return final_results, mc_results
    
    def execute_full_analysis(self):
        """
        Execute complete 3-week framework analysis.
        """
        start_time = datetime.now()
        logger.info("="*60)
        logger.info(f"Starting Climate Risk Assessment: {self.asset_id}, {self.scenario}")
        logger.info(f"Start time: {start_time}")
        logger.info("="*60)
        
        # Week 1
        climate_data, scvr_table = self.run_week1_climate_analysis()
        
        # Week 2
        revenue, bi_losses, cat_losses = self.run_week2_performance_modeling(
            climate_data, scvr_table
        )
        # Free Week 1 data before Week 3 (Monte Carlo) to reduce peak RAM
        del climate_data
        gc.collect()
        
        # Week 3
        final_results, mc_results = self.run_week3_degradation_nav(
            revenue, bi_losses, cat_losses, scvr_table
        )
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info("="*60)
        logger.info("ANALYSIS COMPLETE")
        logger.info(f"Duration: {duration}")
        logger.info(f"Results saved to: {OUTPUT_DIR}")
        logger.info("="*60)
        
        return final_results


def main():
    """
    Command-line interface for framework execution.
    """
    parser = argparse.ArgumentParser(
        description='Climate Risk Assessment Framework'
    )
    
    parser.add_argument(
        '--asset',
        type=str,
        required=True,
        choices=['hayhurst_solar', 'maverick_wind'],
        help='Asset to analyze'
    )
    
    parser.add_argument(
        '--scenario',
        type=str,
        required=True,
        choices=['rcp45', 'rcp85'],
        help='Climate scenario'
    )
    
    parser.add_argument(
        '--monte-carlo',
        action='store_true',
        help='Run Monte Carlo simulations'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Only WARNING+ to console (reduces output; full log still written to file). Use in Colab to avoid timeout from huge log output.'
    )
    
    args = parser.parse_args()
    
    if args.quiet:
        for h in logging.root.handlers:
            if isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler):
                h.setLevel(logging.WARNING)
    
    # Execute framework
    framework = ClimateRiskFramework(
        asset_id=args.asset,
        scenario=args.scenario
    )
    
    results = framework.execute_full_analysis()
    
    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    for key, value in results.items():
        if isinstance(value, float):
            print(f"{key:30s}: {value:10.4f}")
        else:
            print(f"{key:30s}: {value}")
    print("="*60)


if __name__ == "__main__":
    main()
