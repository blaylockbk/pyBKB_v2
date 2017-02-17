import matplotlib
import numpy as np
from matplotlib.projections import register_projection
from matplotlib.ticker import MultipleLocator,FixedLocator,AutoLocator,\
        ScalarFormatter
from matplotlib.pyplot import rcParams,figure,show,draw
from numpy import ma,array,linspace,logspace,log,cos,sin,pi,zeros,exp,arange,trapz,\
        where,concatenate,nan,isnan,argsort,log10,meshgrid
from UserDict import UserDict
from datetime import datetime
import os,sys

# Local thermodynamics stuff, see thermodynamics.py
from thermodynamics import VirtualTemp,Latentc,VaporPressure,MixRatio,GammaW,\
    VirtualTempFromMixR,MixR2VaporPress,DewPoint,Theta,TempK,Density,DensHumid,\
    ThetaE,ThetaV,barometric_equation_inv
from thermodynamics import Rs_da, Cp_da, Epsilon,degCtoK

mpl_version=str(matplotlib.__version__)
mpl_version_digits=[int(ss) for ss in mpl_version.split('.')]
assert mpl_version_digits[0]>=1, "Requires matplotlib version>1.0.0"

if mpl_version_digits[1]<4:
    # Thanks Ryan May for providing the original (and presumably, the current) 
    # implementation of the SkewX preojections
    from skewx_projection_matplotlib_lt_1d4 import SkewXAxes
else:
    # See: http://matplotlib.org/mpl_examples/api/skewt.py
    # The _only_ change to the code is on line 113, where I set
    # rot=45 to suit my axes.
    from skewx_projection import SkewXAxes

# SkewT version
__version__="1.1.0"

class SkewXAxes(SkewXAxes):
    # In the SkewT package, SkewXAxes is a subclass of the one provided 
    # by Ryan May, either from the example on his webpage (circa 2011) or
    # the example on the matplotlib page. I add the following methods.
 
    def other_housekeeping(self,mixratio=array([])):
        # Added by Thomas Chubb
        self.yaxis.grid(True,ls='-',color='y',lw=0.25)
        majorLocatorDegC   = MultipleLocator(10)

        self.xaxis.set_major_locator(majorLocatorDegC)
        self.xaxis.grid(True,color='y',lw=0.3,ls='-')

        self.set_ylabel('Pressure (hPa)',fontsize=10)
        self.set_xlabel('Temperature (C)',fontsize=10)
        yticks=linspace(100,1000,10)
        if self.pmin<100:
            yticks=concatenate((array([50,20,10]),yticks))

        self.set_yticks(yticks)

        self.yaxis.set_major_formatter(ScalarFormatter())
        self.set_xlim(self.tmin,self.tmax)
        self.set_ylim(self.pmax,self.pmin)
        self.spines['right'].set_visible(False)
        self.get_yaxis().set_tick_params(which="both",size=0,labelsize=8)
        self.get_xaxis().set_tick_params(which="both",size=0,labelsize=8)
        

    def add_dry_adiabats(self,T0,P,do_labels=True,**kwargs):
        # Added by Thomas Chubb
        P0=1000.
        T=array([ (st+degCtoK)*(P/P0)**(Rs_da/Cp_da)-degCtoK for st in T0 ])
        labelt=[ (st+degCtoK)*1**(Rs_da/Cp_da) for st in T0 ]

        # gets a pressure level about 1/4 the way up the plot...
        pp=10**(log10(self.pmin**.2*self.pmax**.8))
        xi=where( abs(P-pp)-abs(P-pp).min()<1e-6 )[0][0]

        ndec=log10(self.pmax/pp)/log10(self.pmax/self.pmin)
        tran=self.tmax-self.tmin
        tminl=self.tmin-tran*ndec
        tmaxl=self.tmax-tran*ndec

        if kwargs.has_key('color'): 
            col=kwargs['color']
        else: 
            col='k'
        for tt,ll in zip(T,labelt):
            self.plot(tt,P,**kwargs)
            if do_labels:
                if tt[xi]>tmaxl-2: continue
                if tt[xi]<tminl+2: continue
                self.text(tt[xi],P[xi]+10,'%d'%(ll),fontsize=8,\
                        ha='center',va='bottom',rotation=-30,color=col,\
                        bbox={'facecolor':'w','edgecolor':'w'})
        return T
    

    def add_moist_adiabats(self,T0,P0,do_labels=True,**kwargs):
        # Added by Thomas Chubb
        moist_adiabats=array([moist_ascent(P0,st) for st in T0])
        T=moist_adiabats[:,1,:]
        P=moist_adiabats[0,0,:]

        # gets a pressure level about 3/4 the way up the plot...
        pp=10**(log10(self.pmin**.75*self.pmax**.25))
        xi=where( abs(P-pp)-abs(P-pp).min()<1e-6 )[0][0]

        ndec=log10(self.pmax/pp)/log10(self.pmax/self.pmin)
        tran=self.tmax-self.tmin
        tminl=self.tmin-tran*ndec
        tmaxl=self.tmax-tran*ndec

        if kwargs.has_key('color'): 
            col=kwargs['color']
        else: 
            col='k'
        for tt in T:
            self.plot(tt,P,**kwargs)
            # if (tt[-1]>-60) and (tt[-1]<-10):
            if do_labels:
                if tt[xi]>tmaxl-2: continue
                if tt[xi]<tminl+2: continue
                self.text(tt[xi],P[xi],'%d'%tt[0],ha='center',va='bottom',\
                        fontsize=8, bbox={'facecolor':'w','edgecolor':'w'},color=col)

    def add_mixratio_isopleths(self,w,P,do_labels=True,**kwargs):
        # Added by Thomas Chubb
        e=array([P*ww/(.622+ww) for ww in w])
        T = 243.5/(17.67/log(e/6.112) - 1)
        if kwargs.has_key('color'): 
            col=kwargs['color']
        else: 
            col='k'

        pp=700.
        xi=where( abs(P-pp)-abs(P-pp).min()<1e-6 )[0][0]

        ndec=log10(self.pmax/pp)/log10(self.pmax/self.pmin)
        tran=self.tmax-self.tmin
        tminl=self.tmin-tran*ndec
        tmaxl=self.tmax-tran*ndec

        for tt,mr in zip(T,w):
            self.plot(tt,P.flatten(),**kwargs)
            if do_labels:
                if tt[xi]>tmaxl-2: continue
                if tt[xi]<tminl+2: continue
                if mr*1000<0.1:
                    fmt="%4.2f"
                elif mr*1000<=1.:
                    fmt="%4.1f"
                else:
                    fmt="%d"
                self.text(tt[-1],P[-1],fmt%(mr*1000),\
                        color=col, fontsize=8,ha='center',va='bottom',\
                        bbox={'facecolor':'w','edgecolor':'w'})

# Now register the projection with matplotlib so the user can select
# it.
register_projection(SkewXAxes)

class Sounding(UserDict):
    # Copyright (c) 2013 Thomas Chubb 
    """Utilities to read, write and plot sounding data quickly and without fuss
    
    INPUTS:
    filename:   If creating a sounding from a file, the full file name. The 
        format of this file is quite pedantic and needs to conform 
        to the format given by the University of Wyoming soundings 
        (see weather.uwyo.edu/upperair/sounding.html) 
    data:   Soundings can be made from atmospheric data. This should be 
        in the form of a python dict with (at minimum) the following 
        fields:

        TEMP: dry-bulb temperature (Deg C)
        DWPT: dew point temperature (Deg C)
        PRES: pressure (hPa)
        SKNT: wind speed (knots)
        WDIR: wind direction (deg)

        The following fields are also used, but not required by the 
        plot_skewt routine:

        HGHT (m)
        RELH (%)
        MIXR (g/kg)
        THTA (K)
        THTE (K)
        THTV (K)
    """

    _AllowedKeys=['pres','hght','temp','dwpt','relh','mixr','drct','sknt','thta','thte','thtv']
    

    def __init__(self,filename=None,soundingdata=None):
        UserDict.__init__(self)

        self.soundingdata={}
        if soundingdata is None:
            self.uwyofile(filename)
        else:
            for kk in soundingdata.keys():
                if kk.lower() not in Sounding._AllowedKeys:
                    self[kk]=soundingdata.pop(kk)
                else:
                    dd=soundingdata[kk]
                    if hasattr(dd,'mask'):
                        ddm=dd
                    else:
                        ddm=ma.masked_invalid(dd)
                        ddm=ma.masked_values(ddm,-999)
                    ddm=ma.masked_array(ddm,mask=False).harden_mask()
                    self.soundingdata[kk]=ddm
                if not self.has_key('StationNumber'): self['StationNumber']='(No Number)'
                if not self.has_key('SoundingDate'): self['SoundingDate']='(No Date)'

    def plot_skewt(self,pmax=1050.,pmin=100.,parcel_type='most_unstable',\
            imagename=None, title=None, **kwargs):
        """A wrapper for plotting the skewt diagram for a Sounding instance."""
        
        self.make_skewt_axes(pmax,pmin)
        self.add_profile(**kwargs)
        if parcel_type is not None:
            parcel=self.get_parcel(parcel_type)
            self.lift_parcel(*parcel)
        self.column_diagnostics()

        if isinstance(title, str):
            self.skewxaxis.set_title(title)
        else:
            self.skewxaxis.set_title("%s %s"%(self["StationNumber"],self['SoundingDate']))

        if imagename is not None:
            print("saving figure")
            self.fig.savefig(imagename,dpi=100)

    def add_profile(self,**kwargs):
        """Add a new profile to the SkewT plot.

        This is abstracted from plot_skewt to enable the plotting of
        multiple profiles on a single axis, by updating the data attribute.
        For example:
        >>>
        S=SkewT.Sounding(soundingdata={})
        S.make_skewt_axes()
        S.uwyofile("../examples/94975.2013062800.txt")
        S.add_profile(color="b",bloc=0.5)
        S.uwyofile("../examples/94975.2013070900.txt")
        S.add_profile(color="r",bloc=1.)
        >>>
        Use the kwarg 'bloc' to set the alignment of the wind barbs from 
        the centerline (useful if plotting multiple profiles on the one axis)
        >>>
        Modified 25/07/2013: enforce masking of input soundingdata for this 
        function (does not affect the data attribute).
        """

        # I must be a dummy because I can't make 
        # this work any other way!!
        if kwargs.has_key('bloc'):
            bloc=kwargs.pop('bloc')
        else:
            bloc=0.5
            
        # Need to grab certain elements of an array to thin out wing barbs.
        if kwargs.has_key('skip_style'):
            skip_style=kwargs.pop('skip_style')
        else:
            skip_style=None

        try: 
            pres = ma.masked_invalid(self.soundingdata['pres'])
        except KeyError: 
            raise KeyError, "Pres in hPa (PRES) is required!"

        try: 
            tc=ma.masked_invalid(self.soundingdata['temp'])
        except KeyError: 
            raise KeyError, "Temperature in C (TEMP) is required!"

        try: 
            dwpt=ma.masked_invalid(self.soundingdata['dwpt'])
        except KeyError:
            print "Warning: No DWPT available"
            dwpt=ma.masked_array(zeros(pres.shape),mask=True)

        try:
            sknt=self.soundingdata['sknt']
            
            drct=self.soundingdata['drct']
            rdir = (270.-drct)*(pi/180.)
            uu = ma.masked_invalid(sknt*cos(rdir))
            vv = ma.masked_invalid(sknt*sin(rdir))
        except KeyError:
            print "Warning: No SKNT/DRCT available"
            uu=ma.masked_array(zeros(pres.shape),mask=True)
            vv=ma.masked_array(zeros(pres.shape),mask=True)

        tcprof=self.skewxaxis.plot(tc, pres, zorder=5,**kwargs)
        dpprof=self.skewxaxis.plot(dwpt, pres, zorder=5,**kwargs)

        # this line should no longer cause an exception
        nbarbs=(~uu.mask).sum()

        div = 40 # helps define maximum to skip. Original was 32
        skip=max(1,int(nbarbs/div))
        skip=1 # Don't Skip any levels
        #skip=2 #skip every other

        if kwargs.has_key('color'): 
            bcol=kwargs['color']
        else: 
            bcol='k'

        if kwargs.has_key('alpha'): 
            balph=kwargs['alpha']
        else: 
            balph=1.


        if skip_style=='hrrr':
        # plot fewer in lower atmos, all in upper

            plot_these = np.array([0,5,7,8,9,10,11,12,13,14,15,16,17,18])            
            
            x = np.asarray((zeros(pres.shape)+bloc)-0.5)[plot_these]                        
            y = np.asarray(pres)[plot_these]
            u = np.asarray(uu)[plot_these]
            v = np.asarray(vv)[plot_these]
            self.wbax.barbs(x,y,u,v,\
                    length=5,color=bcol,alpha=balph,lw=.5,\
                    barb_increments=dict(half=2.5, full=5, flag=25),
                    zorder=50)

        elif skip_style=='real':
        # plot a custom amount of barbs
        
            #plot_these = np.array([0,2,3,7,10,12,13,15,16,17,19,20,23]) # June 18 12z           
            plot_these = np.array([0,2,4,5,6,7,8,9,12,13,15,19,20])  # June 19 00z
            
            x = np.asarray((zeros(pres.shape)+bloc)-0.5)[plot_these]                        
            y = np.asarray(pres)[plot_these]
            u = np.asarray(uu)[plot_these]
            v = np.asarray(vv)[plot_these]
            self.wbax.barbs(x,y,u,v,\
                    length=5,color=bcol,alpha=balph,lw=.5,\
                    barb_increments=dict(half=2.5, full=5, flag=25),
                    zorder=50)

        else:
        # Plot only the skipped ones in bottom levels
            self.wbax.barbs((zeros(pres.shape)+bloc)[::skip]-0.5, pres[::skip],\
                    uu[::skip], vv[::skip],\
                    length=6,color=bcol,alpha=balph,lw=.5,\
                    barb_increments=dict(half=2.5, full=5, flag=25),
                    zorder=50)


        self.skewxaxis.other_housekeeping()

        return tcprof

    def make_skewt_axes(self,pmax=1050.,pmin=100.,tmin=-40.,tmax=30.):
        """Set up the skew-t axis the way I like to see it"""
        
        #self.fig = figure(figsize=(3.54,1.8))
        self.fig = figure(figsize=(16,8))
        self.fig.clf()

        self.skewxaxis=self.fig.add_axes([.065,.1,.71,.8], projection='skewx')
        self.skewxaxis.set_yscale('log')
        self.skewxaxis.pmax=pmax
        self.skewxaxis.pmin=pmin
        self.skewxaxis.tmax=tmax
        self.skewxaxis.tmin=tmin

        xticklocs=arange(-80,45,10)
        T0 = xticklocs

        # P=linspace(pmax,pmin,101)
        P=logspace(log10(pmax),log10(pmin),101)

        w = array([0.00001,0.0001,0.0004,0.001, 0.002, 0.004, 0.007, 0.01, 0.016, 0.024, 0.032])
        w = array([0.001, 0.002, 0.004, 0.007, 0.01, 0.016, 0.024, 0.032])
## BKB: Dont add mixratio        
#        self.skewxaxis.add_mixratio_isopleths(w,P[P>=550],color='g',ls='--',alpha=1.,lw=0.5)
        self.skewxaxis.add_dry_adiabats(linspace(210,550,18)-degCtoK,P,color='g',ls='--',alpha=1.,lw=0.3,do_labels=False)
# BKB: Dont add moist adiabat        
        #self.skewxaxis.add_moist_adiabats(linspace(0,44,12),pmax,color='g',ls='--',alpha=1.,lw=0.5)

        self.skewxaxis.set_title("%s %s"%(self['StationNumber'],self['SoundingDate']),fontsize=15)

        self.skewxaxis.other_housekeeping()

        # wind barbs axes
        self.wbax=self.fig.add_axes([0.685,0.1,0.1,0.8],sharey=self.skewxaxis,frameon=False)

        self.wbax.xaxis.set_ticks([],[])
        self.wbax.yaxis.grid(True,ls='-',color='y',lw=0.3)
        for tick in self.wbax.yaxis.get_major_ticks():
            # tick.label1On = False
            pass
        self.wbax.get_yaxis().set_tick_params(size=0,color='y')
        self.wbax.set_xlim(-1.5,1.5)
        self.wbax.get_yaxis().set_visible(False)
        #self.wbax.set_title('m/s',fontsize=7,color='k',ha='right')

        # Set up standard atmosphere height scale on 
        # LHS of plot. 
        majorLocatorKM   = MultipleLocator(2)
        majorLocatorKFT  = MultipleLocator(5)
        minorLocator     = MultipleLocator(1)

        # determine base height from base pressure (nominally 1050 hPa)
        # via hydrostatic equilibrium for standard atmosphere

        # model atmospheric conditions with constant lapse rate and
        # NIST (1013.25hPa and 20C)
        zmin=barometric_equation_inv(0,293.15,101325.,pmax*100.)
        zmax=barometric_equation_inv(0,293.15,101325.,pmin*100.)
        zminf=zmin*3.2808
        zmaxf=zmax*3.2808

        """ Turn off Height Plotter (scale thing on the right side)
        self.kmhax=self.fig.add_axes([0.775,0.1,1e-6,0.8],frameon=True)
        self.kmhax.xaxis.set_ticks([],[])
        self.kmhax.spines['left'].set_color('k')
        self.kmhax.spines['right'].set_visible(False)
        self.kmhax.tick_params(axis='y', colors='k',labelsize=10)
        self.kmhax.set_ylim(zmin*1e-3,zmax*1e-3)
        self.kmhax.set_title("km/kft",fontsize=15)
        self.kmhax.get_yaxis().set_tick_params(which="both",direction='out')
        self.kmhax.yaxis.set_major_locator(majorLocatorKM)
        self.kmhax.yaxis.set_minor_locator(minorLocator)


        self.fthax=self.kmhax.twinx()
        self.fthax.xaxis.set_ticks([],[])
        self.fthax.tick_params(axis='y', colors='k',labelsize=10)
        self.fthax.set_ylim(zminf*1e-3,zmaxf*1e-3)
        self.fthax.get_yaxis().set_tick_params(which="both",direction='out')
        self.fthax.yaxis.set_major_locator(majorLocatorKFT)
        self.fthax.yaxis.set_minor_locator(minorLocator)
        """

    def uwyofile(self,fname):
        """Reads the raw profile data from a Universiy of Wyoming sounding file.

        This is the primary method of IO for SkewT. The University of 
        Wyoming maintains a nice database of global upper air data which is
        kept up-to-date. Given a filename, this method updates the sounding 
        data with the text data in the file.

        NOTES
        1. The input file has to conform *Exactly* to the University of 
           Wyoming file format. This is because I look for data fields at 
           specific places on each line.
        2. I ignore the diagnostics at the end of the file, because the idea 
           is to calculate these myself.
        3. When this no longer works I'll begin reading in a more array-esque 
           way.
        """
        #--------------------------------------------------------------------
        # This *should* be a convenient way to read a uwyo sounding
        #--------------------------------------------------------------------
        fid=open(fname)
        lines=fid.readlines()

        # New: handle whitespace at top of file if present
        while not lines[0].strip():
            lines.pop(0)


        nlines=len(lines)

        lhi=[1, 9,16,23,30,37,46,53,58,65,72]
        rhi=[7,14,21,28,35,42,49,56,63,70,77]


        # initialise output data structure
        output={}

        fields=lines[3].split()
        units=lines[4].split()

        # Handle the file header
        # First line for WRF profiles differs from the UWYO soundings
        header=lines[0]
        if header[:5]=='00000':
            # WRF profile
            self['StationNumber']='00000'
            self['Longitude']=float(header.split()[5].strip(","))
            self['Latitude']=float(header.split()[6])
            self['SoundingDate']=header.split()[-1]
        else:
            self['StationNumber']=header[:5]
            dstr=(' ').join(header.split()[-4:])
            self['SoundingDate']=datetime.strptime(dstr,"%HZ %d %b %Y").strftime("%Y-%m-%d_%H:%M:%S") 

        # This is a data pre-initialisation step. I have used the number of lines minus the number
        # of lines of diagnostics.
        for ff in fields:
            # output[ff.lower()]=zeros((nlines-34))-999.
            output[ff.lower()]=[]

        lcounter=5
        for line,idx in zip(lines[6:],range(nlines)):
            lcounter+=1
            ### Version < 0.1.4
            # try: output[fields[0].lower()][idx]=float(line[lhi[0]:rhi[0]])
            # except ValueError: break

            ### New code. We test for pressure in the first column. 
            ### If there's no pressure, we get out!
            try: 
                output[fields[0].lower()].append(float(line[lhi[0]:rhi[0]]))
            except ValueError: 
                break
            
            for ii in range(1,len(rhi)):
                try: 
                    # Debug only:
                    # print fields[ii].lower(), float(line[lhi[ii]:rhi[ii]].strip())
                    ### Version < 0.1.4
                    # output[fields[ii].lower()][idx]=float(line[lhi[ii]:rhi[ii]].strip())
                     
                    ### New Code. Append to list instead of indexing 
                    ### pre-allocated data. Explicitly allocate -999
                    ### for invalid data (catch ValueError)
                    textdata=line[lhi[ii]:rhi[ii]].strip()
                    output[fields[ii].lower()].append(float(textdata))
                except ValueError: 
                    output[fields[ii].lower()].append(-999.)

        for field in fields:
            ff=field.lower()
            # set mask for missing data
            dd=ma.masked_values(output[ff],-999.)
            dd=ma.masked_array(dd,mask=False)
            dd.harden_mask()
            self.soundingdata[ff]=dd

        return None

    def column_diagnostics(self):
        """Wrapper for column diagnostics"""

        self['Diagnostics']={}
        dtext ="Column:\n"

        self['Diagnostics']['TPW']=self.precipitable_water()
        dtext+="%4s:%6.1f mm"%('TPW', self['Diagnostics']['TPW'])

        self.fig.text(0.825,0.65,dtext,fontname='monospace',va='top',backgroundcolor='white')

    def precipitable_water(self):
        """Calculate Total Precipitable Water (TPW) for sounding.
                                                                           
        TPW is defined as the total column-integrated water vapour. I
        calculate it from the dew point temperature because this is the
        fundamental moisture variable in this module (even though it is RH 
        that is usually measured directly)
        """

        tempk=self.soundingdata['temp']+degCtoK
        prespa=self.soundingdata['pres']*100.
        hghtm=self.soundingdata['hght']

        # Get Water Vapour Mixing Ratio, by calculation
        # from dew point temperature
        try:
            dwptc=self.soundingdata['dwpt']
        except KeyError:
            print "Warning: No MIXR or DWPT for TPW calculation"
            return -999.
        vprespa=VaporPressure(dwptc)
        mixrkg=MixRatio(vprespa,prespa)

        # Calculate density of air (accounting for moisture)
        rho=DensHumid(tempk,prespa,vprespa)

        # Trapezoidal rule to approximate TPW (units kg/m^2==mm)
        tpw=trapz(mixrkg*rho,hghtm)

        return tpw

    def get_cape(self,startp,startt,startdp,totalcape=False):
        """Wrapper for the numerics of calculating CAPE.
                                                                           
        INPUTS:                                                            
        startp,startt,startdp: Definition of the parcel that we will base
                               the calculations on. This can be the output
                               of Sounding.get_parcel() or it can be a user-
                               defined parcel. 
        totalcape [=False]   : Flag defining method of identifying the so-
                               called "Equilibrium Level" (Reference).
                               If False  (default), use the first stable 
                               layer above the LFC, and ignore any CAPE in 
                               unstable layers above this. If True, use all
                               CAPE up to the highest equilibrium level.
                                                                          
        OUTPUTS:                                                           
        P_lcl                : The lifted condensation level (LCL)
        P_lfc                : The level of free convection (LFC). Can be
                               the same as the LCL, or can be NaN if there
                               are no unstable layers.
        P_el                 : The Equilibrium Level, used to determine the
                               CAPE. If totalcape=True, use the highest 
                               equilibrium level, otherwise use the first 
                               stable equilibrium level above the LFC.
        CAPE                 : CAPE calculated from virtual temperature
        CIN                  : CIN calculated from virtual temperature
                                  
        HINT:                     
        parcel=S.get_parcel('mu') 
        lcl,lfc,el,cape,cin=get_cape(*parcel)
        """
        from numpy import interp
        assert startt>=startdp,"Not a valid parcel. Check Td<Tc"

        # fundamental environmental variables
        pres=self.soundingdata['pres']
        temp=self.soundingdata['temp']

        # Get Sub-LCL traces
        presdry,tempdry,tempiso=dry_ascent(startp,startt,startdp,nsteps=101)

        # make lcl variables explicit
        P_lcl=presdry[-1]
        T_lcl=tempdry[-1]

        # Now lift a wet parcel from the intersection point
        # preswet=linspace(P_lcl,100,101)
        preswet,tempwet=moist_ascent(P_lcl,T_lcl,nsteps=101)

        # tparcel is the concatenation of tempdry and 
        # tempwet, and so on.
        tparcel=concatenate((tempdry,tempwet[1:]))
        pparcel=concatenate((presdry,preswet[1:]))
        dpparcel=concatenate((tempiso,tempwet[1:]))

        # Interpolating the environmental profile onto the 
        # parcel pressure coordinate
        # tempenv=interp(preswet,pres[::-1],temp[::-1])
        ## NEW, for total column:
        tempenv=interp(pparcel,pres[::-1],temp[::-1])

        # now solve for the equlibrium levels above LCL
        # (all of them, including unstable ones)
        # eqlev,stab=solve_eq(preswet[::-1],(tempwet-tempenv)[::-1])
        # NEW, for total column:
        # On second thought, we don't really want/need
        # any equilibrium levels below LCL
        # eqlev,stab=solve_eq(pparcel[::-1],(tparcel-tempenv)[::-1])
        # This is equivalent to the old statement :
        eqlev,stab=solve_eq(pparcel[pparcel<=P_lcl][::-1],\
                (tparcel-tempenv)[pparcel<=P_lcl][::-1])

        # Sorting index by decreasing pressure
        I=argsort(eqlev)[::-1]
        eqlev=eqlev[I]; stab=stab[I]


        # temperatures at the equilibrium level
        # tempeq=interp(eqlev,preswet[::-1],tempenv[::-1])
        ## NEW, for total column:
        tempeq=interp(eqlev,pparcel[::-1],tparcel[::-1])

        # This helps with debugging
        # for ii,eq in enumerate(eqlev):
            # print "%5.2f  %5.2f  %2d"%(eq,tempeq[ii],stab[ii])

        # need environmental temperature at LCL
        tenv_lcl=interp(P_lcl,pparcel[::-1],tempenv[::-1])

        isstab=where(stab==1.,True,False)
        unstab=where(stab==1.,False,True)

        if eqlev.shape[0]==0:
            # no unstable layers in entire profile
            # because the parcel never crosses the tenv
            P_lfc=nan
            P_el=nan
        elif T_lcl>tenv_lcl:
            # check LCL to see if this is unstable
            P_lfc=P_lcl
            if totalcape is True:
                P_el=eqlev[isstab][-1]
            else:
                P_el=eqlev[isstab][0]
        elif eqlev.shape[0]>1:
            # Parcel is stable at LCL so LFC is the 
            # first unstable equilibrium level and 
            # "EQ" level is the first stable equilibrium 
            # level
            P_lfc=eqlev[unstab][0]
            if totalcape is True:
                P_el=eqlev[isstab][-1]
            else:
                P_el=eqlev[isstab][0]
        else:
            # catch a problem... if there is only
            # one eqlev and it's unstable (this is 
            # unphysical), then it could be a vertical
            # resolution thing. This is a kind of 
            # "null" option
            if isstab[0]:
                P_el=eqlev[isstab][0]
                P_lfc=nan
            else:
                P_lfc=nan
                P_el=nan

        if isnan(P_lfc):
            return P_lcl,P_lfc,P_el,0,0

        # need to handle case where dwpt is not available 
        # above a certain level for any reason. Most simplest 
        # thing to do is set it to a reasonably low value; 
        # this should be a conservative approach!
        dwpt=self.soundingdata['dwpt'].copy().soften_mask()
        # raise ValueError
        if dwpt[(pres>=P_el).data*(pres<P_lfc).data].mask.any():
            print "WARNING: substituting -200C for masked values of DWPT in this sounding"
        dwpt[dwpt.mask]=-200
        # dwptenv=interp(preswet,pres[::-1],dwpt[::-1])
        # NEW:
        dwptenv=interp(pparcel,pres[::-1],dwpt[::-1])

        hght=self.soundingdata['hght']
        if hght[(pres>=P_el).data].mask.any():
            raise NotImplementedError,\
                    "TODO: Implement standard atmosphere to substitute missing heights"
        # hghtenv=interp(preswet,pres[::-1],self.soundingdata['hght'][::-1])
        # NEW:
        hghtenv=interp(pparcel,pres[::-1],self.soundingdata['hght'][::-1])

        # Areas of POSITIVE Bouyancy
        cond1=(tparcel>=tempenv)*(pparcel<=P_lfc)*(pparcel>P_el)
        # Areas of NEGATIVE Bouyancy
        if totalcape is True:
            cond2=(tparcel<tempenv)*(pparcel>P_el)
        else:
            cond2=(tparcel<tempenv)*(pparcel>P_lfc)
        # Do CAPE calculation
        # 1. Virtual temperature of parcel... remember it's saturated above LCL.
        # e_parcel=VaporPressure(tempwet)
        # Tv_parcel=VirtualTemp(tempwet+degCtoK,preswet*100.,e_parcel)
        # e_env=VaporPressure(dwptenv)
        # Tv_env=VirtualTemp(tempenv+degCtoK,preswet*100.,e_env)
        # TODO: Implement CAPE calculation with virtual temperature
        # (This will affect the significant level calculations as well!!)
        # e_parcel=VaporPressure(dpparcel)
        # Tv_parcel=VirtualTemp(tparcel+degCtoK,pparcel*100.,e_parcel)
        # e_env=VaporPressure(dwptenv)
        # Tv_env=VirtualTemp(tempenv+degCtoK,pparcel*100.,e_env)
        # CAPE=trapz(9.81*(Tv_parcel[cond1]-Tv_env[cond1])/Tv_env[cond1],hghtenv[cond1])
        # CIN=trapz(9.81*(Tv_parcel[cond2]-Tv_env[cond2])/Tv_env[cond2],hghtenv[cond2])

        CAPE=trapz(9.81*(tparcel[cond1]-tempenv[cond1])/(tempenv[cond1] + 273.15),hghtenv[cond1])
        CIN=trapz(9.81*(tparcel[cond2]-tempenv[cond2])/(tempenv[cond2] + 273.15),hghtenv[cond2])

        if False:
           print "%3s  %7s  %7s  %7s  %7s  %7s  %7s  %7s  %7s"%\
                   ("IX", "PRES", "TPARCEL", "DPPARCE", "TENV",\
                   "DPENV", "TV PARC", "TV ENV", "HEIGHT")
           for ix,c2 in enumerate(cond2):
               if c2:
                   print "%3d  %7.3f  %7.3f  %7.3f  %7.3f  %7.3f  %7.3f  %7.3f"+\
                           "  %7.3f"%(ix,pparcel[ix],tparcel[ix],dpparcel[ix],\
                           tempenv[ix],dwptenv[ix],Tv_parcel[ix],Tv_env[ix],hghtenv[ix])
        return P_lcl,P_lfc,P_el,CAPE,CIN

    def lift_parcel(self,*args,**kwargs):
        """Do a lifted parcel analysis on the sounding data"""

        from numpy import interp

        if 'totalcape' in kwargs:
            totalcape=kwargs.pop('totalcape')
        else:
            totalcape=False

        # Stuff for plotting
        # zorder
        zo=4
        # trace colour
        col=[.6,.6,.6]

        if len(args)==4:
            startp,startt,startdp,ptype=args
        elif len(args)==3:
            startp,startt,startdp=args
            ptype=''
        else:
            raise NotImplementedError,"expected 3 or 4 arguments"


        # Get Sub-LCL traces
        presdry,tempdry,tempiso=dry_ascent(startp,startt,startdp)
        T_lcl=tempdry[-1]

        # Parcel diagnostics
        P_lcl,P_lfc,P_el,CAPE,CIN=self.get_cape(startp,startt,startdp,totalcape=totalcape)

        # Get moist ascent traces
        preswet,tempwet=moist_ascent(P_lcl,T_lcl)

        # tparcel is the concatenation of tempdry and 
        # tempwet, and so on.
        tparcel=concatenate((tempdry,tempwet[1:]))
        pparcel=concatenate((presdry,preswet[1:]))

        T_lfc=interp(P_lfc,preswet[::-1],tempwet[::-1])
        T_el=interp(P_el,preswet[::-1],tempwet[::-1])

        # fundamental environmental variables
        pres=self.soundingdata['pres']
        temp=self.soundingdata['temp']
        hght=self.soundingdata['hght']
        dwpt=self.soundingdata['dwpt'].copy().soften_mask()
        dwpt[dwpt.mask]=dwpt.min()

        # interpolate to preswet coordinates
        tempenv=interp(pparcel,pres[::-1],temp[::-1])

        # Plot traces below LCL
        self.skewxaxis.plot(tempdry,presdry,color=col,lw=2,zorder=zo)
        self.skewxaxis.plot(tempiso,presdry,color=col,lw=2,zorder=zo)
        self.skewxaxis.plot(T_lcl,P_lcl,ls='',marker='o',mec=col,mfc=col,zorder=zo)
        # Plot trace above LCL
        self.skewxaxis.plot(tempwet,preswet,color=col,lw=2,zorder=zo)
        # Plot LFC and EL
        self.skewxaxis.plot(T_lfc,P_lfc,ls='',marker='o',mew=2,mec='b',mfc='None',zorder=zo)
        self.skewxaxis.plot(T_el,P_el,ls='',marker='o',mew=2,mec='r',mfc='None',zorder=zo)

        if not isnan(P_lfc):
            # Hatch areas of POSITIVE Bouyancy
            cond1=(tparcel>=tempenv)*(pparcel<=P_lfc)*(pparcel>P_el)
            self.skewxaxis.fill_betweenx(pparcel,tparcel,tempenv,where=cond1,\
                    color="none",hatch='XXX',edgecolor='k',zorder=zo)
            # Hatch areas of NEGATIVE Bouyancy
            if totalcape is True:
                cond2=(tparcel<tempenv)*(pparcel>P_el)
            else:
                cond2=(tparcel<tempenv)*(pparcel>P_lfc)
            self.skewxaxis.fill_betweenx(pparcel,tparcel,tempenv,where=cond2,\
                    color="none",hatch='///',edgecolor='r',zorder=zo)

        # Add text to sounding
        dtext ="Parcel: %s\n"%ptype.upper()
        dtext+="Ps  :%6.1fhPa\n"%startp
        dtext+="TCs :  %4.1fC\n"%startt
        dtext+="TDs :  %4.1fC\n"%startdp
        dtext+="-------------\n"
        dtext+="Plcl:%6.1fhPa\n"%P_lcl
        dtext+="Tlcl:  %4.1fC\n"%T_lcl
        dtext+="Plfc:%6.1fhPa\n"%P_lfc
        dtext+="P_el:%6.1fhPa\n"%P_el
        dtext+="CAPE:%6.1fJ\n"%CAPE
        dtext+="CIN: %6.1fJ"%CIN

        if False:
            h_lcl=interp(P_lcl,pres[::-1],hght[::-1])
            h_lfc=interp(P_lfc,pres[::-1],hght[::-1])
            h_el=interp(P_el,pres[::-1],hght[::-1])
            dtext+="\n-------------\n"
            dtext+="Hlcl:%6.1fm\n"%h_lcl
            dtext+="Hlfc:%6.1fm\n"%h_lfc
            dtext+="H_el:%6.1fm\n"%h_el



        self["Parcel"]={\
                "Ps":startp,\
                "TCs":startt,\
                "TDs":startdp,\
                "Plcl":P_lcl,\
                "Tlcl":T_lcl}

        print "\n---- Lifted Parcel Quantities ----"
        print dtext

        self.fig.text(0.825,0.895,dtext,fontname="monospace",va='top',backgroundcolor='white')
        draw()

    def get_parcel(self,method='ml'):
        """Automatically generate a parcel based on the sounding characteristics
        INPUTS
        method ['mu']   : Parcel type. Choose from the following
                          Mixed Layer  : 'ml'
                          Surface Based: 'sb'
                          Most Unstable: 'mu'
        depth           : Both the mixed layer and the most unstable parcel 
                          require a threshold on the depth of the layer used 
                          to determine the parcel
        OUTPUTS
        (pres,temp,dwpt): The parcel characteristics 
        """

        self.do_thermodynamics()

        if method=='most_unstable' or method=='mu':
            return self.most_unstable_parcel()
        elif method=='surface' or method=='sb':
            return self.surface_parcel()
        if method=='mixed_layer' or method=='ml':
            return self.mixed_layer_parcel()
        else:
            raise NotImplementedError

    def surface_parcel(self):
        """Return ACUTAL lowest parcel, handling frequent missing data from lowest levels"""
        pres=self.soundingdata["pres"]
        temp=self.soundingdata["temp"]
        assert self.soundingdata.has_key('dwpt'), "Moisture needed for parcel calculation! Add DWPT"
        dwpt=self.soundingdata["dwpt"]

        ii=0
        while True:
            if dwpt.mask[ii] or temp.mask[ii]:
                ii+=1
            else:
                return pres[ii],temp[ii],dwpt[ii],'sb'

    def most_unstable_parcel(self,depth=300):
        """Return a parcel representing conditions for the most unstable 
        level in the lowest <depth> hPa"""

        pres=self.soundingdata['pres']
        temp=self.soundingdata['temp']
        dwpt=self.soundingdata['dwpt']
        thta=self.soundingdata['thta']

        cape=zeros(pres.shape)

        for ii in range((pres>pres[0]-depth).sum()):
            if temp.mask[ii]:
                continue
            if dwpt.mask[ii]:
                continue
            theparcel=pres[ii],temp[ii],dwpt[ii]
            try:
                thecape=self.get_cape(*theparcel,totalcape=True)[-2]
            except ValueError: 
                # this is raised when get_cape fails to find
                # equilibrium levels, which happens when the 
                # parcel doesn't "completely" intersect the 
                # sounding profile.
                continue
            cape[ii]=thecape
            # print "%7.2f  %7.2f  %7.2f  %7.2f"%(pres[ii],temp[ii],dwpt[ii],thecape)

        if cape.max()==0.:
            return self.surface_parcel()
        
        # choose max cape
        I=where(cape==cape.max())[0][0]

        # need to descend along adiabat!
        # convert parcel to equivalent surface parcel
        # thetheta=thta[I]
        # parceltemp=(temp[I]+degCtoK)*(pres[0]/pres[I])**(Rs_da/Cp_da)-degCtoK
        # the_e=VaporPressure(dwpt[I])
        # themixr=MixRatio(the_e,pres[I]*100)
        # parcele=MixR2VaporPress(themixr,pres[0]*100)
        # parceldwpt=DewPoint(parcele)
        # return pres[0],parceltemp,parceldwpt,'mu'

        # return conditions at the mu level.
         
        return pres[I],temp[I],dwpt[I],'mu'

  
    def mixed_layer_parcel(self,depth=100):
        """Returns parameters for a parcel initialised by:
        1. Surface pressure (i.e. pressure of lowest level)
        2. Surface temperature determined from mean(theta) of lowest <depth> mbar
        3. Dew point temperature representative of lowest <depth> mbar

        Inputs:
        depth (mbar): depth to average mixing ratio over
        """

        pres=self.soundingdata["pres"]
        temp=self.soundingdata["temp"]
        dwpt=self.soundingdata["dwpt"]

        pres0,temp0,dwpt0,null=self.surface_parcel()

        # identify the layers for averaging
        layers=pres>(pres0-depth)
        
        # average theta over mixheight to give
        # parcel temperature
        thta_mix=Theta(temp[layers]+degCtoK,pres[layers]*100.).mean()
        temp_s=TempK(thta_mix,pres0*100)-degCtoK

        # average mixing ratio over mixheight
        vpres=VaporPressure(dwpt)
        mixr=MixRatio(vpres,pres*100)
        mixr_mix=mixr[layers].mean()
        vpres_s=MixR2VaporPress(mixr_mix,pres0*100)

        # surface dew point temp
        dwpt_s=DewPoint(vpres_s)

        # print "----- Mixed Layer Parcel Characteristics -----"
        # print "Mixed layer depth                     : %5d mb "%depth
        # print "Mean mixed layer potential temperature: %5.1f K"%thta_mix
        # print "Mean mixed layer mixing ratio         : %5.2f g/kg"%(mixr_mix*1e3)

        return pres0,temp_s,dwpt_s,'ml'

        raise NotImplementedError

    def do_thermodynamics(self):

        assert self.soundingdata.has_key('temp'), "Temperature needed for thermodynamics! Add TEMP"
        assert self.soundingdata.has_key('pres'), "Pressure needed for thermodynamics! Add PRES"
        assert self.soundingdata.has_key('dwpt'), "Moisture needed for thermodynamics! Add DWPT"

        # primary variables
        prespa=self.soundingdata['pres']*100.
        tempc=self.soundingdata['temp']
        tempk=tempc+degCtoK
        dwptc=self.soundingdata['dwpt']

        # secondary variables
        e=VaporPressure(dwptc)
        esat=VaporPressure(tempc)

        # assign/extract other variables
        if not self.soundingdata.has_key('thta'):
            self.soundingdata['thta']=Theta(tempk,prespa)
            
        if not self.soundingdata.has_key('thte'):
            self.soundingdata['thte']=ThetaE(tempk,prespa,e)

        if not self.soundingdata.has_key('thtv'):
            self.soundingdata['thtv']=ThetaV(tempk,prespa,e)

        if not self.soundingdata.has_key('relh'):
            self.soundingdata['relh']=100.*e/esat

        return 

def solve_eq(preswet,func):
    """Solve the peicewise-linear stability of a parcel

    INPUTS: variables from the most ascent of a parcel
    preswet: pressure
    func   : piecewise linear function to solve (tw-te)

    OUTPUTS:
    solutions: zeros of the function (tw-te)
    stability: indication of the stability of this solution.

    NOTE ABOUT STABILITY
    Stability is the sign of (d(func)/dP). So if you have used tw-te
    like you were supposed to, d(tw-te)/dP>0 means this is a stbale 
    equilibrium level (flip the sign to envision d(tw-te)/dz).
    """

    from numpy import sign, diff

    # Sorry to be annoying but I'm going to force you to use
    # a monotonically increasing variable
    print diff(preswet)
    assert (sign(diff(preswet))==1).all(), "Use a monotonically increasing abscissa"

    # Identify changes in sign of function
    dsign=sign(func)
    isdiff=zeros(dsign.shape,dtype=bool)
    isdiff[1:]=abs(diff(dsign)).astype(bool)

    # shift to get the value on the other side
    # of the x-axis
    shift=zeros(dsign.shape,dtype=bool)
    shift[:-1]=isdiff[1:]; shift[-1]=isdiff[0]

    # solve by linear interpolation between 
    # values points
    sols=zeros((isdiff.sum()))
    stab=zeros((isdiff.sum()))
    for ii in range(isdiff.sum()):
        f0=func[isdiff][ii]
        f1=func[shift][ii]
        p0=preswet[isdiff][ii]
        p1=preswet[shift][ii]
        slope=(f1-f0)/(p1-p0)
        sols[ii]=p0-f0/slope
        stab[ii]=sign(slope)

    ### Debug with plots
    # fig=figure()
    # ax=fig.add_subplot(111)
    # ax.plot(preswet,func)
    # ax.plot(sols,zeros(sols.shape),ls='',marker='o')
    # ax.plot(preswet[isdiff],func[isdiff],ls='',marker='+',mew=2)
    # ax.plot(preswet[shift],func[shift],ls='',marker='x',mew=2)
    # ax.grid(True)
    # show()

    return sols,stab
        
def dry_ascent(startp,startt,startdp,nsteps=101):
    from numpy import interp
    #--------------------------------------------------------------------
    # Lift a parcel dry adiabatically from startp to LCL.
    # Init temp is startt in C, Init dew point is stwrtdp,
    # pressure levels are in hPa    
    #--------------------------------------------------------------------

    assert startdp<=startt

    if startdp==startt:
        return array([startp]),array([startt]),array([startdp]),

    # Pres=linspace(startp,600,nsteps)
    Pres=logspace(log10(startp),log10(600),nsteps)

    # Lift the dry parcel
    T_dry=(startt+degCtoK)*(Pres/startp)**(Rs_da/Cp_da)-degCtoK 

    # Mixing ratio isopleth
    starte=VaporPressure(startdp)
    startw=MixRatio(starte,startp*100)
    e=Pres*startw/(.622+startw)
    T_iso=243.5/(17.67/log(e/6.112)-1)

    # Solve for the intersection of these lines (LCL).
    # interp requires the x argument (argument 2)
    # to be ascending in order!
    P_lcl=interp(0,T_iso-T_dry,Pres)
    T_lcl=interp(P_lcl,Pres[::-1],T_dry[::-1])

    # presdry=linspace(startp,P_lcl)
    presdry=logspace(log10(startp),log10(P_lcl),nsteps)

    tempdry=interp(presdry,Pres[::-1],T_dry[::-1])
    tempiso=interp(presdry,Pres[::-1],T_iso[::-1])


    return presdry,tempdry,tempiso

def moist_ascent(startp,startt,ptop=10,nsteps=501):
    #--------------------------------------------------------------------
    # Lift a parcel moist adiabatically from startp to endp.
    # Init temp is startt in C, pressure levels are in hPa    
    #--------------------------------------------------------------------
    
    # preswet=linspace(startp,ptop,nsteps)
    preswet=logspace(log10(startp),log10(ptop),nsteps)
    temp=startt
    tempwet=zeros(preswet.shape);tempwet[0]=startt
    for ii in range(preswet.shape[0]-1):
        delp=preswet[ii]-preswet[ii+1]
        temp=temp+100*delp*GammaW(temp+degCtoK,(preswet[ii]-delp/2)*100)
        tempwet[ii+1]=temp

    return preswet,tempwet

if __name__=='__main__':

    if len(sys.argv)==1 or sys.argv[1]=="example1":
        # Do the original examples in the "examples" directory
        examples=("94975.2013070200","94975.2013070900")
        parcels=((1004.,17.4,8.6),(1033.,10.7,-0.9),)
        for ex,pc in zip(examples,parcels):
            sounding=Sounding("./examples/%s.txt"%ex)
            sounding.make_skewt_axes()
            sounding.add_profile(color='r',lw=2)
            sounding.lift_parcel(*pc)
            sounding.column_diagnostics()
            # sounding.fig.savefig("./examples/%s.png"%ex)

    elif sys.argv[1]=="example2":
        # These are some exampels I used in development
        examples=("bna_day1","bna_day1")
        totalcape=(True,False)
        for ex,tc in zip(examples,totalcape):
            sounding=Sounding("./examples/%s.txt"%ex)
            sounding.make_skewt_axes()
            sounding.add_profile(lw=2)
            pc=sounding.get_parcel('mu')
            sounding.lift_parcel(*pc,totalcape=tc)
            # if totalcape is True:
                # sounding.fig.savefig("./examples/%s_totalcape.png"%ex)
            # else:
                # sounding.fig.savefig("./examples/%s_textbookcape.png"%ex)
        
    elif sys.argv[1]=="example3":
        # These examples are some severe weather days in 
        # Australia! Play with the different parcel definitions
        # examples=('94578.2008111612','94578.2008111612','94578.2008111612',)
        examples=('94610.2010032200','94610.2010032200','94610.2010032200',)
        # examples=('94866.2010030600','94866.2010030600','94866.2010030600',)
        parcel_types=('mu','ml','sb')

        for ex,pt in zip(examples,parcel_types):
            sounding=Sounding("./examples/%s.txt"%ex)
            sounding.plot_skewt(parcel_type=pt)
            # sounding.fig.savefig("./examples/%s_%s.png"%(ex,pt))

    elif sys.argv[1]=='example4':
        # Do each of the Aus soundings with a custom parcel
        examples=('94578.2008111612', '94610.2010032200', '94866.2010030600',)
        parcels=((1014.,23.,19.,'user'),(1014.,25,18,'user'),(1000,21,16,'user'))

        for ex,pc in zip(examples,parcels):
            sounding=Sounding("./examples/%s.txt"%ex)
            sounding.make_skewt_axes()
            sounding.add_profile(lw=2)
            sounding.lift_parcel(*pc,totalcape=False)
            # sounding.fig.savefig("./examples/%s_%s.png"%(ex,pc[-1]))
    
    elif sys.argv[1]=='example5':
        # Do each of the Aus soundings with a custom parcel
        examples=("sounding_high_tropo",)

        sounding=Sounding("./examples/%s.txt"%examples[0])
        sounding.make_skewt_axes(tmin=-50,tmax=40,pmin=50)
        sounding.add_profile(lw=2)
        pc=sounding.most_unstable_parcel()
        sounding.lift_parcel(*pc,totalcape=False)
            # sounding.fig.savefig("./examples/%s_%s.png"%(ex,pc[-1]))


    else:
        sounding=Sounding(sys.argv[1])
        sounding.plot_skewt(color='r')
    
    show()

    

