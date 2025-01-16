#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 19:26:51 2024

@author: kohlerm2
"""

# P6.1. Load Combination
# Code converted by ChatGPT from original MATLAB code written by J. Mendoza in July 2019
import numpy as np
import math
from scipy.stats import norm

def form(gx, *vars):
    """
    First Order Reliability Method (FORM) implementation.
    
    Parameters:
    gx : function
        Limit state function in original space.
    vars : list of dictionaries
        Each dictionary represents a random variable with keys 'mu', 'sigma', 'dist', and 'sign'.
        Example: {'mu': 1, 'sigma': 0.5, 'dist': 'norm', 'sign': -1}
    
    Returns:
    BETA : float
        Hasofer-Lind reliability index.
    alpha : list
        First-order sensitivity parameters.
    Pf : float
        FORM approximation of the probability of failure.
    """
    # Algorithm optimization options
    tol = 1e-4  # tolerance on beta
    diff_i = tol + 1  # initialize difference
    i = 0  # iteration counter

    # Number of random variables
    n_rv = len(vars)
    
    # Initial alpha vector
    a = np.array([1 / math.sqrt(n_rv) * var.get('sign', 1) for var in vars if isinstance(var, dict) and 'sign' in var])
    
    # Transform non-normal statistical moments
    u_space = []
    for var in vars:
        if isinstance(var, dict):
            if 'dist' not in var or 'mu' not in var or 'sigma' not in var:
                raise KeyError("Each variable must have 'dist', 'mu', and 'sigma' keys specifying the distribution type, mean, and standard deviation.")
            if var['dist'] == 'norm':
                mu = var['mu']
                sigma = var['sigma']
                u_space.append(lambda u, mu=mu, sigma=sigma: u * sigma + mu)
            elif var['dist'] == 'logn':
                muL, sigmaL = logn2norm(var['mu'], var['sigma'])
                u_space.append(lambda u, muL=muL, sigmaL=sigmaL: np.exp(sigmaL * u + muL))
            elif var['dist'] == 'gumbel':
                a, b = gumb2norm(var['mu'], var['sigma'])
                u_space.append(lambda u, a=a, b=b: b - 1 / a * np.log(-np.log(norm.cdf(u))))
            else:
                raise ValueError("Unsupported distribution type")
    
    # FORM algorithm
    beta = [0]
    us = []
    while diff_i > tol:
        i += 1

        # Find design approximation of design point
        b = beta[-1] if i > 1 else 0
        beta_current = 0
        for j in range(10):  # Iteration to approximate beta
            gu = gx(*[u_space[k](b * a[k]) for k in range(len(u_space))])
            beta_current = b - gu / np.linalg.norm(a)
            if abs(beta_current - b) < tol:
                break
            b = beta_current
        beta.append(beta_current)

        # Approximation of the design point
        us.append(beta[-1] * a)

        # Estimate new alpha vector
        alpha_new = np.array([-gx(*[u_space[k](us[-1][k]) for k in range(len(u_space))]) / np.linalg.norm(a) for k in range(len(u_space))])
        a = alpha_new / np.linalg.norm(alpha_new)

        # Evaluate difference of beta with previous iteration
        if i > 1:
            diff_i = abs(beta[-1] - beta[-2])

    BETA = beta[-1]
    Pf = norm.cdf(-BETA)

    return BETA, a.tolist(), Pf

def logn2norm(mu, sigma):
    """Transforms log-normal parameters to normal parameters."""
    sigmaL = math.sqrt(math.log(1 + (sigma / mu) ** 2))
    muL = math.log(mu) - 0.5 * sigmaL ** 2
    return muL, sigmaL

def gumb2norm(mu, sigma):
    """Transforms Gumbel parameters to normal parameters."""
    a = math.sqrt(6) / math.pi * sigma
    b = mu - 0.5772 / a
    return a, b

# INPUT
b1 = 200    # width [mm]
h1 = 300    # height [mm]
l1 = 5000   # span [mm]

# Material strength [MPa]
mu_Fm = 20
cov_Fm = 0.1
sigma_Fm = mu_Fm * cov_Fm

# Load 1 ~ Gumbel [N/mm]
mu_Q1 = 2
cov_Q1 = 0.2
sigma_Q1 = mu_Q1 * cov_Q1

# Load 2 ~ Gumbel [N/mm]
mu_Q2 = 4
cov_Q2 = 0.4
sigma_Q2 = mu_Q2 * cov_Q2

# Save to input dictionary
input_data_1 = {
    'mu': mu_Q1,
    'sigma': sigma_Q1,
    'dist': 'gumbel',
    'sign': 1
}

input_data_2 = {
    'mu': mu_Q2,
    'sigma': sigma_Q2,
    'dist': 'gumbel',
    'sign': 1
}

# Load combinations
# LC1:
# Q1(LC1) = Q1
# Q2(LC1) = Q2 scaled to T/5, i.e. 360/5=72 reps.
mu_Q2_LC1 = mu_Q2 + math.sqrt(6) / math.pi * sigma_Q2 * math.log(72 / 360)
input_data_2['mu'] = mu_Q2_LC1

beta_LC1, alpha_LC1, Pf_LC1 = form(lambda x1, x2: x1 - 10 * x2 ** 2, input_data_1, input_data_2)  # Compute reliability
print(f'Load case 1: reliability index = {beta_LC1:.2f}')

# LC2:
# Q2(LC2) = Q2
# Q1(LC2) = Q1 scaled to T/5, i.e. 1 rep.
mu_Q1_LC2 = mu_Q1 + math.sqrt(6) / math.pi * sigma_Q1 * math.log(1 / 5)
input_data_1['mu'] = mu_Q1_LC2
input_data_2['mu'] = mu_Q2

beta_LC2, alpha_LC2, Pf_LC2 = form(lambda x1, x2: x1 - 10 * x2 ** 2, input_data_1, input_data_2)  # Compute reliability
print(f'Load case 2: reliability index = {beta_LC2:.2f}')
