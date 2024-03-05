#TODO better filename

import lueftungstool.lib.calc as ltool
import lueftungstool.lib.params_lookups as params_lookups
import lueftungstool.lib.helper as helper
from lueftungstool.lib.params import params_mapping, WNF_list

def humcalc(building_type):
    if building_type in WNF_list:
        return True
    else:
        return False

def prep_calc_co2(
        args,
        result,
        inputs,
        n50,
        Fn50,
        air_permeability,
        T_a,
        v_10m,
        fs,
        fw,
        Ti_avg,
        quantiles,
        size
    ):
    #add defaults to args for co2
    for arg in ["room_type", "airing_type_room"]:
        if arg not in args or args[arg] is None:
            args[arg] = params_mapping[arg]["default"]

    #add defaults to input results
    for field in ["room_type", "airing_type_room"]:
        inputs[field] = args.get(field)

    room_type = args['room_type']

    H_Rm, A_Rm, t_max, CO2_Grenzwert = params_lookups.Raum(
        room_type = room_type,
        inputs = inputs,
        quantiles = quantiles,
        H_Rm = args.get('H_Rm'),
        A_Rm = args.get('A_Rm'),
        size = size
    )
    volume_room = H_Rm*A_Rm

    window_area_room = params_lookups.CO2only_roon(
        room_type,
        inputs,
        window_area_room=args.get("window_area_room"),
        A_Rm=A_Rm,
        size=size
    )

    n50_room = ltool.n50room(
        n50 = n50,
        Fn50 = Fn50,
        air_permeability = air_permeability,
        window_area = window_area_room,
        volume = volume_room
    )

    ACH_airing_room, airing_duration_room = params_lookups.airing_room(
        airing_type_room = args['airing_type_room'],
        inputs = inputs,
        airing_duration_room = args.get('airing_duration_room'),
        size = size
    )

    ActAdu, ActKid = params_lookups.activity_parameters(
        ActAdu = args.get('ActAdu'),
        ActKid = args.get('ActKid'),
    )

    NrAdu, ActAdu, NrKids, ActKid, AgeKid = params_lookups.occupancy_parameters(
        room_type = args['room_type'],
        inputs = inputs,
        NrAdu = args.get('NrAdu'),
        ActAdu = ActAdu,
        NrKids = args.get('NrKids'),
        ActKid = ActKid,
        AgeKid = args.get('AgeKid'),
        size = size
    )

    CO2_Emi = ltool.co2_emission(NrAdu, ActAdu, NrKids, ActKid, AgeKid)


    result["ResCO2"] = ltool.co2_calculation(
        n50 = n50_room,
        T_a = T_a,
        v_10m = v_10m,
        fs = fs,
        fw = fw,
        t_obs = t_max,
        volume = volume_room,
        ACH_airing = ACH_airing_room,
        t_airing = airing_duration_room/60,
        Ti_avg = Ti_avg,
        CO2_emi = CO2_Emi,
        c_threshold = CO2_Grenzwert,
        quantiles = quantiles,
        size = size
    )

def prep_calc_h2o(
        args,
        result,
        inputs,
        building_type,
        thermalbridges_label,
        building_n50,
        n50,
        Fn50,
        air_permeability,
        Ti_avg,
        T_a,
        T_a_damped,
        v_10m,
        rH_a,
        fs,
        fw,
        size
    ):
    #add defaults to args for h2o
    for arg in ["airing_type_home"]:
        if arg not in args or args[arg] is None:
            args[arg] = params_mapping[arg]["default"]

    #add defaults to input results h2o
    for field in ["airing_type_home"]:
        inputs[field] = args.get(field)

    area_home, pers_home = params_lookups.H2Oonlyparams(
        building_type = building_type,
        inputs = inputs,
        area_home = args.get("area_home"),
        pers_home = args.get("pers_home"),
        size = size
    )

    H_unit = params_lookups.H2Oonly_building_standard(
        building_n50 = building_n50,
        inputs = inputs,
        H_unit = args.get("H_unit"),
        size = size
    )

    volume_home = H_unit*area_home

    window_area_unit = params_lookups.H2Oonly_building(
        building_n50 = building_n50,
        inputs = inputs,
        window_area_unit=args.get("window_area_unit"),
        A_Rm=area_home,
        size=size
    )

    n50_unit = ltool.n50room(
        n50 = n50,
        Fn50 = Fn50,
        air_permeability = air_permeability,
        window_area = window_area_unit,
        volume = volume_home
    )

    H2Osource_area_abs, H2Osource_area, H2Osource_pers = params_lookups.H2O_sources(
        H2Osource_category = args.get("H2Osource_category"),
        inputs = inputs,
        H2Osource_area = args.get('H2Osource_area'),
        H2Osource_pers = args.get('H2Osource_pers'),
        H2Osource_area_abs = args.get('H2Osource_area_abs'),
        size = size
    )
    H2Oemi_abs, H2Oemi_pre = ltool.H2O_emission(H2Osource_area_abs, H2Osource_area, H2Osource_pers, area_home, pers_home)
    inputs["H2Osource_category"] = helper.result_stats(H2Oemi_pre)

    ACH_airing_home, airing_duration_home = params_lookups.airing_home(
        airing_type_home = args['airing_type_home'],
        inputs = inputs,
        airing_duration_home = args.get('airing_duration_home'),
        size = size
    )

    Ti_min, Ti_abs, fRSI = params_lookups.calc_temperatures(
        thermalbridges_label=thermalbridges_label,
        inputs=inputs,
        thermalbridges=args.get("thermalbridges"),
        Ti_min=args.get("Ti_min"),
        Ti_abs=args.get("Ti_abs"),
        size=size,
    )

    Vdot_add = args.get("Vdot_add", 0)
    inputs["Vdot_add"] = Vdot_add

    result["ResH2O"] = ltool.humidity_calculation(
        Vol_Unit = H_unit * area_home,
        n50_Unit = n50_unit,
        fRSI = fRSI,
        H2Oemi_abs = H2Oemi_abs,
        H2Oemi_pre = H2Oemi_pre,
        Ti_avg = Ti_avg,
        Ti_abs = Ti_abs,
        Ti_min = Ti_min,
        T_a = T_a,
        T_a_damped = T_a_damped,
        v_10m = v_10m,
        rH_a = rH_a,
        fs = fs,
        fw = fw,
        ACH_airing_home = ACH_airing_home,
        airing_duration_home = airing_duration_home,
        Vdot_add = Vdot_add,
    )

def prep_general(args, size):
    quantiles = [0.05, 0.25, 0.5, 0.75, 0.95]
    inputs = {}
    building_type = args["building_type"]
    building_n50 = args["building_n50"]

    #add defaults to input results general
    for field in ["location", "building_type"]:
        inputs[field] = args.get(field)

    thermalbridges_label = params_lookups.get_thermalbridges_label(
        building_n50=building_n50,
    )
    Ti_avg =  params_lookups.calc_avg_temperatures(
        thermalbridges_label=thermalbridges_label,
        inputs=inputs,
        Ti_avg=args.get("Ti_avg"),
        size=size
    )

    T_a, T_a_damped, v_10m, rH_a = params_lookups.weather(location = args['location'], size=size)
    C, alfa, gama = params_lookups.calc_lage(
        location = args['location'],
        inputs = inputs,
        Shield = args.get('shielding_class'),
        Terr = args.get('terrain_class'),
        quantiles = quantiles,
        size = size
    )

    H_wind, H_stack = params_lookups.calc_LBL_model_factors(
        building_n50 = building_n50,
        building_type = building_type,
        size = size
    )

    n50,air_permeability = params_lookups.building_standard(
        building_n50 = building_n50,
        inputs = inputs,
        window_class = args.get("window_class"),
        size = size
    )

    Fn50 = params_lookups.n50factor(size)

    R, X = params_lookups.Undichtheiten(size)
    fs = ltool.stack_effect_factor(Ti_avg,R,X,H_stack)
    fw = ltool.wind_factor(C,alfa,gama,H_wind,R)

    return inputs, building_n50, n50, Fn50, air_permeability, T_a, T_a_damped, v_10m, fs, fw, Ti_avg, building_type, thermalbridges_label, rH_a, quantiles


def calc_co2(args,size):

    inputs, building_n50, n50, Fn50, air_permeability, T_a, T_a_damped, v_10m, fs, fw, Ti_avg, building_type, thermalbridges_label, rH_a, quantiles = prep_general(args, size)

    result = {
        "inputs": inputs,
    }

    prep_calc_co2(
        args=args,
        result=result,
        inputs=inputs,
        n50=n50,
        Fn50=Fn50,
        air_permeability=air_permeability,
        T_a=T_a,
        v_10m=v_10m,
        fs=fs,
        fw=fw,
        Ti_avg=Ti_avg,
        quantiles=quantiles,
        size=size
    )

    return result

def calc_h2o(args,size):

    inputs, building_n50, n50, Fn50, air_permeability, T_a, T_a_damped, v_10m, fs, fw, Ti_avg, building_type, thermalbridges_label, rH_a, quantiles = prep_general(args, size)

    result = {
        "inputs": inputs,
    }

    prep_calc_h2o(
        args=args,
        result=result,
        inputs=inputs,
        building_type=building_type,
        thermalbridges_label=thermalbridges_label,
        building_n50=building_n50,
        n50=n50,
        Fn50=Fn50,
        air_permeability=air_permeability,
        Ti_avg=Ti_avg,
        T_a=T_a,
        T_a_damped = T_a_damped,
        v_10m=v_10m,
        rH_a=rH_a,
        fs=fs,
        fw=fw,
        size=size
    )

    return result


def calc(args,size):

    inputs, building_n50, n50, Fn50, air_permeability, T_a, T_a_damped, v_10m, fs, fw, Ti_avg, building_type, thermalbridges_label, rH_a, quantiles = prep_general(args, size)

    result = {
        "inputs": inputs,
    }

    prep_calc_co2(
        args=args,
        result=result,
        inputs=inputs,
        n50=n50,
        Fn50=Fn50,
        air_permeability=air_permeability,
        T_a=T_a,
        v_10m=v_10m,
        fs=fs,
        fw=fw,
        Ti_avg=Ti_avg,
        quantiles=quantiles,
        size=size
    )


    if args.get("humcalc", True):
        prep_calc_h2o(
            args=args,
            result=result,
            inputs=inputs,
            building_type=building_type,
            thermalbridges_label=thermalbridges_label,
            building_n50=building_n50,
            n50=n50,
            Fn50=Fn50,
            air_permeability=air_permeability,
            Ti_avg=Ti_avg,
            T_a=T_a,
            T_a_damped=T_a_damped,
            v_10m=v_10m,
            rH_a=rH_a,
            fs=fs,
            fw=fw,
            size=size
        )

    inputs["humcalc"] = args.get("humcalc", True)

    return result
