#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 17 2021
Input for the November 2021 calibration (Case 0 - Default) - All parameters are taken from wordfile sendt by T. Vrouwenvelder by e-mail 
@author: jochenkmacb, ramonh
"""

## This file contains the default input that the user may modify on a graphical interface


def AnalysisOptions(): 
    dat = 0       #Dummy variable defining analysis type (0=reliability-based; 1=risk-based)
    deq = 0       #Dummy variable defining design equation (0=Eq. (6.10); 1= Eq. 6.10a/b)
    dre = 1       #Dummy variable defining reliability elements to be calibrated (e.g.: 1=gamaG/gamaQ; 3=gamaG/gamaQw/gamaQs/gamaQi)
    return dat,deq,dre


def Tref(): 
    Tref= 50
    return Tref

def TargetBeta(): 
    dbt=0                                  #Dummy variable defining target reliability; should be a user defined input specified on a higher level, not here!
    b_t=3.8                                #Only necessary if dbt=0
    return dbt,b_t


def StartValues():
    g_start = {}
    g_start['gg']=1.35
    g_start['gp']=1.35
    g_start['gqw']=1.5
    g_start['gqs']=1.5
    g_start['gqi']=1.5
    g_start['gq']=1.5
    g_start['xi']=0.85
    g_start['psii']=0.7
    g_start['psis']=0.5
    g_start['psiw']=0.6
    g_start['psi']=0.6
    return g_start


def LoadRatios():
    # Discretisation of aq and ag 
    typ='uniform'
    naq=10
    nag=3
    return typ, naq, nag


def RandomVariables(mean_snow, cov_snow, char):
    #--------------------------------------------------------------------------
    ### Random variables
    X = {}
    # Resistance model uncertainty 
    X['X11'] = {}    
    X['X11']['name'] = 'Steel bend.'
    X['X11']['symbol'] = 'theta_{R,sbe}'
    X['X11']['dist'] = 'lognormal'             
    X['X11']['mu'] = 1.15                  #possible bias is introduced here#
    X['X11']['cov'] = 0.05
    X['X11']['aqmin'] = 0.3
    X['X11']['aqmax'] = 0.8
    X['X11']['agmin'] = 0.6
    X['X11']['agmax'] = 1.0
    X['X11']['weight'] = 0.17
    # -------------------------------------------------------------------------
#    X['X12'] = {}    
#    X['X12']['name'] = 'Steel buckling'
#    X['X12']['symbol'] = 'theta_{R,sbu}'
#    X['X12']['dist'] = 'lognormal'             
#    X['X12']['mu'] = 1.0                  #possible bias is introduced here#
#    X['X12']['cov'] = 0.1
#    X['X12']['aqmin'] = 0.2
#    X['X12']['aqmax'] = 0.8
#    X['X12']['agmin'] = 0.6
#    X['X12']['agmax'] = 1.0
    # -------------------------------------------------------------------------
    X['X21'] = {}    
    X['X21']['name'] = 'Concrete comp.'
    X['X21']['symbol'] = 'theta_{R,cc}'
    X['X21']['dist'] = 'lognormal'             
    X['X21']['mu'] = 0.97                  #possible bias is introduced here#
    X['X21']['cov'] = 0.14
    X['X21']['aqmin'] = 0.1
    X['X21']['aqmax'] = 0.7
    X['X21']['agmin'] = 0.6
    X['X21']['agmax'] = 1.0
    X['X21']['weight'] = 0.12
    # -------------------------------------------------------------------------
    X['X22'] = {}    
    X['X22']['name'] = 'Concrete bend.'
    X['X22']['symbol'] = 'theta_{R,cb}'
    X['X22']['dist'] = 'lognormal'             
    X['X22']['mu'] = 1.03                  #possible bias is introduced here#
    X['X22']['cov'] = 0.07
    X['X22']['aqmin'] = 0.1
    X['X22']['aqmax'] = 0.7
    X['X22']['agmin'] = 0.6
    X['X22']['agmax'] = 1.0
    X['X22']['weight'] = 0.4
   # -------------------------------------------------------------------------
    X['X41'] = {}    
    X['X41']['name'] = 'Glulam bend.'
    X['X41']['symbol'] = 'theta_{R,glb}'
    X['X41']['dist'] = 'lognormal'             
    X['X41']['mu'] = 1.0                  #possible bias is introduced here#
    X['X41']['cov'] = 0.1
    X['X41']['aqmin'] = 0.2
    X['X41']['aqmax'] = 0.8
    X['X41']['agmin'] = 0.6
    X['X41']['agmax'] = 1.0
    X['X41']['weight'] = 0.035
    # -------------------------------------------------------------------------
#    X['X42'] = {}    
#    X['X42']['name'] = 'Glulam buckling'
#    X['X42']['symbol'] = 'theta_{R,glbu}'
#    X['X42']['dist'] = 'lognormal'             
#    X['X42']['mu'] = 1.0                  #possible bias is introduced here#
#    X['X42']['cov'] = 0.15
#    X['X42']['aqmin'] = 0.3
#    X['X42']['aqmax'] = 0.8
#    X['X42']['agmin'] = 0.6
#    X['X42']['agmax'] = 1.0
#    X['X42']['weight'] = 0.02
    # -------------------------------------------------------------------------
    X['X51'] = {}    
    X['X51']['name'] = 'Timber bend.'
    X['X51']['symbol'] = 'theta_{R,stb}'
    X['X51']['dist'] = 'lognormal'             
    X['X51']['mu'] = 1.0                  #possible bias is introduced here#
    X['X51']['cov'] = 0.10
    X['X51']['aqmin'] = 0.2
    X['X51']['aqmax'] = 0.8
    X['X51']['agmin'] = 0.6
    X['X51']['agmax'] = 1.0
    X['X51']['weight'] = 0.017
    # -------------------------------------------------------------------------
#    X['X52'] = {}    
#    X['X52']['name'] = 'Solid timber buckling'
#    X['X52']['symbol'] = 'theta_{R,stbu}'
#    X['X52']['dist'] = 'lognormal'             
#    X['X52']['mu'] = 1.0                  #possible bias is introduced here#
#    X['X52']['cov'] = 0.15
#    X['X52']['aqmin'] = 0.3
#    X['X52']['aqmax'] = 0.8
#    X['X52']['agmin'] = 0.6
#    X['X52']['agmax'] = 1.0
#    X['X52']['weight'] = 0.01
    # -------------------------------------------------------------------------
    X['X61'] = {}    
    X['X61']['name'] = 'Masonry'
    X['X61']['symbol'] = 'theta_{R,ma}'
    X['X61']['dist'] = 'lognormal'             
    X['X61']['mu'] = 1.16                  #possible bias is introduced here#
    X['X61']['cov'] = 0.18
    X['X61']['aqmin'] = 0.1
    X['X61']['aqmax'] = 0.7
    X['X61']['agmin'] = 0.6
    X['X61']['agmax'] = 1.0
    X['X61']['weight'] = 0.12
    # -------------------------------------------------------------------------
    X['X71'] = {}    
    X['X71']['name'] = 'Aluminium bend.'
    X['X71']['symbol'] = 'theta_{R,ab}'
    X['X71']['dist'] = 'lognormal'             
    X['X71']['mu'] = 1.27                  #possible bias is introduced here#
    X['X71']['cov'] = 0.15
    X['X71']['aqmin'] = 0.3
    X['X71']['aqmax'] = 0.8
    X['X71']['agmin'] = 0.6
    X['X71']['agmax'] = 1.0
    X['X71']['weight'] = 0.017
    # -------------------------------------------------------------------------
#    X['X72'] = {}    
#    X['X72']['name'] = 'Aluminium buckling'
#    X['X72']['symbol'] = 'theta_{R,abu}'
#    X['X72']['dist'] = 'lognormal'             
#    X['X72']['mu'] = 1.0                  #possible bias is introduced here#
#    X['X72']['cov'] = 0.1
#    X['X72']['aqmin'] = 0.4
#    X['X72']['aqmax'] = 0.8
#    X['X72']['agmin'] = 0.6
#    X['X72']['agmax'] = 1.0
#    X['X72']['weight'] = 0.01
    # -------------------------------------------------------------------------
    X['X81'] = {}    
    X['X81']['name'] = 'Pile found.'
    X['X81']['symbol'] = 'theta_{R,fs}'
    X['X81']['dist'] = 'lognormal'             
    X['X81']['mu'] = 1.0                 #possible bias is introduced here#
    X['X81']['cov'] = 0.2
    X['X81']['aqmin'] = 0.1
    X['X81']['aqmax'] = 0.5
    X['X81']['agmin'] = 0.6
    X['X81']['agmax'] = 1.0
    X['X81']['weight'] = 0.06
    # -------------------------------------------------------------------------
    X['X82'] = {}    
    X['X82']['name'] = 'Shallow found.'
    X['X82']['symbol'] = 'theta_{R,fs}'
    X['X82']['dist'] = 'lognormal'             
    X['X82']['mu'] = 1.0                  #possible bias is introduced here#
    X['X82']['cov'] = 0.15
    X['X82']['aqmin'] = 0.1
    X['X82']['aqmax'] = 0.5
    X['X82']['agmin'] = 0.6
    X['X82']['agmax'] = 1.0
    X['X82']['weight'] = 0.06
    #--------------------------------------------------------------------------
    # Material Strength
    #--------------------------------------------------------------------------
    X['X1'] = {}    
    X['X1']['name'] = 'Steel yield strength'
    X['X1']['symbol'] = 'R_{steel}'
    X['X1']['dist'] = 'lognormal'             
    X['X1']['mu'] = 309
    X['X1']['cov'] = 0.07
    X['X1']['fractile'] = '-'       #(absurd) fractile chosen such that char. value complies with value of 0.83, adopted in previous input (June 2021). Was this value adopted in the AHG calculations?
    X['X1']['gm'] = 1.0
    X['X1']['char'] = 275
    #--------------------------------------------------------------------------
    X['X2'] = {}    
    X['X2']['name'] = 'Concrete compression strength'
    X['X2']['symbol'] = 'R_{concrete}'
    X['X2']['dist'] = 'lognormal'             
    X['X2']['mu'] = 1.00
    X['X2']['cov'] = 0.1
    X['X2']['fractile'] = 0.05               
    X['X2']['gm'] = 1.5
    X['X2']['char'] = []
    #--------------------------------------------------------------------------
    X['X3'] = {}    
    X['X3']['name'] = 'Rebar yield strength'
    X['X3']['symbol'] = 'R_{rebar}'
    X['X3']['dist'] = 'lognormal'             
    X['X3']['mu'] = 1.0
    X['X3']['cov'] = 0.045
    X['X3']['fractile'] = 0.05
    X['X3']['gm'] = 1.15
    X['X3']['char'] = []
    #--------------------------------------------------------------------------
    X['X4'] = {}    
    X['X4']['name'] = 'Glulam bending strength'
    X['X4']['symbol'] = 'R_{glulam}'
    X['X4']['dist'] = 'lognormal'             
    X['X4']['mu'] = 1.0
    X['X4']['cov'] = 0.15
    X['X4']['fractile'] = 0.05
    X['X4']['gm'] = 1.25
    X['X4']['char'] = []
    #--------------------------------------------------------------------------
    X['X5'] = {}    
    X['X5']['name'] = 'Timber strength'
    X['X5']['symbol'] = 'R_{timber}'
    X['X5']['dist'] = 'lognormal'             
    X['X5']['mu'] = 1.0
    X['X5']['cov'] = 0.20
    X['X5']['fractile'] = 0.05
    X['X5']['gm'] = 1.3
    X['X5']['char'] = []
    #--------------------------------------------------------------------------
    X['X6'] = {}    
    X['X6']['name'] = 'Masonry'
    X['X6']['symbol'] = 'R_{masonry}'
    X['X6']['dist'] = 'lognormal'             
    X['X6']['mu'] = 1.0
    X['X6']['cov'] = 0.16
    X['X6']['fractile'] = 0.05
    X['X6']['gm'] = 1.5
    X['X6']['char'] = []
    #--------------------------------------------------------------------------
    X['X7'] = {}    
    X['X7']['name'] = 'Aluminum'
    X['X7']['symbol'] = 'R_{alu}'
    X['X7']['dist'] = 'lognormal'             
    X['X7']['mu'] = 1.0
    X['X7']['cov'] = 0.05
    X['X7']['fractile'] = '-'      #(absurd) fractile chosen such that char. value complies with value of 0.85, adopted in previous input (June 2021). Was this value adopted in the AHG calculations?
    X['X7']['gm'] = 1.1
    X['X7']['char'] = 0.85
    #--------------------------------------------------------------------------
    X['X8'] = {}    
    X['X8']['name'] = 'Soil'
    X['X8']['symbol'] = 'R_{soil}'
    X['X8']['dist'] = 'lognormal'             
    X['X8']['mu'] = 1.0
    X['X8']['cov'] = 0.15
    X['X8']['fractile'] = 0.05
    X['X8']['gm'] = 1.4
    X['X8']['char'] = []
     #--------------------------------------------------------------------------
    X['X9'] = {}    
    X['X9']['name'] = 'CPT'
    X['X9']['symbol'] = 'R_{CPT}'
    X['X9']['dist'] = 'lognormal'             
    X['X9']['mu'] = 1.0
    X['X9']['cov'] = 0.12
    X['X9']['fractile'] = 0.05
    X['X9']['gm'] = 1.5
    X['X9']['char'] = []
    #--------------------------------------------------------------------------
    # Load effect model uncertainty
    #--------------------------------------------------------------------------
    
    X['Y11'] = {}    
    X['Y11']['name'] = 'Load Effect MU Frames'
    X['Y11']['symbol'] = 'theta_{e,1}'
    X['Y11']['dist'] = 'lognormal'        
    X['Y11']['mu'] = 1.0
    X['Y11']['cov'] = 0.1
    X['Y11']['fractile'] = 'not used'
    X['Y11']['char'] = 1.0                ## manual input for char. value               
    #---------------------------------------------------------------------
     # Self weight of structural materials
    #--------------------------------------------------------------------------
    X['Y21'] = {}    
    X['Y21']['name'] = 'Self weight steel'
    X['Y21']['symbol'] = 'G_{steel}'
    X['Y21']['dist'] = 'normal'             
    X['Y21']['mu'] = 1.0
    X['Y21']['cov'] = 0.025
    X['Y21']['fractile'] = 'not used'
    X['Y21']['char'] = 1.0                ## manual input for char. value               
    # --------------------------------------------------------------------
    X['Y22'] = {}    
    X['Y22']['name'] = 'Self weight concrete'
    X['Y22']['symbol'] = 'G_{concrete}'
    X['Y22']['dist'] = 'normal'             
    X['Y22']['mu'] = 1.0
    X['Y22']['cov'] = 0.05
    X['Y22']['fractile'] = 'not used'
    X['Y22']['char'] = 0.98                 ## manual input for char. value               
    # --------------------------------------------------------------------
    X['Y24'] = {}    
    X['Y24']['name'] = 'Self weight glulam'
    X['Y24']['symbol'] = 'G_{glulam}'
    X['Y24']['dist'] = 'normal'             
    X['Y24']['mu'] = 1.0
    X['Y24']['cov'] = 0.1
    X['Y24']['fractile'] = 'not used'
    X['Y24']['char'] = 0.95                 ## manual input for char. value                          
    # --------------------------------------------------------------------
    X['Y25'] = {}    
    X['Y25']['name'] = 'Self weight timber'
    X['Y25']['symbol'] = 'G_{timber}'
    X['Y25']['dist'] = 'normal'             
    X['Y25']['mu'] = 1.00
    X['Y25']['cov'] = 0.1
    X['Y25']['fractile'] = 'not used'  
    X['Y25']['char'] = 0.95                 ## manual input for char. value           
                         
    # --------------------------------------------------------------------
    X['Y26'] = {}    
    X['Y26']['name'] = 'Self weight masonry'
    X['Y26']['symbol'] = 'G_{masonry}'
    X['Y26']['dist'] = 'normal'             
    X['Y26']['mu'] = 1.0
    X['Y26']['cov'] = 0.07
    X['Y26']['fractile'] = 0.5
    X['Y26']['char'] = []                           
    # --------------------------------------------------------------------
    X['Y27'] = {}    
    X['Y27']['name'] = 'Self weight aluminum'
    X['Y27']['symbol'] = 'G_{alu}'
    X['Y27']['dist'] = 'normal'             
    X['Y27']['mu'] = 1.00
    X['Y27']['cov'] = 0.04
    X['Y27']['fractile'] = 0.5
    X['Y27']['char'] = []                               
    # --------------------------------------------------------------------
    X['Y28'] = {}    
    X['Y28']['name'] = 'Self weight soil'
    X['Y28']['symbol'] = 'G_{soil}'
    X['Y28']['dist'] = 'normal'             
    X['Y28']['mu'] = 1.0
    X['Y28']['cov'] = 0.05
    X['Y28']['fractile'] = 0.5
    X['Y28']['char'] = []                               
    #--------------------------------------------------------------------------
    # Permanent load
    #--------------------------------------------------------------------------
    X['Y31'] = {}    
    X['Y31']['name'] = 'Permanent load small V'
    X['Y31']['symbol'] = 'G_{p,sV}'
    X['Y31']['dist'] = 'normal'             
    X['Y31']['mu'] = 1.0
    X['Y31']['cov'] = 0.1
    X['Y31']['fractile'] = 0.5  
    X['Y31']['char'] = []                             
    #---------------------------------------------------------------------------------------
    X['Y32'] = {}    
    X['Y32']['name'] = 'Permanent load large V'
    X['Y32']['symbol'] = 'G_{p,lV}'
    X['Y32']['dist'] = 'normal'             
    X['Y32']['mu'] = 1.0
    X['Y32']['cov'] = 0.2
    X['Y32']['fractile'] = 0.95   
    X['Y32']['char'] = []                              
    #---------------------------------------------------------------------------------------
    # Variable load
    #--------------------------------------------------------------------------
    # Wind___________________________________________
    X['Z11'] = {}   ## Time invariant##                     
    X['Z11']['name'] = 'Wind MU'
    X['Z11']['symbol'] = 'theta_{w}'
    X['Z11']['dist'] = 'lognormal'             
    X['Z11']['mu'] = 0.97
    X['Z11']['cov'] = 0.26
    X['Z11']['fractile'] = '-'  
    X['Z11']['char'] = '-'                                        
    #--------------------------------------------------------------------------
    X['Z1'] = {}    ## Time variant##
    X['Z1']['name'] = 'Wind  50a-extreme'
    X['Z1']['symbol'] = 'Q_{w}'
    X['Z1']['dist'] = 'gumbel'
    X['Z1']['Tr'] = 50                                     # Reference period corresponding to probabilistic model (mu, cov). Must be larger or equal than Tr_bas. Default: 1 y
    X['Z1']['mu'] = 1
    X['Z1']['cov'] = 0.14             
    X['Z1']['Tr_bas'] = 1                                  # Basic reference period. For wind, normally Tr_bas = 1 year (default)
    X['Z1']['fractile'] = 0.98                             # Not needed if char user-defined; otherwise it corresponds to T=Tr_bas if char_method = 0 and to T = max(Tref;Tr_bas) if char_method = 1
    X['Z1']['weight'] = 0.4
    X['Z1']['char_method'] = 0                             # Dummy variable that specifies the method for the determination of char: 0 - MC simulation of both time-dependant (Q) and independent (X_Q) contribution and subsequent determination of char based on specific fractile of the resulting joint variable (XQ*Q); 1 - char directly obtained based on Gumbel dsitribution for Q only (check that char of X_Q = 1.0!) 
    X['Z1']['char'] = []                                   # Char. value may be user-defined    
    #--------------------------------------------------------------------------
    # Snow___________________________________________
    X['Z21'] = {}   ## Time invariant## 
    X['Z21']['name'] = 'Snow MU'
    X['Z21']['symbol'] = 'theta_{w}'
    X['Z21']['dist'] = 'lognormal'             
    X['Z21']['mu'] = 0.81
    X['Z21']['cov'] = 0.26
    X['Z21']['fractile'] = '-'  
    X['Z21']['char'] = '-'                                      
    #--------------------------------------------------------------------------
    X['Z2'] = {}    ## Time variant##
    X['Z2']['name'] = 'Snow 50a-extreme'
    X['Z2']['symbol'] = 'Q_{s}'
    X['Z2']['dist'] = 'gumbel'
    X['Z2']['Tr'] = 50                                     # Reference period corresponding to probabilistic model (mu, cov). Must be larger or equal than Tr_bas. Default: 1 y
    X['Z2']['mu'] = mean_snow
    X['Z2']['cov'] = cov_snow
    X['Z2']['Tr_bas'] = 1                                  # Basic reference period. For snow, normally Tr_bas = 1 year (default)
    X['Z2']['fractile'] = 0.98                             # Not needed if char user-defined; otherwise it corresponds to T=Tr_bas if char_method = 0 and to T = max(Tref;Tr_bas) if char_method = 1
    X['Z2']['weight'] = 0.1
    X['Z2']['char_method'] = 0                             # Dummy variable that specifies the method for the determination of char: 0 - MC simulation of both time-dependant (Q) and independent (X_Q) contribution and subsequent determination of char based on specific fractile of the resulting joint variable (XQ*Q); 1 - char directly obtained based on Gumbel dsitribution for Q only (check that char of X_Q = 1.0!) 
    X['Z2']['char'] = char                                   # Char. value may be user-defined
    #--------------------------------------------------------------------------
    # Imposed___________________________________________
    X['Z31'] = {}   ## Time invariant## 
    X['Z31']['name'] = 'Imposed MU'
    X['Z31']['symbol'] = 'theta_{I}'
    X['Z31']['dist'] = 'lognormal'             
    X['Z31']['mu'] = 1.0
    X['Z31']['cov'] = 0.1     
    X['Z31']['fractile'] = '-'  
    X['Z31']['char'] = '-'                   
    #---------------------------------------------------------------------    
    X['Z3'] = {}    ## Time variant##
    X['Z3']['name'] = 'Imposed 50a-extreme'
    X['Z3']['symbol'] = 'Q_{I}'
    X['Z3']['dist'] = 'gumbel'
    X['Z3']['Tr'] = 50                                     # Reference period corresponding to probabilistic model (mu, cov). Must be larger or equal than Tr_bas. Default: 5 y
    X['Z3']['mu'] = 1
    X['Z3']['cov'] = 0.26                                    
    X['Z3']['Tr_bas'] = 5                                  # Basic reference period. For imposed loads, often Tr_bas = 5 year (default). 
    X['Z3']['fractile'] = 0.99                             # Not needed if char user-defined; otherwise it corresponds to T=Tr_bas if char_method = 0 and to T = max(Tref;Tr_bas) if char_method = 1
    X['Z3']['weight'] = 0.5   
    X['Z3']['char_method'] = 0                             # Dummy variable that specifies the method for the determination of char: 0 - MC simulation of both time-dependant (Q) and independent (X_Q) contribution and subsequent determination of char based on specific fractile of the resulting joint variable (XQ*Q); 1 - char directly obtained based on Gumbel dsitribution for Q only (check that char of X_Q = 1.0!) 
    X['Z3']['char'] = 1.35                                 # Char. value may be user-defined
    #--------------------------------------------------------------------------
    
    return X
###############################################################################
###############################################################################
   

def AssumptionsCosts():             # Provide ISO values as default??
    C={}
#--------------------------------------------------------------------- 
    C['RSC']={}                  # Relative safety costs, C1/C0, per unit of design parameter p 
    #C['RSC']['L']=0.1               # Large
    C['RSC']['N']=0.01              # Normal
    #C['RSC']['S']=0.001             # Small
    #C['RSC']['VS']=0.0001           # VS:Very small
#--------------------------------------------------------------------- 
    C['RFC']={}                  # Relative failure costs, H/C0 (excluding construction costs)
    #C['RFC']['CC1']=0.5             # Minor consequences (0-1)
    C['RFC']['CC2']=2.5             # Moderate consequences (1-4)
    #C['RFC']['CC3']=6.5             # Large consequences (4-8)
#--------------------------------------------------------------------- 
    C['OR']={}                    # Obsolescence rate
    #C['OR']['T=20']=0.05             # 20 years
    C['OR']['T=50']=0.02             # 50 years
    #C['OR']['T=100']=0.01            # 100 years
#--------------------------------------------------------------------- 
    C['IR']={}                   # Interest rate
    #C['IR']['low']=0.01             # Low 
    C['IR']['med']=0.03             # Medium 
    #C['IR']['high']=0.05            # High
#--------------------------------------------------------------------- 
    C['RDC']={}                  # Relative demolition costs
    C['RDC']['const']=0             # Assume negligible; Change if otherwise
#--------------------------------------------------------------------- 
    C['C0']=1                    # Construction costs independent of p (1MU)
    
    return C
