
import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import interp1d

import lueftungstool.lib.helper as helper

def t_c_cummean(C0,C_stat,LWR,t_i):
    c_t=(C0-C_stat)/LWR/t_i*(1-np.exp(-LWR*t_i))+C_stat
    return c_t

def t_gw_calc(C0,C_stat,LWR,t_max,n_max,CO2_Grenzwert,quantiles,size):
    n_i = np.array([np.arange(1, n_max+1)]*size).T
    t_i = t_max*n_i/n_max
    c_t=t_c_cummean(C0,C_stat,LWR,t_i)
    a = c_t.shape[0] - np.argmin(c_t[::-1]>CO2_Grenzwert,axis=0)
    return a*t_max/n_max, np.quantile(c_t,quantiles,axis=1).T

def t_c_inst(C0,C_stat,LWR,t):
    return (C0-C_stat)*np.exp(-LWR*t)+C_stat

def t_c_inst_ode(t, c, c_a, Vdot1, Vdot2, V, ts, t1, t2, CO2_Emi):
    Vdot = Vdot1

    t0 = t-ts
    if t0>0:
        tt = t0 % (t1 + t2)
        if tt>0:
            Vdot = Vdot2
        if tt-t1/t2 > 0:
            Vdot = Vdot1

    dcdt = ((c_a-c)/1e6*Vdot + CO2_Emi/1000)/V*1e6
    return dcdt

def t_c_inst_ode2(t, c, c_a, Vdot1, Vdot2, V, state, CO2_Emi, c_Grenzwert, epsilon_c):
    if c[0] > c_Grenzwert:
        state["lueften"] = True

    Vdot = Vdot1
    if state["lueften"]:
        Vdot = Vdot2

    dcdt = ((c_a-c)/1e6*Vdot + CO2_Emi/1000)/V*1e6

    if state["lueften"] and abs(dcdt) < epsilon_c:
        state["lueften"] = False

    return dcdt


def C0_calc_clip(C0,C_stat,LWR,t):
    return np.max([t_c_inst(C0,C_stat,LWR,t),C_stat],axis=0)

def n50room(n50,Fn50,air_permeability,window_area,volume):
    n50_window = air_permeability*(50/100)**(2/3)*window_area/volume
    n50Max = 2
    return Fn50*(n50Max*n50-n50_window)+n50_window

def stack_effect_factor(Ti_avg,R,X,H_stack):
    fs =((1+R/2)/3)*(1-X**2/(2-R)**2)**(3/2)*(9.81*H_stack/(Ti_avg+273))
    return fs

def wind_factor(C,alfa,gama,H_wind,R):
    fw = C*(1-R)**(1/3)*alfa*(H_wind/10)**gama
    return fw

def co2_emission(NrAdu, ActAdu, NrKids, ActKid, AgeKid):
    CO2_Emi_rate_Erw = 18
    CO2_Emi_rate_Kid = 10

    CO2_Emi = (CO2_Emi_rate_Kid+(AgeKid-6)*(CO2_Emi_rate_Erw-CO2_Emi_rate_Kid)/12)*ActKid*NrKids \
        + CO2_Emi_rate_Erw*ActAdu*NrAdu

    return CO2_Emi

def Lueften(LWR_lueften,t_lueften,CO2_Emi,volume,CO2_aussen,CO2_Grenzwert,CO2_Grenzwert2,size):
    c_stat_lueft = (LWR_lueften*volume*CO2_aussen/1e6+CO2_Emi/1000)/(LWR_lueften*volume)*1e6

    C0__GWfix = C0_calc_clip(CO2_Grenzwert2,c_stat_lueft,LWR_lueften,t_lueften)
    C0 = C0_calc_clip(CO2_Grenzwert,c_stat_lueft,LWR_lueften,t_lueften)

    return C0, C0__GWfix

def Infiltration(Ti_avg,T_a,fs,fw,n50,Vol,v_10m):
    # xxx temp find better position for def
    n = 0.66
    roh = 1.247

    ELA = (n50/3600*Vol*(4/50)**n)/np.sqrt(2*4/roh)
    Vdot = ELA*3600*np.sqrt(fs**2*np.abs(Ti_avg-T_a)+fw**2*v_10m**2)
    return Vdot, ELA

def airing(ACH_airing,t_airing,CO2_emi,volume,c_amb,c_start,size):
    c_stat_airing = (ACH_airing*volume*c_amb/1e6+CO2_emi/1000)/(ACH_airing*volume)*1e6
    c_end = c_inst(c_start,c_stat_airing,ACH_airing,t_airing)
    
    #xxx tbd if needed: long if else only for making sure np.max works in any case depending if variables come as array or single value (maybe not even relevant or more elegant solution possible)
    if isinstance(c_end,np.ndarray) and isinstance(c_stat_airing,np.ndarray):  
        if c_end.shape[0] == c_stat_airing.shape[0]:
            c0_rightdim=c_end
            c_stat_airing_rightdim=c_stat_airing
        else:
            print("array dim doesn't fit :check")       #xxx warning /error message are ignored in frontend? can stay or??
    elif isinstance(c_end,np.ndarray) and ~isinstance(c_stat_airing,np.ndarray):
        c0_rightdim=c_end
        c_stat_airing_rightdim=np.ones(c_end.shape[0]).reshape(-1,1)*c_stat_airing
    elif ~isinstance(c_end,np.ndarray) and isinstance(c_stat_airing,np.ndarray):
        c0_rightdim=np.ones(c_stat_airing.shape[0]).reshape(-1,1)*c_end
        c_stat_airing_rightdim=c_stat_airing
    else:
        c_end = np.max([c_end,c_stat_airing])
        return c_end
        
    #c0 = np.max([c_inst(c_start,c_stat_airing,ACH_airing,t_airing),c_stat_airing],axis=1) # max function to make sure that c0 >= c_stat even for strange inputs (had it in xls for some reason)
    c_end = np.max(np.hstack((c0_rightdim,c_stat_airing_rightdim)),axis=1,keepdims=True)
    return c_end

def c_stationary(c_amb,Vdot,CO2_emi):
    return c_amb+CO2_emi/Vdot*1e3

def c_inst(c0,c_stat,ACH,t):
    return (c0-c_stat)*np.exp(-ACH*t)+c_stat

def c_avg(c0,c_stat,ACH,t):
    return (c0-c_stat)/ACH/t*(1-np.exp(-ACH*t))+c_stat


def t_until_th_anaSol(c_threshold,c0,c_stat,ACH,t_obs):
    dt = 0.1 # xxx arbitrary to make time until threshold is reached larger than observation time 
    log_arg = (c_threshold-c_stat)/(c0-c_stat)
    t_until_threshold =  np.where(log_arg > 0, -np.ma.log(np.ma.array(log_arg, mask=(log_arg<=0)))/ACH, t_obs+dt) # mask array needed with where?
    #t_until_threshold2 =  np.where(log_arg > 0, -np.log(log_arg)/ACH, t_obs+dt)
    return t_until_threshold

def t_until_th_numSol(c_threshold,c_t,t_i):
    dt = 0.1 # xxx arbitrary to make time until threshold is reached larger than observation time 
       
    n_t_until_th = np.argmin(c_t<=c_threshold,axis=1,keepdims=True)      #this method should be more robst, even when first c_t value is > threshold 
    cases_th_not_reached=np.invert(np.any(c_t>c_threshold,axis=1,keepdims=True))
    t_until_th = t_i[0,n_t_until_th]
    t_until_th[cases_th_not_reached] = np.max(t_i,axis=1) + dt
    
    return t_until_th #, n_t_until_th 	# xxx todo: calculate also for cases where c_th isn't reached within t_obs

def calc_result(t_gw,t,c_gw,t_max):
    n_bins = 50
    bins=np.arange(0,n_bins)*t_max/n_bins
    hist,_ = np.histogram(t_gw, bins)

    return {
        "frequency": {
            "x":bins[:-1]*60,
            "y":[hist]
        },
        "timeseries":{
            "x":t,
            "y":c_gw.T
        }
    }

def prep_result(t_until_th,t_i,c_i,c_air,t_obs):
    n_bins = 50     ##xxx tbd define centrally
    bins=np.arange(0,n_bins)*t_obs/n_bins
    hist,_ = np.histogram(t_until_th, bins)

    return {
        "frequency": {
            "x":bins[:-1]*60,
            "y":[hist]
        },
        "timeseries":{
            "x":t_i[0],
            "y":c_i,
        },
        "airing":{
            "x":t_i[0],
            "y":c_air
        }
    }


def c_airing_cycle_prep(t_start, t_duration,t_i):      #xxx change names "air": is for both cycles
    t_air_end=t_start+t_duration
    t_i_array=np.tile(t_i,(t_start.shape[0],1))
    idx_air = (t_i>=t_start) & (t_i<=t_air_end)     #could be moved out of loop for better performance
    idx_air_st=np.minimum(np.searchsorted(t_i.flatten(),t_start.flatten()),t_i.shape[1]-1)      #xxx minimum, because searchsorted will output index max +1, e.g. 1920; exact comp could lead to problems
    t_i_air=t_i_array-t_i_array[list(range(idx_air_st.shape[0])),idx_air_st].reshape(-1,1)
    t_i_air[t_i_air<0]=0        # too avoid very large numbers for t<0
    return t_i_air, idx_air, idx_air_st

def c_airing_cycle(c_i,ACH,t_betw_air,c_stat,c_amb,ACH_airing,t_airing,c_stat_air,t_i,t_obs,calc_method,air_method):
    t_start_air=t_betw_air
    c_i_air = np.copy(c_i)      #regular "=" doesn't copy nested arrays, alternatively use copy.deepcopy 
    jj=1
    while np.any(t_start_air<t_obs):

        # airing period**********************
        t_i_air, idx_air, idx_air_st=c_airing_cycle_prep(t_start_air,t_airing,t_i)
        c_start_air=c_i_air[list(range(idx_air_st.shape[0])),idx_air_st-1].reshape(-1,1)
        c_air = c_inst(c_start_air,c_stat_air,ACH_airing,t_i_air)
        c_i_air[idx_air]=c_air[idx_air]

        # no-airing period*******************
        t_start_noAir=t_start_air + t_airing
        t_i_noAir, idx_noAir, idx_noAir_st=c_airing_cycle_prep(t_start_noAir,t_betw_air,t_i)
        match air_method:
            case "idealC":
                c_start_noAir=np.tile(c_amb,t_start_noAir.shape)
            case "realC":
                c_start_noAir=c_i_air[list(range(idx_noAir_st.shape[0])),idx_noAir_st-1].reshape(-1,1)
            case _:
                print("Warning: airing method not clear: use ideal airing")
                c_start_noAir=np.tile(c_amb,t_start_noAir.shape)

        c_noAir = c_inst(c_start_noAir,c_stat,ACH,t_i_noAir)
        c_i_air[idx_noAir]=c_noAir[idx_noAir]

        # next cycle
        t_start_air=t_start_noAir + t_betw_air
        jj +=1
        if jj>100:
            print(f"Warning: stopped calculation after {jj} airing events")       #xxx message for frontend?
            break
    
    if calc_method=="avgC":
        return helper.movavg(c_i_air)
    return c_i_air


# Functions needed for humidity calculation
#note for formulas: reference temperature for all roh's (vapor density) and all Vdot's (air flows) is Ti, no matter of actual air temperature

def C2K(C):
    """converts from Celcius to Kelvin"""
    K = C + 273.15
    return K

def SatPress(T):
    """saturation pressure according to Magnus Formula with T in Celcius"""
    E = 611.2*np.exp(17.62*T/(243.12+T))
    return E

def VapDens_AA(rH_a,Ti,Ta):
    """calculates vapor density of ambient air (AA)@Ta at indoor temperature Ti"""
    roh_a = rH_a*SatPress(Ta)/(461.5*C2K(Ti))
    return roh_a

def VapDens_IA(H2Oemi,AirFlow,Ti,Ti_min,Ta,rH_a):
    """calculates vapor density with H2O source (H2Oemi) and ventilation (AirFlow@Ti) for air at temperature Ti_min"""
    roh_a = VapDens_AA(rH_a,Ti,Ta)
    roh_i = (H2Oemi/24/AirFlow + roh_a) * C2K(Ti)/C2K(Ti_min) #calculate vapor density for condition Ti, then convert density to Ti_min
    return roh_i

def SurfTemp(fRSI,Ti_min,Ta_damped):
    Tsi = fRSI*(Ti_min-Ta_damped)+Ta_damped
    return Tsi

def WatAct(VapDens,Ti_min,Tsi):
    aw = VapDens*461.5*C2K(Ti_min)/SatPress(Tsi)
    return aw

def MouldRisk_old(aw,limit):    #nicht mehr benoetigt
    MR=np.count_nonzero(aw > limit)/aw.size
    return MR

def ReqAirFlow(H2OEmi,aw_limit,Ti,Tsi,Ta,rH_a):
    roh_a = VapDens_AA(rH_a,Ti,Ta)
    Vdot_req = H2OEmi/24/(aw_limit*SatPress(Tsi)/461.5/C2K(Ti)-roh_a)
    return Vdot_req

def ReqELA(Vdot_req,Ti,Ta,v_10m,fs,fw):
    ELA=Vdot_req/3600/np.sqrt(fs**2*np.abs(Ti-Ta)+fw**2*v_10m**2)*10000
    return ELA

def MouldRisk(fRSI,H2Oemi,Vdot_tot,Vdot_inf,Ti,Ti_min,Ta,Ta_damped,rH_a,v_10m,fs,fw,aw_limit,Perc_accept):
    roh_i=VapDens_IA(H2Oemi,Vdot_tot,Ti,Ti_min,Ta,rH_a)
    Tsi=SurfTemp(fRSI,Ti_min,Ta_damped)
    aw=WatAct(roh_i,Ti_min,Tsi)
    
    Vdot_req_tot=ReqAirFlow(H2Oemi,aw_limit,Ti,Tsi,Ta,rH_a)
    Vdot_req_wInf = np.maximum(np.zeros(Vdot_req_tot.size), Vdot_req_tot-Vdot_inf) #ACHTUNG: hier leichte Abweichung zu xls (da wird fuer Abwesenheit Vdot_inf auf Ti_abs umgerechnet? Fehler? check?)
    Frac_Inf_insuff=np.count_nonzero(Vdot_req_wInf > 0)/Vdot_req_wInf.size
    
    Vdot_req_wInfandWin=np.maximum(np.zeros(Vdot_req_tot.size),Vdot_req_tot-Vdot_tot) #ACHTUNG: hier leichte Abweichung zu xls (da wird fuer Abwesenheit Vdot_inf auf Ti_abs umgerechnet? Fehler? check?) 
    Vdot_add=np.quantile(Vdot_req_wInfandWin,Perc_accept)
    ELA_req_wInfandWin=ReqELA(Vdot_req_wInfandWin,Ti,Ta,v_10m,fs,fw)
    ELA_add=np.quantile(ELA_req_wInfandWin,Perc_accept)
    
    MR=np.count_nonzero(aw > aw_limit)/aw.size
    return MR,ELA_add,Vdot_add,Frac_Inf_insuff,Vdot_req_tot,aw

def H2O_emission(H2Osource_area_abs, H2Osource_area, H2Osource_pers, area_home, pers_home):
    H2Oemi_abs = H2Osource_area_abs * area_home * 24 / 1000
    H2Oemi_pre = (H2Osource_area * area_home + H2Osource_pers * pers_home) * 24 / 1000

    return H2Oemi_abs, H2Oemi_pre

def humidity_calculation(Vol_Unit, n50_Unit, fRSI, H2Oemi_abs, H2Oemi_pre, Ti_avg, Ti_abs, Ti_min, T_a, T_a_damped, v_10m, rH_a, fs, fw, ACH_airing_home, airing_duration_home, Vdot_add):
    result = {}

    #T_a_damped now defined concurrently with T_a and passed through

    #tbd:in code
    aw_limit=0.8
    Perc_accept=0.99

    #calculation of air flows
    Vdot_Inf = Infiltration(Ti_avg,T_a,fs,fw,n50_Unit,Vol_Unit,v_10m)
    Vdot_Win = ACH_airing_home*airing_duration_home/60/24*Vol_Unit
    Vdot_Tot=Vdot_Inf+Vdot_Win+Vdot_add
    result["Vdot_Inf"] = helper.result_stats(Vdot_Inf)
    result["Vdot_Tot"] = helper.result_stats(Vdot_Tot)

    #mould risk calculation: absence
    MouldRisk_abs,ELA_acc_abs,Vdot_acc_abs,Frac_Inf_insuff_abs,Vdot_req_abs,aw_abs=MouldRisk(fRSI,H2Oemi_abs,Vdot_Tot-Vdot_Win,Vdot_Inf,Ti_avg,Ti_abs,T_a,T_a_damped,rH_a,v_10m,fs,fw,aw_limit,Perc_accept)
    result["MouldRisk_abs"] = MouldRisk_abs
    result["Vdot_req_abs"] = helper.result_stats(Vdot_req_abs)
    result["Frac_Inf_insuff_abs"] = Frac_Inf_insuff_abs
    result["Vdot_acc_abs"] = helper.signif(Vdot_acc_abs,2)
    result["ELA_acc_abs"] = helper.signif(ELA_acc_abs,2)

    #mould risk calculation: presence
    MouldRisk_pre,ELA_acc_pre,Vdot_acc_pre,Frac_Inf_insuff_pre,Vdot_req_pre,aw_pre=MouldRisk(fRSI,H2Oemi_pre,Vdot_Tot,Vdot_Inf,Ti_avg,Ti_min,T_a,T_a_damped,rH_a,v_10m,fs,fw,aw_limit,Perc_accept)
    result["MouldRisk_pre"] = MouldRisk_pre
    result["Vdot_req_pre"] = helper.result_stats(Vdot_req_pre)
    result["Frac_Inf_insuff_pre"] = Frac_Inf_insuff_pre
    result["Vdot_acc_pre"] = helper.signif(Vdot_acc_pre,2)
    result["ELA_acc_pre"] = helper.signif(ELA_acc_pre,2)

    Vdot_req = Vdot_req_abs+Vdot_req_pre
    LWR_Tot = Vdot_Tot/Vol_Unit
    LWR_Inf = Vdot_Inf/Vol_Unit
    LWR_req = Vdot_req/Vol_Unit

    result["plot"] = {}

    n_bins = 70
    for i, (tot,inf,req), xmax in zip(
            ["Vdot", "ACR"],
            [[Vdot_Tot, Vdot_Inf, Vdot_req], [LWR_Tot, LWR_Inf, LWR_req]],
            [Vdot_Tot.mean(), LWR_Tot.mean()]
        ):
        bins=np.arange(0,n_bins)/n_bins*xmax*3
        hist_tot,_ = np.histogram(np.clip(tot,bins[0],bins[-1]), bins)
        hist_inf,_ = np.histogram(np.clip(inf,bins[0],bins[-1]), bins)
        hist_req,_ = np.histogram(np.clip(req,bins[0],bins[-1]), bins)

        result["plot"][i] = {}
        result["plot"][i]["x"] = bins[:-1]
        result["plot"][i]["y"] = [hist_tot, hist_inf, hist_req]

    n_bins = 50
    bins=np.arange(0,n_bins)/n_bins
    for i,aw in zip(["abs","pre"], [aw_abs,aw_pre]):
        hist_aw,_ = np.histogram(np.clip(aw,bins[0],bins[-1]), bins)

        result["plot"][i] = {}
        result["plot"][i]["x"] = bins[:-1]
        result["plot"][i]["y"] = [hist_aw]

    result["MouldRisk"] = np.max([MouldRisk_abs,MouldRisk_pre])
    result["Vdot_acc"] = helper.signif(np.max([Vdot_acc_abs,Vdot_acc_pre]),2)
    result["ELA_acc"] = helper.signif(np.max([ELA_acc_abs,ELA_acc_pre]),2)

    return result

def co2_calculation(
        n50, T_a, v_10m, fs, fw, t_obs, volume, ACH_airing, t_airing, Ti_avg, CO2_emi, c_threshold, quantiles, size = 1000
    ):
    
    # allow for user entry
    Vdot_const = 0  # xxx interface to be implemented
    #define ambient CO2 conc xxx check for better location
    c_amb = 450

    # determine infiltration air flow
    Vdot, ELA = Infiltration(Ti_avg,T_a,fs,fw,n50,volume,v_10m)
    Vdot += Vdot_const
    Vdot = Vdot.reshape(-1,1)
    volume= volume.reshape(-1,1)
    ACH = Vdot/volume
    ACH_airing = ACH_airing.reshape(-1,1)
    Vdot_airing = ACH_airing*volume
    ACH_airing = ACH_airing.reshape(-1,1)
    CO2_emi=CO2_emi.reshape(-1,1)
    t_airing = t_airing.reshape(-1,1)

    c_stat = c_stationary(c_amb,Vdot,CO2_emi)
    c_stat_air = c_stationary(c_amb,Vdot_airing,CO2_emi)
      
    n_max=192*10   #tbd xxx define differently
    n_i = np.arange(1, n_max+1)
    #t_i = t_obs*n_i/n_max
    t_i = np.linspace(0,t_obs,n_max+1)[1:].reshape(1,-1)

    #eval_qua=0.5    #xxx tbd better defintion
    #c_instC_idealC0_med=np.quantile(c_instC_idealC0,eval_qua,axis=0)
    
    ## instant concentration and ideal airing 11111111111111111111111111111
    # calculate time between airing (analytically, not further used)
    t_instC_idealC0_a=t_until_th_anaSol(c_threshold,c_amb,c_stat,ACH,t_obs)

    # calculate evolution of concentration
    c_instC_idealC0 = c_inst(c_amb,c_stat,ACH,t_i)
    # select (5) quantiles of the time evolution curves
    c_instC_idealC0_qua, c_instC_idealC0_qidx = helper.quantile_pos(c_instC_idealC0, quantiles)
    # calculate time between airing (numerically)
    t_instC_idealC0=t_until_th_numSol(c_threshold,c_instC_idealC0,t_i)
    # calculate evolution of concentration accounting for airing events (for all cases)
    c_instC_idealC0_air=c_airing_cycle(c_instC_idealC0,ACH,t_instC_idealC0,c_stat,c_amb,ACH_airing,t_airing,c_stat_air,t_i,t_obs,"instC","idealC")
    # select (5) quantiles for airing evolution
    c_instC_idealC0_air_qua=c_instC_idealC0_air[c_instC_idealC0_qidx,:]
    # prepare histogramm and other plot data
    res_instC_idealC0=prep_result(t_instC_idealC0,t_i,c_instC_idealC0_qua,c_instC_idealC0_air_qua,t_obs)

    ## average concentration and ideal airing 222222222222222222222222222
    c_avgC_idealC0 = c_avg(c_amb,c_stat,ACH,t_i)
    c_avgC_idealC0_qua, c_avgC_idealC0_qidx = helper.quantile_pos(c_avgC_idealC0, quantiles)
    t_avgC_idealC0=t_until_th_numSol(c_threshold,c_avgC_idealC0,t_i)

    c_avgC_idealC0_air=c_airing_cycle(c_instC_idealC0,ACH,t_avgC_idealC0,c_stat,c_amb,ACH_airing,t_airing,c_stat_air,t_i,t_obs,"avgC","idealC")
    c_avgC_idealC0_air_qua=c_avgC_idealC0_air[c_avgC_idealC0_qidx,:]
    res_avgC_idealC0=prep_result(t_avgC_idealC0,t_i,c_avgC_idealC0_qua,c_avgC_idealC0_air_qua,t_obs)

    ## instant concentration and real airing 3333333333333333333333333333
    c0_instC = airing(ACH_airing,t_airing,CO2_emi,volume,c_amb,c_threshold,size)
    c_instC_realC0 = c_inst(c0_instC,c_stat,ACH,t_i)
    c_instC_realC0_qua, c_instC_realC0_qidx = helper.quantile_pos(c_instC_realC0, quantiles)
    t_instC_realC0=t_until_th_numSol(c_threshold,c_instC_realC0,t_i)
    t_instC_realC0_a=t_until_th_anaSol(c_threshold,c0_instC,c_stat,ACH,t_obs)

    c_instC_realC0_air=c_airing_cycle(c_instC_realC0,ACH,t_instC_realC0,c_stat,c_amb,ACH_airing,t_airing,c_stat_air,t_i,t_obs,"instC","realC")
    c_instC_realC0_air_qua=c_instC_realC0_air[c_instC_realC0_qidx,:]
    res_instC_realC0=prep_result(t_instC_realC0,t_i,c_instC_realC0_qua,c_instC_realC0_air_qua,t_obs)

    ## average concentration and real airing 4444444444444444444444444444
    c0_avgC = c0_instC                  #initial guess: use c0 based on c_inst, i.e. c0 calculated when c_inst hits c_threshold  
    t_avgC_realC0 = t_avgC_idealC0       #initial guess: use time until threshold from ideal airing
    ii=0
    ii_max=100          # xxx tbd move to diff loc 
    c0_convCrit_Lim=5   # xxx tbd move to diff loc
    while ii < ii_max:
        c_instC_avgC4thresh = c_inst(c0_avgC,c_stat,ACH,t_avgC_realC0)
        c0_avgC_new = airing(ACH_airing,t_airing,CO2_emi,volume,c_amb,c_instC_avgC4thresh,size)
        c_avgC_realC0 = c_avg(c0_avgC_new,c_stat,ACH,t_i)
        t_avgC_realC0=t_until_th_numSol(c_threshold,c_avgC_realC0,t_i)
        
        c0_convCrit=abs(c0_avgC_new-c0_avgC) < c0_convCrit_Lim
        if all(c0_convCrit):
            print(f"Convergence achieved after {ii} iterations.")       #xxx message for frontend?
            break

        c0_avgC=c0_avgC_new
        ii +=1
    else:
        print(f"Maximum number of iterations ({ii}) reached without convergence.")      #xxx message for frontend?

    c_avgC_realC0_qua, c_avgC_realC0_qidx = helper.quantile_pos(c_avgC_realC0, quantiles)
    c_avgC_realC0_air=c_airing_cycle(c_instC_realC0,ACH,t_avgC_realC0,c_stat,c_amb,ACH_airing,t_airing,c_stat_air,t_i,t_obs,"avgC","realC")
    c_avgC_realC0_air_qua=c_avgC_realC0_air[c_avgC_realC0_qidx,:]
    res_avgC_realC0=prep_result(t_avgC_realC0,t_i,c_avgC_realC0_qua,c_avgC_realC0_air_qua,t_obs)
    
    ## final evaluation**************************
    # definition which evaluation and which quantile is used for evaluation if ventilation is sufficient
    # average concentration (because Austria's guideline value is defined this way) and realstic airing is applied
    # the median (50th quantile) is used a decision criteria, i.e. up to 50% of the cases might not meet the IAQ guidelinne with reasonable airing intervall
    t_qua4eval=0.5      # xxx parameter, tbd define somewhere else
    t_until_th_eval = np.quantile(t_avgC_realC0,t_qua4eval)*60
    t_reasonable = t_obs*60
    airing_acceptable = t_until_th_eval >= t_reasonable #>= used instead of > in xls version
    
    result = {
        "airing_acceptable": airing_acceptable,
        "t_reasonable": t_reasonable,
        "t_avgC_realC0": helper.result_stats(t_avgC_realC0*60),
        "t_instC_realC0": helper.result_stats(t_instC_realC0*60),
        "t_avgC_idealC0": helper.result_stats(t_avgC_idealC0*60),
        "t_instC_idealC0": helper.result_stats(t_instC_idealC0*60),
        "ELA": helper.result_stats(ELA),
        "Vdot": helper.result_stats(Vdot),
        "ACR": helper.result_stats(ACH),
        "CO2_stat": helper.result_stats(c_stat),
        
        "t_instC_idealC0_a": helper.result_stats(t_instC_idealC0_a*60),
        "t_instC_realC0_a": helper.result_stats(t_instC_realC0_a*60),
        "c0_instC": helper.result_stats(c0_instC),
        "c0_avgC": helper.result_stats(c0_avgC),
        "c_instC_avgC4thresh": helper.result_stats(c_instC_avgC4thresh),
        "plot": {
            "instC_idealC0": res_instC_idealC0,
            "avgC_idealC0": res_avgC_idealC0,
            "instC_realC0": res_instC_realC0,
            "avgC_realC0": res_avgC_realC0,            
        },
    }

    return result
