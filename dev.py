
import lueftungstool.lib.calc as ltool

def format_quantile(quantile):
    return f"<{quantile[0]}|{quantile[2]}|{quantile[4]}>"

def print_row(text,quantile):
    print(text.ljust(75,' '), str(quantile[2]).ljust(10), format_quantile(quantile))

if __name__ == "__main__":
    quantiles = [0.05, 0.25, 0.5, 0.75, 0.95]
    size = 1000
    raumart = "Schlafzimmer"

    CO2_Emi = ltool.co2_emission(
        raumart = raumart,
        size = size
    )

    H_Rm, A_Rm = ltool.Raum(
        raumart = raumart,
        size = size
    )

    result = ltool.calc(
        location = "Wien",
        gebaeude_n50 = "Standard Neubau",
        gebaeudeart = "Mehrfamilienhaus",
        waermebruecken = "Standard Neubau",
        H_Rm = H_Rm,
        A_Rm = A_Rm,
        luefungsart = "Querlüftung",
        Shield = None,
        Terr = None,
        CO2_Emi = CO2_Emi,
        WNF = None,
        Feuchtelastkategorie = "Mittel",
        m_H2Od = None,
        m_H2Ok = None,
        m_H2Od0 = None,
        quantiles = quantiles,
        size = size
    )

    print("#Ergebnis CO2 Bewertung")
    print("Fensterlüftung praktikabel/zumutbar:".ljust(75), result["Fensterlueftung"])
    print_row("Weil errechnete Zeit zwischen erforderlichen Fensterlüften [min]:", result["t_gw_erreicht"]["Quantile"])
    print("Dies ist kürzer als die zumutbare Zeit zwischen Fensterlüften [min]:".ljust(75), result["t_zumutbar"])
    print_row("Informativ: Zeit zwischen erf. Fensterlüften bei idealem Lüften [min]:", result["t_gw_ueberschritten"]["Quantile"])
    print()
    print("#Detailergebnisse CO2 Bewertung")
    print_row("errechnete Luftmenge aufgrund natürlicher Lüftung [m³/h]:", result["Vdot"])
    print_row("errechneter natürlicher Luftwechsel [1/h]:", result["LWR"])
    print_row("Zeit bis CO2-Stundenmittelwert=1000 ppm - realistisches Lüften [min]:", result["t_gw_erreicht"]["Quantile"])
    print_row("Zeit bis CO2-Momentanwert=1000 ppm - realistisches Lüften [min]:", result["t_gw_periodisch"]["Quantile"])
    print_row("Zeit bis CO2-Stundenmittelwert=1000 ppm - ideales Lüften [min]:", result["t_gw_ueberschritten"]["Quantile"])
    print_row("Zeit bis CO2-Momentanwert=1000 ppm - ideales Lüften [min]:", result["t_gw_ideal"]["Quantile"])
    print_row("CO2 Konzentration im stationären Fall (t→∞) [ppm]:", result["C_stat"])

    if "MouldRisk" in result:
        print()
        print("#Ergebnis Schimmelrisiko Bewertung (nur für Wohnbau)")
        print("Schimmelrisiko als Wahrscheinlichkeit".ljust(75),"%.1f"%(result["MouldRisk"]["MouldRisk"]*100),"%")
        print()
        print("#Anwesenheitsfall (inkl. aktives Lüften)")
        print("Erforderliche Luftmenge zur Feuchteabfuhr [m³/h]:".ljust(75),"?")
        print_row("Luftmenge durch Fugenlüftung [m³/h]:".ljust(75),result["MouldRisk"]["Vdot_Inf"])
        print("Wahrscheinlichkeit dass Fugenlüftung alleine nicht ausreicht:".ljust(75),"?")
        print_row("Luftmenge durch Fugenlüftung + Fensterlüftung [m³/h]:".ljust(75), result["MouldRisk"]["Vdot_Tot"])
        print("Wahrscheinlichkeit dass Fugenlüftung und Fensterlüftung nicht ausreicht:".ljust(75),"%.1f"%(result["MouldRisk"]["MouldRisk_pre"]*100),"%")
        print("Erforderliche zusätzliche Luftmenge damit Wahrscheinlichkeit <1% [m³/h]:".ljust(75),"?")
        print("dafür erforderlicher zusätzlicher freier Querschnitt [cm²]:".ljust(75),"?")
        print()
        print("#Abwesenheitsfall")
        print("Erforderliche Luftmenge zur Feuchteabfuhr [m³/h]:".ljust(75),"?")
        print_row("Luftmenge durch Fugenlüftung [m³/h]:".ljust(75),result["MouldRisk"]["Vdot_Inf"])
        print("Wahrscheinlichkeit dass Fugenlüftung nicht ausreicht:".ljust(75),"%.1f"%(result["MouldRisk"]["MouldRisk_abs"]*100),"%")
        print("Erforderliche zusätzliche Luftmenge damit Wahrscheinlichkeit<1% [m³/h]:".ljust(75),"?")
        print("dafür erforderlicher zusätzlicher freier Querschnitt [cm²]:".ljust(75),"?")

    import matplotlib.pyplot as plt

    plt.figure()
    plt.bar(result["t_gw_erreicht"]["Häufigkeit"]["x"], result["t_gw_erreicht"]["Häufigkeit"]["y"][0], width=60)
    plt.savefig("Häufigkeit.png")

    plt.figure()
    for i in range(0,len(quantiles)):
        plt.plot(result["t_gw_erreicht"]["Mittelwert"]["x"], result["t_gw_erreicht"]["Mittelwert"]["y"][i])
    plt.savefig("Mittelwert.png")
