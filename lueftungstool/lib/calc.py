
import numpy as np
from scipy.stats import beta as scipy_beta

import lueftungstool.lib.params as params

def beta_scaled(alpha,beta,min_value,max_value,size):
    return np.random.default_rng().beta(a=alpha, b=beta, size=size)*(max_value-min_value)+min_value

def fixed_or_beta_scaled(key, param, field, size):
    if not field:
        return beta_scaled(*param[key],size=size)
    else:
        return np.array([field]*size)

def beta_scaled_range(alpha,beta,min_value,max_value,start,stop,size):
    x = np.linspace(start,stop,size)
    return scipy_beta.ppf(np.random.choice(x,size),alpha,beta)*(max_value-min_value)+min_value

def fixed_or_beta_scaled_range(key, param, start, stop, field, size):
    if not field:
        return beta_scaled_range(*param[key], start, stop, size=size)
    else:
        return np.array([field]*size)

def map_values(a, d):
    b = np.copy(a)
    for k, v in d.items():
        b[a==k] = v
    return b

#https://stackoverflow.com/questions/18915378/rounding-to-significant-figures-in-numpy
def signif(x, p):
    x = np.asarray(x)
    x_positive = np.where(np.isfinite(x) & (x != 0), np.abs(x), 10**(p-1))
    mags = 10 ** (p - 1 - np.floor(np.log10(x_positive)))
    return np.round(x * mags) / mags

def result_stats(value,precision=2):
    mean = signif(np.mean(value),precision)
    q = np.quantile(value,[0.05, 0.25, 0.5, 0.75, 0.95])
    error = signif((q[-1] - q[0])/2,precision)
    q = signif(q,precision)
    return {"mean": mean, "error": error, "median":q[2], "quantiles":q}

def result_stats_integer(value,precision=2):
    q = np.quantile(value,[0.05, 0.25, 0.5, 0.75, 0.95])
    return {"min": np.min(value), "max": np.max(value), "quantiles":signif(q,precision)}

def t_gw_calc(C0,C_stat,LWR,t_max,n_max,CO2_Grenzwert,quantiles,size):
    n_i = np.array([np.arange(1, n_max+1)]*size).T
    c_t=(C0-C_stat)/LWR/(t_max*n_i/n_max)*(1-np.exp(-LWR*(t_max*n_i/n_max)))+C_stat
    return np.argmax(c_t>CO2_Grenzwert,axis=0)*t_max/n_max, np.quantile(c_t,quantiles,axis=1).T

def C0_calc(C0,C_stat,LWR,t):
    return (C0-C_stat)*np.exp(-LWR*t/60)+C_stat

def C0_calc_clip(C0,C_stat,LWR,t):
    return np.max([C0_calc(C0,C_stat,LWR,t),C_stat],axis=0)


def weather(location):
    T_a = params.location2T_a[location]
    v_10m = params.location2v_10m[location]
    rH = params.location2rH[location]
    return T_a, v_10m, rH

def calc_lage(location, inputs, Shield, Terr, quantiles, size):
    Shield = params.name2Shield_class[Shield] if Shield is not None else None
    Terr = params.name2Terr_class[Terr] if Terr is not None else None

    #Lage/Exposition
    Shield = np.round(fixed_or_beta_scaled(location, params.location2Shield, Shield, size))
    Terr = np.round(fixed_or_beta_scaled(location, params.location2Terr, Terr, size))

    inputs["terrain_class"] = result_stats_integer(Terr)
    inputs["shielding_class"] = result_stats_integer(Shield)

    C = map_values(Shield,params.Shield_class2C)
    alfa = map_values(Shield,params.Terr_class2alfa)
    gama = map_values(Terr,params.Terr_class2gama)

    return C, alfa, gama

def calc_dichtheit(building_n50, building_type, inputs, quantiles, size):
    #Gebäudichtheit
    n50 = beta_scaled(*params.n50_map[building_n50],size=size)

    inputs["building_n50"] = result_stats(n50)

    H_wind_min = 3
    H_stack_min = 3
    H_Bldg = beta_scaled(*params.gebaeudeart2H_Bldg[building_type],size=size)
    H_wind = np.max(
        [[H_wind_min]*size, H_Bldg*beta_scaled(*params.gebaeudeart2H_WindRel[building_type],size=size)],
        axis=0
    )
    H_stack = np.max([[H_stack_min]*size, H_Bldg*beta_scaled(*params.H_StackRel[building_n50],size=size)], axis=0)

    return n50, H_wind, H_stack

def Undichtheiten(size):
    #Verteilung Undichtheiten
    LeakDistr_1 = beta_scaled(5,7,0,1,size=size) #Anteil Decke+Boden 5,7,0,1
    LeakDistr_2 = beta_scaled(4,4,0,1,size=size) #Anteil Decke von Anteil Decke+Boden 4,4,0,1

    Anteil_Decke = LeakDistr_1*LeakDistr_2
    Anteil_Boden = LeakDistr_1*(1-LeakDistr_2)

    R = Anteil_Decke+Anteil_Boden
    X = Anteil_Decke-Anteil_Boden

    return R,X

def Raum(room_type, inputs, quantiles, H_Rm = None, A_Rm = None, window_area = None, size = 1000):
    A_Rm = fixed_or_beta_scaled(room_type, params.raumart2A_Rm, A_Rm, size)
    H_Rm = fixed_or_beta_scaled(room_type, params.raumart2H_Rm, H_Rm, size)

    if window_area is None:
        WinRat_Rm = beta_scaled(*params.raumart2WinRat_Rm[room_type], size)
        window_area = WinRat_Rm*A_Rm

    inputs["H_Rm"] = result_stats(H_Rm)
    inputs["A_Rm"] = result_stats(A_Rm)
    inputs["window_area"] = result_stats(window_area)

    t_max = params.room_type2t_max[room_type]

    return H_Rm, A_Rm, window_area, t_max

def Infiltration(Ti_avg,T_a,C,alfa,gama,H_wind,R,X,H_stack,n50,Vol,v_10m):
    fw = C*(1-R)**(1/3)*alfa*(H_wind/10)**gama
    fs =((1+R/2)/3)*(1-X**2/(2-R)**2)**(3/2)*(9.81*H_stack/(Ti_avg+273))

    n = 0.66
    roh = 1.247

    ELA_tot = (n50/3600*Vol*(4/50)**n)/np.sqrt(2*4/roh)
    Vdot = ELA_tot*3600*np.sqrt(fs**2*(Ti_avg-T_a)+fw**2*v_10m**2)

    return Vdot,fs,fw

def co2_emission(room_type, inputs, quantiles, NrAdu = None, ActAdu = None, NrKids = None, ActKid = None, AgeKid = None, size = 1000):
    AgeKid = fixed_or_beta_scaled(room_type, params.raumart2AgeKid, AgeKid, size)

    ActKid = fixed_or_beta_scaled(room_type, params.raumart2ActKid, ActKid, size=size)
    NrKids = np.round(fixed_or_beta_scaled(room_type, params.raumart2Nr_Kid, NrKids, size=size))
    ActAdu = fixed_or_beta_scaled(room_type, params.raumart2ActAdu, ActAdu,size=size)
    NrAdu = np.round(fixed_or_beta_scaled(room_type, params.raumart2Nr_Adu, NrAdu,size=size))

    inputs["AgeKid"] = result_stats(AgeKid)
    inputs["ActKid"] = result_stats(ActKid)
    inputs["NrKids"] = result_stats_integer(NrKids)
    inputs["ActAdu"] = result_stats(ActAdu)
    inputs["NrAdu"] = result_stats_integer(NrAdu)

    CO2_Emi_rate_Erw = 18
    CO2_Emi_rate_Kid = 10

    CO2_Emi = (CO2_Emi_rate_Kid+(AgeKid-6)*(CO2_Emi_rate_Erw-CO2_Emi_rate_Kid)/12)*ActKid*NrKids \
        + CO2_Emi_rate_Erw*ActAdu*NrAdu

    return CO2_Emi

def Lueften(LWR_lueften,t_lueften,CO2_Emi,A_Rm,H_Rm,CO2_aussen,CO2_Grenzwert,CO2_Grenzwert2,size):
    c_stat_lueft = (LWR_lueften*A_Rm*H_Rm*CO2_aussen/1e6+CO2_Emi/1000)/(LWR_lueften*A_Rm*H_Rm)*1e6

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


def calc(
        location, building_n50, building_type, inputs, t_max, thermalbridges, H_Rm, A_Rm, Shield, Terr, window_area, window_class, pers_home, airing_type_home, airing_duration_home, airing_type_room, airing_duration_room, Ti_avg, Ti_abs, Ti_min, fRSI, CO2_Emi, area_home, H2Osource_category, H2Osource_area, H2Osource_pers, H2Osource_area_abs, quantiles, size = 1000
    ):
    T_a, v_10m, rH_a = weather(location)
    C, alfa, gama = calc_lage(location, inputs, Shield, Terr, quantiles, size)
    n50, H_wind, H_stack = calc_dichtheit(building_n50, building_type, inputs, quantiles, size)

    if thermalbridges is None:
        thermalbridges = params.map_n502waermebruecken[building_n50]
        inputs["thermalbridges"] = thermalbridges
    Ti_avg = fixed_or_beta_scaled(thermalbridges, params.waermebruecken2Ti_avg, Ti_avg, size=size)
    R, X = Undichtheiten(size)
    inputs["Ti_avg"] = result_stats(Ti_avg)

    window_class = params.name2window_class[window_class] if window_class is not None else None
    window_class = np.round(fixed_or_beta_scaled(building_n50, params.window_class, window_class, size=size))
    inputs["window_class"] = result_stats_integer(window_class)

    air_permeability = map_values(window_class,params.window_class2air_permeability)
    n50_window_room = air_permeability*(50/100)**(2/3)*window_area/(A_Rm*H_Rm)

    n50Max = 2
    Fn50 = beta_scaled(*params.Fn50, size=size)
    n50_room =  Fn50*(n50Max*n50-n50_window_room)+n50_window_room

    Vdot_const = 0  # allow for user entry
    volume_room = A_Rm*H_Rm
    Vdot,_,_ = Infiltration(
        Ti_avg,T_a,C,alfa,gama,H_wind,R,X,H_stack,n50_room,volume_room,v_10m
    )
    Vdot += Vdot_const
    LWR = Vdot/volume_room

    CO2_aussen = 450
    CO2_Grenzwert = 1000
    CO2_Grenzwert2 = 1250 #? CA

    LWR_lueften = beta_scaled(*params.luefungsart2WinACH[airing_type_room],size=size)
    t_lueften = fixed_or_beta_scaled(airing_type_room, params.luefungsart2WinDur, airing_duration_room, size=size)
    inputs["airing_duration_room"] = result_stats(t_lueften)

    C_stat = (Vdot*CO2_aussen/1e6+CO2_Emi/1000)/Vdot*1e6
    C0, C0__GWfix = Lueften(
        LWR_lueften,t_lueften,CO2_Emi,A_Rm,H_Rm,CO2_aussen,CO2_Grenzwert,CO2_Grenzwert2,size
    )

    n_max = 192
    C0_avg2 = C0__GWfix #? CC #genähert

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

    #Momentanwert - realistisches Lüften
    log_arg = (CO2_Grenzwert-C_stat)/(C0-C_stat)
    t_gw_periodisch = np.where(log_arg > 0, -np.log(log_arg)/LWR, t_max)

    stats_data_gw_periodisch = calc_result(
        t_gw_periodisch,
        c_quantiles_t_gw_erreicht, #todo
        c_quantiles_gw_erreicht, #todo
        t_max,
    )

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

    #Momentanwert - ideales Lüften
    log_arg = (CO2_Grenzwert-C_stat)/(CO2_aussen-C_stat)
    t_gw_ideal = np.where(log_arg > 0, -np.log(log_arg)/LWR, t_max)

    stats_data_gw_ideal = calc_result(
        t_gw_ideal,
        c_quantiles_t_gw_erreicht, #todo
        c_quantiles_gw_erreicht, #todo
        t_max,
    )

    t_gw_erreicht_m = np.quantile(t_gw_erreicht,0.5)*60
    t_reasonable = t_max*60
    Fensterlueftung = t_gw_erreicht_m>t_reasonable

    result = {}

  # humidity calculation
    if building_type in params.WNF_list:
        humcalc = True
    else:
        humcalc = False
    if humcalc:
        result["ResH2O"] = {}

        area_home = fixed_or_beta_scaled(building_type, params.WNF, area_home, size)

        inputs["area_home"] = result_stats(area_home)

        source_category_min_max = [0,1] if H2Osource_category is None else params.Feuchtelastkategorie[H2Osource_category]

        H2Osource_area_abs = fixed_or_beta_scaled_range(
            "Quellstärke [g/h] Wohnen bei Abwesenheit",
            params.m_H2Od0,
            *source_category_min_max,
            H2Osource_area_abs,
            size
        )
        H2Osource_area = fixed_or_beta_scaled_range(
            "Quellstärke [g/h] Wohnen Flächenabhängig",
            params.m_H2Od,
            *source_category_min_max,
            H2Osource_area,
            size
        )
        H2Osource_pers = fixed_or_beta_scaled_range(
            "Quellstärke [g/h] Wohnen PersABH",
            params.m_H2Ok,
            *source_category_min_max,
            H2Osource_pers,
            size
        )
        inputs["H2Osource_area_abs"] = result_stats(H2Osource_area_abs)
        inputs["H2Osource_area"] = result_stats(H2Osource_area)
        inputs["H2Osource_pers"] = result_stats(H2Osource_pers)

        if pers_home is None:
            OccDens = beta_scaled(*params.OccDens[building_type], size)
            pers_home = area_home/OccDens
        inputs["pers_home"] = result_stats(pers_home)

        #tbd: through interface
        Vol_Unit = H_Rm * area_home

        Ti_min = fixed_or_beta_scaled(thermalbridges, params.waermebruecken2Ti_min, Ti_min, size=size)
        Ti_abs = fixed_or_beta_scaled(thermalbridges, params.waermebruecken2Ti_abs, Ti_abs, size=size)
        fRSI = fixed_or_beta_scaled(thermalbridges, params.waermebruecken2fRSI, fRSI,size=size)
        inputs["Ti_min"] = result_stats(Ti_min)
        inputs["Ti_abs"] = result_stats(Ti_abs)
        inputs["fRSI"] = result_stats(fRSI)

        H2Oemi_abs = H2Osource_area_abs * area_home * 24 / 1000
        H2Oemi_pre = (H2Osource_area * area_home + H2Osource_pers * pers_home) * 24 / 1000
        inputs["H2Osource_category"] = result_stats(H2Oemi_pre)

        ACH_Win = beta_scaled(*params.luefungsart2WinACH[airing_type_home],size=size)
        Dur_Win = fixed_or_beta_scaled(airing_type_home, params.luefungsart2WinDur2, airing_duration_home,size=size)
        Vdot_add = 0 #additional ventilation air flow (for expert use/interface) tbd:add text in output when active
        inputs["airing_duration_home"] = result_stats(Dur_Win)
        
        #tbd: through functions
        R, X = Undichtheiten(size)
        n50_Unit = n50_room
        Ta_damped= 1.7

        #tbd:in code
        aw_limit=0.8
        Perc_accept=0.99

        #calculation of air flows
        Vdot_Inf,fs,fw= Infiltration(Ti_avg,T_a,C,alfa,gama,H_wind, R, X,H_stack,n50_Unit,Vol_Unit,v_10m)
        Vdot_Win = ACH_Win*Dur_Win/60/24*Vol_Unit
        Vdot_Tot=Vdot_Inf+Vdot_Win+Vdot_add
        result["ResH2O"]["Vdot_Inf"] = result_stats(Vdot_Inf)
        result["ResH2O"]["Vdot_Tot"] = result_stats(Vdot_Tot)

        #mould risk calculation: absence
        MouldRisk_abs,ELA_acc_abs,Vdot_acc_abs,Frac_Inf_insuff_abs,Vdot_req_abs,aw_abs=MouldRisk(fRSI,H2Oemi_abs,Vdot_Tot-Vdot_Win,Vdot_Inf,Ti_avg,Ti_abs,T_a,Ta_damped,rH_a,v_10m,fs,fw,aw_limit,Perc_accept)
        result["ResH2O"]["MouldRisk_abs"] = MouldRisk_abs
        result["ResH2O"]["Vdot_req_abs"] = result_stats(Vdot_req_abs)
        result["ResH2O"]["Frac_Inf_insuff_abs"] = Frac_Inf_insuff_abs
        result["ResH2O"]["Vdot_acc_abs"] = signif(Vdot_acc_abs,2)
        result["ResH2O"]["ELA_acc_abs"] = signif(ELA_acc_abs,2)

        #mould risk calculation: presence
        MouldRisk_pre,ELA_acc_pre,Vdot_acc_pre,Frac_Inf_insuff_pre,Vdot_req_pre,aw_pre=MouldRisk(fRSI,H2Oemi_pre,Vdot_Tot,Vdot_Inf,Ti_avg,Ti_min,T_a,Ta_damped,rH_a,v_10m,fs,fw,aw_limit,Perc_accept)
        result["ResH2O"]["MouldRisk_pre"] = MouldRisk_pre
        result["ResH2O"]["Vdot_req_pre"] = result_stats(Vdot_req_pre)
        result["ResH2O"]["Frac_Inf_insuff_pre"] = Frac_Inf_insuff_pre
        result["ResH2O"]["Vdot_acc_pre"] = signif(Vdot_acc_pre,2)
        result["ResH2O"]["ELA_acc_pre"] = signif(ELA_acc_pre,2)

        Vdot_req = Vdot_req_abs+Vdot_req_pre
        LWR_Tot = Vdot_Tot/Vol_Unit
        LWR_Inf = Vdot_Inf/Vol_Unit
        LWR_req = Vdot_req/Vol_Unit

        result["ResH2O"]["plot"] = {}

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

            result["ResH2O"]["plot"][i] = {}
            result["ResH2O"]["plot"][i]["x"] = bins[:-1]
            result["ResH2O"]["plot"][i]["y"] = [hist_tot, hist_inf, hist_req]

        n_bins = 50
        bins=np.arange(0,n_bins)/n_bins
        for i,aw in zip(["abs","pre"], [aw_abs,aw_pre]):
            hist_aw,_ = np.histogram(np.clip(aw,bins[0],bins[-1]), bins)

            result["ResH2O"]["plot"][i] = {}
            result["ResH2O"]["plot"][i]["x"] = bins[:-1]
            result["ResH2O"]["plot"][i]["y"] = [hist_aw]

        result["ResH2O"]["MouldRisk"] = np.max([MouldRisk_abs,MouldRisk_pre])
        result["ResH2O"]["Vdot_acc"] = signif(np.max([Vdot_acc_abs,Vdot_acc_pre]),2)

    result.update({
        "ResCO2":{
            "airing_acceptable": Fensterlueftung,
            "t_reasonable": t_reasonable,
            "t_avgC_realC0": result_stats(t_gw_erreicht*60),
            "t_instC_realC0": result_stats(t_gw_periodisch*60),
            "t_avgC_idealC0": result_stats(t_gw_ueberschritten*60),
            "t_instC_idealC0": result_stats(t_gw_ideal*60),
            "Vdot": result_stats(Vdot),
            "ACR": result_stats(LWR),
            "CO2_stat": result_stats(C_stat),
            "plot": {
                "t_avgC_realC0": stats_data_gw_erreicht,
                "t_instC_realC0": stats_data_gw_periodisch,
                "t_avgC_idealC0": stats_data_gw_ueberschritten,
                "t_instC_idealC0": stats_data_gw_ideal,
            },
        },
        "inputs": inputs
    })

    return result
