#Import 
import numpy as np
import scipy.stats as stats

import B_mainclass as form
import C_Input_AHG as inp
import D_Preprocessing as prep
import measurements as meas
from municipalities import municipalities_data
from elevation import get_elevations
from statistics import mean
from math import ceil
from A_funcstat import get_values

# The normalized FORM algorythm used in the project assignment. The characteristic value is calculated from the directory/csv file. The elevation chosen is the average of all the elevations
# from elevation_samples.py. The form is done by calculating the CoV from the data. However, it doesn't make sense to normalize when the absolute value of the data is relevant? 
# I also have trouble normalizing the characteristic value. a_q and a_g is chosen arbitrarily. 


def char(name):
    
    sk_0=municipalities_data[name]['sk_0']
    hg=municipalities_data[name]['hg']
    dsk=municipalities_data[name]['dsk']
    sk_maks=municipalities_data[name]['sk_maks']
    latitude=municipalities_data[name]['coordinates']['latitude']
    longitude=municipalities_data[name]['coordinates']['longitude']
    
    elevation=mean(get_values('C:/Users/hakon/SnowAnalysis_JK/stored_data/municipalities_data_elevation.csv',name, 'Elevation'))
    

    n=max(ceil((elevation-hg)/100), 0)

    if sk_maks==None:
        sk=sk_0+dsk*n
    
    else:
        sk=min(sk_0+dsk*n, sk_maks)

    return sk



def municipality_form(name):   #Calculate beta


    snow_maxima=get_values('C:/Users/hakon/SnowAnalysis_JK/stored_data/municipalities_data_swe.csv', name, 'SWE')
    
    
    #If the coordinate is in the sea or lake, there will be no values.
    if np.isnan(snow_maxima[0]):
        return np.nan, np.nan
    
    
    
    loc, scale = stats.gumbel_r.fit(snow_maxima)

    gamma = 0.57722  

    # Compute mean and standard deviation
    mean_gumbel = loc + gamma * scale
    std_gumbel = (np.pi / np.sqrt(6)) * scale
    mean_snow_=mean_gumbel*9.8*2/100 # Converting mm to kN/m
    # Compute CoV
    cov_snow = std_gumbel / mean_gumbel

    char_=char(name)


    X = prep.RandomVariablesAux(mean_snow_, cov_snow, char_)

    #Arbitrary values
    g_ = inp.StartValues()
    aqq=0.9
    agg=0.1
    deq=1

    P_= X['Y31']                # Permanent load                                                
    XX_ = X['Y11']              # Load effect model uncertainty
    Q_ = X['Z2']                # Variable load 
    XQ_ = X[X['Z2']['MUV']]     #
    XR_= X['X11']               # Resistance model uncertainty
    R_ = X[X['X11']['RV']]      # Material property
    G_ = X[X['X11']['GV']]      # Self weight


    zet = form.ZBETA(ag=agg, aq=aqq, XR=XR_, R=R_, XX=XX_, G=G_, P=P_, XQ=XQ_, Q=Q_, g=g_, d=deq)
    z=zet.__zeta__()                    #find design variable z per single case
    BETA,ALPHA = zet.f1(z)              #find the corresponding beta index and the alpha values
    return BETA,ALPHA

