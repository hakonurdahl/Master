
import numpy as np
import scipy as sp



def MAIN(h_mean, h_cov, s_k):   #m, - , kN/m^3

    def reliability(W_Rd, S_Ed, S_cov):
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

        ##### LSF and variables from Optimising Monitoring: Standards, Reliability Basis and Application to Assessment of Roof Snow Load Risks, Dimitris Diamantidis ###

        XR = {}    
        XR['name'] = 'Resistance model uncertainty.'
        XR['symbol'] = 'theta_{R}'
        XR['dist'] = 'lognormal'             
        XR['mu'] = 1.1                 #possible bias is introduced here#
        XR['cov'] = 0.05
        XR['sigma'] = XR['mu']*XR['cov']
        XR['par'] = distparam(XR['dist'])(XR['mu'],XR['sigma'])
        XR['x2u'] = {}
        XR['x2u'] = x2u(XR['dist'],XR['par'])
        XR['xdiffu'] = {}
        XR['xdiffu'] = xdiffu(XR['dist'],XR['par'])
        XR['sign']=-1

        f_yd = {}    
        f_yd['name'] = 'Yield strength S275.'
        f_yd['symbol'] = 'f_{yd}'
        f_yd['dist'] = 'lognormal'             
        f_yd['mu'] = 309000                  #possible bias is introduced here#
        f_yd['cov'] = 0.07
        f_yd['sigma'] = f_yd['mu']*f_yd['cov']
        f_yd['par'] = distparam(f_yd['dist'])(f_yd['mu'],f_yd['sigma'])
        f_yd['x2u'] = {}
        f_yd['x2u'] = x2u(f_yd['dist'],f_yd['par'])
        f_yd['xdiffu'] = {}
        f_yd['xdiffu'] = xdiffu(f_yd['dist'],f_yd['par'])
        f_yd['sign']=-1

        XE = {}    
        XE['name'] = 'Load effect uncertainty.'
        XE['symbol'] = 'theta_{E}'
        XE['dist'] = 'lognormal'             
        XE['mu'] = 1                 #possible bias is introduced here#
        XE['cov'] = 0.05
        XE['sigma'] = XE['mu']*XE['cov']
        XE['par'] = distparam(XE['dist'])(XE['mu'],XE['sigma'])
        XE['x2u'] = {}
        XE['x2u'] = x2u(XE['dist'],XE['par'])
        XE['xdiffu'] = {}
        XE['xdiffu'] = xdiffu(XE['dist'],XE['par'])
        XE['sign']=1

        dens = {}    
        dens['name'] = 'Steel density.'
        dens['symbol'] = 'gamma_{S}'
        dens['dist'] = 'normal'             
        dens['mu'] = 77                  #possible bias is introduced here#
        dens['cov'] = 0.01
        dens['sigma'] = dens['mu']*dens['cov']
        dens['par'] = distparam(dens['dist'])(dens['mu'],dens['sigma'])
        dens['x2u'] = {}
        dens['x2u'] = x2u(dens['dist'],dens['par'])
        dens['xdiffu'] = {}
        dens['xdiffu'] = xdiffu(dens['dist'],dens['par'])
        dens['sign']=1


        L=5
        #IPE200 This is inaccurate. Changes with W_Rd  -HU
        A=2.9e-6
        b=5


        S = {}    
        S['name'] = 'Snow'
        S['symbol'] = 'S'
        S['dist'] = 'gumbel'             
        S['mu'] = S_Ed                 #possible bias is introduced here#
        S['cov'] = S_cov
        S['sigma'] = S['mu']*S['cov']
        S['par'] = distparam(S['dist'])(S['mu'],S['sigma'])
        S['x2u'] = {}
        S['x2u'] = x2u(S['dist'],S['par'])
        S['xdiffu'] = {}
        S['xdiffu'] = xdiffu(S['dist'],S['par'])
        S['sign']=1

        roof = {}    
        roof['name'] = 'Roof.'
        roof['symbol'] = 'Roof'
        roof['dist'] = 'normal'             
        roof['mu'] = 0.6                  #possible bias is introduced here#
        roof['cov'] = 0.05
        roof['sigma'] = roof['mu']*roof['cov']
        roof['par'] = distparam(roof['dist'])(roof['mu'],roof['sigma'])
        roof['x2u'] = {}
        roof['x2u'] = x2u(roof['dist'],roof['par'])
        roof['xdiffu'] = {}
        roof['xdiffu'] = xdiffu(roof['dist'],roof['par'])
        roof['sign']=1


        def gU(W_Rd, u):        
            lsf = XR['x2u'](u[0])*W_Rd*f_yd['x2u'](u[1])-XE['x2u'](u[2])*L**2/8*(dens['x2u'](u[3])*A+S['x2u'](u[4])*b+roof['x2u'](u[5])*b)
            return lsf


        def alphanext():
            # Gradient of lsf
            gdiff = []
            gdiff.append(lambda u: XR['xdiffu'](u[0]) * W_Rd*f_yd['x2u'](u[1])) #over XR
            gdiff.append(lambda u: XR['x2u'](u[0]) * f_yd['xdiffu'](u[1])*W_Rd) #over f_yd
            gdiff.append(lambda u: -XE['xdiffu'](u[2])*L**2/8*(dens['x2u'](u[3])*A+S['x2u'](u[4])*b+roof['x2u'](u[4])*b)) #over XE
            gdiff.append(lambda u: -XE['x2u'](u[2])*L**2/8*(dens['xdiffu'](u[3])*A)) #over dens
            gdiff.append(lambda u: -XE['x2u'](u[2])*L**2/8*(S['xdiffu'](u[4])*b)) #over S
            gdiff.append(lambda u: -XE['x2u'](u[2])*L**2/8*(roof['xdiffu'](u[5])*b)) #over roof
                
            k = lambda u: np.sqrt(gdiff[0](u)**2+gdiff[1](u)**2+gdiff[2](u)**2+gdiff[3](u)**2+gdiff[4](u)**2+gdiff[5](u)**2)
            
            anext = []
            anext.append(lambda u: -gdiff[0](u)/k(u))
            anext.append(lambda u: -gdiff[1](u)/k(u))
            anext.append(lambda u: -gdiff[2](u)/k(u))
            anext.append(lambda u: -gdiff[3](u)/k(u))
            anext.append(lambda u: -gdiff[4](u)/k(u))
            anext.append(lambda u: -gdiff[5](u)/k(u))


            return anext



        def f1():
            
                gab = lambda a,b: gU(W_Rd, a*b)                        # lsf as a funciton of alpha and beta
                anext = alphanext()
                signa = np.array([XR['sign'],f_yd['sign'],XE['sign'],dens['sign'],S['sign'],roof['sign']])
                alpha0 = 1/np.sqrt(len(signa)) * signa     # Initial alpha-vector
                
                beta,alpha = form(gab,anext,alpha0)
                #print(Q['par'])
                return beta, alpha


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

        def mcstest():
            nos=10**7
            fail=[]
            xr=distinv(XR['dist'])(np.random.random_sample((nos)),XR['par'])
            f_yd_=distinv(f_yd['dist'])(np.random.random_sample((nos)),f_yd['par'])
            xe=distinv(XE['dist'])(np.random.random_sample((nos)),XE['par'])
            dens_=distinv(dens['dist'])(np.random.random_sample((nos)),dens['par'])
            s=distinv(S['dist'])(np.random.random_sample((nos)),S['par'])
            roof_=distinv(roof['dist'])(np.random.random_sample((nos)),roof['par'])
                
            fail = -(W_Rd*xr*f_yd_-xe*L**2/8*(dens_*A+s*b+roof_*b))

                
            nfail=np.sum(np.heaviside(fail,1))
            Pf=nfail/nos
            betamcs=-sp.stats.norm.ppf(Pf,0,1)
            #betamcs=np.sum(fail)
            #print(np.mean(xr),np.mean(r),np.mean(xx),np.mean(g),np.mean(p),np.mean(xq),np.mean(q))
            return betamcs
        #


        b_mc=mcstest()
        b_form=f1()[0]
        return b_form, b_mc



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

    x_k_roof=distCHAR('normal',0.95)(0.6*5,0.6*0.05*5) #kN/m
    x_k_dens=distCHAR('normal',0.95)(77*2.9e-6*5,77*2.9e-6*5*0.01) #kN/m. Negligable

    L=5 #This should be global 

    def resistance(s_k_):
        q_Ed=1.2*x_k_roof+1.5*s_k_*5
        M_Ed=q_Ed*L**2/8
        W_Rd=M_Ed/(275e3/1.05) #m^3
        return W_Rd

    W_Rd_=resistance(s_k)

    #Ill use a tentative density for snow 300kg/m^3

    water_dens=1000 #kg/m^3
    g=9.81
    

    b_f, b_mc = reliability(W_Rd_, (h_mean*water_dens*g)*1e-3,h_cov)
    return b_f, b_mc


