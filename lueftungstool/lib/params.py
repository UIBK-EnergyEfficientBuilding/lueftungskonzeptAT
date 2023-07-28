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

standort2Terr = {
    "Innsbruck":[1,1,2.5,4.5],
    "Wien":[1,1,2.5,5.5],
}
standort2Shield = {
    "Innsbruck":[1,1,1.5,4.5],
    "Wien":[1,1,2.5,5.5],
}
standort2T_a = {
    "Innsbruck":-0.5,
    "Wien":1.7,
}
standort2v_10m = {
    "Innsbruck":1.2,
    "Wien":3.4,
}
standort_list = ["Innsbruck", "Wien"]

gebaeudeart2H_Bldg = {
    "Einfamilienhaus/Reihenhaus":[2,4,3,12],
    "Mehrfamilienhaus":[2,4,3,18],
    "Apartmentblock":[2,4,3,60],
}
gebaeudeart2H_WindRel = {
    "Einfamilienhaus/Reihenhaus":[1,1,1,1],
    "Mehrfamilienhaus":[1,1,0,1],
    "Apartmentblock":[1,1,0,1],
}
gebaeudeart2Ti_avg = {
    "Altbau mit durchbetonierten Bauteilen (Balkone, etc)":[3,3,18,22],
    "Altbau (mit normalen Wärmebrücken)":[3,3,18,22],
    "Standard Neubau":[3,3,19,23],
}
gebaeudeart_list = ["Einfamilienhaus/Reihenhaus", "Mehrfamilienhaus", "Apartmentblock"]

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
raumart_list = ["Schlafzimmer", "Wohnzimmer"]

luefungsart2WinACH = {
    "Querlüftung":[3,3,10,30],
    "einseitig":[3,3,5,15],
}
luefungsart2WinDur = {
    "Querlüftung":[3,3,3,7],
    "einseitig":[3,3,3,15],
}
luefungsart_list = ["Querlüftung", "einseitig"]

n50_map = {
    "Altbau":[3,3,3,4],
    "Undichter Altbau": [3,3,3,7],
    "Standard Neubau": [3,3,1,2],
}
n50_map_list = list(n50_map.keys())
