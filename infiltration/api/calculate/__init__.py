from flask import request
from flask_restx import Namespace, Resource, fields
from infiltration.lib.calc import calc
import infiltration.lib.params as params

namespace = Namespace('calculate', '#todo')

class NullableFloat(fields.Float):
    __schema_type__ = ['number', "null"]
    __schema_example__ = 'null'

calculation_parameter_model = namespace.model('CalculationParameter', {
    'standort': fields.String(default="Wien",
        required=True,
        enum=params.standort_list,
        description='#todo'
    ),
    'gebaeude_n50': fields.String(default="Standard Neubau",
        required=True,
        enum=params.n50_map_list,
        description='#todo'
    ),
    'gebaeudeart': fields.String(default="Mehrfamilienhaus",
        required=True,
        enum=params.gebaeudeart_list,
        description='#todo'
    ),
    'H_Rm': NullableFloat(
        required=False,
        description='Raumhöhe'  
    ),
    'A_Rm': NullableFloat    (
        required=False,
        description='Raumfläche'
    ),
    'raumart': fields.String(default="Schlafzimmer",
        required=True,
        enum=params.raumart_list,
        description='#todo'
    ),
    'luefungsart': fields.String(default="Querlüftung",
        required=True,
        enum=params.luefungsart_list,
        description='#todo'
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
        description="Fensterlüftung praktikabel/zumutbar - Ja/Nein"
    ),
    't_zumutbar': fields.Float(
        description="Fensterlüftung praktikabel/zumutbar - Zeit [min]"
    ),
    'C_stat': fields.List(fields.Float(), default=[0,1,2,3,5],
        readonly=True,
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

@namespace.route('')
class Calculate(Resource):

    @namespace.expect(calculation_parameter_model, validate=True)
    @namespace.marshal_with(calculation_result_model)
    @namespace.response(500, 'Internal Server error')
    def get(self):
        return calc(
            standort = request.json['standort'],
            gebaeude_n50 = request.json['gebaeude_n50'],
            gebaeudeart = request.json['gebaeudeart'],
            H_Rm = request.json['H_Rm'],
            A_Rm = request.json['A_Rm'],
            raumart = request.json['raumart'],
            luefungsart = request.json['luefungsart'],
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
