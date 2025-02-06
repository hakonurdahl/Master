#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 15 18:32:28 2020
@author: jochenkmacb adapted from jorgemen
"""
import numpy as np
import scipy as sp
import A_funcstat
class ZBETA:
    def __init__(self, ag, aq, XR, R, XX, G, P, XQ, Q, g,d):
        self.ag = ag
        self.aq = aq
        self.XR = XR
        self.R = R
        self.XX = XX
        self.G = G
        self.P = P
        self.XQ = XQ
        self.Q = Q
        self.g = g
        self.d = d              
    def __zeta__(self):
        xrk = self.XR['char']
        rk = self.R['char']
        gk = self.G['char']
        pk = self.P['char']
        qk = self.Q['char']
        g_g = self.g['gg']
        g_p = self.g['gp']
        g_q = self.g['gq']          
        g_r = self.R['gm']
        ag = self.ag
        aq = self.aq
        deq=self.d              
        if deq == 0:
            z = ((1-aq)*(ag*gk*g_g+(1-ag)*pk*g_p)+aq*qk*g_q)*g_r/(xrk*rk)
        elif deq == 1:
            xi = self.g['xi']       
            psi = self.g['psi']     
            z_alt = [0] * 2
            z_alt[0]= ((1-aq)*(ag*gk*g_g+(1-ag)*pk*g_p)+aq*qk*psi*g_q)*g_r/(xrk*rk)
            z_alt[1]= ((1-aq)*(ag*gk*g_g*xi+(1-ag)*pk*g_p*xi)+aq*qk*g_q)*g_r/(xrk*rk)
            z=np.max(z_alt)
        return z
 
    
    def f1(self,z):
    
        gab = lambda a,b: self.gU(a*b,z)                        # lsf as a funciton of alpha and beta
        anext = self.alphanext(z)
        signa = np.array([self.XR['sign'],self.R['sign'],self.XX['sign'],self.G['sign'],self.P['sign'],self.XQ['sign'],self.Q['sign']])
        alpha0 = 1/np.sqrt(len(signa)) * signa     # Initial alpha-vector
        
        beta,alpha = A_funcstat.form(gab,anext,alpha0)
        #print(self.Q['par'])
        return beta, alpha
  
   
#    def gX(self,x,z):
#        lsf = z*x[0]*x[1]-((1-self.aq)*(self.ag*x[2]+(1-self.ag)*x[3])+self.aq*x[4]*x[5])
#        return lsf
    
    def gU(self,u,z):
        #lsf = gX([self.XR['x2u'](u[0]),self.R['x2u'](u[1]),self.G['x2u'](u[2]),self.P['x2u'](u[3]),self.XQ['x2u'](u[4]),self.Q['x2u'](u[5])],z)
        lsf = z*self.XR['x2u'](u[0])*self.R['x2u'](u[1])-self.XX['x2u'](u[2])*((1-self.aq)*(self.ag*self.G['x2u'](u[3])+(1-self.ag)*self.P['x2u'](u[4]))+self.aq*self.XQ['x2u'](u[5])*self.Q['x2u'](u[6]))
        return lsf
    

    def alphanext(self,z):
        # Gradient of lsf
        gdiff = []
        gdiff.append(lambda u: z*self.XR['xdiffu'](u[0]) * self.R['x2u'](u[1])) #over XR
        gdiff.append(lambda u: z*self.XR['x2u'](u[0]) * self.R['xdiffu'](u[1])) #over R
        gdiff.append(lambda u: -self.XX['xdiffu'](u[2])*((1-self.aq)*(self.ag*self.G['x2u'](u[3])+(1-self.ag)*self.P['x2u'](u[4]))+self.aq*self.XQ['x2u'](u[5])*self.Q['x2u'](u[6])))
        gdiff.append(lambda u: -self.XX['x2u'](u[2]) * (1-self.aq)*(self.ag)*self.G['xdiffu'](u[3]))
        gdiff.append(lambda u: -self.XX['x2u'](u[2]) * (1-self.aq)*(1-self.ag)*self.P['xdiffu'](u[4]))
        gdiff.append(lambda u: -self.XX['x2u'](u[2]) * self.aq*self.XQ['xdiffu'](u[5])*self.Q['x2u'](u[6]))
        gdiff.append(lambda u: -self.XX['x2u'](u[2]) * self.aq*self.XQ['x2u'](u[5])*self.Q['xdiffu'](u[6]))
        
        k = lambda u: np.sqrt(gdiff[0](u)**2+gdiff[1](u)**2+gdiff[2](u)**2+gdiff[3](u)**2+gdiff[4](u)**2+gdiff[5](u)**2+gdiff[6](u)**2)
    
        anext = []
        anext.append(lambda u: -gdiff[0](u)/k(u))
        anext.append(lambda u: -gdiff[1](u)/k(u))
        anext.append(lambda u: -gdiff[2](u)/k(u))
        anext.append(lambda u: -gdiff[3](u)/k(u))
        anext.append(lambda u: -gdiff[4](u)/k(u))
        anext.append(lambda u: -gdiff[5](u)/k(u))
        anext.append(lambda u: -gdiff[6](u)/k(u))

        return anext



    def mcstesta(self,z):
        nos=10**7
        fail=[]
        uu=np.random.normal(0, 1, (7, nos, 1))
        fail=-self.gU(uu,z)
        nfail=np.sum(np.heaviside(fail,1))
        Pf=nfail/nos
        betamcs=-sp.stats.norm.ppf(Pf,0,1)
        #betamcs=np.sum(fail)
        return betamcs
    
    def mcstest(self,z):
        nos=10**7
        fail=[]
        xr=A_funcstat.distinv(self.XR['dist'])(np.random.random_sample((nos)),self.XR['par'])
        r=A_funcstat.distinv(self.R['dist'])(np.random.random_sample((nos)),self.R['par'])
        xx=A_funcstat.distinv(self.XX['dist'])(np.random.random_sample((nos)),self.XX['par'])
        g=A_funcstat.distinv(self.G['dist'])(np.random.random_sample((nos)),self.G['par'])
        p=A_funcstat.distinv(self.P['dist'])(np.random.random_sample((nos)),self.P['par'])
        xq=A_funcstat.distinv(self.XQ['dist'])(np.random.random_sample((nos)),self.XQ['par'])
        q=A_funcstat.distinv(self.Q['dist'])(np.random.random_sample((nos)),self.Q['par'])
        
        fail = -(z*xr*r-xx*((1-self.aq)*(self.ag*g+(1-self.ag)*p)+self.aq*xq*q))

        
        nfail=np.sum(np.heaviside(fail,1))
        Pf=nfail/nos
        betamcs=-sp.stats.norm.ppf(Pf,0,1)
        #betamcs=np.sum(fail)
        #print(np.mean(xr),np.mean(r),np.mean(xx),np.mean(g),np.mean(p),np.mean(xq),np.mean(q))
        return betamcs
#
#funcstat.distinv(XR['dist'])(np.random.random_sample((nos)),XR['par'])
#
##class Distance:
##    def __init__(self, v0, a):
##        self.v0 = v0
##        self.a = a
##
##    def __call__(self, t):
##        v0, a = self.v0, self.a  # make local variables
##        return v0*t + 0.5*a*t**2
##    
##d = Distance(v0=0,a=9.81)
##length=d.__call__(3)
##print(length)