#Import 
import numpy as np
import scipy.stats as stats
import scipy as sp
import scipy.optimize as opt
import B_mainclass as form
import C_Input_AHG as inp
import D_Preprocessing as prep
import swe as meas
from municipalities import municipalities_data
from elevation import get_elevations
from statistics import mean
from math import ceil
from A_funcstat import get_values
from scipy.stats import gumbel_r



input_data = {

    #Period

    "tot": {"period": (1960, 2024), "scenario": None},
    "new": {"period": (1991, 2024),"scenario": None},
    "old": {"period": (1960, 1990),"scenario": None},
    "future_rcp45": {"period": (2024, 2074),"scenario": "rcp45"},
    "future_rcp85": {"period": (2024, 2074),"scenario": "rcp85"},

    #Variable

    "beta": {"limits": (3,6),"label": "Reliability Index ($\\beta$)", "title": "Municipalities Colored by Reliability Index ($\\beta$)"},
    "char": {"limits": (0, 10),"label": "Characteristic Value", "title": "Municipalities Colored by Characteristic Value"},
    "CoV": {"limits": (0,1),"label": "Coefficient of Variance", "title": "Municipalities Colored by Coefficient of Variance"},

}

# The normalized FORM algorythm used in the project assignment. The characteristic value is calculated from the directory/csv file. The elevation chosen is the average of all the elevations
# from elevation_samples.py. The form is done by calculating the CoV from the data. However, it doesn't make sense to normalize when the absolute value of the data is relevant? 
# I also have trouble normalizing the characteristic value. a_q and a_g is chosen arbitrarily. 



def char(name):
    
    sk_0=municipalities_data[name]['sk_0']
    hg=municipalities_data[name]['hg']
    dsk=municipalities_data[name]['dsk']
    sk_maks=municipalities_data[name]['sk_maks']
    
    elevation=mean(get_values('C:/Users/hakon/SnowAnalysis_HU/stored_data/elevation.csv',name, 'elevation'))

    n=max(ceil((elevation-hg)/100), 0)

    if sk_maks==None:
        sk=sk_0+dsk*n
    
    else:
        sk=min(sk_0+dsk*n, sk_maks)



    return sk

def char_actual(name):
    snow_maxima=get_values(f'C:/Users/hakon/SnowAnalysis_HU/stored_data/swe_tot.csv', name, 'swe')
    loc_, scale_ = stats.gumbel_r.fit(snow_maxima)
    x_k = gumbel_r.ppf(0.98, loc=loc_, scale=scale_)
    return x_k*9.8*2/1000 # Converting mm to kN/m

def prop(name, time):
    snow_maxima=get_values(f'C:/Users/hakon/SnowAnalysis_HU/stored_data/swe_{time}.csv', name, 'swe')

    if np.sum(snow_maxima)<10:
        loc, scale = 0.01, 0.01
    else:
        loc, scale = stats.gumbel_r.fit(snow_maxima)

    gamma = 0.57722  

    # Compute mean and standard deviation
    mean_gumbel = loc + gamma * scale
    std_gumbel = (np.pi / np.sqrt(6)) * scale
    mean_snow_=mean_gumbel*9.8*2/1000 # Converting mm to kN/m

    # Compute CoV
    cov_snow = std_gumbel / mean_gumbel
    
    return mean_snow_, cov_snow

def municipality_form(name, time, char_assigned=None):   #Calculate beta

    

    mean_snow_, cov_snow = prop(name, time)
    
    if char_assigned == None:
        char_=char(name)*2
    else:
        char_=char_assigned
    #mean_snow_,cov_snow,char_ = 0.0001,0.0001,0.001  
    X = prep.RandomVariablesAux(mean_snow_, cov_snow, char_)


    g_ = inp.StartValues()
    aqq=0.9
    agg=0.1
    deq=1

    P_= X['Y32']                # Permanent load                                                
    XX_ = X['Y11']              # Load effect model uncertainty
    Q_ = X['Z2']                # Variable load 
    XQ_ = X[X['Z2']['MUV']]     #
    XR_= X['X11']               # Resistance model uncertainty
    R_ = X[X['X11']['RV']]      # Material property
    G_ = X[X['X11']['GV']]      # Self weight

    zet = form.ZBETA(ag=agg, aq=aqq, XR=XR_, R=R_, XX=XX_, G=G_, P=P_, XQ=XQ_, Q=Q_, g=g_, d=deq)
    z=zet.__zeta__()                    #find design variable z per single case
    BETA,ALPHA = zet.f1(z)              #find the corresponding beta index and the alpha values

    #Calculate reliaiblity index with Monte Carlo instead of FORM
    #BETA = 1
    if BETA==1:

        BETA_mcs=zet.mcstest(z)
        if BETA_mcs > 100:
            return 12, ALPHA
        
        else:

            return BETA_mcs, ALPHA


    return BETA,ALPHA



def calibration(name, time, beta_target):
    """
    Iterates through three bounded regions (0-9, 9-18, 18-27) and finds the 
    characteristic value where the beta value is within the target range.
    """

    beta_target_range=(beta_target-0.1, beta_target+0.1)

    


    def func_opt(char_opt):
        beta, _ = municipality_form(name, time, char_opt)
        return np.abs(beta - np.mean(beta_target_range))  # Optimize to the center of the target range

    # Define boundaries to iterate over
    bounds_list = [(0, 5.1), (5, 10.1), (10, 18.1), (18, 27),(26,40)]


    for bnds in bounds_list:
        res = opt.minimize_scalar(func_opt, bounds=bnds, method='bounded')
        optimal_char = res.x
        optimal_beta, _ = municipality_form(name, time, optimal_char)

        # Check if the beta is within the target range
        if beta_target_range[0] <= optimal_beta <= beta_target_range[1]:
            return optimal_char, optimal_beta

    return "Error", "Error"


run=0

if run ==1:

    municiaplities=["Evenes", "Skjervøy", "Jølster", "Nordkapp"]


    for municipality in municiaplities:
        BETA_, ALPHA_=municipality_form(municipality, "tot", None)
        print(municipality,",",BETA_)


