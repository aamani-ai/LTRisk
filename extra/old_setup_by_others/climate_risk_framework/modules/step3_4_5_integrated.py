"""
STEPS 3-5: Business Interruption, Equipment Degradation, and NAV Calculation

This module contains the core financial impact calculations:
- Step 3: Business Interruption losses with HCR tables
- Step 4: Equipment degradation modeling with EFR tables  
- Step 5: NAV impairment calculation and uncertainty quantification

Author: Climate Risk Assessment Team
Date: 2025
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from scipy import stats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================================================================
# STEP 3: BUSINESS INTERRUPTION MODULE
# ==================================================================

class BusinessInterruptionModel:
    """
    Calculates business interruption losses using HCR tables.
    
    BI_loss = InfraSure_BI × HCR
    (InfraSure BI already scaled by SCVR)
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.hcr_base = config['HCR_BASE']
        self.cat_events = config['CATASTROPHIC_EVENTS']
        logger.info("Business Interruption Model initialized")
    
    def develop_hcr_tables(self, scvr_data: pd.DataFrame) -> pd.DataFrame:
        """
        Develop Hazard Change Ratio tables from SCVR values.
        
        HCR quantifies % increase in hazard frequency/severity as function of SCVR.
        """
        logger.info("Developing HCR tables")
        
        hcr_results = []
        
        for hazard, params in self.hcr_base.items():
            for _, row in scvr_data.iterrows():
                year = row['year']
                scenario = row['scenario']
                
                # Map SCVR dependencies to HCR
                hcr_value = 1.0  # Base multiplier
                
                for scvr_var in params['scvr_dependency']:
                    scvr_val = row.get(f'{scvr_var}_scvr', 1.0)
                    hcr_value *= scvr_val
                
                hcr_results.append({
                    'year': year,
                    'scenario': scenario,
                    'hazard': hazard,
                    'hcr': hcr_value,
                    'impact_level': params['impact_level']
                })
        
        return pd.DataFrame(hcr_results)
    
    def call_infrasure_bi(self, asset_id: str, scenario: str) -> pd.DataFrame:
        """
        Call InfraSure Business Interruption model.
        
        **PLACEHOLDER**: Replace with actual InfraSure BI function.
        
        Returns BI estimates already scaled by SCVR.
        """
        logger.warning("Using placeholder BI model - replace with InfraSure call")
        
        # Simulate BI estimates
        years = range(2025, 2051)
        bi_data = []
        
        for year in years:
            bi_data.append({
                'year': year,
                'asset_id': asset_id,
                'scenario': scenario,
                'bi_base_loss_mwh': np.random.uniform(100, 500)  # MWh lost
            })
        
        return pd.DataFrame(bi_data)
    
    def calculate_bi_losses(
        self,
        infrasure_bi: pd.DataFrame,
        hcr_table: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calculate total BI losses: BI_loss = InfraSure_BI × HCR
        """
        logger.info("Calculating BI losses")
        
        # Merge BI with HCR
        bi_losses = []
        
        for hazard in hcr_table['hazard'].unique():
            hazard_hcr = hcr_table[hcr_table['hazard'] == hazard]
            
            merged = pd.merge(
                infrasure_bi,
                hazard_hcr[['year', 'scenario', 'hcr']],
                on=['year', 'scenario'],
                how='left'
            )
            
            merged['hazard'] = hazard
            merged['bi_loss_mwh'] = merged['bi_base_loss_mwh'] * merged['hcr']
            
            bi_losses.append(merged)
        
        bi_df = pd.concat(bi_losses, ignore_index=True)
        
        # Sum across hazards
        total_bi = bi_df.groupby(['year', 'scenario', 'asset_id'])['bi_loss_mwh'].sum().reset_index()
        total_bi.rename(columns={'bi_loss_mwh': 'total_bi_loss_mwh'}, inplace=True)
        
        return total_bi
    
    def model_catastrophic_events(self, scvr_data: pd.DataFrame) -> pd.DataFrame:
        """
        Model catastrophic event losses (simplified methodology).
        """
        logger.info("Modeling catastrophic events")
        
        cat_losses = []
        
        for _, row in scvr_data.iterrows():
            year = row['year']
            scenario = row['scenario']
            
            # Hurricane
            wind_scvr = row.get('wind_scvr', 1.0)
            hurricane_freq = self.cat_events['hurricane']['historical_frequency_per_year'] * wind_scvr
            hurricane_loss = np.random.binomial(1, hurricane_freq) * np.random.uniform(5000, 10000)
            
            # Ice storm
            cold_scvr = row.get('cold_wave_scvr', 1.0)
            ice_freq = self.cat_events['extreme_ice_storm']['historical_frequency_per_year'] * cold_scvr
            ice_loss = np.random.binomial(1, ice_freq) * np.random.uniform(8000, 15000)
            
            cat_losses.append({
                'year': year,
                'scenario': scenario,
                'hurricane_loss_mwh': hurricane_loss,
                'ice_storm_loss_mwh': ice_loss,
                'total_cat_loss_mwh': hurricane_loss + ice_loss
            })
        
        return pd.DataFrame(cat_losses)


# ==================================================================
# STEP 4: EQUIPMENT DEGRADATION MODULE
# ==================================================================

class EquipmentDegradationModel:
    """
    Models equipment degradation and useful life impairment.
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.solar_params = config['SOLAR_DEGRADATION']
        self.wind_params = config['WIND_DEGRADATION']
        logger.info("Equipment Degradation Model initialized")
    
    def develop_efr_tables(
        self,
        scvr_data: pd.DataFrame,
        asset_type: str
    ) -> pd.DataFrame:
        """
        Develop Equipment Failure Ratio tables.
        """
        logger.info(f"Developing EFR tables for {asset_type}")
        
        efr_results = []
        
        for _, row in scvr_data.iterrows():
            year = row['year']
            scenario = row['scenario']
            
            if asset_type == 'solar_pv':
                # Temperature degradation
                heat_scvr = row.get('heat_wave_scvr', 1.0)
                temp_efr = 0.005 * (heat_scvr - 1)  # 0.5% per unit SCVR
                
                # UV degradation (climate zone dependent)
                uv_efr = 0.002  # Base rate
                
                # Soiling
                dry_spell_scvr = row.get('dry_spell_scvr', 1.0)
                soiling_efr = 0.003 * dry_spell_scvr
                
                total_efr = temp_efr + uv_efr + soiling_efr
                
            elif asset_type == 'wind_turbine':
                # Icing
                freeze_scvr = row.get('freeze_scvr', 1.0)
                icing_efr = 0.004 * (freeze_scvr - 1)
                
                # Blade erosion
                erosion_efr = 0.0035  # ~7% over 20 years
                
                # Fatigue
                wind_scvr = row.get('wind_scvr', 1.0)
                fatigue_efr = 0.002 * wind_scvr
                
                total_efr = icing_efr + erosion_efr + fatigue_efr
            
            else:
                total_efr = 0.0
            
            efr_results.append({
                'year': year,
                'scenario': scenario,
                'asset_type': asset_type,
                'total_efr': total_efr
            })
        
        return pd.DataFrame(efr_results)
    
    def calculate_degradation_losses(
        self,
        revenue_base: pd.DataFrame,
        efr_table: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calculate revenue losses from equipment degradation.
        """
        logger.info("Calculating degradation losses")
        
        merged = pd.merge(
            revenue_base,
            efr_table[['year', 'scenario', 'total_efr']],
            on=['year', 'scenario'],
            how='left'
        )
        
        # Cumulative degradation over time
        merged = merged.sort_values('year')
        merged['cumulative_efr'] = merged.groupby('scenario')['total_efr'].cumsum()
        
        # Degradation loss
        merged['degradation_loss_revenue'] = merged['revenue_usd'] * merged['cumulative_efr']
        
        return merged
    
    def calculate_impaired_useful_life(
        self,
        eul: int,
        efr_table: pd.DataFrame,
        cat_damage_factor: float = 0.0
    ) -> int:
        """
        Calculate Impaired Useful Life (IUL).
        
        IUL = EUL × [1 - Σ(EFR_i × SCVR_i)] × [1 - Cat_Damage_Factor]
        """
        logger.info("Calculating Impaired Useful Life")
        
        # Average EFR across analysis period
        avg_efr = efr_table['total_efr'].mean()
        
        # Apply formula
        iul = eul * (1 - avg_efr) * (1 - cat_damage_factor)
        iul = int(np.round(iul))
        
        logger.info(f"EUL: {eul} years → IUL: {iul} years")
        
        return iul


# ==================================================================
# STEP 5: NAV IMPAIRMENT CALCULATION MODULE
# ==================================================================

class NAVCalculator:
    """
    Calculates Net Asset Value impairment ratios.
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.wacc = config['WACC_BASE']
        self.mc_config = config['MONTE_CARLO']
        logger.info("NAV Calculator initialized")
    
    def calculate_asset_performance_climate(
        self,
        revenue_base: pd.DataFrame,
        bi_losses: pd.DataFrame,
        cat_losses: pd.DataFrame,
        degradation_losses: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calculate: AP = Revenue_base - BI_loss - Cat_loss - Degradation_loss
        """
        logger.info("Calculating climate-adjusted asset performance")
        
        # Merge all components
        ap = revenue_base.copy()
        
        ap = pd.merge(ap, bi_losses[['year', 'scenario', 'total_bi_loss_mwh']],
                     on=['year', 'scenario'], how='left')
        ap = pd.merge(ap, cat_losses[['year', 'scenario', 'total_cat_loss_mwh']],
                     on=['year', 'scenario'], how='left')
        ap = pd.merge(ap, degradation_losses[['year', 'scenario', 'degradation_loss_revenue']],
                     on=['year', 'scenario'], how='left')
        
        # Fill NaN with 0
        ap.fillna(0, inplace=True)
        
        # Convert MWh losses to revenue losses
        ap['bi_loss_revenue'] = ap['total_bi_loss_mwh'] * ap['ppa_price']
        ap['cat_loss_revenue'] = ap['total_cat_loss_mwh'] * ap['ppa_price']
        
        # Calculate net performance
        ap['asset_performance_climate'] = (
            ap['revenue_usd'] -
            ap['bi_loss_revenue'] -
            ap['cat_loss_revenue'] -
            ap['degradation_loss_revenue']
        )
        
        return ap
    
    def calculate_npv(
        self,
        cash_flows: pd.Series,
        discount_rate: float = None
    ) -> float:
        """
        Calculate Net Present Value.
        
        NPV = Σ [Cash_flow_t / (1+WACC)^t]
        """
        if discount_rate is None:
            discount_rate = self.wacc
        
        years = np.arange(len(cash_flows))
        discount_factors = 1 / (1 + discount_rate) ** years
        npv = (cash_flows * discount_factors).sum()
        
        return npv
    
    def calculate_nav_impairment_ratio(
        self,
        npv_climate: float,
        npv_base: float
    ) -> float:
        """
        Calculate: NAV Impairment Ratio = NPV_Climate / NPV_Base
        """
        if npv_base > 0:
            ratio = npv_climate / npv_base
        else:
            ratio = 0.0
        
        logger.info(f"NAV Impairment Ratio: {ratio:.4f}")
        
        return ratio
    
    def run_monte_carlo(
        self,
        base_scenario: Dict,
        n_iterations: int = None
    ) -> pd.DataFrame:
        """
        Run Monte Carlo simulations for uncertainty quantification.
        
        Varies:
        - HCR values (±20%)
        - EFR values (±15%)
        - Catastrophic event frequencies (±30%)
        """
        if n_iterations is None:
            n_iterations = self.mc_config['n_iterations']
        
        logger.info(f"Running Monte Carlo simulation: {n_iterations} iterations")
        
        np.random.seed(self.mc_config['random_seed'])
        
        results = []
        
        for i in range(n_iterations):
            # Sample parameter variations
            hcr_var = np.random.uniform(0.8, 1.2)  # ±20%
            efr_var = np.random.uniform(0.85, 1.15)  # ±15%
            cat_var = np.random.uniform(0.7, 1.3)  # ±30%
            
            # Recalculate with varied parameters
            # (Simplified - full implementation would re-run entire framework)
            
            npv_climate_varied = base_scenario['npv_climate'] * (
                hcr_var * 0.4 + efr_var * 0.3 + cat_var * 0.3
            )
            
            nav_ratio = npv_climate_varied / base_scenario['npv_base']
            
            results.append({
                'iteration': i,
                'hcr_variation': hcr_var,
                'efr_variation': efr_var,
                'cat_variation': cat_var,
                'npv_climate': npv_climate_varied,
                'nav_ratio': nav_ratio
            })
        
        mc_df = pd.DataFrame(results)
        
        # Calculate percentiles
        percentiles = self.mc_config['confidence_intervals']
        for p in percentiles:
            val = mc_df['nav_ratio'].quantile(p/100)
            logger.info(f"P{p}: {val:.4f}")
        
        return mc_df


def main():
    """Test integrated modules."""
    from config.config import (
        HCR_BASE, CATASTROPHIC_EVENTS,
        SOLAR_DEGRADATION, WIND_DEGRADATION,
        WACC_BASE, MONTE_CARLO
    )
    
    config = {
        'HCR_BASE': HCR_BASE,
        'CATASTROPHIC_EVENTS': CATASTROPHIC_EVENTS,
        'SOLAR_DEGRADATION': SOLAR_DEGRADATION,
        'WIND_DEGRADATION': WIND_DEGRADATION,
        'WACC_BASE': WACC_BASE,
        'MONTE_CARLO': MONTE_CARLO
    }
    
    # Test BI model
    bi_model = BusinessInterruptionModel(config)
    print("BI Model initialized")
    
    # Test Degradation model
    deg_model = EquipmentDegradationModel(config)
    print("Degradation Model initialized")
    
    # Test NAV calculator
    nav_calc = NAVCalculator(config)
    print("NAV Calculator initialized")


if __name__ == "__main__":
    main()
