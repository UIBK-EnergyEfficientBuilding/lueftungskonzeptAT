
import json
import os.path

import numpy as np
from scipy.stats import beta as scipy_beta

import lueftungstool.lib.params as params
import lueftungstool.lib.helper as helper


def beta_scaled(alpha,beta,min_value,max_value,size):
    return np.random.default_rng().beta(a=alpha, b=beta, size=size)*(max_value-min_value)+min_value

def fixed_or_beta_scaled(key, param, field, size):
    if field is None:
        return beta_scaled(*param[key],size=size)
    else:
        return np.array([field]*size)

def float_or_beta_scaled(field, param, size):
    try:
        float(field)
        return np.array([field]*size)
    except ValueError:
        return beta_scaled(*param[field],size=size)

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


weather_data = None
if os.path.exists("weather_data.json"):
    with open("weather_data.json", "r") as inp:
        weather_data = json.load(inp)
        for k1 in weather_data:
            for k2 in weather_data[k1]:
                weather_data[k1][k2] = np.array(weather_data[k1][k2])

def weather(location, size):
    if weather_data:
        d = weather_data[location]
        choice = np.random.choice(np.arange(0,len(d["T_a"]),1), size)

        T_a = d["T_a"][choice]
        v_10m = d["v_10m"][choice]
        rH = d["rH"][choice]
        MvgAvgWin=24            #xxx move to config: moving average window to calculate damped T_a for fRSI calculation 
        T_a_damped = d["T_a"][choice-MvgAvgWin]

    else:                       #xxx only to avoid errors when executing without weatherfile
        T_a = params.location2T_a[location]
        v_10m = params.location2v_10m[location]
        rH = params.location2rH[location]
        T_a_damped = T_a          #not correct, just to allow calculation 

    return T_a, T_a_damped, v_10m, rH 

def calc_lage(location, inputs, Shield, Terr, quantiles, size):
    Shield = params.name2Shield_class[Shield] if Shield is not None else None
    Terr = params.name2Terr_class[Terr] if Terr is not None else None

    #Lage/Exposition
    Shield = np.round(fixed_or_beta_scaled(location, params.location2Shield, Shield, size))
    Terr = np.round(fixed_or_beta_scaled(location, params.location2Terr, Terr, size))

    inputs["terrain_class"] = helper.result_stats_integer(Terr)
    inputs["shielding_class"] = helper.result_stats_integer(Shield)

    C = map_values(Shield,params.Shield_class2C)
    alfa = map_values(Shield,params.Terr_class2alfa)
    gama = map_values(Terr,params.Terr_class2gama)

    return C, alfa, gama


def building_standard(building_n50,inputs,window_class,size):
    n50 = float_or_beta_scaled(building_n50, params.n50_map, size=size)
    inputs["building_n50"] = helper.result_stats(n50)

    window_class = params.name2window_class[window_class] if window_class is not None else None
    window_class = np.round(fixed_or_beta_scaled(building_n50, params.window_class, window_class, size=size))
    inputs["window_class"] = helper.result_stats_integer(window_class)
    air_permeability = map_values(window_class,params.window_class2air_permeability)

    return n50,air_permeability

def get_thermalbridges_label(building_n50):
    thermalbridges_label = params.map_n502waermebruecken.get(building_n50)
    return thermalbridges_label

def calc_avg_temperatures(thermalbridges_label, inputs, Ti_avg, size):
    Ti_avg = fixed_or_beta_scaled(thermalbridges_label, params.waermebruecken2Ti_avg, Ti_avg, size=size)
    inputs["Ti_avg"] = helper.result_stats(Ti_avg)
    return Ti_avg

def calc_temperatures(thermalbridges_label, inputs, thermalbridges, Ti_min, Ti_abs, size):

    if thermalbridges is None:
        thermalbridges = thermalbridges_label

    Ti_min = fixed_or_beta_scaled(thermalbridges_label, params.waermebruecken2Ti_min, Ti_min, size=size)
    Ti_abs = fixed_or_beta_scaled(thermalbridges_label, params.waermebruecken2Ti_abs, Ti_abs, size=size)
    inputs["Ti_min"] = helper.result_stats(Ti_min)
    inputs["Ti_abs"] = helper.result_stats(Ti_abs)

    fRSI = float_or_beta_scaled(thermalbridges, params.waermebruecken2fRSI, size=size)
    inputs["thermalbridges"] = helper.result_stats(fRSI)

    return Ti_min, Ti_abs, fRSI

def n50factor(size):
    Fn50 = beta_scaled(*params.Fn50, size=size)
    return Fn50

def calc_LBL_model_factors(building_n50, building_type, size):
    H_wind_min = 3
    H_stack = beta_scaled(*params.gebaeudeart2H_Bldg[building_type],size=size)
    H_wind = np.max(
        [[H_wind_min]*size, H_stack*beta_scaled(*params.gebaeudeart2H_WindRel[building_type],size=size)],
        axis=0
    )

    if not helper.castorfalse(building_n50, float):
        H_StackRel = beta_scaled(*params.H_StackRel[building_n50], size)
    else:
        H_StackRel = np.array([0]*size)

    H_stack_min = 3
    H_stack = np.max([[H_stack_min]*size, H_stack*H_StackRel], axis=0)

    return H_wind, H_stack

def H2Oonly_building_standard(building_n50,inputs,H_unit,size):
    H_unit = fixed_or_beta_scaled(building_n50, params.H_unit, H_unit, size)
    inputs["H_unit"] = helper.result_stats(H_unit)

    return H_unit

def H2Oonlyparams(building_type, inputs, area_home, pers_home, size):
    area_home = fixed_or_beta_scaled(building_type, params.WNF, area_home, size)
    inputs["area_home"] = helper.result_stats(area_home)

    if pers_home is None:
        OccDens = beta_scaled(*params.OccDens[building_type], size)
        pers_home = area_home/OccDens
    inputs["pers_home"] = helper.result_stats(pers_home)

    return area_home, pers_home

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

    inputs["H_Rm"] = helper.result_stats(H_Rm)
    inputs["A_Rm"] = helper.result_stats(A_Rm)
    inputs["window_area"] = helper.result_stats(window_area)

    t_max = params.room_type2t_max[room_type]
    CO2_Grenzwert = params.room_type2CO2_Grenzwert[room_type]

    return H_Rm, A_Rm, window_area, t_max, CO2_Grenzwert

def activity_parameters(ActAdu, ActKid):

    if ActAdu and not isinstance(ActAdu, float):
        ActAdu = params.activity_level[ActAdu]

    if ActKid and not isinstance(ActKid, float):
        ActKid = params.activity_level[ActKid]

    return ActAdu, ActKid

def occupancy_parameters(room_type, inputs, NrAdu = None, ActAdu = None, NrKids = None, ActKid = None, AgeKid = None, size = 1000):
    AgeKid = fixed_or_beta_scaled(room_type, params.raumart2AgeKid, AgeKid, size)

    ActKid = fixed_or_beta_scaled(room_type, params.raumart2ActKid, ActKid, size=size)
    NrKids = np.round(fixed_or_beta_scaled(room_type, params.raumart2Nr_Kid, NrKids, size=size))
    ActAdu = fixed_or_beta_scaled(room_type, params.raumart2ActAdu, ActAdu,size=size)
    NrAdu = np.round(fixed_or_beta_scaled(room_type, params.raumart2Nr_Adu, NrAdu,size=size))

    inputs["AgeKid"] = helper.result_stats(AgeKid)
    inputs["ActKid"] = helper.result_stats(ActKid)
    inputs["NrKids"] = helper.result_stats_integer(NrKids)
    inputs["ActAdu"] = helper.result_stats(ActAdu)
    inputs["NrAdu"] = helper.result_stats_integer(NrAdu)

    return NrAdu, ActAdu, NrKids, ActKid, AgeKid

def airing_room(airing_type_room, inputs, airing_duration_room, size):

    ACH_airing_room = beta_scaled(*params.luefungsart2WinACH[airing_type_room],size=size)
    airing_duration_room = fixed_or_beta_scaled(airing_type_room, params.luefungsart2WinDur, airing_duration_room, size=size)
    inputs["airing_duration_room"] = helper.result_stats(airing_duration_room)

    return ACH_airing_room, airing_duration_room

def airing_home(airing_type_home, inputs, airing_duration_home, size):
    ACH_airing_home = beta_scaled(*params.luefungsart2WinACH[airing_type_home],size=size)
    airing_duration_home = fixed_or_beta_scaled(airing_type_home, params.luefungsart2WinDur2, airing_duration_home,size=size)
    inputs["airing_duration_home"] = helper.result_stats(airing_duration_home)

    return ACH_airing_home, airing_duration_home

def H2O_sources(H2Osource_category, inputs, H2Osource_area_abs, H2Osource_area, H2Osource_pers, size):
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
    inputs["H2Osource_area_abs"] = helper.result_stats(H2Osource_area_abs)
    inputs["H2Osource_area"] = helper.result_stats(H2Osource_area)
    inputs["H2Osource_pers"] = helper.result_stats(H2Osource_pers)

    return H2Osource_area_abs, H2Osource_area, H2Osource_pers
