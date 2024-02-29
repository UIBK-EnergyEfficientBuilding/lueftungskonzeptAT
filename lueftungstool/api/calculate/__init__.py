

import lueftungstool.lib.calc2 as calc2
from lueftungstool.lib.params import params_mapping, params_mapping_co2, params_mapping_h2o
import lueftungstool.lib.helper as helper

from typing import Literal

from http import HTTPStatus
from pydantic import BaseModel, Field, ValidationError
from pydantic_core import InitErrorDetails
from flask import make_response, abort, current_app

from flask_openapi3 import APIBlueprint

blueprint = APIBlueprint("api", __name__, url_prefix='/api')
namespace = blueprint


class CalculationParameterGeneral(BaseModel):
    location: Literal[*params_mapping["location"]["values"]] = Field(
        enum=params_mapping["location"]["values"],
        example=params_mapping["location"]["default"],
        description="Standort"
    #location: Literal[*["Wien", "St. Pölten", "Eisenstadt", "Graz", "Klagenfurt", "Linz", "Salzburg", "Innsbruck", "Bregenz", "St. Anton", "Lienz", "Zell am See", "Schladming", "Leoben", "Gmünd"]] = Field(
    #    enum=params_mapping["location"]["values"],
    #    example=params_mapping["location"]["default"],
    #    description="Standort"
    )
    building_n50: float | Literal[*params_mapping["building_n50"]["values"]] = Field(
        enum=params_mapping["building_n50"]["values"],
        example=params_mapping["building_n50"]["default"],
        description="Luftdichtigkeit n50-Wert (Gebäude) [1/h]"
    )
    H_Rm: float | None = Field(None, description="Höhe (betrachteter Raum) [m]:")
    A_Rm: float | None = Field(None, description="Fläche (betrachteter Raum) [m²]:")
    room_type: Literal[*params_mapping["room_type"]["values"]] | None = Field(
        None,
        enum=params_mapping["room_type"]["values"],
        description="Raumart (betrachteter Raum):"
    )
    window_area: float | None = Field(None, description="Fläche öffenbare Fenster (betrachteter Raum) [m²]:")
    window_class: Literal[*params_mapping["window_class"]["values"]] | None = Field(
        None,
        enum=params_mapping["window_class"]["values"],
        description="Fensterklasse nach EN12207 (betrachteter Raum)"
    )
    terrain_class: Literal[*params_mapping["terrain_class"]["values"]] | None = Field(
        None,
        enum=params_mapping["terrain_class"]["values"],
        description="Gelände-/Terrainklasse (Windeinfluss)"
    )
    shielding_class: Literal[*params_mapping["shielding_class"]["values"]] | None = Field(
        None,
        enum=params_mapping["shielding_class"]["values"],
        description="Abschirmung-/Shieldingklasse (Windeinfluss)"
    )

    Ti_avg: float | None = Field(None, description="Mittlere Raumtemperatur in gesamten Wohneinheit [°C]")


class CalculationParameterCO2(CalculationParameterGeneral):
    building_type: Literal[*params_mapping["building_type"]["values"]] = Field(
        enum=params_mapping["building_type"]["values"],
        example=params_mapping["building_type"]["default"],
        description="Gebäudeart"
    )

    airing_type_room: Literal[*params_mapping["airing_type_room"]["values"]] | None = Field(
        None,
        enum=params_mapping["airing_type_room"]["values"],
        description="Lüftungsmöglichkeit (betrachteter Raum):"
    )
    airing_duration_room: float | None = Field(None, description="Lüftungsdauer pro Lüftungsvorgang [min]")

    NrAdu: float | None = Field(None, description="Anzahl Erwachsene")
    ActAdu: float | Literal[*params_mapping["ActAdu"]["values"]] | None = Field(
        None,
        enum=params_mapping["ActAdu"]["values"],
        description="Aktivität Erwachsene [met]"
    )
    NrKids: float | None = Field(None, description="Anzahl Kinder")
    ActKid: float | Literal[*params_mapping["ActKid"]["values"]] | None = Field(
        None,
        enum=params_mapping["ActKid"]["values"],
        description="Aktivität Kinder [met]"
    )
    AgeKid: float | None = Field(None, description="Mittleres Alter der Kinder [a]")


class CalculationParameterH2O(CalculationParameterGeneral):
    building_type: Literal[*params_mapping_h2o["building_type"]["values"]] = Field(
        enum=params_mapping_h2o["building_type"]["values"],
        example=params_mapping_h2o["building_type"]["default"],
        description="Gebäudeart"
    )

    H2Osource_category: Literal[*params_mapping["H2Osource_category"]["values"]] | None = Field(
        None,
        enum=params_mapping["H2Osource_category"]["values"],
        description="Feuchtelast [l/d]:"
    )
    H2Osource_area: float | None = Field(None, description="Feuchtequellstärke pro m² bei Anwesenheit [g/(hm²)]")
    H2Osource_pers: float | None = Field(None, description="Feuchtequellstärke pro Pers bei Anwesenheit [g/(hPers)]")
    H2Osource_area_abs: float | None = Field(None, description="Feuchtequellstärke pro m² bei Abwesenheit [g/(hm²)]")
    area_home: float | None = Field(None, description="Fläche gesamte Wohneinheit [m²]:")
    pers_home: float | None = Field(None, description="Personenanzahl (gesamter Wohneinheit)")
    H_unit: float | None = Field(None, description="Wohnungshöhe")
    airing_type_home: Literal[*params_mapping["airing_type_home"]["values"]] | None = Field(
        None,
        enum=params_mapping["airing_type_home"]["values"],
        description="Lüftungsmöglichkeit (gesamte Wohneinheit)"
    )
    airing_duration_home: float | None = Field(
        None, description="Lüftungsdauer gesamt, z.B. morgens und abends [min/Tag]"
    )
    thermalbridges: float | Literal[*params_mapping["thermalbridges"]["values"]] | None = Field(
        None,
        enum=params_mapping["thermalbridges"]["values"],
        description="Wärmebrücken / fRSI-Wert"
    )
    Ti_min: float | None = Field(None, description="Raumtemperatur im kühlsten Raum [°C]")
    Ti_abs: float | None = Field(None, description="Minimale Raumtemperatur bei längerer Abwesenheit [°C]")


class CalculationParameter(CalculationParameterCO2, CalculationParameterH2O):
    humcalc: bool = Field(True)


class PlotData(BaseModel):
    x: list[float]
    y: list[list[float]]


class AiringResultData(BaseModel):
    frequency: PlotData = Field(description='Zeit bis Grenzwert erreicht - Häufigkeit')
    timeseries: PlotData = Field(description='CO2 Konzentration')
    airing: PlotData = Field(description='CO2 Konzentration - Fenster offen')


class MouldriskPlot(BaseModel):
    ACR: PlotData = Field(description='Mittlere Luftwechselrate [1/h]')
    Vdot: PlotData = Field(description='Mittlerer Luftvolumenstrom [m³/h]')
    abs: PlotData = Field(description='Fälle mit Schimmelrisiko bei Anwesenheit')
    pre: PlotData = Field(description='Fälle mit Schimmelrisiko bei Abwesenheit')


class ResCo2Plot(BaseModel):
    avgC_realC0: AiringResultData = Field(description='Gleitender Mittelwert - Realistisches Lüftungsverhalten')
    instC_realC0: AiringResultData = Field(description='Momentanwert - Realistisches Lüftungsverhalten')
    avgC_idealC0: AiringResultData = Field(description='Gleitender Mittelwert - Ideale Lüftung')
    instC_idealC0: AiringResultData = Field(description='Momentanwert - Ideale Lüftung')


class ResultStatsFloat(BaseModel):
    mean: float
    error: float
    median: float
    quantiles: tuple[float, float, float, float, float] = Field(example=(1, 2, 3, 4, 5))


class ResultStatsInteger(BaseModel):
    min: int
    max: int
    quantiles: tuple[int, int, int, int, int] = Field(example=(1, 2, 3, 4, 5))


class ResCO2Model(BaseModel):
    airing_acceptable: bool = Field(..., description="Fensterlüftung praktikabel/zumutbar")
    t_reasonable: float = Field(..., description="Dies ist kürzer als die zumutbare Zeit zwischen Fensterlüften [min]")

    airing_acceptable: bool = Field(..., description="Fensterlüftung praktikabel/zumutbar")
    t_reasonable: float = Field(..., description="Dies ist kürzer als die zumutbare Zeit zwischen Fensterlüften [min]")
    t_avgC_realC0: ResultStatsFloat = Field(
        description='Zeit bis CO2-Stundenmittelwert=1000 ppm - realistisches Lüften [min]')
    t_instC_realC0: ResultStatsFloat = Field(
        description='Zeit bis CO2-Momentanwert=1000 ppm - realistisches Lüften [min]')
    t_avgC_idealC0: ResultStatsFloat = Field(
        description='Zeit bis CO2-Stundenmittelwert=1000 ppm - ideales Lüften [min]')
    t_instC_idealC0: ResultStatsFloat = Field(description='Zeit bis CO2-Momentanwert=1000 ppm - ideales Lüften [min]')
    CO2_stat: ResultStatsFloat = Field(description='CO2 Konzentration im stationären Fall')
    Vdot: ResultStatsFloat = Field(description='errechnete Luftmenge aufgrund natürlicher Lüftung [m³/h]')
    ACR: ResultStatsFloat = Field(description='errechneter natürlicher Luftwechsel [1/h]')

    t_instC_idealC0_a: ResultStatsFloat = Field(description='xxx tbd')
    t_instC_realC0_a: ResultStatsFloat = Field(description='xxx tbd')
    c0_instC: ResultStatsFloat = Field(description='xxx tbd')
    c0_avgC: ResultStatsFloat = Field(description='xxx tbd')
    c_instC_avgC4thresh: ResultStatsFloat = Field(description='')
    plot: ResCo2Plot = Field(description='Lüftungsverhalten - Plot data')


class ResH2OModel(BaseModel):
    MouldRisk: float = Field(..., example=0.219, description='Schimmelrisiko als Wahrscheinlichkeit')
    Vdot_acc: float = Field(
        ..., example=29.0, description='Erforderliche zusätzliche Luftmenge damit Wahrscheinlichkeit<1% [m³/h]')
    ELA_acc: float = Field(
        ..., example=120, description='dafür erforderlicher zusätzlicher freier Querschnitt [cm²]')

    Vdot_Inf: ResultStatsFloat = Field(description='Luftmenge durch Fugenlüftung [m³/h]')
    Vdot_Tot: ResultStatsFloat = Field(description='Luftmenge durch Fugenlüftung + Fensterlüftung [m³/h]')

    Vdot_req_pre: ResultStatsFloat = Field(description='Erforderliche Luftmenge zur Feuchteabfuhr [m³/h]')
    Frac_Inf_insuff_pre: float = Field(
        example=1, description='Wahrscheinlichkeit dass Fugenlüftung alleine nicht ausreicht')
    MouldRisk_pre: float = Field(
        example=0.072, description='Wahrscheinlichkeit dass Fugenlüftung und Fensterlüftung nicht ausreicht')
    Vdot_acc_pre: float = Field(
        example=12, description='Erforderliche zusätzliche Luftmenge damit Wahrscheinlichkeit <1% [m³/h]')
    ELA_acc_pre: float = Field(example=120, description='dafür erforderlicher zusätzlicher freier Querschnitt [cm²]')

    Vdot_req_abs: ResultStatsFloat = Field(description='Erforderliche Luftmenge zur Feuchteabfuhr [m³/h]')
    Frac_Inf_insuff_abs: float = Field(
        example=0.219, description='Wahrscheinlichkeit dass Fugenlüftung alleine nicht ausreicht')
    MouldRisk_abs: float = Field(example=0.219, description='Wahrscheinlichkeit dass Fugenlüftung nicht ausreicht')
    Vdot_acc_abs: float = Field(
        defaule=3.1, description='Erforderliche zusätzliche Luftmenge damit Wahrscheinlichkeit<1% [m³/h]')
    ELA_acc_abs: float = Field(example=41, description='dafür erforderlicher zusätzlicher freier Querschnitt [cm²]]')
    plot: MouldriskPlot = Field(description='Feuchtebewertung (Nur Wohnen) - Plot data')


class InputsResultModelGeneral(BaseModel):
    location: str
    building_n50: ResultStatsFloat
    building_type: str
    H_Rm: ResultStatsFloat
    A_Rm: ResultStatsFloat
    room_type: str
    window_area: ResultStatsFloat
    window_class: ResultStatsInteger
    terrain_class: ResultStatsInteger
    shielding_class: ResultStatsInteger

    Ti_avg: ResultStatsFloat = Field(None)


class InputsResultModelCO2(InputsResultModelGeneral):
    airing_type_room: str = Field(None)
    airing_duration_room: ResultStatsFloat = Field(None)
    terrain_class: ResultStatsInteger
    shielding_class: ResultStatsInteger

    NrAdu: ResultStatsInteger = Field(None)
    ActAdu: ResultStatsFloat = Field(None)
    NrKids: ResultStatsInteger = Field(None)
    ActKid: ResultStatsFloat = Field(None)
    AgeKid: ResultStatsFloat = Field(None)

    Ti_avg: ResultStatsFloat = Field(None)


class InputsResultModelH2O(InputsResultModelGeneral):
    H2Osource_category: ResultStatsFloat = Field(None)
    H2Osource_area: ResultStatsFloat = Field(None)
    H2Osource_pers: ResultStatsFloat = Field(None)
    H2Osource_area_abs: ResultStatsFloat = Field(None)
    H_unit: ResultStatsFloat = Field(None)
    area_home: ResultStatsFloat = Field(None)
    pers_home: ResultStatsFloat = Field(None)
    airing_type_home: str = Field(None)
    airing_duration_home: ResultStatsFloat = Field(None)
    thermalbridges: ResultStatsFloat = Field(None)
    Ti_min: ResultStatsFloat = Field(None)
    Ti_abs: ResultStatsFloat = Field(None)


class InputsResultModel(InputsResultModelH2O, InputsResultModelCO2):
    humcalc: bool


class CalculationResult(BaseModel):
    ResCO2: ResCO2Model = Field(None, description='Ergebnis CO2 Bewertung')
    ResH2O: ResH2OModel = Field(None, description='Ergebnis Schimmelrisiko Bewertung (nur für Wohnbau)')
    inputs: InputsResultModel = Field(..., description='inputs')


class CalculationResultCO2(BaseModel):
    ResCO2: ResCO2Model = Field(None, description='Ergebnis CO2 Bewertung')
    inputs: InputsResultModelCO2 = Field(..., description='inputs')


class CalculationResultH2O(BaseModel):
    ResH2O: ResH2OModel = Field(None, description='Ergebnis Schimmelrisiko Bewertung (nur für Wohnbau)')
    inputs: InputsResultModelH2O = Field(..., description='inputs')


def validate_dependentRequired(query: CalculationParameter, humcalc):
    needed = {"building_n50": ["window_class", "Ti_avg"]}
    if humcalc:
        needed["building_n50"] += ["thermalbridges", "Ti_min", "Ti_abs", "H_unit"]

    missing = []

    for k1, v1 in needed.items():
        if helper.castorfalse(getattr(query, k1), float):
            for v2 in v1:
                if getattr(query, v2) is None:
                    missing.append(InitErrorDetails(loc=[v2], type="missing"))

    if missing:
        e = ValidationError.from_exception_data(title="missing dependentRequired fields", line_errors=missing)
        validation_error_callback = getattr(current_app, "validation_error_callback")
        abort(validation_error_callback(e))


@namespace.get("/calculate/validate_inputs")
def validate_inputs(query: CalculationParameter):
    if query.humcalc:
        query.humcalc = calc2.humcalc(query.building_type)
    validate_dependentRequired(query, query.humcalc)

    response = make_response({}, HTTPStatus.OK)
    response.mimetype = "application/json"
    return response


@namespace.get("/calculate",
               responses={
                   HTTPStatus.OK: CalculationResult,
                   429: None
               })
def calculate(query: CalculationParameter):
    if query.humcalc:
        query.humcalc = calc2.humcalc(query.building_type)
    validate_dependentRequired(query, query.humcalc)

    args = query.model_dump()
    size = 1000
    message = CalculationResult(**calc2.calc(args, size))

    response = make_response(message.model_dump_json(), HTTPStatus.OK)
    response.mimetype = "application/json"
    return response


@namespace.get("/calculate/CO2/validate_inputs")
def validate_inputs_co2(query: CalculationParameterCO2):
    validate_dependentRequired(query, False)

    response = make_response({}, HTTPStatus.OK)
    response.mimetype = "application/json"
    return response


@namespace.get("/calculate/CO2",
               responses={
                   HTTPStatus.OK: CalculationResultCO2,
                   429: None
               })
def calculate_co2(query: CalculationParameterCO2):
    validate_dependentRequired(query, False)

    args = query.model_dump()
    size = 1000
    message = CalculationResultCO2(**calc2.calc_co2(args, size))

    response = make_response(message.model_dump_json(), HTTPStatus.OK)
    response.mimetype = "application/json"
    return response


@namespace.get("/calculate/H2O/validate_inputs")
def validate_inputs_h2o(query: CalculationParameterH2O):
    validate_dependentRequired(query, True)

    response = make_response({}, HTTPStatus.OK)
    response.mimetype = "application/json"
    return response


@namespace.get("/calculate/H2O",
               responses={
                   HTTPStatus.OK: CalculationResultH2O,
                   429: None
               })
def calculate_h2o(query: CalculationParameterH2O):
    validate_dependentRequired(query, True)

    args = query.model_dump()
    size = 1000
    message = CalculationResultH2O(**calc2.calc_h2o(args, size))

    response = make_response(message.model_dump_json(), HTTPStatus.OK)
    response.mimetype = "application/json"
    return response


class ParameterResult(BaseModel):
    values: list[str] = Field(description='Mögliche Werte für den angegebenen Parameter')
    default: str | None = Field(None)


class ParameterResultsGeneral(BaseModel):
    location: ParameterResult
    building_type: ParameterResult
    room_type: ParameterResult
    building_n50: ParameterResult
    terrain_class: ParameterResult
    shielding_class: ParameterResult
    window_class: ParameterResult


class ParameterResultsCO2(ParameterResultsGeneral):
    airing_type_room: ParameterResult
    ActAdu: ParameterResult
    ActKid: ParameterResult


class ParameterResultsH2O(ParameterResultsGeneral):
    airing_type_home: ParameterResult
    thermalbridges: ParameterResult
    H2Osource_category: ParameterResult


class ParameterResults(ParameterResultsCO2, ParameterResultsH2O):
    pass


@namespace.get('/calculate/params',
               responses={
                   HTTPStatus.OK: ParameterResults,
               })
def params():
    message = ParameterResults(**params_mapping)

    response = make_response(message.model_dump_json(), HTTPStatus.OK)
    response.mimetype = "application/json"
    return response


@namespace.get('/calculate/CO2/params',
               responses={
                   HTTPStatus.OK: ParameterResultsCO2,
               })
def params_co2():
    message = ParameterResultsCO2(**params_mapping_co2)

    response = make_response(message.model_dump_json(), HTTPStatus.OK)
    response.mimetype = "application/json"
    return response


@namespace.get('/calculate/H2O/params',
               responses={
                   HTTPStatus.OK: ParameterResultsH2O,
               })
def params_h2o():
    message = ParameterResultsH2O(**params_mapping_h2o)

    response = make_response(message.model_dump_json(), HTTPStatus.OK)
    response.mimetype = "application/json"
    return response
