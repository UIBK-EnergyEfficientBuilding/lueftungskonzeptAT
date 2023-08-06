
import lueftungstool.lib.calc as ltool

def format_quantile(quantile):
    return f"<{quantile[0]}|{quantile[2]}|{quantile[4]}>"

def print_row(text,quantile):
    print(text.ljust(70,' '), str(quantile[2]).ljust(10), format_quantile(quantile))

if __name__ == "__main__":
    quantiles = [0.05, 0.25, 0.5, 0.75, 0.95]
    size = 1000
    raumart = "Schlafzimmer"

    result = ltool.calc(
        standort = "Wien",
        gebaeude_n50 = "Standard Neubau",
        gebaeudeart = "Mehrfamilienhaus",
        H_Rm = None,
        A_Rm = None,
        raumart = raumart,
        luefungsart = "Querlüftung",
        quantiles = quantiles,
        size = size
    )

    print("#Ergebnis CO2 Bewertung")
    print("Fensterlüftung praktikabel/zumutbar:".ljust(70), result["Fensterlueftung"])
    print_row("Weil errechnete Zeit zwischen erforderlichen Fensterlüften [min]:", result["t_gw_erreicht"]["Quantile"])
    print("Dies ist kürzer als die zumutbare Zeit zwischen Fensterlüften [min]:".ljust(70), result["t_zumutbar"])
    print_row("Informativ: Zeit zwischen erf. Fensterlüften bei idealem Lüften [min]:", result["t_gw_ueberschritten"]["Quantile"])
    print()
    print("#Detailergebnisse CO2 Bewertung")
    print_row("Zeit bis CO2-Stundenmittelwert=1000 ppm - realistisches Lüften [min]:", result["t_gw_erreicht"]["Quantile"])
    print_row("Zeit bis CO2-Momentanwert=1000 ppm - realistisches Lüften [min]:", result["t_gw_periodisch"]["Quantile"])
    print_row("Zeit bis CO2-Stundenmittelwert=1000 ppm - ideales Lüften [min]:", result["t_gw_ueberschritten"]["Quantile"])
    print_row("Zeit bis CO2-Momentanwert=1000 ppm - ideales Lüften [min]:", result["t_gw_ideal"]["Quantile"])
    print_row("CO2 Konzentration im stationären Fall (t→∞) [ppm]:", result["C_stat"])


    import matplotlib.pyplot as plt

    plt.figure()
    plt.bar(result["t_gw_erreicht"]["Häufigkeit"]["x"], result["t_gw_erreicht"]["Häufigkeit"]["y"][0], width=60)
    plt.savefig("Häufigkeit.png")

    plt.figure()
    for i in range(0,len(quantiles)):
        plt.plot(result["t_gw_erreicht"]["Mittelwert"]["x"], result["t_gw_erreicht"]["Mittelwert"]["y"][i])
    plt.savefig("Mittelwert.png")
