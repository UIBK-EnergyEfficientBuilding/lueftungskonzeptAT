from flask import request
from flask_restx import Namespace, Resource, fields, reqparse
import lueftungstool.lib.calc as ltool
import lueftungstool.lib.params as params

def add_model_to_parser(parser,model):
    for k,v in model.items():
        a = v.schema()
        parser.add_argument(
            name=k,
            type={"string":str,"number":float,"integer":float}[a["type"]],
            help=a["description"],
            required=v.required,
            default=a["default"],
            choices=a.get("enum",None)
        )


namespace = Namespace('calculate', '#todo')


params_mapping = {
    "location":{
        "values":params.location_list,
        "default":"Wien",
    },
    "building_type":{
        "values":params.buiding_type_list,
        "default":"Mehrfamilienhaus",
    },
    "room_type":{
        "values":params.room_type_list,
        "default":"Schlafzimmer",
    },
    "airing_type_room":{
        "values":params.airing_type_list,
        "default":"Querlüftung",
    },
    "airing_type_home":{
        "values":params.airing_type_list,
        "default":"Querlüftung",
    },
    "building_n50":{
        "values":params.n50_map_list,
        "default":"Standard Neubau",
    },
    "thermalbridges":{
        "values":params.waermebruecken_list,
    },
    "H2Osource_category":{
        "values":params.Feuchtelastkategorie_list,
    },
    "terrain_class":{
        "values":params.Terr_class_list,
    },
    "shielding_class":{
        "values":params.Shield_class_list,
    },
    "window_class":{
        "values":params.window_class_list,
    },
}

calculation_parameter_model = namespace.model('CalculationParameter', {
    'location': fields.String(default=params_mapping["location"]["default"],
        required=True,
        enum=params_mapping["location"]["values"],
        description="Standort",
    ),
    'building_n50': fields.String(default=params_mapping["building_n50"]["default"],
        required=True,
        enum=params_mapping["building_n50"]["values"],
        description="Luftdichtigkeit n50-Wert (Gebäude) [1/h]",
    ),
    'building_type': fields.String(default=params_mapping["building_type"]["default"],
        required=True,
        enum=params_mapping["building_type"]["values"],
        description="Gebäudeart",
    ),
    'thermalbridges': fields.String(
        required=False,
        enum=params_mapping["thermalbridges"]["values"],
        description="Wärmebrücken",
    ),
    'fRSI': fields.Float(
        required=False,
        description="fRSI-Wert",
    ),
    'H_Rm': fields.Float(
        required=False,
        description="Höhe (betrachteter Raum) [m]:",
    ),
    'A_Rm': fields.Float(
        required=False,
        description="Fläche (betrachteter Raum) [m²]:",
    ),
    'room_type': fields.String(default=params_mapping["room_type"]["default"],
        required=True,
        enum=params_mapping["room_type"]["values"],
        description="Raumart (betrachteter Raum):",
    ),
    'window_area': fields.Float(
        required=False,
        description="Fläche öffenbare Fenster (betrachteter Raum) [m²]:",
    ),
    'window_class': fields.String(
        required=False,
        enum=params_mapping["window_class"]["values"],
        description="Fensterklasse nach EN12207 (betrachteter Raum)",
    ),
    'airing_type_room': fields.String(default=params_mapping["airing_type_room"]["default"],
        required=False,
        enum=params_mapping["airing_type_room"]["values"],
        description="Lüftungsmöglichkeit (betrachteter Raum):",
    ),
    'airing_duration_room': fields.Float(
        required=False,
        description="Lüftungsdauer pro Lüftungsvorgang [min]",
    ),
    'terrain_class': fields.String(
        required=False,
        enum=params_mapping["terrain_class"]["values"],
        description="Gelände-/Terrainklasse (Windeinfluss)",
    ),
    'shielding_class': fields.String(
        required=False,
        enum=params_mapping["shielding_class"]["values"],
        description="Abschirmung-/Shieldingklasse (Windeinfluss)",
    ),

    'NrAdu': fields.Float(
        required=False,
        description="Anzahl Erwachsene",
    ),
    'ActAdu': fields.Float(
        required=False,
        description="Aktivität Erwachsene [met]",
    ),
    'NrKids': fields.Float(
        required=False,
        description="Anzahl Kinder",
    ),
    'ActKid': fields.Float(
        required=False,
        description="Aktivität Kinder [met]",
    ),
    'AgeKid': fields.Float(
        required=False,
        description="Mittleres Alter der Kinder [a]",
    ),

    'H2Osource_category': fields.String(
        required=False,
        enum=params_mapping["H2Osource_category"]["values"],
        description="Feuchtelast [l/d]:",
    ),
    'H2Osource_area': fields.Float(
        required=False,
        description="Feuchtequellstärke pro m² bei Anwesenheit [g/(hm²)]",
    ),
    'H2Osource_pers': fields.Float(
        required=False,
        description="Feuchtequellstärke pro Pers bei Anwesenheit [g/(hPers)]",
    ),
    'H2Osource_area_abs': fields.Float(
        required=False,
        description="Feuchtequellstärke pro m² bei Abwesenheit [g/(hm²)]",
    ),
    'area_home': fields.Float(
        required=False,
        description="Fläche gesamte Wohneinheit [m²]:",
    ),
    'pers_home': fields.Float(
        required=False,
        description="Personenanzahl (gesamter Wohneinheit)",
    ),
    'airing_type_home': fields.String(default=params_mapping["airing_type_home"]["default"],
        required=False,
        enum=params_mapping["airing_type_home"]["values"],
        description="Lüftungsmöglichkeit (gesamte Wohneinheit)",
    ),
    'airing_duration_home': fields.Float(
        required=False,
        description="Lüftungsdauer gesamt, z.B. morgens und abends [min/Tag]",
    ),
    'Ti_avg': fields.Float(
        required=False,
        description="Mittlere Raumtemperatur in gesamten Wohneinheit [°C]",
    ),
    'Ti_min': fields.Float(
        required=False,
        description="Raumtemperatur im kühlsten Raum [°C]",
    ),
    'Ti_abs': fields.Float(
        required=False,
        description="Minimale Raumtemperatur bei längerer Abwesenheit [°C]",
    ),

})


result_stats_float_model = namespace.model('ResultStatsFloat', {
    "mean": fields.Float(),
    "error": fields.Float(),
    "median": fields.Float(),
    "quantiles": fields.List(fields.Float(), example=[1,2,3,4,5])
})

result_stats_integer_model = namespace.model('ResultStatsInteger', {
    "min": fields.Integer(),
    "max": fields.Integer(),
    "quantiles": fields.List(fields.Integer(), example=[1,2,3,4,5])
})

plot_data = namespace.model('plot_data', {
    "x":fields.List(fields.Float(), example=[0,1,2,3,5]),
    "y":fields.List(fields.List(fields.Float()), example=[[0,1,2,3,5]]),
})

airing_resultdata = namespace.model('airing_resultdata', {
    'frequency': fields.Nested(
        plot_data,
        description='Zeit bis Grenzwert erreicht - Häufigkeit'
    ),
    'timeseries': fields.Nested(
        plot_data,
        description='CO2 Konzentration'
    ),
})

mouldrisk_plot = namespace.model('mouldrisk_plot', {
    'ACR': fields.Nested(
        plot_data,
        description='Mittlere Luftwechselrate [1/h]'
    ),
    'Vdot': fields.Nested(
        plot_data,
        description='Mittlerer Luftvolumenstrom [m³/h]'
    ),
    'abs': fields.Nested(
        plot_data,
        description='Fälle mit Schimmelrisiko bei Anwesenheit'
    ),
    'pre': fields.Nested(
        plot_data,
        description='Fälle mit Schimmelrisiko bei Abwesenheit'
    ),
})

mould_risk = namespace.model('ResH2O', {
    'MouldRisk': fields.Float(
        example=0.219,
        description='Schimmelrisiko als Wahrscheinlichkeit'
    ),
    'Vdot_acc': fields.Float(
        example=29.0,
        description='Erforderliche zusätzliche Luftmenge damit Wahrscheinlichkeit<1% [m³/h]'
    ),

    "Vdot_Inf": fields.Nested(result_stats_float_model,
        description='Luftmenge durch Fugenlüftung [m³/h]'
    ),
    "Vdot_Tot": fields.Nested(result_stats_float_model,
        description='Luftmenge durch Fugenlüftung + Fensterlüftung [m³/h]'
    ),

    "Vdot_req_pre": fields.Nested(result_stats_float_model,
        description='Erforderliche Luftmenge zur Feuchteabfuhr [m³/h]'
    ),
    'Frac_Inf_insuff_pre': fields.Float(
        example=1,
        description='Wahrscheinlichkeit dass Fugenlüftung alleine nicht ausreicht'
    ),
    'MouldRisk_pre': fields.Float(
        example=0.072,
        description='Wahrscheinlichkeit dass Fugenlüftung und Fensterlüftung nicht ausreicht'
    ),
    "Vdot_acc_pre": fields.Float(
        example=12,
        description='Erforderliche zusätzliche Luftmenge damit Wahrscheinlichkeit <1% [m³/h]'
    ),
    "ELA_acc_pre": fields.Float(
        example=120,
        description='dafür erforderlicher zusätzlicher freier Querschnitt [cm²]'
    ),

    "Vdot_req_abs": fields.Nested(result_stats_float_model,
        description='Erforderliche Luftmenge zur Feuchteabfuhr [m³/h]'
    ),
    'Frac_Inf_insuff_abs': fields.Float(
        example=0.219,
        description='Wahrscheinlichkeit dass Fugenlüftung alleine nicht ausreicht'
    ),
    'MouldRisk_abs': fields.Float(
        example=0.219,
        description='Wahrscheinlichkeit dass Fugenlüftung nicht ausreicht'
    ),
    "Vdot_acc_abs": fields.Float(
        defaule=3.1,
        description='Erforderliche zusätzliche Luftmenge damit Wahrscheinlichkeit<1% [m³/h]'
    ),
    "ELA_acc_abs": fields.Float(
        example=41,
        description='dafür erforderlicher zusätzlicher freier Querschnitt [cm²]]'
    ),
    'plot': fields.Nested(
        mouldrisk_plot,
        description='Feuchtebewertung (Nur Wohnen) - Plot data'
    ),
})

res_co2_plot = namespace.model('res_co2_plot', {
    't_avgC_realC0': fields.Nested(
        airing_resultdata,
        description='Gleitender Mittelwert - Realistisches Lüftungsverhalten'
    ),
    't_instC_realC0': fields.Nested(
        airing_resultdata,
        description='Momentanwert - Realistisches Lüftungsverhalten'
    ),
    't_avgC_idealC0': fields.Nested(
        airing_resultdata,
        description='Gleitender Mittelwert - Ideale Lüftung'
    ),
    't_instC_idealC0': fields.Nested(
        airing_resultdata,
        description='Momentanwert - Ideale Lüftung'
    ),
})

res_co2 = namespace.model('ResCO2', {
    'airing_acceptable': fields.Boolean(
        description="Fensterlüftung praktikabel/zumutbar"
    ),
    't_reasonable': fields.Float(
        description="Dies ist kürzer als die zumutbare Zeit zwischen Fensterlüften [min]"
    ),
    "t_avgC_realC0": fields.Nested(result_stats_float_model,
        description='Zeit bis CO2-Stundenmittelwert=1000 ppm - realistisches Lüften [min]'
    ),
    "t_instC_realC0": fields.Nested(result_stats_float_model,
        description='Zeit bis CO2-Momentanwert=1000 ppm - realistisches Lüften [min]'
    ),
    "t_avgC_idealC0": fields.Nested(result_stats_float_model,
        description='Zeit bis CO2-Stundenmittelwert=1000 ppm - ideales Lüften [min]'
    ),
    "t_instC_idealC0": fields.Nested(result_stats_float_model,
        description='Zeit bis CO2-Momentanwert=1000 ppm - ideales Lüften [min]'
    ),
    'CO2_stat': fields.Nested(result_stats_float_model,
        description='CO2 Konzentration im stationären Fall'
    ),
    'Vdot': fields.Nested(result_stats_float_model,
        description='errechnete Luftmenge aufgrund natürlicher Lüftung [m³/h]'
    ),
    'ACR': fields.Nested(result_stats_float_model,
        description='errechneter natürlicher Luftwechsel [1/h]'
    ),
    'plot': fields.Nested(
        res_co2_plot,
        description='Lüftungsverhalten - Plot data'
    ),
})

inputs_result_model  = namespace.model('InputsResult', {
    'location': fields.String(),
    'building_n50': fields.Nested(result_stats_float_model),
    'building_type': fields.String(),
    'thermalbridges': fields.String(),
    'fRSI': fields.Nested(result_stats_float_model),
    'H_Rm': fields.Nested(result_stats_float_model),
    'A_Rm': fields.Nested(result_stats_float_model),
    'room_type': fields.String(),
    'window_area': fields.Nested(result_stats_float_model),
    'window_class': fields.Nested(result_stats_integer_model),
    'airing_type_room': fields.String(),
    'airing_duration_room': fields.Nested(result_stats_float_model),
    'terrain_class': fields.Nested(result_stats_integer_model),
    'shielding_class': fields.Nested(result_stats_integer_model),

    'NrAdu': fields.Nested(result_stats_integer_model),
    'ActAdu': fields.Nested(result_stats_float_model),
    'NrKids': fields.Nested(result_stats_integer_model),
    'ActKid': fields.Nested(result_stats_float_model),
    'AgeKid': fields.Nested(result_stats_float_model),

    'H2Osource_category': fields.Nested(result_stats_float_model),
    'H2Osource_area': fields.Nested(result_stats_float_model),
    'H2Osource_pers': fields.Nested(result_stats_float_model),
    'H2Osource_area_abs': fields.Nested(result_stats_float_model),
    'area_home': fields.Nested(result_stats_float_model),
    'pers_home': fields.Nested(result_stats_float_model),
    'airing_type_home': fields.String(),
    'airing_duration_home': fields.Nested(result_stats_float_model),
    'Ti_avg': fields.Nested(result_stats_float_model),
    'Ti_min': fields.Nested(result_stats_float_model),
    'Ti_abs': fields.Nested(result_stats_float_model),
})

calculation_result_model = namespace.model('CalculationResult', {
    'ResCO2': fields.Nested(
        res_co2,
        description='Ergebnis CO2 Bewertung'
     ),
    'ResH2O': fields.Nested(
        mould_risk,
        description='Ergebnis Schimmelrisiko Bewertung (nur für Wohnbau)'
    ),
    'inputs': fields.Nested(
        inputs_result_model,
        description='inputs'
    ),
})

valitation_error_model = namespace.model('ValitationError', {
    'message': fields.String(example="Input payload validation failed"),
    'errors': fields.Raw(example="""{
        "H_Rm": "could not convert string to float: 'a'",
        "A_Rm": "could not convert string to float: 'b'"
    }
""")
})


parser = reqparse.RequestParser(bundle_errors=True)
add_model_to_parser(parser,calculation_parameter_model)

@namespace.route('')
class Calculate(Resource):
    @namespace.expect(parser, validate=True)
    @namespace.marshal_with(calculation_result_model)
    @namespace.response(500, 'Internal Server error')
    @namespace.response(400, 'BAD REQUEST', model=valitation_error_model)
    @namespace.response(429, 'TOO MANY REQUESTS')
    def get(self):
        args = parser.parse_args()

        size = 1000
        building_type = args["building_type"]

        inputs = {}
        quantiles = [0.05, 0.25, 0.5, 0.75, 0.95]

        #add defaults to input results
        for field in params_mapping:
            inputs[field] = args[field]

        NrAdu, ActAdu, NrKids, ActKid, AgeKid = ltool.occupancy_parameters(
            room_type = args['room_type'],
            inputs = inputs,
            NrAdu = args['NrAdu'],
            ActAdu = args['ActAdu'],
            NrKids = args['NrKids'],
            ActKid = args['ActKid'],
            AgeKid = args['AgeKid'],
            size = size
        )

        CO2_Emi = ltool.co2_emission(NrAdu, ActAdu, NrKids, ActKid, AgeKid)

        H_Rm, A_Rm, window_area, t_max = ltool.Raum(
            room_type = args['room_type'],
            inputs = inputs,
            quantiles = quantiles,
            H_Rm = args['H_Rm'],
            A_Rm = args['A_Rm'],
            window_area = args['window_area'],
            size = size
        )

        T_a, v_10m, rH_a = ltool.weather(location = args['location'],)
        C, alfa, gama = ltool.calc_lage(
            location = args['location'],
            inputs = inputs,
            Shield = args['shielding_class'],
            Terr = args['terrain_class'],
            quantiles = quantiles,
            size = size
        )

        n50_room, H_wind, H_stack, Ti_avg, Ti_min, Ti_abs, fRSI, area_home, pers_home = ltool.calc_dichtheit(
            building_n50 = args["building_n50"],
            building_type = building_type,
            thermalbridges = args["thermalbridges"],
            inputs = inputs,
            Ti_avg = args["Ti_avg"],
            Ti_min = args["Ti_min"],
            Ti_abs = args["Ti_abs"],
            fRSI = args["fRSI"],
            window_class = args["window_class"],
            window_area = window_area,
            A_Rm = A_Rm,
            H_Rm = H_Rm,
            area_home = args["area_home"],
            pers_home = args["pers_home"],
            quantiles = quantiles,
            size = size
        )

        R, X = ltool.Undichtheiten(size)

        if building_type in params.WNF_list:
            humcalc = True
        else:
            humcalc = False

        ACH_airing_room, airing_duration_room = ltool.airing_room(
            airing_type_room = args['airing_type_room'],
            inputs = inputs,
            airing_duration_room = args['airing_duration_room'],
            size = size
        )

        H2Osource_area_abs, H2Osource_area, H2Osource_pers = ltool.H2O_sources(
            H2Osource_category = args["H2Osource_category"],
            inputs = inputs,
            H2Osource_area = args['H2Osource_area'],
            H2Osource_pers = args['H2Osource_pers'],
            H2Osource_area_abs = args['H2Osource_area_abs'],
            size = size
        )
        H2Oemi_abs, H2Oemi_pre = ltool.H2O_emission(H2Osource_area_abs, H2Osource_area, H2Osource_pers, area_home, pers_home)
        inputs["H2Osource_category"] = ltool.result_stats(H2Oemi_pre)

        ACH_airing_home, airing_duration_home = ltool.airing_home(
            airing_type_home = args['airing_type_home'],
            inputs = inputs,
            airing_duration_home = args['airing_duration_home'],
            size = size
        )

        return ltool.calc(
            humcalc = humcalc,
            n50_room = n50_room,

            T_a = T_a,
            v_10m = v_10m,
            rH_a = rH_a,
            C = C,
            alfa = alfa,
            gama = gama,
            H_wind = H_wind,
            R = R,
            X = X,
            H_stack = H_stack,

            inputs = inputs,
            t_max = t_max,
            H_Rm = H_Rm,
            A_Rm = A_Rm,
            ACH_airing_room = ACH_airing_room,
            airing_duration_room = airing_duration_room,
            ACH_airing_home = ACH_airing_home,
            airing_duration_home = airing_duration_home,
            H2Oemi_abs = H2Oemi_abs,
            H2Oemi_pre = H2Oemi_pre,
            Ti_avg = Ti_avg,
            Ti_abs = Ti_abs,
            Ti_min = Ti_min,
            fRSI = fRSI,
            CO2_Emi = CO2_Emi,
            area_home = area_home,
            quantiles = quantiles,
            size = size
        )

parameter_result_model =  namespace.model('ParameterResults', {
        field: fields.List(
            fields.Nested(namespace.model('ParameterResult', {
                "values": fields.List(fields.String(description='Mögliche Werte für den angegebenen Parameter')),
                "default": fields.String(),
        })))
        for field in params_mapping
})

@namespace.route('/params')
class Parameter(Resource):
    @namespace.marshal_with(parameter_result_model)
    @namespace.response(500, 'Internal Server error')
    def get(self):
        return params_mapping
