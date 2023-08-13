
from flask_restx import fields

from lueftungstool.api.calculate import calculation_parameter_model, inputs_result_model
from tests.api_base import MyTestCase


class ApiParams(MyTestCase):
    def test_verify_calculation_parameters_are_present_at_params_endpoint(self):
        for field,item in calculation_parameter_model.items():
            if isinstance(item, fields.String):
                with self.app.test_request_context(f'/api/calculate/params/{field}', method='GET'):
                    res = self.app.full_dispatch_request()
                    self.assertTrue(res.status_code == 200, f"field: {field}, {res.json}")
                    result = res.json.get("values")
                    self.assertIsInstance(result, list)
                    self.assertGreater(len(result), 0)

class ApiCalculation(MyTestCase):
    def test_verify_all_input_fields_are_present_in_results(self):
        self.assertCountEqual(calculation_parameter_model.keys(), inputs_result_model.keys())

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
