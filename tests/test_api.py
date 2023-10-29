
import typing

from lueftungstool.api.calculate import CalculationParameter, InputsResultModel
from tests.api_base import MyTestCase

from typing import _LiteralGenericAlias

class ApiParams(MyTestCase):

    def test_verify_calculation_parameters_are_present_at_params_endpoint(self):
        with self.app.test_request_context(f'/api/calculate/params', method='GET'):
            res = self.app.full_dispatch_request()
            self.assertTrue(res.status_code == 200, res.json)

            a = []
            for field,item in CalculationParameter.model_fields.items():
                if type(item.annotation) == _LiteralGenericAlias:
                    a.append(field)
                else:
                    for t in typing.get_args(item.annotation):
                        if type(t) == _LiteralGenericAlias:
                            a.append(field)

            self.assertCountEqual(a, res.json.keys())

class ApiCalculation(MyTestCase):
    def test_verify_all_input_fields_are_present_in_results(self):
        self.assertCountEqual(CalculationParameter.model_fields.keys(), InputsResultModel.model_fields.keys())

    def test_building_type_without_H2O_calculation(self):
        with self.app.test_request_context(
                '/api/calculate',
                query_string={
                    "location": "Wien",
                    "building_n50": "Standard Neubau",
                    "building_type": "Schule/Kindergarten",
                    "room_type": "Schlafzimmer",
                },
                method='GET'
            ):
            res = self.app.full_dispatch_request()
            self.assertTrue(res.status_code == 200, res.json)

    def test_verify_alle_input_fields_have_a_value_in_results(self):
        with self.app.test_request_context(
                '/api/calculate',
                query_string={
                    "location": "Wien",
                    "building_n50": "Standard Neubau",
                    "building_type": "Mehrfamilienhaus",
                    "room_type": "Schlafzimmer",
                },
                method='GET'
            ):
            res = self.app.full_dispatch_request()
            self.assertTrue(res.status_code == 200, res.json)
            for field in res.json["inputs"]:
                self.assertTrue(res.json["inputs"][field] is not None, f"field '{field}' is None")
