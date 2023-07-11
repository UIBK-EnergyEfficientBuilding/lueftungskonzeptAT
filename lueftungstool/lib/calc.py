
import numpy as np

import lueftungstool.lib.params as params

def beta_scaled(alpha,beta,min_value,max_value,size):
    return np.random.default_rng().beta(a=alpha, b=beta, size=size)*(max_value-min_value)+min_value

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

def t_gw_calc(C0,C_stat,LWR,t_max,n_max,CO2_Grenzwert,quantiles,size):
    n_i = np.array([np.arange(1, n_max+1)]*size).T
    c_t=(C0-C_stat)/LWR/(t_max*n_i/n_max)*(1-np.exp(-LWR*(t_max*n_i/n_max)))+C_stat
    return np.argmax(c_t>CO2_Grenzwert,axis=0)*t_max/n_max, np.quantile(c_t,quantiles,axis=1).T

def C0_calc(C0,C_stat,LWR,t):
    return (C0-C_stat)*np.exp(-LWR*t/60)+C_stat

def C0_calc_clip(C0,C_stat,LWR,t):
    return np.max([C0_calc(C0,C_stat,LWR,t),C_stat],axis=0)


def calc_standort(standort):
    T_a = params.standort2TNorm[standort]
    v_10m = 3.2
    return T_a, v_10m

def calc_lage(standort, size):
    #Lage/Exposition
    Shield = np.round(beta_scaled(*params.standort2Shield[standort],size=size))
    Terr = np.round(beta_scaled(*params.standort2Terr[standort],size=size))

    C = map_values(Shield,params.Shield_class2C)
    alfa = map_values(Shield,params.Terr_class2alfa)
    gama = map_values(Terr,params.Terr_class2gama)

    return C, alfa, gama

def calc_dichtheit(gebaeude_n50, gebaeudeart, size):
    #Gebäudichtheit
    n50 = beta_scaled(*params.n50_map[gebaeude_n50],size=size)

    H_Bldg = beta_scaled(*params.gebaeudeart2H_Bldg[gebaeudeart],size=size)
    Windeff = np.max(
        [[3]*size, H_Bldg*beta_scaled(*params.gebaeudeart2H_WindRel[gebaeudeart],size=size)],
        axis=0
    )
    return n50, H_Bldg, Windeff

def Undichtheiten(size):
    #Verteilung Undichtheiten
    LeakDistr_1 = beta_scaled(5,7,0,1,size=size) #Anteil Decke+Boden 5,7,0,1
    LeakDistr_2 = beta_scaled(4,4,0,1,size=size) #Anteil Decke von Anteil Decke+Boden 4,4,0,1

    Anteil_Decke = LeakDistr_1*LeakDistr_2
    Anteil_Boden = LeakDistr_1*(1-LeakDistr_2)

    R = Anteil_Decke+Anteil_Boden
    X = Anteil_Decke-Anteil_Boden

    return R,X

def Raum(raumart, H_Rm, A_Rm, size):
    if not A_Rm:
        A_Rm = beta_scaled(*params.raumart2A_Rm[raumart],size=size)
    else:
        A_Rm = np.array([A_Rm]*size)
    if not H_Rm:
        H_Rm = beta_scaled(*params.raumart2H_Rm[raumart],size=size)
    else:
        H_Rm = np.array([H_Rm]*size)

    return H_Rm, A_Rm

def Luftwechsel(Ti_avg,T_a,C,alfa,gama,Windeff,R,X,Kamineff,n50_Raum,H_Rm,A_Rm,Vdot_const,v_10m):
    fw = C*(1-R)**(1/3)*alfa*(Windeff/10)**gama
    fs =((1+R/2)/3)*(1-X**2/(2-R)**2)**(3/2)*(9.81*Kamineff/(Ti_avg+273))

    n = 0.66
    roh = 1.247

    ELA_tot = (n50_Raum/3600*A_Rm*H_Rm*(4/50)**n)/np.sqrt(2*4/roh)
    Vdot = ELA_tot*3600*np.sqrt(fs**2*(Ti_avg-T_a)+fw**2*v_10m**2) + Vdot_const
    LWR = Vdot/(A_Rm*H_Rm)

    return Vdot,LWR

def co2_emission(raumart,size):
    AgeKid = beta_scaled(*params.raumart2AgeKid[raumart],size=size)

    ActKid = beta_scaled(*params.raumart2ActKid[raumart],size=size)
    NrKids = np.round(beta_scaled(*params.raumart2Nr_Kid[raumart],size=size))
    ActAdu = beta_scaled(*params.raumart2ActAdu[raumart],size=size)
    NrAdu = np.round(beta_scaled(*params.raumart2Nr_Adu[raumart],size=size))

    CO2_Emi_rate_Erw = 18
    CO2_Emi_rate_Kid = 10

    CO2_Emi = (CO2_Emi_rate_Kid+(AgeKid-6)*(CO2_Emi_rate_Erw-CO2_Emi_rate_Kid)/12)*ActKid*NrKids \
        + CO2_Emi_rate_Erw*ActAdu*NrAdu

    return CO2_Emi

def Lueften(luefungsart,CO2_Emi,A_Rm,H_Rm,CO2_aussen,CO2_Grenzwert,CO2_Grenzwert2,size):
    LWR_lueften = beta_scaled(*params.luefungsart2WinACH[luefungsart],size=size)
    t_lueften = beta_scaled(*params.luefungsart2WinDur[luefungsart],size=size)

    c_stat_lueft = (LWR_lueften*A_Rm*H_Rm*CO2_aussen/1e6+CO2_Emi/1000)/(LWR_lueften*A_Rm*H_Rm)*1e6

    C0__GWfix = C0_calc_clip(CO2_Grenzwert2,c_stat_lueft,LWR_lueften,t_lueften)
    C0 = C0_calc_clip(CO2_Grenzwert,c_stat_lueft,LWR_lueften,t_lueften)

    return C0, C0__GWfix

def calc_result(t_gw,t,c_gw,t_max,quantiles):
    n_bins = 50
    bins=np.arange(0,n_bins)*t_max/n_bins
    hist,_ = np.histogram(t_gw, bins)

    return {
        "Quantile": signif(np.quantile(t_gw,quantiles),2),
        "Häufigkeit": {
            "x":bins[:-1]*60,
            "y":[hist]
        },
        "Mittelwert":{
            "x":t,
            "y":c_gw.T
        }
    }

def calc(
        standort, gebaeude_n50, gebaeudeart, H_Rm, A_Rm, raumart, luefungsart, quantiles, size=1000
    ):
    T_a, v_10m = calc_standort(standort)
    C, alfa, gama = calc_lage(standort, size)
    n50, H_Bldg, Windeff = calc_dichtheit(gebaeude_n50, gebaeudeart, size)
    H_Rm, A_Rm = Raum(raumart, H_Rm, A_Rm, size)
    Ti_avg = beta_scaled(*params.gebaeudeart2Ti_avg["Altbau (mit normalen Wärmebrücken)"],size=size)
    R, X = Undichtheiten(size)

    n50_Raum = n50
    Kamineff = 3
    Vdot_const = 0
    Vdot, LWR = Luftwechsel(
        Ti_avg,T_a,C,alfa,gama,Windeff,R,X,Kamineff,n50_Raum,H_Rm,A_Rm,Vdot_const,v_10m
    )

    CO2_Emi = co2_emission(raumart,size)

    CO2_aussen = 450
    CO2_Grenzwert = 1000
    CO2_Grenzwert2 = 1250 #? CA

    C_stat = (Vdot*CO2_aussen/1e6+CO2_Emi/1000)/Vdot*1e6
    C0, C0__GWfix = Lueften(
        luefungsart,CO2_Emi,A_Rm,H_Rm,CO2_aussen,CO2_Grenzwert,CO2_Grenzwert2,size
    )

    n_max = 192
    t_max = 8 #Schlafzimmer
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
        quantiles
    )

    import matplotlib.pyplot as plt

    plt.figure()
    plt.bar(stats_data_gw_erreicht["Häufigkeit"]["x"], stats_data_gw_erreicht["Häufigkeit"]["y"][0], width=60)
    plt.savefig("Häufigkeit.png")

    plt.figure()
    for i in range(0,5):
        print(i)
        plt.plot(stats_data_gw_erreicht["Mittelwert"]["x"], stats_data_gw_erreicht["Mittelwert"]["y"][i])
    plt.savefig("Mittelwert.png")
    

    #Momentanwert - realistisches Lüften
    log_arg = (CO2_Grenzwert-C_stat)/(C0-C_stat)
    t_gw_periodisch = np.where(log_arg > 0, -np.log(log_arg)/LWR, t_max)

    stats_data_gw_periodisch = calc_result(
        t_gw_periodisch,
        c_quantiles_t_gw_erreicht, #todo
        c_quantiles_gw_erreicht, #todo
        t_max,
        quantiles
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
        quantiles
    )

    #Momentanwert - ideales Lüften
    log_arg = (CO2_Grenzwert-C_stat)/(CO2_aussen-C_stat)
    t_gw_ideal = np.where(log_arg > 0, -np.log(log_arg)/LWR, t_max)

    stats_data_gw_ideal = calc_result(
        t_gw_ideal,
        c_quantiles_t_gw_erreicht, #todo
        c_quantiles_gw_erreicht, #todo
        t_max,
        quantiles
    )

    print(
        f"Zeit bis CO2-Stundenmittelwert={CO2_Grenzwert} ppm - realistisches Lüften [min]:",
        np.quantile(t_gw_erreicht,quantiles)*60
    )
    print(
        f"Zeit bis CO2-Momentanwert={CO2_Grenzwert} ppm - realistisches Lüften [min]:",
        np.quantile(t_gw_periodisch,quantiles)*60
    )
    print(
        f"Zeit bis CO2-Stundenmittelwert={CO2_Grenzwert} ppm - ideales Lüften [min]:",
        np.quantile(t_gw_ueberschritten,quantiles)*60
    )
    print(
        f"Zeit bis CO2-Momentanwert={CO2_Grenzwert} ppm - ideales Lüften [min]:",
        np.quantile(t_gw_ideal,quantiles)*60
    )
    print(
        "CO2 Konzentration im stationären Fall (t→∞) [ppm]:",
        np.quantile(C_stat,quantiles)
    )

    t_gw_erreicht_m = np.quantile(t_gw_erreicht,0.5)*60
    t_zumutbar = t_max*60
    Fensterlueftung = t_gw_erreicht_m>t_zumutbar

    print(f"""
Fensterlüftung praktikabel/zumutbar:                                 {Fensterlueftung}
Weil errechnete Zeit zwischen erforderlichen Fensterlüften [min]:    {t_gw_erreicht_m:.0f} Minuten
Dies ist kürzer als die zumutbare Zeit zwischen Fensterlüften [min]: {t_zumutbar:.0f} Minuten
"""
    )

    return {
        "Fensterlueftung": Fensterlueftung,
        "t_zumutbar": t_zumutbar,
        "t_gw_erreicht": stats_data_gw_erreicht,
        "t_gw_periodisch": stats_data_gw_periodisch,
        "t_gw_ueberschritten": stats_data_gw_ueberschritten,
        "t_gw_ideal": stats_data_gw_ideal,
        "C_stat": signif(np.quantile(C_stat,quantiles),2),
    }
