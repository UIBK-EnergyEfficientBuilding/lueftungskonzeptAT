Shield_class2C = {
    1:0.34,
    2:0.3,
    3:0.25,
    4:0.19,
    5:0.11,
}
Terr_class2alfa = {
    1:1.3,
    2:1,
    3:0.85,
    4:0.67,
    5:0.471,
}
Terr_class2gama = {
    1:0.1,
    2:0.15,
    3:0.2,
    4:0.25,
    5:0.35,
}

name2Terr_class = {
    "Freistehend": 1,
    "Lockere Siedlungsstruktur": 2,
    "Dorfstruktur": 3,
    "Städtische Struktur": 4,
    "Innerstädtisch": 5,
}
Terr_class_list = list(name2Terr_class.keys())

name2Shield_class = {
    "Sehr windausgesetzt": 1,
    "Leicht windgeschützt": 2,
    "Moderat windgeschützt": 3,
    "Sehr windgeschützt": 4,
    "Extem windgeschützt": 5,
}
Shield_class_list = list(name2Shield_class.keys())

name2window_class = {
    "1: sehr undicht":1,
    "2: eher undicht":2,
    "3: mit guter Dichtung":3,
    "4: mit sehr guter Dichtung":4,
}
window_class_list = list(name2window_class.keys())
window_class2air_permeability = {
    1:50.0,
    2:27.0,
    3:9.0,
    4:3.0,
}

location2Terr = {
    "Innsbruck":[1,1,2.5,4.5],
    "Wien":[1,1,2.5,5.5],
}
location2Shield = {
    "Innsbruck":[1,1,1.5,4.5],
    "Wien":[1,1,2.5,5.5],
}
location2T_a = {
    "Innsbruck":-0.5,
    "Wien":1.7,
}
location2v_10m = {
    "Innsbruck":1.2,
    "Wien":3.4,
}
location2rH = {
    "Innsbruck":0.84,
    "Wien":0.78,
}

location_list = ["Innsbruck", "Wien"]

gebaeudeart2H_Bldg = {
    "Einfamilienhaus/Reihenhaus":[2,4,3,12],
    "Mehrfamilienhaus":[2,4,3,18],
    "Apartmentblock":[2,4,3,60],
    "Schule/Kindergarten": [2,4,3,15],
}
gebaeudeart2H_WindRel = {
    "Einfamilienhaus/Reihenhaus":[1,1,1,1],
    "Mehrfamilienhaus":[1,1,0,1],
    "Apartmentblock":[1,1,0,1],
    "Schule/Kindergarten": [1,1,0,1],
}
buiding_type_list = ["Einfamilienhaus/Reihenhaus", "Mehrfamilienhaus", "Apartmentblock", "Schule/Kindergarten"]

map_n502waermebruecken = {
    "Undichter Altbau": "Altbau mit durchbetonierten Bauteilen (Balkone, etc)",
    "Altbau": "Altbau (mit normalen Wärmebrücken)",
    "Standard Neubau": "Standard Neubau",
    "Neubau - eher dicht": "NEH (mit geringen Wärmebrücken)",
    "Neubau - sehr dicht": "NEH (minimale Wärmebrücken)",
}

waermebruecken2Ti_avg = {
    "Altbau mit durchbetonierten Bauteilen (Balkone, etc)":[3,3,18,22],
    "Altbau (mit normalen Wärmebrücken)":[3,3,18,22],
    "Standard Neubau":[3,3,19,23],
    "NEH (mit geringen Wärmebrücken)":[3,3,20,24],
    "NEH (minimale Wärmebrücken)":[3,3,20,24],
}
waermebruecken_list = list(waermebruecken2Ti_avg.keys())

waermebruecken2Ti_min = {
    "Altbau mit durchbetonierten Bauteilen (Balkone, etc)":[3,3,16,20],
    "Altbau (mit normalen Wärmebrücken)":[3,3,16,20],
    "Standard Neubau":[3,3,17,20],
    "NEH (mit geringen Wärmebrücken)":[3,3,18,22],
    "NEH (minimale Wärmebrücken)":[3,3,18,22],
}
waermebruecken2Ti_abs = {
    "Altbau mit durchbetonierten Bauteilen (Balkone, etc)":[3,3,14,18],
    "Altbau (mit normalen Wärmebrücken)":[3,3,14,18],
    "Standard Neubau":[3,3,15,19],
    "NEH (mit geringen Wärmebrücken)":[3,3,16,20],
    "NEH (minimale Wärmebrücken)":[3,3,16,20],
}

waermebruecken2fRSI = {
    "Altbau mit durchbetonierten Bauteilen (Balkone, etc)":[3,3,0.4,0.6],
    "Altbau (mit normalen Wärmebrücken)":[3,3,0.5,0.7],
    "Standard Neubau":[3,3,0.6,0.8],
    "NEH (mit geringen Wärmebrücken)":[3,3,0.7,0.9],
    "NEH (minimale Wärmebrücken)":[3,3,0.85,0.95],
}

raumart2A_Rm = {
    "Schlafzimmer":[2.5,4,6,30],
    "Wohnzimmer":[2,3.6,12,60],
}
raumart2H_Rm = {
    "Schlafzimmer":[3,3,2.4,2.6],
    "Wohnzimmer":[3,3,2.4,2.6],
}
raumart2Nr_Adu = {
    "Schlafzimmer":[2,2,1,2],
    "Wohnzimmer":[2,3,1,2],
}
raumart2ActAdu = {
    "Schlafzimmer":[3,3,0.6,1],
    "Wohnzimmer":[3,3,1,1.4],
}
raumart2Nr_Kid = {
    "Schlafzimmer":[1,10,0,3],
    "Wohnzimmer":[1,5,1,4],
}
raumart2ActKid = {
    "Schlafzimmer":[3,3,0.6,1],
    "Wohnzimmer":[3,3,1,1.4],
}
raumart2AgeKid = {
    "Schlafzimmer": [1,3,0,4],
    "Wohnzimmer": [1,1,1,18],
}
raumart2WinRat_Rm = {
    "Schlafzimmer": [3,3,0.1,0.5],
    "Wohnzimmer": [3,3,0.1,0.5],
}
room_type2t_max = {
    "Schlafzimmer": 8,
    "Wohnzimmer": 2,
}
room_type_list = ["Schlafzimmer", "Wohnzimmer"]

activity_level = {
    "Ruhend": 0.8,
    "Sitzend entspannt": 1,
    "Sitzende Tätigkeit": 1.2,
    "Stehend Entspannt": 1.2,
    "Stehende Tätigkeit": 1.3,
    "Mäßige körp. Tätikeit": 1.5,
    "Workout": 3,
}
activity_level_list = list(activity_level.keys())

luefungsart2WinACH = {
    "Querlüftung":[3,3,10,30],
    "Einseitige Fensterfront":[3,3,5,15],
}
luefungsart2WinDur = {
    "Querlüftung":[3,3,3,7],
    "Einseitige Fensterfront":[3,3,3,15],
}
luefungsart2WinDur2 = {
    "Querlüftung":[3,3,5,25],
    "Einseitige Fensterfront":[3,3,5,35],
}
airing_type_list = ["Querlüftung", "Einseitige Fensterfront"]

window_class = {
    "Undichter Altbau":[1,1,1,4],
    "Altbau":[1,1,2,4],
    "Standard Neubau":[1,1,3,4],
    "Neubau - eher dicht":[1,1,4,4],
    "Neubau - sehr dicht":[1,1,4,4],
}
H_StackRel = {
    "Altbau":[1,1,0,1],
    "Undichter Altbau": [1,1,0,1],
    "Standard Neubau": [1,1,0,0.1],
    "Neubau - eher dicht": [1,1,0,0.1],
    "Neubau - sehr dicht": [1,1,0,0.1],
}
n50_map = {
    "Altbau":[3,3,3,4],
    "Undichter Altbau": [3,3,3,7],
    "Standard Neubau": [3,3,1,2],
    "Neubau - eher dicht": [3,3,0.6,1],
    "Neubau - sehr dicht": [3,3,0.2,0.6],
}
n50_map_list = list(n50_map.keys())

Fn50 = [4,4,0,1]

WNF = {
    "Einfamilienhaus/Reihenhaus":[1,1,100,250],
    "Mehrfamilienhaus":[2,6,50,200],
    "Apartmentblock":[2,4,40,120],
}
WNF_list = list(WNF.keys())

WNF = {
    "Einfamilienhaus/Reihenhaus":[1,1,100,250],
    "Mehrfamilienhaus":[2,6,50,200],
    "Apartmentblock":[2,4,40,120],
}

Feuchtelastkategorie = {
    "Niedrig":[0, 0.4],
    "Mittel":[0.3, 0.7],
    "Hoch":[0.6, 1,]
}
Feuchtelastkategorie_list = list(Feuchtelastkategorie.keys())

m_H2Od0 = {
    "Quellstärke [g/h] Wohnen bei Abwesenheit": [1,1,0,0.56],
    "ungenutzt": [1,1,0.056,0.278],
}
m_H2Od = {
    "Quellstärke [g/h] Wohnen Flächenabhängig": [1,1,0.28,0.83],
    "ungenutzt": [1,1,0.083,1.66],
}
m_H2Ok = {
    "Quellstärke [g/h] Wohnen PersABH": [3,3,41.67,83.33],
    "ungenutzt": [1,1,83.33,166.67],
}

OccDens = {
    "Einfamilienhaus/Reihenhaus":[2,4,30,120],
    "Mehrfamilienhaus":[2,4,15,100],
    "Apartmentblock":[2,4,15,80],
}
OccDens_list = list(OccDens.keys())

params_mapping = {
    "location":{
        "values":location_list,
        "default":"Wien",
    },
    "building_type":{
        "values":buiding_type_list,
        "default":"Mehrfamilienhaus",
    },
    "room_type":{
        "values":room_type_list,
        "default":"Schlafzimmer",
    },
    "airing_type_room":{
        "values":airing_type_list,
        "default":"Querlüftung",
    },
    "airing_type_home":{
        "values":airing_type_list,
        "default":"Querlüftung",
    },
    "building_n50":{
        "values":n50_map_list,
        "default":"Standard Neubau",
    },
    "thermalbridges":{
        "values":waermebruecken_list,
    },
    "H2Osource_category":{
        "values":Feuchtelastkategorie_list,
    },
    "terrain_class":{
        "values":Terr_class_list,
    },
    "shielding_class":{
        "values":Shield_class_list,
    },
    "window_class":{
        "values":window_class_list,
    },
    "ActLevelAdu":{
        "values":activity_level_list,
    },
    "ActLevelKid":{
        "values":activity_level_list,
    },
}
