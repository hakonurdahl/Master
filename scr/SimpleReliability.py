#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 18 15:33:35 2024

@author: kohlerm2
"""

import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
import scipy.stats
from scipy.stats import norm


#Snow 

sk = 3.2

covEC = 0.51

ms =sk/(1+norm.ppf(0.98)*covEC)

ss = ms*covEC


# Resistance

mr = 1
sr = 0.15

rk = mr+norm.ppf(0.05)*sr


z = 1.5*1.3*sk/rk


betaEC = (z*mr-ms)/np.sqrt((z*sr)**2+ss**2)

msm=2.64
ssm=1.46

betaMessung =  (z*mr-msm)/np.sqrt((z*sr)**2+ssm**2)



print(betaEC,betaMessung)