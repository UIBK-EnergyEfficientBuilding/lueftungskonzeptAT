#TODO better filename

import lueftungstool.lib.calc as ltool
import lueftungstool.lib.params_lookups as params_lookups
import lueftungstool.lib.helper as helper
from lueftungstool.lib.params import params_mapping, WNF_list

def calc(args,size):
    inputs = {}
    quantiles = [0.05, 0.25, 0.5, 0.75, 0.95]

    #add defaults to args
    for arg in ["airing_type_room", "airing_type_home"]:
        if arg not in args or args[arg] is None:
            args[arg] = params_mapping[arg]["default"]

    building_type = args["building_type"]
    building_n50 = args["building_n50"]

    #add defaults to input results
    for field in params_mapping:
        inputs[field] = args.get(field)

    ActAdu, ActKid = params_lookups.activity_parameters(
        activity_level_adu = args.get('ActLevelAdu'),
        activity_level_kid = args.get('ActLevelKid'),
        inputs = inputs,
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

    H_Rm, A_Rm, window_area, t_max = params_lookups.Raum(
        room_type = args['room_type'],
        inputs = inputs,
        quantiles = quantiles,
        H_Rm = args.get('H_Rm'),
        A_Rm = args.get('A_Rm'),
        window_area = args.get('window_area'),
        size = size
    )

    T_a, v_10m, rH_a = params_lookups.weather(location = args['location'],)
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

    thermalbridges = params_lookups.building_standard2thermalbridges(
        building_n50 = building_n50,
        inputs = inputs,
        thermalbridges = args.get("thermalbridges"),
    )

    Ti_avg, Ti_min, Ti_abs, fRSI = params_lookups.calc_temperatures(
        thermalbridges = thermalbridges,
        inputs = inputs,
        Ti_avg = args.get("Ti_avg"),
        Ti_min = args.get("Ti_min"),
        Ti_abs = args.get("Ti_abs"),
        fRSI = args.get("fRSI"),
        size = size
    )

    Fn50 = params_lookups.n50factor(size)

    n50_room = ltool.n50room(
        n50 = n50,
        Fn50 = Fn50,
        air_permeability = air_permeability,
        window_area = window_area,
        A_Rm = A_Rm,
        H_Rm = H_Rm,
    )

    ACH_airing_room, airing_duration_room = params_lookups.airing_room(
        airing_type_room = args['airing_type_room'],
        inputs = inputs,
        airing_duration_room = args.get('airing_duration_room'),
        size = size
    )

    R, X = params_lookups.Undichtheiten(size)
    fs = ltool.stack_effect_factor(Ti_avg,R,X,H_stack)
    fw = ltool.wind_factor(C,alfa,gama,H_wind,R)

    result = {
        "inputs": inputs,
    }
    result["ResCO2"] = ltool.co2_calculation(
        n50_room = n50_room,
        T_a = T_a,
        v_10m = v_10m,
        fs = fs,
        fw = fw,
        t_max = t_max,
        volume_room = A_Rm*H_Rm,
        ACH_airing_room = ACH_airing_room,
        airing_duration_room = airing_duration_room, 
        Ti_avg = Ti_avg,
        CO2_Emi = CO2_Emi,
        quantiles = quantiles,
        size = size
    )

    if building_type in WNF_list:
        humcalc = True
    else:
        humcalc = False

    if humcalc:
        area_home, pers_home = params_lookups.H2Oonlyparams(
            building_type = building_type,
            inputs = inputs,
            area_home = args.get("area_home"),
            pers_home = args.get("pers_home"),
            size = size
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

        result["ResH2O"] = ltool.humidity_calculation(
            Vol_Unit = H_Rm * area_home,
            n50_Unit = n50_room,
            fRSI = fRSI,
            H2Oemi_abs = H2Oemi_abs,
            H2Oemi_pre = H2Oemi_pre,
            Ti_avg = Ti_avg,
            Ti_abs = Ti_abs,
            Ti_min = Ti_min,
            T_a = T_a,
            v_10m = v_10m,
            rH_a = rH_a,
            fs = fs,
            fw = fw,
            ACH_airing_home = ACH_airing_home,
            airing_duration_home = airing_duration_home,
        )

    return result
