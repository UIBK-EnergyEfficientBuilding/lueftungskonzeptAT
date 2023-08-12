
import lueftungstool.lib.calc as ltool

def format_quantile(quantile):
    return f"<{quantile[0]}|{quantile[2]}|{quantile[4]}>"

def print_row(text,quantile):
    print(text.ljust(75,' '), str(quantile[2]).ljust(10), format_quantile(quantile))

if __name__ == "__main__":
    quantiles = [0.05, 0.25, 0.5, 0.75, 0.95]
    size = 1000
    signDig=2   #tbd add to a settings dict
    room_type = "Schlafzimmer"

    inputs = {}

    CO2_Emi = ltool.co2_emission(
        room_type = room_type,
        inputs = inputs,
        quantiles = quantiles,
        size = size
    )

    H_Rm, A_Rm = ltool.Raum(
        room_type = room_type,
        inputs = inputs,
        quantiles = quantiles,
        size = size
    )

    result = ltool.calc(
        location = "Wien",
        building_n50 = "Standard Neubau",
        building_type = "Mehrfamilienhaus",
        inputs = inputs,
        thermalbridges = "Standard Neubau",
        H_Rm = H_Rm,
        A_Rm = A_Rm,
        airing_type_room = "Querlüftung",
        Shield = None,
        Terr = None,
        CO2_Emi = CO2_Emi,
        area_home = None,
        H2Osource_category = "Mittel",
        H2Osource_area = None,
        H2Osource_pers = None,
        H2Osource_area_abs = None,
        quantiles = quantiles,
        size = size
    )

    print("#Eingaben Gebäude/Raum")
    print("Standort:".ljust(75), "?")
    print("Gebäudeart:".ljust(75), "?")
    print_row("Luftdichtigkeit n50-Wert (Gebäude) [1/h]:".ljust(75), result["inputs"]["building_n50"])
    print("Raumart (betrachteter Raum):".ljust(75), "?")
    print_row("Fläche (betrachteter Raum) [m²]:".ljust(75), result["inputs"]["A_Rm"])
    print_row("Höhe (betrachteter Raum) [m]:".ljust(75), result["inputs"]["H_Rm"])
    print("Fläche öffenbare Fenster (betrachteter Raum) [m²]:".ljust(75), "?")
    print("Fensterklasse nach EN12207 (betrachteter Raum)".ljust(75), "?")
    print("Lüftungsmöglichkeit (betrachteter Raum):".ljust(75), "?")
    print("Lüftungsdauer pro Lüftungsvorgang [min]:".ljust(75), "?")
    print_row("Gelände-/Terrainklasse (Windeinfluss)".ljust(75), result["inputs"]["terrainklasse"])
    print_row("Abschirmung-/Shieldingklasse (Windeinfluss)".ljust(75), result["inputs"]["shieldingklasse"])
    print("Eingaben Personen für betrachteten Raum".ljust(75), "?")
    print_row("Anzahl Erwachsene:".ljust(75), result["inputs"]["NrAdu"])
    print_row("Aktivität Erwachsene [met]:".ljust(75), result["inputs"]["ActAdu"])
    print_row("Anzahl Kinder:".ljust(75), result["inputs"]["NrKids"])
    print_row("Aktivität Kinder [met]:".ljust(75), result["inputs"]["ActKid"])
    print_row("Mittleres Alter der Kinder [a]".ljust(75), result["inputs"]["AgeKid"])
    if "ResH2O" in result:
        print()
        print("#Eingaben für Schimmelrisiko Bewertung (nur für Wohnbau)")
        print("Berechnung durchführen:".ljust(75), "Ja")
        print("Wärmebrücken / fRSI-Wert".ljust(75), "?")
        print("Feuchtelast [l/d]:".ljust(75), "?")
        print_row("Feuchtequellstärke pro m² bei Anwesenheit [g/(hm²)]".ljust(75), result["inputs"]["H2Osource_area"])
        print_row("Feuchtequellstärke pro Pers bei Anwesenheit [g/(hPers)]".ljust(75), result["inputs"]["H2Osource_pers"])
        print_row("Feuchtequellstärke pro m² bei Abwesenheit [g/(hm²)]".ljust(75), result["inputs"]["H2Osource_area_abs"])
        print_row("Fläche gesamte Wohneinheit [m²]:".ljust(75), result["inputs"]["area_home"])
        print_row("Personenanzahl (gesamter Wohneinheit):".ljust(75), result["inputs"]["AvgPers"])
        print("Lüftungsmöglichkeit (gesamte Wohneinheit):".ljust(75), "?")
        print("Lüftungsdauer gesamt, z.B. morgens und abends [min/Tag]:".ljust(75), "?")
        print("Mittlere Raumtemperatur in gesamten Wohneinheit [°C]:".ljust(75), "?")
        print("Raumtemperatur im kühlsten Raum [°C]:".ljust(75), "?")
        print("Minimale Raumtemperatur bei längerer Abwesenheit [°C]:".ljust(75), "?")



    print("#Ergebnis CO2 Bewertung")
    print("Fensterlüftung praktikabel/zumutbar:".ljust(75), result["airing_acceptable"])
    print_row("Weil errechnete Zeit zwischen erforderlichen Fensterlüften [min]:", result["t_avgC_realC0"]["quantiles"])
    print("Dies ist kürzer als die zumutbare Zeit zwischen Fensterlüften [min]:".ljust(75), result["t_reasonable"])
    print_row("Informativ: Zeit zwischen erf. Fensterlüften bei idealem Lüften [min]:", result["t_avgC_idealC0"]["quantiles"])
    print()
    print("#Detailergebnisse CO2 Bewertung")
    print_row("errechnete Luftmenge aufgrund natürlicher Lüftung [m³/h]:", result["Vdot"])
    print_row("errechneter natürlicher Luftwechsel [1/h]:", result["ACR"])
    print_row("Zeit bis CO2-Stundenmittelwert=1000 ppm - realistisches Lüften [min]:", result["t_avgC_realC0"]["quantiles"])
    print_row("Zeit bis CO2-Momentanwert=1000 ppm - realistisches Lüften [min]:", result["t_instC_realC0"]["quantiles"])
    print_row("Zeit bis CO2-Stundenmittelwert=1000 ppm - ideales Lüften [min]:", result["t_avgC_idealC0"]["quantiles"])
    print_row("Zeit bis CO2-Momentanwert=1000 ppm - ideales Lüften [min]:", result["t_instC_idealC0"]["quantiles"])
    print_row("CO2 Konzentration im stationären Fall (t→∞) [ppm]:", result["CO2_stat"])

    if "ResH2O" in result:
        print()
        print("#Ergebnis Schimmelrisiko Bewertung (nur für Wohnbau)")
        print("Schimmelrisiko als Wahrscheinlichkeit".ljust(75),"%.1f"%(result["ResH2O"]["MouldRisk"]*100),"%")
        print()
        print("#Anwesenheitsfall (inkl. aktives Lüften)")
        print_row("Erforderliche Luftmenge zur Feuchteabfuhr [m³/h]:".ljust(75),result["ResH2O"]["Vdot_req_pre"])
        print_row("Luftmenge durch Fugenlüftung [m³/h]:".ljust(75),result["ResH2O"]["Vdot_Inf"])
        print("Wahrscheinlichkeit dass Fugenlüftung alleine nicht ausreicht:".ljust(75),"%.1f"%(result["ResH2O"]["Frac_Inf_insuff_pre"]*100),"%")
        print_row("Luftmenge durch Fugenlüftung + Fensterlüftung [m³/h]:".ljust(75), result["ResH2O"]["Vdot_Tot"])
        print("Wahrscheinlichkeit dass Fugenlüftung und Fensterlüftung nicht ausreicht:".ljust(75),"%.1f"%(result["ResH2O"]["MouldRisk_pre"]*100),"%")
        print("Erforderliche zusätzliche Luftmenge damit Wahrscheinlichkeit <1% [m³/h]:".ljust(75),result["ResH2O"]["Vdot_acc_pre"])
        print("dafür erforderlicher zusätzlicher freier Querschnitt [cm²]:".ljust(75),result["ResH2O"]["ELA_acc_pre"])
        print()
        print("#Abwesenheitsfall")
        print_row("Erforderliche Luftmenge zur Feuchteabfuhr [m³/h]:".ljust(75),result["ResH2O"]["Vdot_req_abs"])
        print_row("Luftmenge durch Fugenlüftung [m³/h]:".ljust(75),result["ResH2O"]["Vdot_Inf"])
        #print("Wahrscheinlichkeit dass Fugenlüftung alleine nicht ausreicht:".ljust(75),"%.1f"%(result["ResH2O"]["Frac_Inf_insuff_abs"]*100),"%") #wenn kein Vdot_add (nur Experteneingabe) dann gleich wie MouldRisk_abs
        print("Wahrscheinlichkeit dass Fugenlüftung nicht ausreicht:".ljust(75),"%.1f"%(result["ResH2O"]["MouldRisk_abs"]*100),"%")
        print("Erforderliche zusätzliche Luftmenge damit Wahrscheinlichkeit<1% [m³/h]:".ljust(75),result["ResH2O"]["Vdot_acc_abs"])
        print("dafür erforderlicher zusätzlicher freier Querschnitt [cm²]:".ljust(75),result["ResH2O"]["ELA_acc_abs"])

    import matplotlib.pyplot as plt

    plt.figure()
    plt.bar(result["t_avgC_realC0"]["frequency"]["x"], result["t_avgC_realC0"]["frequency"]["y"][0], width=60)
    plt.savefig("ResCO2_frequency.png")

    plt.figure()
    for i in range(0,len(quantiles)):
        plt.plot(result["t_avgC_realC0"]["timeseries"]["x"], result["t_avgC_realC0"]["timeseries"]["y"][i])
    plt.savefig("ResCO2_timeseries.png")

    for i in ["abs", "pre"]:
        plt.figure()
        plt.bar(result["ResH2O"]["plot"][i]["x"], result["ResH2O"]["plot"][i]["y"][0],width=0.01)
        plt.ylabel(f"Häufigkeit (n={size})")
        plt.xlabel("aw Wert [-]")
        plt.savefig(f"ResH2O_aw_{i}.png")

    for i,xlabel in zip(["Vdot", "LWR"],["Mittlerer Luftvolumenstrom [1/h]","Mittlere Luftwechselrate [1/h]"]):
        plt.figure()
        for l,j in zip(("Inf+Fen","Inf","Erf"),list(range(0,3))):
            plt.plot(result["ResH2O"]["plot"][i]["x"], result["ResH2O"]["plot"][i]["y"][j], marker=".", label=l)
        plt.legend()
        plt.ylabel(f"Häufigkeit (n={size})")
        plt.xlabel(xlabel)
        plt.savefig(f"ResH2O_Airflows_{i}.png")
