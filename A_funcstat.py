# -*- coding: utf-8 -*-
"""
Created on Mon Apr 12 12:36:23 2021

@author: ramon
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 29 14:21:22 2020
@author: jorgemen
"""


import csv
import os
import ast


import numpy as np
import scipy as sp
import scipy.stats
 
def distDV(dist, alpha):
    """Compute the design value based on standard alpha and beta"""
    def lognDV(mu,sigma):
        if mu>0:
            x_d=mu*np.exp(-0.5*np.log(1+(mu*sigma)**2)+alpha*3.8*np.sqrt(np.log(1+(mu*sigma)**2)))
        else:
            raise Exception('Lognormal mean needs be larger than 0')
        return x_d
    def normDV(m,s):
        x_d=m+alpha*3.8*s
        return x_d
    def gumbDV(m,s):
        x_d=m-s*(np.sqrt(6)/np.pi)*(0.5772+np.log(-np.log(sp.stats.norm.cdf(alpha*3.8))))
        return x_d
    switcher={
            'normal':normDV,
            'lognormal':lognDV,
            'gumbel':gumbDV
            }
    return switcher.get(dist,"Distribution out of scope")

def distCHAR(dist,p):
    """Compute the design value based on distribution fractile"""
    def lognCHAR(mu,sigma):
        
        if mu>0:
            x_k=mu*np.exp(-0.5*np.log(1+(mu*sigma)**2)+sp.stats.norm.ppf(p)*np.sqrt(np.log(1+(mu*sigma)**2)))
        else:
            raise Exception('Lognormal mean needs be larger than 0')
        return x_k
    def normCHAR(m,s):
        x_k=m+sp.stats.norm.ppf(p)*s
        return x_k
    def gumbCHAR(m,s):
        x_k=m-s*(np.sqrt(6)/np.pi)*(0.5772+np.log(-np.log(p)))
        return x_k
    switcher={
            'normal':normCHAR,
            'lognormal':lognCHAR,
            'gumbel':gumbCHAR
            }
    return switcher.get(dist,"Distribution out of scope")
   
def distparam(dist):
    """Compute the distribution parameters of distribution specified in dist
    given mean and standard deviation"""
    def logn2param(mu,sigma):
        # Takes the parameters of the log-normal distribution and transforms them
        # to the parameters of the associated normal distribution
        if mu>0:
            par1 = np.log( (mu**2) / np.sqrt(sigma**2 + mu**2) )
            par2 = np.sqrt( np.log( sigma**2/mu**2 + 1) )
        else:
            raise Exception('Lognormal par1 needs be larger than 0')
        return par1,par2
    def norm2param(m,s):
        return m,s
    def gumb2norm(m,s):
        # Takes the expected value m and standard devatiation s of a Gumbel 
        # distribution and finds the scale and shape parameters (a and b)
        # F = exp( -exp( -a*(x-b) ) )
        a = np.pi/( np.sqrt(6)*s )
        b = m - 0.5772156649/a
        return a,b
    switcher={
            'normal':norm2param,
            'lognormal':logn2param,
            'gumbel':gumb2norm
            }
    return switcher.get(dist,"Distribution out of scope")

def diststat(dist):
    """Compute the distribution parameters of distribution specified in dist
    given mean and standard deviation"""
    def lognstat(m,s):
        """Created by Jorge Mendoza February, 2020
        Takes the parameters of the log-normal distribution and transforms them
        to the parameters of the associated normal distribution"""
        mu = np.exp(m + s**2 / 2.0)
        sigma = np.sqrt(np.exp(2 * m + s**2) * (np.exp(s**2) - 1))
        return mu,sigma

    def normstat(mu,sigma):
        return mu,sigma
    def gumbstat(a,b):
        """Created by Jorge Mendoza May, 2019
        Obtains statistical moments of Gumbel distribution. The Gumbel
        distribution is defined as F = exp(-exp(-a*(x-b)));"""
        sigma = np.pi/(np.sqrt(6)*a);
        mu = b + 0.5772156649/a;
        return mu,sigma
    switcher={
            'normal':normstat,
            'lognormal':lognstat,
            'gumbel':gumbstat
            }
    return switcher.get(dist,"Distribution out of scope")


def distpdf(dist):
    """Return pdf of dist in Matlab-like style"""
    def lognpdf(x,m,s): return sp.stats.lognorm.pdf(x,s,scale=np.exp(m))
    switcher={
        #'normal':normpdf,
        'lognormal':lognpdf,
        #'gumbel':gumbpdf
        }
    return switcher.get(dist,"Distribution out of scope")

def distcdf(dist):
    """Return cdf of dist in Matlab-like style"""
    def normcdf(x,**kwargs):
        if kwargs.get('mu', None) == None:
            mu = 0
        else: 
            mu = kwargs.get('mu', None)
        if kwargs.get('sigma', None) == None:
            sigma = 1
        else: 
            sigma = kwargs.get('sigma', None)
        
        return sp.stats.norm.cdf(x,mu,sigma)
    def logncdf(x,m,s): return sp.stats.lognorm.cdf(x,s,scale=np.exp(m))
    switcher={
        'normal':normcdf,
        'lognormal':logncdf,
        # 'gumbel':gumbpdf
        }
    return switcher.get(dist,"Distribution out of scope")

# def distinv(dist):
#     """Return inverse funcition of dist in Matlab-like style"""
#     def norminv(p,mu,sigma): return sp.stats.norm.ppf(p,mu,sigma)
#     def logninv(p,m,s): return sp.stats.lognorm.ppf(p,s,scale=np.exp(m))
#     def gumbinv(p,a,b): return b - 1/a * np.log(-np.log( p ))
#     switcher={
#         'normal':norminv,
#         'lognormal':logninv,
#         'gumbel':gumbinv
#         }
#     return switcher.get(dist,"Distribution out of scope")

def distinv(dist):
    """Return inverse funcition of dist in Matlab-like style"""
    def norminv(p,param): return sp.stats.norm.ppf(p,param[0],param[1])
    def logninv(p,param): return sp.stats.lognorm.ppf(p,param[1],scale=np.exp(param[0]))
    def gumbinv(p,param): return param[1] - 1/param[0] * np.log(-np.log( p ))
    switcher={
        'normal':norminv,
        'lognormal':logninv,
        'gumbel':gumbinv
        }
    return switcher.get(dist,"Distribution out of scope")

        

def x2u(dist,param):
    """Returns function to map a point from the x-space to the u-space given a
    distribution type and the distribution parameters"""
    def normx2u(u):
        return u*param[1]+param[0]
    
    def lognx2u(u):
        return np.exp(param[1]*u+param[0])
        
    def gumbx2u(u):
        if u>5.:
            u=5.
        return param[1]-1./param[0]*np.log(-np.log(sp.stats.norm.cdf(u)))
    switcher={
            'normal':normx2u,
            'lognormal':lognx2u,
            'gumbel':gumbx2u,
            }
    return switcher.get(dist,"Distribution out of scope")

def xdiffu(dist,param):
    """Returns derivative of a random variable x with distribution dist with 
    respect to u given dist and the distribution parameters"""
    def normxdiffu(u):
        return param[1]
    
    def lognxdiffu(u):
        return param[1]*np.exp(param[1]*u+param[0])
        
    def gumbxdiffu(u):
        return -sp.stats.norm.pdf(u) / (param[0] * sp.stats.norm.cdf(u)* np.log(sp.stats.norm.cdf(u)))
    switcher={
            'normal':normxdiffu,
            'lognormal':lognxdiffu,
            'gumbel':gumbxdiffu,
            }
    return switcher.get(dist,"Distribution out of scope")
    
def form(gab,anext,alpha0):
    """Perform gradient-based optimization to compute FORM estimation of the 
    reliability index given:
        - a limit state function expressed as a function of the alpha-vector 
        and the beta-modulus
        - the gradient-based next alpha-vector given a new beta
        - an initial guess of the alpha-vector"""
    tol = 0.001
    diff_i = tol+1
    alpha = alpha0
    beta = []
    while diff_i > tol:
        # LSF u-space at iteration i
        gb =  lambda b: gab(alpha,b)   
        beta.append(sp.optimize.fsolve(gb,1)[0])
        us = []
        for i in np.arange(0, len(alpha0)):
            us.append(beta[-1]*alpha[i])
            
        for i in np.arange(0, len(alpha0)):
            alpha[i] = anext[i](us)
        if len(beta)>2:
            diff_i = abs(beta[-1] - beta[-2])
    #print(beta) #used for debugging                    
    return beta[-1],alpha 

def mle_logn(data,x0,negll):
    """Calculate Maximum likelihood estimation of log-normal distributed 
    variable given data and initial guess (moments of data) """
    negll_opt = lambda theta: negll(theta,data)
    res = sp.optimize.minimize(negll_opt,x0,method='BFGS')
    return res.x,res.hess_inv

def truncate(n, decimals=0):
    multiplier = 10 ** decimals
    return int(n * multiplier) / multiplier


#Read csv files -HU
def get_values(csv_file_path, municipality_name,variable):
    """Reads values for a given municipality from a CSV file."""
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            # Check if the municipality name matches
            if row["Municipality"] == municipality_name:
                # Parse the values safely using ast.literal_eval()
                values = ast.literal_eval(row[variable])
                return values
                
    # Return None if the municipality is not found
    print(f"No data found for municipality: {municipality_name}")
    return None