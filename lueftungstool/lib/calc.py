
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

def n50room(n50,Fn50,air_permeability,window_area,A_Rm,H_Rm):
    n50_window_room = air_permeability*(50/100)**(2/3)*window_area/(A_Rm*H_Rm)
    n50Max = 2
    n50_room =  Fn50*(n50Max*n50-n50_window_room)+n50_window_room
    return n50_room

def stack_effect_factor(Ti_avg,R,X,H_stack):
    fs =((1+R/2)/3)*(1-X**2/(2-R)**2)**(3/2)*(9.81*H_stack/(Ti_avg+273))
    return fs

def wind_factor(C,alfa,gama,H_wind,R):
    fw = C*(1-R)**(1/3)*alfa*(H_wind/10)**gama
    return fw

def Infiltration(Ti_avg,T_a,fs,fw,n50,Vol,v_10m):
    n = 0.66
    roh = 1.247

    ELA_tot = (n50/3600*Vol*(4/50)**n)/np.sqrt(2*4/roh)
    Vdot = ELA_tot*3600*np.sqrt(fs**2*(Ti_avg-T_a)+fw**2*v_10m**2)

    return Vdot

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
    ELA=Vdot_req/3600/np.sqrt(fs**2*(Ti-Ta)+fw**2*v_10m**2)*10000
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

def humidity_calculation(Vol_Unit, n50_Unit, fRSI, H2Oemi_abs, H2Oemi_pre, Ti_avg, Ti_abs, Ti_min, T_a, v_10m, rH_a, fs, fw, ACH_airing_home, airing_duration_home):
    result = {}

    #tbd: through interface
    Vdot_add = 0 #additional ventilation air flow (for expert use/interface) tbd:add text in output when active

    #tbd: through functions
    Ta_damped= 1.7

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
    MouldRisk_abs,ELA_acc_abs,Vdot_acc_abs,Frac_Inf_insuff_abs,Vdot_req_abs,aw_abs=MouldRisk(fRSI,H2Oemi_abs,Vdot_Tot-Vdot_Win,Vdot_Inf,Ti_avg,Ti_abs,T_a,Ta_damped,rH_a,v_10m,fs,fw,aw_limit,Perc_accept)
    result["MouldRisk_abs"] = MouldRisk_abs
    result["Vdot_req_abs"] = helper.result_stats(Vdot_req_abs)
    result["Frac_Inf_insuff_abs"] = Frac_Inf_insuff_abs
    result["Vdot_acc_abs"] = helper.signif(Vdot_acc_abs,2)
    result["ELA_acc_abs"] = helper.signif(ELA_acc_abs,2)

    #mould risk calculation: presence
    MouldRisk_pre,ELA_acc_pre,Vdot_acc_pre,Frac_Inf_insuff_pre,Vdot_req_pre,aw_pre=MouldRisk(fRSI,H2Oemi_pre,Vdot_Tot,Vdot_Inf,Ti_avg,Ti_min,T_a,Ta_damped,rH_a,v_10m,fs,fw,aw_limit,Perc_accept)
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
            [Vdot_req.mean(), LWR_Tot.mean()]
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

    return result

def co2_calculation(
        n50_room, T_a, v_10m, fs, fw, t_max, volume_room, ACH_airing_room, airing_duration_room, Ti_avg, CO2_Emi, CO2_Grenzwert, quantiles, size = 1000
    ):

    Vdot_const = 0  # allow for user entry

    Vdot = Infiltration(Ti_avg,T_a,fs,fw,n50_room,volume_room,v_10m)
    Vdot += Vdot_const
    LWR = Vdot/volume_room

    CO2_aussen = 450
    CO2_Grenzwert2 = {1000:1250,1400:1745}[CO2_Grenzwert] #? MC2.CA4 1250 1745 #FIXME

    C_stat = (Vdot*CO2_aussen/1e6+CO2_Emi/1000)/Vdot*1e6
    C0, C0__GWfix = Lueften(
        ACH_airing_room,airing_duration_room/60,CO2_Emi,volume_room,CO2_aussen,CO2_Grenzwert,CO2_Grenzwert2,size
    )

    n_max = 192
    C0_avg2 = C0__GWfix #? CC #genähert

    dt = t_max/n_max

    volume_room_m = np.median(volume_room)
    CO2_Emi_m = np.median(CO2_Emi)

    Vdot1 = np.median(Vdot)
    Vdot2 = np.median(ACH_airing_room)*volume_room_m

    #Stundenmittelwert - realistisches Lüften
    t_gw_erreicht, c_quantiles_gw_erreicht = t_gw_calc(
        C0_avg2,C_stat,LWR,t_max,n_max,CO2_Grenzwert,quantiles,size=size
    )
    c_quantiles_t_gw_erreicht = np.arange(1, n_max+1)*t_max/n_max

    stats_data_gw_erreicht = calc_result(
        t_gw_erreicht,
        c_quantiles_t_gw_erreicht,
        c_quantiles_gw_erreicht,
        t_max,
    )

    t1 = np.median(airing_duration_room)/60
    t2 = np.median(t_gw_erreicht)
    ts = t2

    res = solve_ivp(t_c_inst_ode, [0,t_max], [np.median(C0_avg2)], args=(CO2_aussen, Vdot1, Vdot2, volume_room_m, ts, t1, t2, CO2_Emi_m), max_step=dt)

    lin = interp1d(res.t, helper.cum_mean(res.y[0]))

    stats_data_gw_erreicht["airing"] = {
            "x":c_quantiles_t_gw_erreicht,
            "y":[lin(c_quantiles_t_gw_erreicht)]
    }

    #Momentanwert - realistisches Lüften
    log_arg = (CO2_Grenzwert-C_stat)/(C0-C_stat)
    t_gw_periodisch = np.where(log_arg > 0, -np.log(log_arg)/LWR, t_max)

    n_i = np.array([np.arange(1, n_max+1)]*size).T
    t_i = t_max*n_i/n_max
    c_quantiles_gw_periodisch = np.quantile(t_c_inst(C0_avg2, C_stat, LWR, t_i),quantiles,axis=1).T
    c_quantiles_t_gw_periodisch = np.arange(1, n_max+1)*t_max/n_max

    stats_data_gw_periodisch = calc_result(
        t_gw_periodisch,
        c_quantiles_t_gw_periodisch,
        c_quantiles_gw_periodisch,
        t_max,
    )

    t2 = np.median(t_gw_periodisch)
    ts = t2
    res = solve_ivp(t_c_inst_ode, [0,t_max], [np.median(C0_avg2)], args=(CO2_aussen, Vdot1, Vdot2, volume_room_m, ts, t1, t2, CO2_Emi_m), max_step=dt)

    lin = interp1d(res.t, res.y[0])

    stats_data_gw_periodisch["airing"] = {
            "x":c_quantiles_t_gw_periodisch,
            "y":[lin(c_quantiles_t_gw_periodisch)]
    }

    #Stundenmittelwert - ideales Lüften
    t_gw_ueberschritten, c_quantiles_gw_ueberschritten = t_gw_calc(
        CO2_aussen,C_stat,LWR,t_max,n_max,CO2_Grenzwert,quantiles,size=size
    )
    c_quantiles_t_gw_ueberschritten = np.arange(1, n_max+1)*t_max/n_max

    stats_data_gw_ueberschritten = calc_result(
        t_gw_ueberschritten,
        c_quantiles_t_gw_ueberschritten,
        c_quantiles_gw_ueberschritten,
        t_max,
    )


    epsilon_c = 50
    t2 = np.median(t_gw_ueberschritten)
    ts = t2

    res = solve_ivp(t_c_inst_ode2, [0,t_max], [CO2_aussen], args=(CO2_aussen, Vdot1, Vdot2, volume_room_m, {"lueften":False}, CO2_Emi_m, CO2_Grenzwert, epsilon_c), max_step=dt)

    lin = interp1d(res.t, helper.cum_mean(res.y[0]))

    stats_data_gw_ueberschritten["airing"] = {
            "x":c_quantiles_t_gw_ueberschritten,
            "y":[lin(c_quantiles_t_gw_ueberschritten)]
    }

    #Momentanwert - ideales Lüften
    log_arg = (CO2_Grenzwert-C_stat)/(CO2_aussen-C_stat)
    t_gw_ideal = np.where(log_arg > 0, -np.log(log_arg)/LWR, t_max)

    n_i = np.array([np.arange(1, n_max+1)]*size).T
    t_i = t_max*n_i/n_max
    c_quantiles_gw_ideal = np.quantile(t_c_inst(CO2_aussen, C_stat, LWR, t_i),quantiles,axis=1).T
    c_quantiles_t_gw_ideal = np.arange(1, n_max+1)*t_max/n_max

    stats_data_gw_ideal = calc_result(
        t_gw_ideal,
        c_quantiles_t_gw_ideal,
        c_quantiles_gw_ideal,
        t_max,
    )

    t2 = np.median(t_gw_ideal)
    ts = t2
    res = solve_ivp(t_c_inst_ode2, [0,t_max], [CO2_aussen], args=(CO2_aussen, Vdot1, Vdot2, volume_room_m, {"lueften":False}, CO2_Emi_m, CO2_Grenzwert, epsilon_c), max_step=dt)

    lin = interp1d(res.t, res.y[0])

    stats_data_gw_ideal["airing"] = {
            "x":c_quantiles_t_gw_ideal,
            "y":[lin(c_quantiles_t_gw_ideal)]
    }

    t_gw_erreicht_m = np.quantile(t_gw_erreicht,0.5)*60
    t_reasonable = t_max*60
    Fensterlueftung = t_gw_erreicht_m>t_reasonable

    result = {
        "airing_acceptable": Fensterlueftung,
        "t_reasonable": t_reasonable,
        "t_avgC_realC0": helper.result_stats(t_gw_erreicht*60),
        "t_instC_realC0": helper.result_stats(t_gw_periodisch*60),
        "t_avgC_idealC0": helper.result_stats(t_gw_ueberschritten*60),
        "t_instC_idealC0": helper.result_stats(t_gw_ideal*60),
        "Vdot": helper.result_stats(Vdot),
        "ACR": helper.result_stats(LWR),
        "CO2_stat": helper.result_stats(C_stat),
        "plot": {
            "t_avgC_realC0": stats_data_gw_erreicht,
            "t_instC_realC0": stats_data_gw_periodisch,
            "t_avgC_idealC0": stats_data_gw_ueberschritten,
            "t_instC_idealC0": stats_data_gw_ideal,
        },
    }

    return result
