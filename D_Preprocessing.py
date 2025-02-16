#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  7 12:18:41 2021
Preprocessing - This file contains auxiliary functions that preprocess the input data for the subsequent analysis
@author: ramonh
"""
import numpy as np
import scipy as sp
import math
import A_funcstat

#################################################
# SPECIFY THE INPUTFILE FOR YOUR ANALYSIS HERE!!#
#################################################
import C_Input_AHG as inp
#################################################     


  
                        # X, C, Load ratios and Tref should correspond to the user-defined cases (overwrite default X given in DefaultInput.py)
#C = inp.AssumptionsCosts()                        
typ, naq, nag = inp.LoadRatios()
Tref = inp.Tref()


def disc_a(aqmin,aqmax,naq,typ):
                              
# Auxiliary function for discretisation of load ratios
#def disc_a(aqmin,aqmax,naq,typ):
    if typ == 'normal':
        con = 2     #how peaked is the normal distribution at the mean con=1:: aqmin is the 1/naq fractile. con=2:: aqmin is the 1/2naq fractile
        aqmean=aqmin+(aqmax-aqmin)/2
        aqst=(aqmin-aqmean)/sp.stats.norm.ppf((1/(con*naq)), loc=0, scale=1)
        xaq=np.linspace(1/naq,1-1/naq,naq,typ)
        aq=[] 
        for ixaq in xaq:
            aq.append(sp.stats.norm.ppf(ixaq, loc=aqmean, scale=aqst))
            aq[0]=aqmin
        aq[naq-1]=aqmax
        return aq
    elif typ == 'uniform':
        aq=[]
    aq=np.linspace(aqmin,aqmax,naq)
    return aq

def MatAsign():
# Auxiliary function for assigment of material properties to failure modes                       
    M = {}
    M['X11']='X1'
    M['X12']='X1'
    M['X21']='X2'
    M['X22']='X3'
    M['X41']='X4'
    M['X42']='X4'
    M['X51']='X5'
    M['X52']='X5'
    M['X61']='X6'
    M['X71']='X7'
    M['X72']='X7'
    M['X81']='X9'
    M['X82']='X8'
    return M


## Assigning the coeffiecient of variance of snow
def RandomVariablesAux(mean_snow, cov_snow, char):
    X = inp.RandomVariables(mean_snow, cov_snow, char) 
# Auxiliary function that completes characterization of user-specified random variables
    # All variables 
    for key in X:
        # Standard deviation and function parameters
        X[key]['sigma'] = X[key]['mu']*X[key]['cov']
        X[key]['par'] = A_funcstat.distparam(X[key]['dist'])(X[key]['mu'],X[key]['sigma'])
        # Variable loads 
        if key[0]=='Z' and len(key)==2:
            # Assign model uncertainty
            X[key]['MUV']=key+'1'
            # Sign for initial alpha vector 
            X[key]['sign'] = 1
            X[key+'1']['sign'] = 1
            #Characteristic value       
            # Determine mu and sigma corresponding to Tr,bas for calculation of char (depending on Tr > or = Tr,bas and Tref <= or > Tr_bas)
            if X[key]['Tr'] > X[key]['Tr_bas']:
                    X[key]['mu'] = X[key]['mu']+(np.sqrt(6)/math.pi)*X[key]['sigma']*np.log(X[key]['Tr_bas']/X[key]['Tr'])
                    X[key]['cov'] = X[key]['sigma']/X[key]['mu']
                    if  X[key]['Tr_bas'] >= Tref: 
                        X[key]['mu'] = 1.0
                        X[key]['sigma']=X[key]['mu']*X[key]['cov']
                        X[key]['Tr'] = X[key]['Tr_bas']
            else:
                if X[key]['Tr_bas'] < Tref:                     
                    X[key]['mu'] = X[key]['mu']+(np.sqrt(6)/math.pi)*X[key]['sigma']*np.log(Tref/X[key]['Tr_bas'])
                    X[key]['cov'] = X[key]['sigma']/X[key]['mu']
                    X[key]['mu'] = 1.0
                    X[key]['sigma']=X[key]['mu']*X[key]['cov']
                    X[key]['mu'] = X[key]['mu']+(np.sqrt(6)/math.pi)*X[key]['sigma']*np.log(X[key]['Tr_bas']/Tref)
                    X[key]['Tr'] = Tref
            # Determine distribution parameters
            X[key]['par'] = A_funcstat.distparam(X[key]['dist'])(X[key]['mu'],X[key]['sigma'])
            # Determine char unless user-defined
            if not X[key]['char']:
                n=10000000 #number of simulations
                q=np.random.lognormal(X[key+'1']['par'][0], X[key+'1']['par'][1], n) #lognormal
                q1=X[key]['par'][1] - 1/X[key]['par'][0] * np.log(-np.log( np.random.rand(n) )) #Gumbel
                q3=q*q1
                q4=np.sort(q3)
                X[key]['char']=q4[int(X[key]['fractile']*n)]
            #Set mean value back to 1.0 and recalculate cov if Tref > Tr,bas
            if Tref > X[key]['Tr_bas']: 
                X[key]['mu'] = 1.0
                X[key]['cov'] = X[key]['sigma']/X[key]['mu']
                X[key]['par'] = A_funcstat.distparam(X[key]['dist'])(X[key]['mu'],X[key]['sigma'])
            #Alternative approach to char calculation (as in fib MC2020): char directly obtained from time-independent part (char of time invariant part = 1.0!) 
            if X[key]['char_method'] == 1: 
                X[key]['char'] = X[key]['mu']-X[key]['sigma']*(0.45+0.78*np.log(-np.log(X[key]['fractile'])))
        # Resistance variables
        elif key[0]=='X':
            # Sign for initial alpha vector
            X[key]['sign'] = -1
            # Model uncertainties
            if len(key)==3:
                # Load ratio arrays
                X[key]['aq'] = disc_a(X[key]['aqmin'],X[key]['aqmax'],naq,typ) 
                X[key]['ag'] = disc_a(X[key]['agmin'],X[key]['agmax'],nag,typ)
                # Characteristic values                                                  
                X[key]['char'] = 1.0   # (by convention)
                # Assignment of self-weight
                X[key]['GV']='Y2'+ key[1]
                # Assignment of material property
                X[key]['RV']= MatAsign()[key]
            # Material resistance
            else:
                # Characteristic values
                if not X[key]['char']:
                    X[key]['char'] = A_funcstat.distinv(X[key]['dist'])(X[key]['fractile'],X[key]['par']) 
        # Permanent loads
        elif key[0]=='Y':
            # Sign for initial alpha vector and char. value
            X[key]['sign'] = 1
            if not X[key]['char']:
                X[key]['char'] = A_funcstat.distinv(X[key]['dist'])(X[key]['fractile'],X[key]['par']) 
        # User defined function that performs transformation and differentiation for FORM algorithms- hand them over to the main program
        X[key]['x2u'] = {}
        X[key]['x2u'] = A_funcstat.x2u(X[key]['dist'],X[key]['par'])
        X[key]['xdiffu'] = {}
        X[key]['xdiffu'] = A_funcstat.xdiffu(X[key]['dist'],X[key]['par'])
    return X


def XZ_iter(): 
#Auxiliary function that creates and returns user-defined X and Z dictionaries (Characterization of failure mode/material and variable load)
    X_iter=[]       
    Z_iter=[]  
    for key in X:
        if key[0]=='Z' and len(key)==2:
            Z_iter.append(key)                                                               
        elif key[0]=='X' and len(key)==3:                                                      
            X_iter.append(key)                                                                                                                                           
    return X_iter, Z_iter
       

def C_iter(): 
#Auxiliary function that creates and returns user-defined C dictionary (Cost-related assumptions)
    RSC_iter=[]
    RFC_iter=[]
    OR_iter=[]
    IR_iter=[]    
    RDC_iter=[]  
    for key in C:
        if key=='RSC':
            for key1 in C[key]:
                RSC_iter.append(key1)
        elif key=='RFC':
            for key1 in C[key]:
                RFC_iter.append(key1)
        elif key=='OR':
            for key1 in C[key]:
                OR_iter.append(key1)
        elif key=='IR':
            for key1 in C[key]:
                IR_iter.append(key1)
        elif key=='RDC':
            for key1 in C[key]:
                RDC_iter.append(key1)    
    return RSC_iter, RFC_iter, OR_iter, IR_iter, RDC_iter


def aq_converter(key_perm_load,key_var_load,aqk):
# Auxiliary function which converts aqk ratios (qk/(qk+pk)) in the real (p) system into aq values in the z-system
    def ObjFun_aq(aq):
        aqk_it=1/(X[key_perm_load]['char']/X[key_var_load]['char']*(1-aq)/aq+1)
        Obj=(aqk_it-aqk)**2
        return Obj
    
    def Inter(aq):
        aq_iter=ObjFun_aq(aq)
        return aq_iter
    
    def Minim(x):
        ssd_min=Inter(x[0])
        return ssd_min
    x0 = 0.5
    res = sp.optimize.minimize(Minim, x0, method='SLSQP', options={'ftol': 1e-8, 'eps': 1e-8})
    aq=res.x[0]
    return aq
                
def aqk_converter(key_perm_load,key_var_load,aq):
# Auxiliary function which converts aq values in the z-system to aqk ratios (qk/(qk+pk)) in the real (p) system 
    aqk=1/(1+X[key_perm_load]['char']/X[key_var_load]['char']*(1-aq)/aq)
    return aqk        
    
        