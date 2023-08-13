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
        "values":params.airing_type_home_list,
        "default":"Querlüftung",
    },
    "building_n50":{
        "values":params.n50_map_list,
        "default":"Standard Neubau",
    },
    "thermalbridges":{
        "values":params.waermebruecken_list,
        "default":"Standard Neubau",
    },
    "H2Osource_category":{
        "values":params.Feuchtelastkategorie_list,
        "default":"Mittel",
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
    'thermalbridges': fields.String(default=params_mapping["thermalbridges"]["default"],
        required=False,
        enum=params_mapping["thermalbridges"]["values"],
        description="Wärmebrücken / fRSI-Wert",
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
    'window_class': fields.Integer(
        required=False,
        min=1,
        max=4,
        description="Fensterklasse nach EN12207 (betrachteter Raum)",
    ),
    'airing_type_room': fields.String(default=params_mapping["airing_type_room"]["default"],
        required=False,
        enum=params_mapping["airing_type_room"]["values"],
        description="Lüftungsmöglichkeit (betrachteter Raum):",
    ),
    'terrain_class': fields.Integer(
        required=False,
        min=1,
        max=5,
        description="Gelände-/Terrainklasse (Windeinfluss)",
    ),
    'shielding_class': fields.Integer(
        required=False,
        min=1,
        max=5,
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

    'H2Osource_category': fields.String(default=params_mapping["H2Osource_category"]["default"],
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
    'airing_duration': fields.Float(
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

plot_data = namespace.model('plot_data', {
    "x":fields.List(fields.Float(), example=[0,1,2,3,5]),
    "y":fields.List(fields.List(fields.Float()), example=[[0,1,2,3,5]]),
})

airing_resultdata = namespace.model('airing_resultdata', {
    "quantiles": fields.List(fields.Float(),
        example=[0.26,0.43,0.68,1.1,1.6],
        description='Zeit bis Grenzwert erreicht - [P5,P25,Med,P75,P95]'
    ),
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

    "Vdot_Inf": fields.List(fields.Float(),
        example=[3.7,5.3,7.6,11,16],
        description='Luftmenge durch Fugenlüftung [m³/h]'
    ),
    "Vdot_Tot": fields.List(fields.Float(),
        example=[35,43,51,62,79],
        description='Luftmenge durch Fugenlüftung + Fensterlüftung [m³/h]'
    ),

    "Vdot_req_pre": fields.List(fields.Float(),
        example=[19,25,32,42,63],
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

    "Vdot_req_abs": fields.List(fields.Float(),
        example=[2.9,4,5.1,6.5,8.9],
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

res_co2 = namespace.model('ResCO2', {
    'airing_acceptable': fields.Boolean(
        description="Fensterlüftung praktikabel/zumutbar"
    ),
    't_reasonable': fields.Float(
        description="Dies ist kürzer als die zumutbare Zeit zwischen Fensterlüften [min]"
    ),
    'CO2_stat': fields.List(fields.Float(), example=[ 7900, 13000, 19000, 28000, 46000],
        description='CO2 Konzentration im stationären Fall'
    ),
    'Vdot': fields.List(fields.Float(), example=[0.73, 1.1,  1.4,  1.9,  3.1],
        description='errechnete Luftmenge aufgrund natürlicher Lüftung [m³/h]'
    ),
    'ACR': fields.List(fields.Float(), example=[0.024, 0.03, 0.039, 0.05, 0.066],
        description='errechneter natürlicher Luftwechsel [1/h]'
    ),
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

inputs_result_model  = namespace.model('InputsResult', {
    'location': fields.String(),
    'building_n50': fields.List(fields.Float(), example=[1,2,3,4,5]),
    'building_type': fields.String(),
    'thermalbridges': fields.String(),
    'H_Rm': fields.List(fields.Float(), example=[1,2,3,4,5]),
    'A_Rm': fields.List(fields.Float(), example=[1,2,3,4,5]),
    'room_type': fields.String(),
    'window_area': fields.List(fields.Float(), example=[1,2,3,4,5]),
    'window_class': fields.List(fields.Integer(), example=[1,2,3,4,5]),
    'airing_type_room': fields.String(),
    'terrain_class': fields.List(fields.Integer(), example=[1,2,3,4,5]),
    'shielding_class': fields.List(fields.Integer(), example=[1,2,3,4,5]),

    'NrAdu': fields.List(fields.Float(), example=[1,2,3,4,5]),
    'ActAdu': fields.List(fields.Float(), example=[1,2,3,4,5]),
    'NrKids': fields.List(fields.Float(), example=[1,2,3,4,5]),
    'ActKid': fields.List(fields.Float(), example=[1,2,3,4,5]),
    'AgeKid': fields.List(fields.Float(), example=[1,2,3,4,5]),

    'H2Osource_category': fields.String(),
    'H2Osource_area': fields.List(fields.Float(), example=[1,2,3,4,5]),
    'H2Osource_pers': fields.List(fields.Float(), example=[1,2,3,4,5]),
    'H2Osource_area_abs': fields.List(fields.Float(), example=[1,2,3,4,5]),
    'area_home': fields.List(fields.Float(), example=[1,2,3,4,5]),
    'pers_home': fields.List(fields.Float(), example=[1,2,3,4,5]),
    'airing_type_home': fields.String(),
    'airing_duration': fields.List(fields.Float(), example=[1,2,3,4,5]),
    'Ti_avg': fields.List(fields.Float(), example=[1,2,3,4,5]),
    'Ti_min': fields.List(fields.Float(), example=[1,2,3,4,5]),
    'Ti_abs': fields.List(fields.Float(), example=[1,2,3,4,5]),
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

        errors = {}
        if 'shielding_class' in args and args['shielding_class'] is not None:
            if not args['shielding_class'] in params.Shield_class2C:
                errors["shielding_class"] = f"{args['shielding_class']} is not in {list(params.Shield_class2C.keys())}"
        if 'terrain_class' in args and args['terrain_class'] is not None:
            if not args['terrain_class'] in params.Shield_class2C:
                errors["terrain_class"] = f"{args['terrain_class']} is not in {list(params.Shield_class2C.keys())}"
        if 'window_class' in args and args['window_class'] is not None:
            if not args['window_class'] in [1,2,3,4]:
                errors["window_class"] = f"{args['window_class']} is not in [1,2,3,4]"

        if len(errors.keys()) != 0:
            namespace.abort(
                400, "Input payload validation failed", errors=errors
            )

        size = 1000

        inputs = {}
        quantiles = [0.05, 0.25, 0.5, 0.75, 0.95]

        #add defaults to input results
        for field in [
                "location", "building_type", "thermalbridges", "room_type",
                "airing_type_room", "H2Osource_category", "airing_type_home",
            ]:
            inputs[field] = args[field]

        #dummy data
        inputs["window_area"] = [1,2,3,4,5]
        inputs["window_class"] = [1,2,3,4,5]
        inputs["airing_duration"] = [1,2,3,4,5]
        inputs["Ti_avg"] = [1,2,3,4,5]
        inputs["Ti_min"] = [1,2,3,4,5]
        inputs["Ti_abs"] = [1,2,3,4,5]

        CO2_Emi = ltool.co2_emission(
            room_type = args['room_type'],
            inputs = inputs,
            quantiles = quantiles,
            NrAdu = args['NrAdu'],
            ActAdu = args['ActAdu'],
            NrKids = args['NrKids'],
            ActKid = args['ActKid'],
            AgeKid = args['AgeKid'],
            size = size
        )

        H_Rm, A_Rm = ltool.Raum(
            room_type = args['room_type'],
            inputs = inputs,
            quantiles = quantiles,
            H_Rm = args['H_Rm'],
            A_Rm = args['A_Rm'],
            size = size
        )

        return ltool.calc(
            location = args['location'],
            building_n50 = args['building_n50'],
            building_type = args['building_type'],
            inputs = inputs,
            thermalbridges = args['thermalbridges'],
            H_Rm = H_Rm,
            A_Rm = A_Rm,
            airing_type_room = args['airing_type_room'],
            Shield = args['shielding_class'],
            Terr = args['terrain_class'],
            # todo
            #window_area
            #window_class
            #luefungsdauer
            #pers_home
            #airing_type_home
            #airing_duration
            #Ti_avg
            #Ti_abs
            #Ti_min
            CO2_Emi = CO2_Emi,
            area_home = args['area_home'],
            H2Osource_category = args["H2Osource_category"],
            H2Osource_area = args['H2Osource_area'],
            H2Osource_pers = args['H2Osource_pers'],
            H2Osource_area_abs = args['H2Osource_area_abs'],
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
