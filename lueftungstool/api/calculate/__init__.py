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
    'standort': fields.String(default="Wien",
        required=True,
        enum=params.location_list,
        description="Standort",
    ),
    'gebaeude_n50': fields.String(default="Standard Neubau",
        required=True,
        enum=params.n50_map_list,
        description="Luftdichtigkeit n50-Wert (Gebäude) [1/h]",
    ),
    'gebaeudeart': fields.String(default="Mehrfamilienhaus",
        required=True,
        enum=params.gebaeudeart_list,
        description="Gebäudeart",
    ),
    'waermebruecken': fields.String(default="Standard Neubau",
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
    'raumart': fields.String(default="Schlafzimmer",
        required=True,
        enum=params.raumart_list,
        description="Raumart (betrachteter Raum):",
    ),
    'fensterflaeche': fields.Float(
        required=False,
        description="Fläche öffenbare Fenster (betrachteter Raum) [m²]:",
    ),
    'fensterklasse': fields.Integer(
        required=False,
        min=1,
        max=4,
        description="Fensterklasse nach EN12207 (betrachteter Raum)",
    ),
    'luefungsart': fields.String(default="Querlüftung",
        required=True,
        enum=params.luefungsart_list,
        description="Lüftungsmöglichkeit (betrachteter Raum):",
    ),
    'terrainklasse': fields.Integer(
        required=False,
        min=1,
        max=5,
        description="Gelände-/Terrainklasse (Windeinfluss)",
    ),
    'shieldingklasse': fields.Integer(
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

    'WNF': fields.Float(
        required=False,
        description="Fläche gesamte Wohneinheit [m²]:",
    ),
    'Feuchtelastkategorie': fields.String(default="Mittel",
        required=True,
        enum=params.Feuchtelastkategorie_list,
        description="Feuchtelast [l/d]:",
    ),
    'm_H2Od': fields.Float(
        required=False,
        description="Feuchtequellstärke pro m² bei Anwesenheit [g/(hm²)]",
    ),
    'm_H2Ok': fields.Float(
        required=False,
        description="Feuchtequellstärke pro Pers bei Anwesenheit [g/(hPers)]",
    ),
    'm_H2Od0': fields.Float(
        required=False,
        description="Feuchtequellstärke pro m² bei Abwesenheit [g/(hm²)]",
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

calculation_result_model = namespace.model('CalculationResult', {
    'Fensterlueftung': fields.Boolean(
        description="Fensterlüftung praktikabel/zumutbar"
    ),
    't_zumutbar': fields.Float(
        description="Dies ist kürzer als die zumutbare Zeit zwischen Fensterlüften [min]"
    ),
    'C_stat': fields.List(fields.Float(), default=[ 7900, 13000, 19000, 28000, 46000],
        description='CO2 Konzentration im stationären Fall'
    ),
    'Vdot': fields.List(fields.Float(), default=[0.73, 1.1,  1.4,  1.9,  3.1],
        description='errechnete Luftmenge aufgrund natürlicher Lüftung [m³/h]'
    ),
    'LWR': fields.List(fields.Float(), default=[0.024, 0.03, 0.039, 0.05, 0.066],
        description='errechneter natürlicher Luftwechsel [1/h]'
    ),
    't_gw_erreicht': fields.Nested(
        lueften_statistik,
        description='Gleitender Mittelwert - Realistisches Lüftungsverhalten'
    ),
    't_gw_periodisch': fields.Nested(
        lueften_statistik,
        description='Momentanwert - Realistisches Lüftungsverhalten'
    ),
    't_gw_ueberschritten': fields.Nested(
        lueften_statistik,
        description='Gleitender Mittelwert - Ideale Lüftung'
    ),
    't_gw_ideal': fields.Nested(
        lueften_statistik,
        description='Momentanwert - Ideale Lüftung'
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
        if 'shieldingklasse' in args and args['shieldingklasse'] is not None:
            if not args['shieldingklasse'] in params.Shield_class2C:
                errors["shieldingklasse"] = f"{args['shieldingklasse']} is not in {list(params.Shield_class2C.keys())}"
        if 'terrainklasse' in args and args['terrainklasse'] is not None:
            if not args['terrainklasse'] in params.Shield_class2C:
                errors["terrainklasse"] = f"{args['terrainklasse']} is not in {list(params.Shield_class2C.keys())}"
        if 'fensterklasse' in args and args['fensterklasse'] is not None:
            if not args['fensterklasse'] in [1,2,3,4]:
                errors["fensterklasse"] = f"{args['fensterklasse']} is not in [1,2,3,4]"

        if len(errors.keys()) != 0:
            namespace.abort(
                400, "Input payload validation failed", errors=errors
            )

        size = 1000

        CO2_Emi = ltool.co2_emission(
            raumart = args['raumart'],
            NrAdu = args['NrAdu'],
            ActAdu = args['ActAdu'],
            NrKids = args['NrKids'],
            ActKid = args['ActKid'],
            AgeKid = args['AgeKid'],
            size = size
        )

        H_Rm, A_Rm = ltool.Raum(
            raumart = args['raumart'],
            H_Rm = args['H_Rm'],
            A_Rm = args['A_Rm'],
            size = size
        )

        return ltool.calc(
            location = args['standort'],
            gebaeude_n50 = args['gebaeude_n50'],
            gebaeudeart = args['gebaeudeart'],
            waermebruecken = args['waermebruecken'],
            H_Rm = H_Rm,
            A_Rm = A_Rm,
            luefungsart = args['luefungsart'],
            Shield = args['shieldingklasse'],
            Terr = args['terrainklasse'],
            # todo
            #fensterflaeche
            #fensterklasse
            #luefungsdauer
            CO2_Emi = CO2_Emi,
            WNF = args['WNF'],
            Feuchtelastkategorie = args["Feuchtelastkategorie"],
            m_H2Od = args['m_H2Od'],
            m_H2Ok = args['m_H2Ok'],
            m_H2Od0 = args['m_H2Od0'],
            quantiles = [0.05, 0.25, 0.5, 0.75, 0.95],
            size = size
        )

parameter_result_model =  namespace.model('ParameterResult', {
    'values': fields.List(fields.String(),  
        description='Mögliche Werte für den angegebenen Parameter'
    )
})

params_mapping = {
    "standort":params.location_list,
    "gebaeudeart":params.gebaeudeart_list,
    "raumart":params.raumart_list,
    "luefungsart":params.luefungsart_list,
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
