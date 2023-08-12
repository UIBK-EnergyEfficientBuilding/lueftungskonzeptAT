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

calculation_parameter_model = namespace.model('CalculationParameter', {
    'location': fields.String(default="Wien",
        required=True,
        enum=params.location_list,
        description="Standort",
    ),
    'building_n50': fields.String(default="Standard Neubau",
        required=True,
        enum=params.n50_map_list,
        description="Luftdichtigkeit n50-Wert (Gebäude) [1/h]",
    ),
    'building_type': fields.String(default="Mehrfamilienhaus",
        required=True,
        enum=params.gebaeudeart_list,
        description="Gebäudeart",
    ),
    'thermalbridges': fields.String(default="Standard Neubau",
        required=True,
        enum=params.waermebruecken_list,
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
    'room_type': fields.String(default="Schlafzimmer",
        required=True,
        enum=params.raumart_list,
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
    'airing_type_room': fields.String(default="Querlüftung",
        required=True,
        enum=params.luefungsart_list,
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

    'H2Osource_category': fields.String(default="Mittel",
        required=True,
        enum=params.Feuchtelastkategorie_list,
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
    'airing_type_home': fields.Float(
        required=False,
        description="Lüftungsmöglichkeit (gesamte Wohneinheit)",
    ),
    'airing_duration': fields.Float(
        required=False,
        description="Lüftungsdauer gesamt, z.B. morgens und abends [min/Tag]",
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
    "x":fields.List(fields.Float(), default=[0,1,2,3,5]),
    "y":fields.List(fields.List(fields.Float()), default=[[0,1,2,3,5]]),
})

lueften_statistik = namespace.model('LüftenStatistik', {
    "Quantile": fields.List(fields.Float(),
        default=[0.26,0.43,0.68,1.1,1.6],
        description='Zeit bis Grenzwert erreicht - [P5,P25,Med,P75,P95]'
    ),
    'Häufigkeit': fields.Nested(
        plot_data,
        description='Zeit bis Grenzwert erreicht - Häufigkeit'
    ),
    'Mittelwert': fields.Nested(
        plot_data,
        description='CO2 Konzentration - Mittelwert'
    ),
})

mould_risk = namespace.model('MouldRisk', {
    'MouldRisk': fields.Float(
        default=0.219,
        description='Schimmelrisiko als Wahrscheinlichkeit'
    ),

    "Vdot_Inf": fields.List(fields.Float(),
        default=[3.7,5.3,7.6,11,16],
        description='Luftmenge durch Fugenlüftung [m³/h]'
    ),
    "Vdot_Tot": fields.List(fields.Float(),
        default=[35,43,51,62,79],
        description='Luftmenge durch Fugenlüftung + Fensterlüftung [m³/h]'
    ),

    "Vdot_req_pre": fields.List(fields.Float(),
        default=[19,25,32,42,63],
        description='Erforderliche Luftmenge zur Feuchteabfuhr [m³/h]'
    ),
    'Frac_Inf_insuff_pre': fields.Float(
        default=1,
        description='Wahrscheinlichkeit dass Fugenlüftung alleine nicht ausreicht'
    ),
    'MouldRisk_pre': fields.Float(
        default=0.072,
        description='Wahrscheinlichkeit dass Fugenlüftung und Fensterlüftung nicht ausreicht'
    ),
    "Vdot_acc_pre": fields.Float(
        default=12,
        description='Erforderliche zusätzliche Luftmenge damit Wahrscheinlichkeit <1% [m³/h]'
    ),
    "ELA_acc_pre": fields.Float(
        default=120,
        description='dafür erforderlicher zusätzlicher freier Querschnitt [cm²]'
    ),

    "Vdot_req_abs": fields.List(fields.Float(),
        default=[2.9,4,5.1,6.5,8.9],
        description='Erforderliche Luftmenge zur Feuchteabfuhr [m³/h]'
    ),
    'Frac_Inf_insuff_abs': fields.Float(
        default=0.219,
        description='Wahrscheinlichkeit dass Fugenlüftung alleine nicht ausreicht'
    ),
    'MouldRisk_abs': fields.Float(
        default=0.219,
        description='Wahrscheinlichkeit dass Fugenlüftung nicht ausreicht'
    ),
    "Vdot_acc_abs": fields.Float(
        defaule=3.1,
        description='Erforderliche zusätzliche Luftmenge damit Wahrscheinlichkeit<1% [m³/h]'
    ),
    "ELA_acc_abs": fields.Float(
        default=41,
        description='dafür erforderlicher zusätzlicher freier Querschnitt [cm²]]'
    ),
})

calculation_result_model = namespace.model('CalculationResult', {
    'airing_acceptable': fields.Boolean(
        description="Fensterlüftung praktikabel/zumutbar"
    ),
    't_reasonable': fields.Float(
        description="Dies ist kürzer als die zumutbare Zeit zwischen Fensterlüften [min]"
    ),
    'CO2_stat': fields.List(fields.Float(), default=[ 7900, 13000, 19000, 28000, 46000],
        description='CO2 Konzentration im stationären Fall'
    ),
    'Vdot': fields.List(fields.Float(), default=[0.73, 1.1,  1.4,  1.9,  3.1],
        description='errechnete Luftmenge aufgrund natürlicher Lüftung [m³/h]'
    ),
    'ACR': fields.List(fields.Float(), default=[0.024, 0.03, 0.039, 0.05, 0.066],
        description='errechneter natürlicher Luftwechsel [1/h]'
    ),
    't_avgC_realC0': fields.Nested(
        lueften_statistik,
        description='Gleitender Mittelwert - Realistisches Lüftungsverhalten'
    ),
    't_instC_realC0': fields.Nested(
        lueften_statistik,
        description='Momentanwert - Realistisches Lüftungsverhalten'
    ),
    't_avgC_idealC0': fields.Nested(
        lueften_statistik,
        description='Gleitender Mittelwert - Ideale Lüftung'
    ),
    't_instC_idealC0': fields.Nested(
        lueften_statistik,
        description='Momentanwert - Ideale Lüftung'
    ),
    'MouldRisk': fields.Nested(
        mould_risk,
        description='Ergebnis Schimmelrisiko Bewertung (nur für Wohnbau)'
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

parameter_result_model =  namespace.model('ParameterResult', {
    'values': fields.List(fields.String(),  
        description='Mögliche Werte für den angegebenen Parameter'
    )
})

params_mapping = {
    "location":params.location_list,
    "building_type":params.gebaeudeart_list,
    "room_type":params.raumart_list,
    "airing_type_room":params.luefungsart_list,
    "n50_map":params.n50_map_list,
}

@namespace.route('/params/<string:name>')
class Parameter(Resource):
    @namespace.marshal_with(parameter_result_model)
    @namespace.response(404, 'Not Found')
    @namespace.response(500, 'Internal Server error')
    def get(self, name):
        if name not in params_mapping:
            return namespace.abort(404, "Not Found")
        return {"values":params_mapping[name]}
