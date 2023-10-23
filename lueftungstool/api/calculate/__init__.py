
import lueftungstool.lib.calc2 as calc2
from lueftungstool.lib.params import params_mapping

from http import HTTPStatus
from pydantic import BaseModel, Field
from flask import make_response

from flask_openapi3 import APIBlueprint

blueprint = APIBlueprint("api", __name__, url_prefix='/api')
namespace = blueprint


class CalculationParameter(BaseModel):
    location: str = Field(
        params_mapping["location"]["default"], enum=params_mapping["location"]["values"], description="Standort")
    building_n50: str = Field(
        params_mapping["building_n50"]["default"], enum=params_mapping["building_n50"]["values"], description="Luftdichtigkeit n50-Wert (Gebäude) [1/h]")
    building_type: str = Field(params_mapping["building_type"]["default"],
                               enum=params_mapping["building_type"]["values"], description="Gebäudeart",)
    thermalbridges: str | None = Field(
        None, enum=params_mapping["thermalbridges"]["values"], description="Wärmebrücken")
    fRSI: float | None = Field(None, description="fRSI-Wert")
    H_Rm: float | None = Field(None, description="Höhe (betrachteter Raum) [m]:")
    A_Rm: float | None = Field(None, description="Fläche (betrachteter Raum) [m²]:")
    room_type: str | None = Field(
        None, enum=params_mapping["room_type"]["values"], description="Raumart (betrachteter Raum):")
    window_area: float | None = Field(None, description="Fläche öffenbare Fenster (betrachteter Raum) [m²]:")
    window_class: str | None = Field(
        None, enum=params_mapping["window_class"]["values"], description="Fensterklasse nach EN12207 (betrachteter Raum)")
    airing_type_room: str | None = Field(
        None, enum=params_mapping["airing_type_room"]["values"], description="Lüftungsmöglichkeit (betrachteter Raum):")
    airing_duration_room: float | None = Field(None, description="Lüftungsdauer pro Lüftungsvorgang [min]")
    terrain_class: str | None = Field(
        None, enum=params_mapping["terrain_class"]["values"], description="Gelände-/Terrainklasse (Windeinfluss)")
    shielding_class: str | None = Field(None, enum=params_mapping["shielding_class"]["values"],
                                        description="Abschirmung-/Shieldingklasse (Windeinfluss)")

    NrAdu: float | None = Field(None, description="Anzahl Erwachsene")
    ActAdu: float | None = Field(None, description="Aktivität Erwachsene [met]")
    ActLevelAdu: str | None = Field(
        None, enum=params_mapping["ActLevelAdu"]["values"], description="Aktivitäts Level Erwachsene [met]")
    NrKids: float | None = Field(None, description="Anzahl Kinder")
    ActKid: float | None = Field(None, description="Aktivität Kinder [met]",)
    ActLevelKid: str | None = Field(
        None, enum=params_mapping["ActLevelKid"]["values"], description="Aktivitäts Level Kinder [met]"
    )
    AgeKid: float | None = Field(None, description="Mittleres Alter der Kinder [a]")

    H2Osource_category: str | None = Field(
        None, enum=params_mapping["H2Osource_category"]["values"], description="Feuchtelast [l/d]:")
    H2Osource_area: float | None = Field(None, description="Feuchtequellstärke pro m² bei Anwesenheit [g/(hm²)]")
    H2Osource_pers: float | None = Field(None, description="Feuchtequellstärke pro Pers bei Anwesenheit [g/(hPers)]")
    H2Osource_area_abs: float | None = Field(None, description="Feuchtequellstärke pro m² bei Abwesenheit [g/(hm²)]")
    area_home: float | None = Field(None, description="Fläche gesamte Wohneinheit [m²]:")
    pers_home: float | None = Field(None, description="Personenanzahl (gesamter Wohneinheit)")
    airing_type_home: str | None = Field(
        None, enum=params_mapping["airing_type_home"]["values"], description="Lüftungsmöglichkeit (gesamte Wohneinheit)")
    airing_duration_home: float | None = Field(
        None, description="Lüftungsdauer gesamt, z.B. morgens und abends [min/Tag]")
    Ti_avg: float | None = Field(None, description="Mittlere Raumtemperatur in gesamten Wohneinheit [°C]")
    Ti_min: float | None = Field(None, description="Raumtemperatur im kühlsten Raum [°C]")
    Ti_abs: float | None = Field(None, description="Minimale Raumtemperatur bei längerer Abwesenheit [°C]")


class PlotData(BaseModel):
    x: list[float]
    y: list[list[float]]


class AiringResultData(BaseModel):
    frequency: PlotData = Field(description='Zeit bis Grenzwert erreicht - Häufigkeit')
    timeseries: PlotData = Field(description='CO2 Konzentration')


class MouldriskPlot(BaseModel):
    ACR: PlotData = Field(description='Mittlere Luftwechselrate [1/h]')
    Vdot: PlotData = Field(description='Mittlerer Luftvolumenstrom [m³/h]')
    abs: PlotData = Field(description='Fälle mit Schimmelrisiko bei Anwesenheit')
    pre: PlotData = Field(description='Fälle mit Schimmelrisiko bei Abwesenheit')


class ResCo2Plot(BaseModel):
    t_avgC_realC0: AiringResultData = Field(description='Gleitender Mittelwert - Realistisches Lüftungsverhalten')
    t_instC_realC0: AiringResultData = Field(description='Momentanwert - Realistisches Lüftungsverhalten')
    t_avgC_idealC0: AiringResultData = Field(description='Gleitender Mittelwert - Ideale Lüftung')
    t_instC_idealC0: AiringResultData = Field(description='Momentanwert - Ideale Lüftung')


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
    plot: ResCo2Plot = Field(description='Lüftungsverhalten - Plot data')


class ResH2OModel(BaseModel):
    MouldRisk: float = Field(..., example=0.219, description='Schimmelrisiko als Wahrscheinlichkeit')
    Vdot_acc: float = Field(
        ..., example=29.0, description='Erforderliche zusätzliche Luftmenge damit Wahrscheinlichkeit<1% [m³/h]')

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


class InputsResultModel(BaseModel):
    location: str
    building_n50: ResultStatsFloat
    building_type: str
    thermalbridges: str
    fRSI: ResultStatsFloat
    H_Rm: ResultStatsFloat
    A_Rm: ResultStatsFloat
    room_type: str
    window_area: ResultStatsFloat
    window_class: ResultStatsInteger
    airing_type_room: str
    airing_duration_room: ResultStatsFloat
    terrain_class: ResultStatsInteger
    shielding_class: ResultStatsInteger

    NrAdu: ResultStatsInteger
    ActAdu: ResultStatsFloat
    ActLevelAdu: str
    NrKids: ResultStatsInteger
    ActKid: ResultStatsFloat
    ActLevelKid: str
    AgeKid: ResultStatsFloat

    H2Osource_category: ResultStatsFloat | None = Field(None)
    H2Osource_area: ResultStatsFloat = Field(None)
    H2Osource_pers: ResultStatsFloat = Field(None)
    H2Osource_area_abs: ResultStatsFloat = Field(None)
    area_home: ResultStatsFloat = Field(None)
    pers_home: ResultStatsFloat = Field(None)
    airing_type_home: str = Field(None)
    airing_duration_home: ResultStatsFloat = Field(None)
    Ti_avg: ResultStatsFloat = Field(None)
    Ti_min: ResultStatsFloat = Field(None)
    Ti_abs: ResultStatsFloat = Field(None)


class CalculationResult(BaseModel):
    ResCO2: ResCO2Model = Field(..., description='Ergebnis CO2 Bewertung')
    ResH2O: ResH2OModel = Field(None, description='Ergebnis Schimmelrisiko Bewertung (nur für Wohnbau)')
    inputs: InputsResultModel = Field(..., description='inputs')


@namespace.get("/calculate",
               responses={
                   HTTPStatus.OK: CalculationResult,
                   429: None
               })
def calculate(query: CalculationParameter):
    args = query.model_dump()
    size = 1000
    message = CalculationResult(**calc2.calc(args, size))

    response = make_response(message.model_dump_json(), HTTPStatus.OK)
    response.mimetype = "application/json"
    return response


class ParameterResult(BaseModel):
    values: list[str] = Field(description='Mögliche Werte für den angegebenen Parameter')
    default: str | None = Field(None)


class ParameterResults(BaseModel):
    location: ParameterResult
    building_type: ParameterResult
    room_type: ParameterResult
    airing_type_room: ParameterResult
    airing_type_home: ParameterResult
    building_n50: ParameterResult
    thermalbridges: ParameterResult
    H2Osource_category: ParameterResult
    terrain_class: ParameterResult
    shielding_class: ParameterResult
    window_class: ParameterResult
    ActLevelAdu: ParameterResult
    ActLevelKid: ParameterResult


@namespace.get('/params',
               responses={
                   HTTPStatus.OK: ParameterResults,
               })
def params():
    message = ParameterResults(**params_mapping)

    response = make_response(message.model_dump_json(), HTTPStatus.OK)
    response.mimetype = "application/json"
    return response
