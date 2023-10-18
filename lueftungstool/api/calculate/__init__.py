from flask import request
from flask_restx import Namespace, Resource, fields, reqparse

import lueftungstool.lib.calc2 as calc2
from lueftungstool.lib.params import params_mapping


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
    'airing_type_room': fields.String(
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
    'ActLevelAdu': fields.String(
        required=False,
        enum=params_mapping["ActLevelAdu"]["values"],
        description="Aktivitäts Level Erwachsene [met]",
    ),
    'NrKids': fields.Float(
        required=False,
        description="Anzahl Kinder",
    ),
    'ActKid': fields.Float(
        required=False,
        description="Aktivität Kinder [met]",
    ),
    'ActLevelKid': fields.String(
        required=False,
        enum=params_mapping["ActLevelKid"]["values"],
        description="Aktivitäts Level Kinder [met]",
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
    'airing_type_home': fields.String(
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
    'ActLevelAdu': fields.String(),
    'NrKids': fields.Nested(result_stats_integer_model),
    'ActKid': fields.Nested(result_stats_float_model),
    'ActLevelKid': fields.String(),
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
        return calc2.calc(args,size)

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
