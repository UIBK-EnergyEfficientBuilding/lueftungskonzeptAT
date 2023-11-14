
import typing

from lueftungstool.api.calculate import CalculationParameter, CalculationParameterCO2, CalculationParameterH2O, InputsResultModel
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

    def test_verify_calculation_parameters_are_present_at_params_co2_endpoint(self):
        with self.app.test_request_context(f'/api/calculate/CO2/params', method='GET'):
            res = self.app.full_dispatch_request()
            self.assertTrue(res.status_code == 200, res.json)

            a = []
            for field,item in CalculationParameterCO2.model_fields.items():
                if type(item.annotation) == _LiteralGenericAlias:
                    a.append(field)
                else:
                    for t in typing.get_args(item.annotation):
                        if type(t) == _LiteralGenericAlias:
                            a.append(field)

            self.assertCountEqual(a, res.json.keys())


    def test_verify_calculation_parameters_are_present_at_params_h2o_endpoint(self):
        with self.app.test_request_context(f'/api/calculate/H2O/params', method='GET'):
            res = self.app.full_dispatch_request()
            self.assertTrue(res.status_code == 200, res.json)

            a = []
            for field,item in CalculationParameterH2O.model_fields.items():
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

    def test_zero_as_value_for_NrAdu(self):
        with self.app.test_request_context(
                '/api/calculate',
                query_string={
                    "location": "Wien",
                    "building_n50": "Standard Neubau",
                    "building_type": "Mehrfamilienhaus",
                    "NrAdu": "0",
                },
                method='GET'
            ):
            res = self.app.full_dispatch_request()
            self.assertTrue(res.status_code == 200, res.json)
            self.assertTrue(res.json["inputs"]["NrAdu"]["min"] == 0, res.json["inputs"]["NrAdu"])
            self.assertTrue(res.json["inputs"]["NrAdu"]["max"] == 0, res.json["inputs"]["NrAdu"])

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

    def test_building_n50_with_number_calculation(self):
        with self.app.test_request_context(
                '/api/calculate',
                query_string={
                    "location": "Wien",
                    "building_type": "Mehrfamilienhaus",
                    "building_n50": "1.5",
                    "window_class": "2: eher undicht",
                    "thermalbridges": "0.7",
                    "Ti_avg": "21",
                    "Ti_min": "18",
                    "Ti_abs": "17",
                },
                method='GET'
            ):
            res = self.app.full_dispatch_request()
            self.assertTrue(res.status_code == 200, res.json)

class ApiDependentRequired(MyTestCase):
    def test_building_n50_with_number_calculation_h2o_ok(self):

        for test in [{
                "location": "Wien",
                "building_type": "Mehrfamilienhaus",
                "building_n50": "1.5",
                "window_class": "2: eher undicht",
                "thermalbridges": "0.7",
                "Ti_avg": "21",
                "Ti_min": "18",
                "Ti_abs": "17",
            }
        ]:

            with self.app.test_request_context(
                    '/api/calculate/H2O',
                    query_string=test,
                    method='GET'
                ):
                res = self.app.full_dispatch_request()
                self.assertTrue(res.status_code == 200, res.json)

    def test_building_n50_with_number_calculation_h2o_missing(self):

        for test,missing in [[{
                "location": "Wien",
                "building_type": "Mehrfamilienhaus",
                "building_n50": "1.5",
                "window_class": "2: eher undicht",
                "thermalbridges": "0.7",
                "Ti_avg": "21",
            }, ["Ti_min", "Ti_abs"]],[{
                "location": "Wien",
                "building_type": "Mehrfamilienhaus",
                "building_n50": "1.5",
                "window_class": "2: eher undicht",
                "Ti_min": "18",
                "Ti_abs": "17",
            }, ["thermalbridges","Ti_avg"]],[{
                "location": "Wien",
                "building_type": "Mehrfamilienhaus",
                "building_n50": "1.5",
                "window_class": "2: eher undicht",
                "thermalbridges": "0.7",
            }, ["Ti_avg","Ti_min","Ti_abs"]]
        ]:

            with self.app.test_request_context(
                    '/api/calculate/H2O',
                    query_string=test,
                    method='GET'
                ):
                res = self.app.full_dispatch_request()
                self.assertTrue(res.status_code == 422, res.json)
                self.assertCountEqual(missing, [a['loc'][0] for a in res.json])


    def test_building_n50_with_number_calculation_co2_ok(self):

        for test in [{
                "location": "Wien",
                "building_type": "Mehrfamilienhaus",
                "building_n50": "1.5",
                "window_class": "2: eher undicht",
                "Ti_avg": "21",
            },
        ]:

            with self.app.test_request_context(
                    '/api/calculate/CO2',
                    query_string=test,
                    method='GET'
                ):
                res = self.app.full_dispatch_request()
                self.assertTrue(res.status_code == 200, res.json)

    def test_building_n50_with_number_calculation_co2_missing(self):

        for test,missing in [[{
                "location": "Wien",
                "building_type": "Mehrfamilienhaus",
                "building_n50": "1.5",
                "window_class": "2: eher undicht",
            }, ["Ti_avg"]]
        ]:

            with self.app.test_request_context(
                    '/api/calculate/CO2',
                    query_string=test,
                    method='GET'
                ):
                res = self.app.full_dispatch_request()
                self.assertTrue(res.status_code == 422, res.json)
                self.assertCountEqual(missing, [a['loc'][0] for a in res.json])
