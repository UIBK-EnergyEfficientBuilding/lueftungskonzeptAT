from lueftungstool.lib.calc import calc

quantiles=[0.05, 0.5, 0.95]

result = calc(
    standort="Wien",
    gebaeude_n50="Standard Neubau",
    gebaeudeart="Mehrfamilienhaus",
    H_Rm=None,
    A_Rm=None, 
    raumart="Schlafzimmer",
    luefungsart="Querlüftung",
    quantiles=quantiles
)


import matplotlib.pyplot as plt

plt.figure()
plt.bar(result["t_gw_erreicht"]["Häufigkeit"]["x"], result["t_gw_erreicht"]["Häufigkeit"]["y"][0], width=60)
plt.savefig("Häufigkeit.png")

plt.figure()
for i in range(0,len(quantiles)):
    print(i)
    plt.plot(result["t_gw_erreicht"]["Mittelwert"]["x"], result["t_gw_erreicht"]["Mittelwert"]["y"][i])
plt.savefig("Mittelwert.png")

print(result)
