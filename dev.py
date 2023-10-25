
import lueftungstool.lib.calc2 as calc2

def format_quantile(quantile):
    return f"<{quantile[0]}|{quantile[2]}|{quantile[4]}>"

def print_row_mean(text,result_stats):
    print(text.ljust(75,' '), f'{result_stats["mean"]}+-{result_stats["error"]}'.ljust(20), format_quantile(result_stats["quantiles"]))

def print_row_median(text,result_stats):
    print(text.ljust(75,' '), f'{result_stats["median"]}'.ljust(20), format_quantile(result_stats["quantiles"]))

def print_row_integer(text,result_stats):
    print(text.ljust(75,' '), f'{result_stats["min"]} bis {result_stats["max"]}'.ljust(20), format_quantile(result_stats["quantiles"]))

if __name__ == "__main__":
    profile = False

    quantiles = [0.05, 0.25, 0.5, 0.75, 0.95]
    size = 1000
    signDig=2   #tbd add to a settings dict

    args = {
        "location": "Wien",
        "building_n50": "Standard Neubau",
        "building_type": "Mehrfamilienhaus",
    }

    if profile:
        import cProfile
        pr = cProfile.Profile()
        size *= 100

    if profile: pr.enable()
    result = calc2.calc(args,size)
    if profile: pr.disable()

    print("#Eingaben Gebäude/Raum")
    print("Standort:".ljust(75), result["inputs"]["location"])
    print("Gebäudeart:".ljust(75), result["inputs"]["building_type"])
    print_row_mean("Luftdichtigkeit n50-Wert (Gebäude) [1/h]:".ljust(75), result["inputs"]["building_n50"])
    print("Raumart (betrachteter Raum):".ljust(75), result["inputs"]["room_type"])
    print_row_mean("Fläche (betrachteter Raum) [m²]:".ljust(75), result["inputs"]["A_Rm"])
    print_row_mean("Höhe (betrachteter Raum) [m]:".ljust(75), result["inputs"]["H_Rm"])
    print_row_mean("Fläche öffenbare Fenster (betrachteter Raum) [m²]:".ljust(75), result["inputs"]["window_area"])
    print_row_integer("Fensterklasse nach EN12207 (betrachteter Raum)".ljust(75), result["inputs"]["window_class"])
    print("Lüftungsmöglichkeit (betrachteter Raum):".ljust(75), result["inputs"]["airing_type_room"])
    print_row_mean("Lüftungsdauer pro Lüftungsvorgang [min]:".ljust(75), result["inputs"]["airing_duration_room"])
    print_row_integer("Gelände-/Terrainklasse (Windeinfluss)".ljust(75), result["inputs"]["terrain_class"])
    print_row_integer("Abschirmung-/Shieldingklasse (Windeinfluss)".ljust(75), result["inputs"]["shielding_class"])
    print("Eingaben Personen für betrachteten Raum".ljust(75), "?")
    print_row_integer("Anzahl Erwachsene:".ljust(75), result["inputs"]["NrAdu"])
    print_row_mean("Aktivität Erwachsene [met]:".ljust(75), result["inputs"]["ActAdu"])
    print_row_integer("Anzahl Kinder:".ljust(75), result["inputs"]["NrKids"])
    print_row_mean("Aktivität Kinder [met]:".ljust(75), result["inputs"]["ActKid"])
    print_row_mean("Mittleres Alter der Kinder [a]".ljust(75), result["inputs"]["AgeKid"])

    print()
    print("#Ergebnis CO2 Bewertung")
    print("Fensterlüftung praktikabel/zumutbar:".ljust(75), result["ResCO2"]["airing_acceptable"])
    print_row_median("Weil errechnete Zeit zwischen erforderlichen Fensterlüften [min]:", result["ResCO2"]["t_avgC_realC0"])
    print("Dies ist kürzer als die zumutbare Zeit zwischen Fensterlüften [min]:".ljust(75), result["ResCO2"]["t_reasonable"])
    print_row_median("Informativ: Zeit zwischen erf. Fensterlüften bei idealem Lüften [min]:", result["ResCO2"]["t_avgC_idealC0"])
    print()
    print("#Detailergebnisse CO2 Bewertung")
    print_row_median("errechnete Luftmenge aufgrund natürlicher Lüftung [m³/h]:", result["ResCO2"]["Vdot"])
    print_row_median("errechneter natürlicher Luftwechsel [1/h]:", result["ResCO2"]["ACR"])
    print_row_median("Zeit bis CO2-Stundenmittelwert=1000 ppm - realistisches Lüften [min]:", result["ResCO2"]["t_avgC_realC0"])
    print_row_median("Zeit bis CO2-Momentanwert=1000 ppm - realistisches Lüften [min]:", result["ResCO2"]["t_instC_realC0"])
    print_row_median("Zeit bis CO2-Stundenmittelwert=1000 ppm - ideales Lüften [min]:", result["ResCO2"]["t_avgC_idealC0"])
    print_row_median("Zeit bis CO2-Momentanwert=1000 ppm - ideales Lüften [min]:", result["ResCO2"]["t_instC_idealC0"])
    print_row_median("CO2 Konzentration im stationären Fall (t→∞) [ppm]:", result["ResCO2"]["CO2_stat"])
    print()

    if "ResH2O" in result:
        print("#Eingaben für Schimmelrisiko Bewertung (nur für Wohnbau)")
        print("Berechnung durchführen:".ljust(75), "Ja")
        print("Wärmebrücken".ljust(75), result["inputs"]["thermalbridges"])
        print_row_mean("fRSI-Wert".ljust(75), result["inputs"]["fRSI"])
        print_row_mean("Feuchtelast [l/d]:".ljust(75), result["inputs"]["H2Osource_category"])
        print_row_mean("Feuchtequellstärke pro m² bei Anwesenheit [g/(hm²)]".ljust(75), result["inputs"]["H2Osource_area"])
        print_row_mean("Feuchtequellstärke pro Pers bei Anwesenheit [g/(hPers)]".ljust(75), result["inputs"]["H2Osource_pers"])
        print_row_mean("Feuchtequellstärke pro m² bei Abwesenheit [g/(hm²)]".ljust(75), result["inputs"]["H2Osource_area_abs"])
        print_row_mean("Fläche gesamte Wohneinheit [m²]:".ljust(75), result["inputs"]["area_home"])
        print_row_mean("Personenanzahl (gesamter Wohneinheit):".ljust(75), result["inputs"]["pers_home"])
        print("Lüftungsmöglichkeit (gesamte Wohneinheit):".ljust(75), result["inputs"]["airing_type_home"])
        print_row_mean("Lüftungsdauer gesamt, z.B. morgens und abends [min/Tag]:".ljust(75), result["inputs"]["airing_duration_home"])
        print_row_mean("Mittlere Raumtemperatur in gesamten Wohneinheit [°C]:".ljust(75), result["inputs"]["Ti_avg"])
        print_row_mean("Raumtemperatur im kühlsten Raum [°C]:".ljust(75), result["inputs"]["Ti_min"])
        print_row_mean("Minimale Raumtemperatur bei längerer Abwesenheit [°C]:".ljust(75), result["inputs"]["Ti_abs"])
        print()
        print("#Ergebnis Schimmelrisiko Bewertung (nur für Wohnbau)")
        print("Schimmelrisiko als Wahrscheinlichkeit".ljust(75),"%.1f"%(result["ResH2O"]["MouldRisk"]*100),"%")
        print("Erforderliche zusätzliche Luftmenge damit Wahrscheinlichkeit<1% [m³/h]:".ljust(75),"%.1f"%(result["ResH2O"]["Vdot_acc"]))
        print()
        print("#Anwesenheitsfall (inkl. aktives Lüften)")
        print_row_median("Erforderliche Luftmenge zur Feuchteabfuhr [m³/h]:".ljust(75),result["ResH2O"]["Vdot_req_pre"])
        print_row_median("Luftmenge durch Fugenlüftung [m³/h]:".ljust(75),result["ResH2O"]["Vdot_Inf"])
        print("Wahrscheinlichkeit dass Fugenlüftung alleine nicht ausreicht:".ljust(75),"%.1f"%(result["ResH2O"]["Frac_Inf_insuff_pre"]*100),"%")
        print_row_median("Luftmenge durch Fugenlüftung + Fensterlüftung [m³/h]:".ljust(75), result["ResH2O"]["Vdot_Tot"])
        print("Wahrscheinlichkeit dass Fugenlüftung und Fensterlüftung nicht ausreicht:".ljust(75),"%.1f"%(result["ResH2O"]["MouldRisk_pre"]*100),"%")
        print("Erforderliche zusätzliche Luftmenge damit Wahrscheinlichkeit <1% [m³/h]:".ljust(75),result["ResH2O"]["Vdot_acc_pre"])
        print("dafür erforderlicher zusätzlicher freier Querschnitt [cm²]:".ljust(75),result["ResH2O"]["ELA_acc_pre"])
        print()
        print("#Abwesenheitsfall")
        print_row_median("Erforderliche Luftmenge zur Feuchteabfuhr [m³/h]:".ljust(75),result["ResH2O"]["Vdot_req_abs"])
        print_row_median("Luftmenge durch Fugenlüftung [m³/h]:".ljust(75),result["ResH2O"]["Vdot_Inf"])
        #print("Wahrscheinlichkeit dass Fugenlüftung alleine nicht ausreicht:".ljust(75),"%.1f"%(result["ResH2O"]["Frac_Inf_insuff_abs"]*100),"%") #wenn kein Vdot_add (nur Experteneingabe) dann gleich wie MouldRisk_abs
        print("Wahrscheinlichkeit dass Fugenlüftung nicht ausreicht:".ljust(75),"%.1f"%(result["ResH2O"]["MouldRisk_abs"]*100),"%")
        print("Erforderliche zusätzliche Luftmenge damit Wahrscheinlichkeit<1% [m³/h]:".ljust(75),result["ResH2O"]["Vdot_acc_abs"])
        print("dafür erforderlicher zusätzlicher freier Querschnitt [cm²]:".ljust(75),result["ResH2O"]["ELA_acc_abs"])
        print()

    import matplotlib.pyplot as plt

    for i in ["t_avgC_realC0", "t_instC_realC0", "t_avgC_idealC0", "t_instC_idealC0"]:
        plt.figure()
        plt.bar(result["ResCO2"]["plot"][i]["frequency"]["x"], result["ResCO2"]["plot"][i]["frequency"]["y"][0], width=60)
        plt.grid(True)
        plt.savefig(f"ResCO2_frequency_{i}.png")

        plt.figure()
        for j,linestyle in zip(range(0,len(quantiles)),[":","--","-","--",":"]):
            plt.plot(result["ResCO2"]["plot"][i]["timeseries"]["x"], result["ResCO2"]["plot"][i]["timeseries"]["y"][j], linestyle=linestyle, color="gray")
        plt.ylim(0,3000)
        plt.grid(True)
        plt.savefig(f"ResCO2_timeseries_{i}.png")

    if "ResH2O" in result:
        for i in ["abs", "pre"]:
            plt.figure()
            plt.bar(result["ResH2O"]["plot"][i]["x"], result["ResH2O"]["plot"][i]["y"][0],width=0.01)
            plt.ylabel(f"Häufigkeit (n={size})")
            plt.xlabel("aw Wert [-]")
            plt.grid(True)
            plt.savefig(f"ResH2O_aw_{i}.png")

        for i,xlabel in zip(["Vdot", "ACR"],["Mittlerer Luftvolumenstrom [1/h]","Mittlere Luftwechselrate [1/h]"]):
            plt.figure()
            for l,j in zip(("Inf+Fen","Inf","Erf"),list(range(0,3))):
                plt.plot(result["ResH2O"]["plot"][i]["x"], result["ResH2O"]["plot"][i]["y"][j], marker=".", label=l)
            plt.legend()
            plt.ylabel(f"Häufigkeit (n={size})")
            plt.xlabel(xlabel)
            plt.grid(True)
            plt.savefig(f"ResH2O_Airflows_{i}.png")

    if profile:
        import pstats
        p = pstats.Stats(pr).strip_dirs()
        p.sort_stats(pstats.SortKey.CUMULATIVE).print_stats(15)
        p.sort_stats(pstats.SortKey.TIME).print_stats(15)
