#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 27 20:46:34 2024

@author: kohlerm2
"""

import matplotlib.pyplot as plt
import numpy as np
#from scipy.stats import gumbel_r

# # Given values 50 years from background eurocode
# mu_X_T_max = 1  # Mean
# sigma_X_T_max = 0.2  # Standard deviation
# n = 0.02  # from 50 years to 1 

# p = 0.98
# xk = 3.5

# # Formula: 
# mu_X_nT_max = mu_X_T_max + (np.sqrt(6) / np.pi) * sigma_X_T_max * np.log(n)


# cov_X_nT_max = sigma_X_T_max/mu_X_nT_max

# #Parameters
# a =-(np.log(-np.log(p))-np.pi/(cov_X_nT_max*6**0.5)-np.euler_gamma)/xk
# u = np.pi/(cov_X_nT_max*6**0.5*a)+np.euler_gamma/a

# meanx = u-np.euler_gamma/a
# stdx = np.pi/(a*6**0.5)

def gumbelei(m, s, xc):
    n = 0.02  # from 50 years to 1 
    p = 0.98
    # Formula: 
    mn = m + (np.sqrt(6) / np.pi) * s * np.log(n)

    cov = s/mn

    # Parameters calculation for Gumbel distribution
    a = -(np.log(-np.log(p)) - np.pi / (cov * np.sqrt(6)) - np.euler_gamma) / xc
    u = np.pi / (cov * np.sqrt(6) * a) + np.euler_gamma / a

    return a, u

a, u = gumbelei(1,0.2,350)


#Define the x range
x = np.linspace(0, 600, 1000)

# Calculate y = exp(-exp(-a*(x-u)))
y = np.exp(-np.exp(-a * (x - u)))

# Create the plot
plt.figure(figsize=(8, 6))
plt.plot(x, y, label=f'y = exp(-exp(-{a}*(x-{u})))', color='blue')

# Add labels and title
plt.xlabel('x')
plt.ylabel('y')
plt.title('Plot of y = exp(-exp(-a*(x-u)))')
plt.grid(True)



# Display the plot
plt.show()  # Ensure the plot is displayed