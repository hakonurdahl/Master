import numpy as np
import scipy.stats as stats
import scipy.optimize as opt

import B_mainclass as form
import C_Input_AHG as inp
import D_Preprocessing as prep
import measurements as meas
from municipalities import municipalities_data
from elevation import get_elevations
from statistics import mean
from math import ceil
from A_funcstat import get_values


def calibration(name, beta_target):
    """
    Iterates through three bounded regions (0-9, 9-18, 18-27) and finds the 
    characteristic value where the beta value is within the target range.
    """

    beta_target_range=(beta_target-0.01, beta_target+0.01)

    def municipality_form_opt(name, char):  # Calculate beta
        snow_maxima = get_values('C:/Users/hakon/SnowAnalysis_JK/stored_data/municipalities_data_swe_tot.csv', name, 'SWE')
        
        if np.isnan(snow_maxima[0]):
            return np.nan, np.nan
        
        loc, scale = stats.gumbel_r.fit(snow_maxima)
        gamma = 0.57722  
        
        mean_gumbel = loc + gamma * scale
        std_gumbel = (np.pi / np.sqrt(6)) * scale
        mean_snow_ = mean_gumbel * 9.8 * 2 / 1000  # Convert mm to kN/m
        cov_snow = std_gumbel / mean_gumbel
        char_ = char * 2
        
        X = prep.RandomVariablesAux(mean_snow_, cov_snow, char_)
        g_ = inp.StartValues()
        aqq, agg, deq = 0.9, 0.1, 1
        
        P_, XX_, Q_ = X['Y31'], X['Y11'], X['Z2']
        XQ_, XR_, R_ = X[X['Z2']['MUV']], X['X11'], X[X['X11']['RV']]
        G_ = X[X['X11']['GV']]
        
        zet = form.ZBETA(ag=agg, aq=aqq, XR=XR_, R=R_, XX=XX_, G=G_, P=P_, XQ=XQ_, Q=Q_, g=g_, d=deq)
        z = zet.__zeta__()
        BETA, ALPHA = zet.f1(z)
        
        return BETA, ALPHA

    def func_opt(char):
        beta, _ = municipality_form_opt(name, char)
        return np.abs(beta - np.mean(beta_target_range))  # Optimize to the center of the target range

    # Define boundaries to iterate over
    bounds_list = [(0, 9), (9, 18), (18, 27)]

    for bnds in bounds_list:
        res = opt.minimize_scalar(func_opt, bounds=bnds, method='bounded')
        optimal_char = res.x
        optimal_beta, _ = municipality_form_opt(name, optimal_char)

        # Check if the beta is within the target range
        if beta_target_range[0] <= optimal_beta <= beta_target_range[1]:
            return optimal_char, optimal_beta

    # If no valid beta is found, return NaN
    return np.nan, np.nan

