#Import 
import numpy as np
import scipy.stats as stats

import B_mainclass as form
import C_Input_AHG as inp
import D_Preprocessing as prep
import measurements as meas
from municipalities import municipalities_data
from elevation_points import samples
from elevation import get_elevations
from statistics import mean
from math import ceil


def char(name):
    
    sk_0=municipalities_data[name]['sk_0']
    hg=municipalities_data[name]['hg']
    dsk=municipalities_data[name]['dsk']
    sk_maks=municipalities_data[name]['sk_maks']
    latitude=municipalities_data[name]['coordinates']['latitude']
    longitude=municipalities_data[name]['coordinates']['longitude']
    points=samples(name)
    
    run_=0      #To avoid using API

    if run_==1:
        elevation = mean(get_elevations(points))
    else:
        elevation=0

    n=max(ceil((elevation-hg)/100), 0)

    if sk_maks==None:
        sk=sk_0+dsk*n
    
    else:
        sk=min(sk_0+dsk*n, sk_maks)

    return sk



def form(name):   #Calculate beta


    snow_maxima=meas.measurements(name)['swe']
    loc, scale = stats.gumbel_r.fit(snow_maxima)

    gamma = 0.57722  

    # Compute mean and standard deviation
    mean_gumbel = loc + gamma * scale
    std_gumbel = (np.pi / np.sqrt(6)) * scale

    # Compute CoV
    cov_snow = std_gumbel / mean_gumbel

    char=char(name)


    X = prep.RandomVariablesAux(cov_snow, char)

    g_ = inp.StartValues()
    aqq=0.9
    agg=0.1
    deq=1

    P_= X['Y31']                #                                                 
    XX_ = X['Y11']              #
    Q_ = X['Z2']                #variable load 
    XQ_ = X[X['Z2']['MUV']]     #
    XR_= X['X11']               #resistance model uncertainty
    R_ = X[X['X11']['RV']]      #material property
    G_ = X[X['X11']['GV']]      #


    zet = form.ZBETA(ag=agg, aq=aqq, XR=XR_, R=R_, XX=XX_, G=G_, P=P_, XQ=XQ_, Q=Q_, g=g_, d=deq)
    z=zet.__zeta__()                    #find design variable z per single case
    BETA,ALPHA = zet.f1(z)              #find the corresponding beta index and the alpha values
    return BETA,ALPHA


#BETA,ALPHA=MAIN('Loppa')
#print(BETA)