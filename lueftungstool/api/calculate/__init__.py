from flask import request
from flask_restx import Namespace, Resource, fields, reqparse
from lueftungstool.lib.calc import calc
import lueftungstool.lib.params as params

def add_model_to_parser(parser,model):
    for k,v in model.items():
        a = v.schema()
        parser.add_argument(
            name=k,
            type={"string":str,"number":float}[a["type"]],
            help=a["description"],
            required=v.required,
            default=a["default"],
            choices=a.get("enum",None)
        )


namespace = Namespace('calculate', '#todo')

calculation_parameter_model = namespace.model('CalculationParameter', {
    'standort': fields.String(default="Wien",
        required=True,
        enum=params.standort_list,
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
    'luefungsart': fields.String(default="Querlüftung",
        required=True,
        enum=params.luefungsart_list,
        description="Lüftungsmöglichkeit (betrachteter Raum):",
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
        return calc(
            standort = args['standort'],
            gebaeude_n50 = args['gebaeude_n50'],
            gebaeudeart = args['gebaeudeart'],
            H_Rm = args['H_Rm'],
            A_Rm = args['A_Rm'],
            raumart = args['raumart'],
            luefungsart = args['luefungsart'],
            quantiles = [0.05, 0.25, 0.5, 0.75, 0.95],
        )

parameter_result_model =  namespace.model('ParameterResult', {
    'values': fields.List(fields.String(),  
        description='Mögliche Werte für den angegebenen Parameter'
    )
})

params_mapping = {
    "standort":params.standort_list,
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
