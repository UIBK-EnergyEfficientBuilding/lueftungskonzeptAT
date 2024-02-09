import numpy as np
import helper as helper
import matplotlib.pyplot as plt

def Infiltration(Ti_avg,T_a,fs,fw,n50,Vol,v_10m):
    # xxx temp find better position for def
    n = 0.66
    roh = 1.247

    ELA = (n50/3600*Vol*(4/50)**n)/np.sqrt(2*4/roh)
    Vdot = ELA*3600*np.sqrt(fs**2*np.abs(Ti_avg-T_a)+fw**2*v_10m**2)
    return Vdot, ELA

def airing(ACH_airing,t_airing,CO2_emi,volume,c_amb,c_start,size):
    c_stat_airing = (ACH_airing*volume*c_amb/1e6+CO2_emi/1000)/(ACH_airing*volume)*1e6
    c_end = c_inst(c_start,c_stat_airing,ACH_airing,t_airing)
    
    #xxx tbd if needed: long if else only for making sure np.max works in any case depending if variables come as array or single value (maybe not even relevant or more elegant solution possible)
    if isinstance(c_end,np.ndarray) and isinstance(c_stat_airing,np.ndarray):  
        if c_end.shape[0] == c_stat_airing.shape[0]:
            c0_rightdim=c_end
            c_stat_airing_rightdim=c_stat_airing
        else:
            print("array dim doesn't fit :check")       #xxx warning /error message are ignored in frontend? can stay or??
    elif isinstance(c_end,np.ndarray) and ~isinstance(c_stat_airing,np.ndarray):
        c0_rightdim=c_end
        c_stat_airing_rightdim=np.ones(c_end.shape[0]).reshape(-1,1)*c_stat_airing
    elif ~isinstance(c_end,np.ndarray) and isinstance(c_stat_airing,np.ndarray):
        c0_rightdim=np.ones(c_stat_airing.shape[0]).reshape(-1,1)*c_end
        c_stat_airing_rightdim=c_stat_airing
    else:
        c_end = np.max([c_end,c_stat_airing])
        return c_end
        
    #c0 = np.max([c_inst(c_start,c_stat_airing,ACH_airing,t_airing),c_stat_airing],axis=1) # max function to make sure that c0 >= c_stat even for strange inputs (had it in xls for some reason)
    c_end = np.max(np.hstack((c0_rightdim,c_stat_airing_rightdim)),axis=1,keepdims=True)
    return c_end

def c_stationary(c_amb,Vdot,CO2_emi):
    return c_amb+CO2_emi/Vdot*1e3

def c_inst(c0,c_stat,ACH,t):
    return (c0-c_stat)*np.exp(-ACH*t)+c_stat

def c_avg(c0,c_stat,ACH,t):
    return (c0-c_stat)/ACH/t*(1-np.exp(-ACH*t))+c_stat

def c_avg_online(c0_avg,c_i,t_i):
    return ()

def t_until_th_anaSol(c_threshold,c0,c_stat,ACH,t_obs):
    dt = 0.1 # xxx arbitrary to make time until threshold is reached larger than observation time 
    log_arg = (c_threshold-c_stat)/(c0-c_stat)
    t_until_threshold =  np.where(log_arg > 0, -np.ma.log(np.ma.array(log_arg, mask=(log_arg<=0)))/ACH, t_obs+dt) # mask array needed with where?
    #t_until_threshold2 =  np.where(log_arg > 0, -np.log(log_arg)/ACH, t_obs+dt)
    return t_until_threshold

def t_until_th_numSol(c_threshold,c_t,t_i):
    dt = 0.1 # xxx arbitrary to make time until threshold is reached larger than observation time 
       
    n_t_until_th = np.argmin(c_t<=c_threshold,axis=1,keepdims=True)      #this method should be more robst, even when first c_t value is > threshold 
    cases_th_not_reached=np.invert(np.any(c_t>c_threshold,axis=1,keepdims=True))
    t_until_th = t_i[0,n_t_until_th]
    t_until_th[cases_th_not_reached] = np.max(t_i,axis=1) + dt
    
    return t_until_th #, n_t_until_th 	# xxx todo: calculate also for cases where c_th isn't reached within t_obs

def c_airing_cycle_prep(t_start, t_duration,t_i):      #xxx change names "air": is for both cycles
    t_air_end=t_start+t_duration
    t_i_array=np.tile(t_i,(t_start.shape[0],1))
    idx_air = (t_i>=t_start) & (t_i<=t_air_end)     #could be moved out of loop for better performance
    idx_air_st=np.minimum(np.searchsorted(t_i.flatten(),t_start.flatten()),t_i.shape[1]-1)      #xxx minimum, because searchsorted will output index max +1, e.g. 1920; exact comp could lead to problems
    t_i_air=t_i_array-t_i_array[list(range(idx_air_st.shape[0])),idx_air_st].reshape(-1,1)
    t_i_air[t_i_air<0]=0        # too avoid very large numbers for t<0
    return t_i_air, idx_air, idx_air_st

def c_airing_cycle2(c_instC_idealC0,ACH,t_instC_idealC0,c_stat,c_amb,ACH_airing,t_airing,c_stat_air,t_i):
    t_start_air=t_instC_idealC0
    c_instC_idealC0_air = c_instC_idealC0
    jj=1
    while np.any(t_start_air<t_obs):

        # airing period**********************
        t_i_air, idx_air, idx_air_st=c_airing_cycle_prep(t_start_air,t_airing,t_i)
        c_start_air=c_instC_idealC0_air[list(range(idx_air_st.shape[0])),idx_air_st-1].reshape(-1,1)
        #c_air = c_inst(c_instC_idealC0[t_i==t_air_start].reshape(-1,1),c_stat_air,ACH_airing,t_i_air)
        c_air = c_inst(c_start_air,c_stat_air,ACH_airing,t_i_air)
        c_instC_idealC0_air[idx_air]=c_air[idx_air]

        # no-airing period*******************
        t_start_noAir=t_start_air + t_airing
        t_i_noAir, idx_noAir, idx_noAir_st=c_airing_cycle_prep(t_start_noAir,t_instC_idealC0,t_i)
        #c_start_noAir=c_instC_idealC0_air[list(range(idx_noAir_st.shape[0])),idx_noAir_st-1].reshape(-1,1)
        c_start_noAir=np.tile(c_amb,t_start_noAir.shape)
        c_noAir = c_inst(c_start_noAir,c_stat,ACH,t_i_noAir)
        c_instC_idealC0_air[idx_noAir]=c_noAir[idx_noAir]

        # next cycle
        t_start_air=t_start_noAir + t_instC_idealC0
        jj +=1
        if jj>100:
            print(f"Warning: stopped calculation after {jj} airing events")       #xxx message for frontend?
            break
    return c_instC_idealC0_air


def c_airing_cycle(c_i,ACH,t_betw_air,c_stat,c_amb,ACH_airing,t_airing,c_stat_air,t_i,calc_method,air_method):
    t_start_air=t_betw_air
    c_i_air = np.copy(c_i)      #regular "=" doesn't copy nested arrays, alternatively use copy.deepcopy 
    jj=1
    while np.any(t_start_air<t_obs):

        # airing period**********************
        t_i_air, idx_air, idx_air_st=c_airing_cycle_prep(t_start_air,t_airing,t_i)
        c_start_air=c_i_air[list(range(idx_air_st.shape[0])),idx_air_st-1].reshape(-1,1)
        c_air = c_inst(c_start_air,c_stat_air,ACH_airing,t_i_air)
        c_i_air[idx_air]=c_air[idx_air]

        # no-airing period*******************
        t_start_noAir=t_start_air + t_airing
        t_i_noAir, idx_noAir, idx_noAir_st=c_airing_cycle_prep(t_start_noAir,t_betw_air,t_i)
        match air_method:
            case "idealC":
                c_start_noAir=np.tile(c_amb,t_start_noAir.shape)
            case "realC":
                c_start_noAir=c_i_air[list(range(idx_noAir_st.shape[0])),idx_noAir_st-1].reshape(-1,1)
            case _:
                print("Warning: airing method not clear: use ideal airing")
                c_start_noAir=np.tile(c_amb,t_start_noAir.shape)

        c_noAir = c_inst(c_start_noAir,c_stat,ACH,t_i_noAir)
        c_i_air[idx_noAir]=c_noAir[idx_noAir]

        # next cycle
        t_start_air=t_start_noAir + t_betw_air
        jj +=1
        if jj>100:
            print(f"Warning: stopped calculation after {jj} airing events")       #xxx message for frontend?
            break
    
    if calc_method=="avgC":
        return helper.movavg(c_i_air)
    return c_i_air

def co2_calculation(
        n50, T_a, v_10m, fs, fw, t_obs, volume, ACH_airing, t_airing, Ti_avg, CO2_emi, c_threshold, quantiles, size = 1000
    ):
    
    # allow for user entry
    Vdot_const = 0  # xxx interface to be implemented
    #define ambient CO2 conc xxx check for better location
    c_amb = 450

    # determine infiltration air flow
    Vdot, ELA = Infiltration(Ti_avg,T_a,fs,fw,n50,volume,v_10m)
    Vdot += Vdot_const
    ACH = Vdot/volume
    Vdot_airing = ACH_airing*volume

    c_stat = c_stationary(c_amb,Vdot,CO2_emi)
    c_stat_air = c_stationary(c_amb,Vdot_airing,CO2_emi)
      
    n_max=192*10   #tbd xxx define differently
    n_i = np.arange(1, n_max+1)
    #t_i = t_obs*n_i/n_max
    t_i = np.linspace(0,t_obs,n_max+1)[1:].reshape(1,-1)

    #eval_qua=0.5    #xxx tbd better defintion
    #c_instC_idealC0_med=np.quantile(c_instC_idealC0,eval_qua,axis=0)
    
    ## instant concentration and ideal airing 11111111111111111111111111111
    t_instC_idealC0_a=t_until_th_anaSol(c_threshold,c_amb,c_stat,ACH,t_obs)

    c_instC_idealC0 = c_inst(c_amb,c_stat,ACH,t_i)
    c_instC_idealC0_qua, c_instC_idealC0_qidx = helper.quantile_pos(c_instC_idealC0, quantiles)
    t_instC_idealC0=t_until_th_numSol(c_threshold,c_instC_idealC0,t_i)

    c_instC_idealC0_air=c_airing_cycle(c_instC_idealC0,ACH,t_instC_idealC0,c_stat,c_amb,ACH_airing,t_airing,c_stat_air,t_i,"instC","idealC")[c_instC_idealC0_qidx,:]

    ## average concentration and ideal airing 222222222222222222222222222
    c_avgC_idealC0 = c_avg(c_amb,c_stat,ACH,t_i)
    c_avgC_idealC0_qua, c_avgC_idealC0_qidx = helper.quantile_pos(c_avgC_idealC0, quantiles)
    t_avgC_idealC0=t_until_th_numSol(c_threshold,c_avgC_idealC0,t_i)

    c_avgC_idealC0_air=c_airing_cycle(c_instC_idealC0,ACH,t_avgC_idealC0,c_stat,c_amb,ACH_airing,t_airing,c_stat_air,t_i,"avgC","idealC")[c_avgC_idealC0_qidx,:]

    ## instant concentration and real airing 3333333333333333333333333333
    c0_instC = airing(ACH_airing,t_airing,CO2_emi,volume,c_amb,c_threshold,size)
    c_instC_realC0 = c_inst(c0_instC,c_stat,ACH,t_i)
    c_instC_realC0_qua, c_instC_realC0_qidx = helper.quantile_pos(c_instC_realC0, quantiles)
    t_instC_realC0=t_until_th_numSol(c_threshold,c_instC_realC0,t_i)
    t_instC_realC0_a=t_until_th_anaSol(c_threshold,c0_instC,c_stat,ACH,t_obs)

    c_instC_realC0_air=c_airing_cycle(c_instC_realC0,ACH,t_instC_realC0,c_stat,c_amb,ACH_airing,t_airing,c_stat_air,t_i,"instC","realC")[c_instC_realC0_qidx,:]

    ## average concentration and real airing 4444444444444444444444444444
    c0_avgC = c0_instC                  #initial guess: use c0 based on c_inst, i.e. c0 calculated when c_inst hits c_threshold  
    t_avgC_realC0 = t_avgC_idealC0       #initial guess: use time until threshold from ideal airing
    ii=0
    ii_max=100          # xxx tbd move to diff loc 
    c0_convCrit_Lim=5   # xxx tbd move to diff loc
    while ii < ii_max:
        c_instC_avgC4thresh = c_inst(c0_avgC,c_stat,ACH,t_avgC_realC0)
        c0_avgC_new = airing(ACH_airing,t_airing,CO2_emi,volume,c_amb,c_instC_avgC4thresh,size)
        c_avgC_realC0 = c_avg(c0_avgC_new,c_stat,ACH,t_i)
        t_avgC_realC0=t_until_th_numSol(c_threshold,c_avgC_realC0,t_i)
        
        c0_convCrit=abs(c0_avgC_new-c0_avgC) < c0_convCrit_Lim
        if all(c0_convCrit):
            print(f"Convergence achieved after {ii} iterations.")       #xxx message for frontend?
            break

        c0_avgC=c0_avgC_new
        ii +=1
    else:
        print(f"Maximum number of iterations ({ii}) reached without convergence.")      #xxx message for frontend?

    c_avgC_realC0_qua, c_avgC_realC0_qidx = helper.quantile_pos(c_avgC_realC0, quantiles)
    c_avgC_realC0_air=c_airing_cycle(c_instC_realC0,ACH,t_avgC_realC0,c_stat,c_amb,ACH_airing,t_airing,c_stat_air,t_i,"avgC","realC")[c_avgC_realC0_qidx,:]

    # definition which evaluation and which quantile is used for evaluation if ventilation is sufficient
    # average concentration (because Austria's guideline value is defined this way) and realstic airing is applied
    # the median (50th quantile) is used a decision criteria, i.e. up to 50% of the cases might not meet the IAQ guidelinne with reasonable airing intervall
    t_qua4eval=0.5      # xxx parameter, tbd define somewhere else
    t_until_th_eval = np.quantile(t_avgC_realC0,t_qua4eval)*60
    t_reasonable = t_obs*60
    airing_acceptable = t_until_th_eval >= t_reasonable #>= used instead of > in xls version
    
    result = {
        "airing_acceptable": airing_acceptable,
        "t_reasonable": t_reasonable,
        "t_avgC_realC0": helper.result_stats(t_avgC_realC0*60),
        "t_instC_realC0": helper.result_stats(t_instC_realC0*60),
        "t_avgC_idealC0": helper.result_stats(t_avgC_idealC0*60),
        "t_instC_idealC0": helper.result_stats(t_instC_idealC0*60),
        "ELA": helper.result_stats(ELA),
        "Vdot": helper.result_stats(Vdot),
        "ACR": helper.result_stats(ACH),
        "CO2_stat": helper.result_stats(c_stat),
        
        "t_instC_idealC0_a": helper.result_stats(t_instC_idealC0_a*60),
        "t_instC_realC0_a": helper.result_stats(t_instC_realC0_a*60),
        "c0_instC": helper.result_stats(c0_instC),
        "c0_avgC": helper.result_stats(c0_avgC),
        "c_instC_avgC4thresh": helper.result_stats(c_instC_avgC4thresh),
        "plot": {
            "c_instC_idealC0_qua": c_instC_idealC0_qua,
            "c_avgC_idealC0_qua": c_avgC_idealC0_qua,
            "c_instC_realC0_qua": c_instC_realC0_qua,
            "c_avgC_realC0_qua": c_avgC_realC0_qua,
            
            "c_instC_idealC0_air": c_instC_idealC0_air,
            "c_avgC_idealC0_air": c_avgC_idealC0_air,
            "c_instC_realC0_air": c_instC_realC0_air,
            "c_avgC_realC0_air": c_avgC_realC0_air,

            "t_i": t_i,
        },
    }

    return result

def print_row_median(text,result_stats):
    print(text.ljust(75,' '), f'{result_stats["median"]}'.ljust(20), format_quantile(result_stats["quantiles"]))

def format_quantile(quantile):
    return f"<{quantile[0]}|{quantile[2]}|{quantile[4]}>"
    

if __name__ == "__main__":
    size=1000
    n50_room=np.linspace(3,5,size).reshape(-1,1)
    #n50_room=3.5
    T_a = 0
    v_10m = 3
    fs = 0.08035
    fw = 0.12434
    t_obs = 8
    volume = 45
    #ACH_airing =20 
    ACH_airing=np.linspace(10,20,size).reshape(-1,1)
    #t_airing_min = 10
    t_airing_min=np.linspace(3,7,size).reshape(-1,1)
    Ti_avg = 20
    CO2_emi =21.6
    c_threshold =1000
    quantiles = [0.05,0.25,0.5,0.75,0.95]
    
    result=co2_calculation(n50_room, T_a, v_10m, fs, fw, t_obs, volume, ACH_airing, t_airing_min/60, Ti_avg, CO2_emi, c_threshold, quantiles, size)

    print()
    print("#Ergebnis CO2 Bewertung")
    print("Fensterlüftung praktikabel/zumutbar:".ljust(75), result["airing_acceptable"])
    print()
    print("#Detailergebnisse CO2 Bewertung")
    print_row_median("effective leakage area [m²]:", result["ELA"])
    print_row_median("errechnete Luftmenge aufgrund natürlicher Lüftung [m³/h]:", result["Vdot"])
    print_row_median("errechneter natürlicher Luftwechsel [1/h]:", result["ACR"])
    print()
    print_row_median("Analytisch: Zeit bis CO2-Momentanwert=1000 ppm - reales Lüften [min]:", result["t_instC_realC0_a"])
    print_row_median("Analytisch: Zeit bis CO2-Momentanwert=1000 ppm - ideales Lüften [min]:", result["t_instC_idealC0_a"])
    print()
    print_row_median("Zeit bis CO2-Momentanwert=1000 ppm - reales Lüften [min]:", result["t_instC_realC0"])
    print_row_median("Zeit bis CO2-Momentanwert=1000 ppm - ideales Lüften [min]:", result["t_instC_idealC0"])
    print_row_median("Zeit bis CO2-Mittelwert=1000 ppm - reales Lüften [min]:", result["t_avgC_realC0"])
    print_row_median("Zeit bis CO2-Mittelwert=1000 ppm - ideales Lüften [min]:", result["t_avgC_idealC0"])
    print()
    print_row_median("CO2 Konzentration im stationären Fall (t→∞) [ppm]:", result["CO2_stat"])
    
    print_row_median("CO2 nach realem Lüften - Limit als Momentanwert [ppm]:", result["c0_instC"])
    print_row_median("CO2 nach realem Lüften - Limit als Mittelwert [ppm]:", result["c0_avgC"])
    print_row_median("CO2 Konzentration (Momentanwert) bei Erreichen des Mittelwert-Limits [ppm]:", result["c_instC_avgC4thresh"])
    #print(result["plot"]["c_instC_idealC0_qua"][0:1,:])
    print()

    for i in ["c_instC_idealC0","c_avgC_idealC0","c_instC_realC0","c_avgC_realC0"]:
    #for i in ["c_instC_idealC0","c_avgC_idealC0"]:
        # plt.figure()
        # plt.bar(result["ResCO2"]["plot"][i]["frequency"]["x"], result["ResCO2"]["plot"][i]["frequency"]["y"][0], width=60)
        # plt.grid(True)
        # plt.savefig(f"ResCO2_frequency_{i}.png")

        plt.figure(i)
        for j,linestyle in zip(range(0,len(quantiles)),[":","--","-","--",":"]):
        #for j,linestyle in zip(range(0,10),[":","--","-","--",":",":","--","-","--",":"]):
            # x=result["plot"]["t_i"].T
            # y=result["plot"][i].T
            # plt.plot(x, y, linestyle=("-","--"),color="green")
            plt.plot(result["plot"]["t_i"].T, result["plot"][i+"_qua"][j,:].T, linestyle=linestyle, color="gray")
            
        
        # x = result["ResCO2"]["plot"][i]["airing"]["x"]
        # y = result["ResCO2"]["plot"][i]["airing"]["y"][0]
        plt.plot(result["plot"]["t_i"].T, result["plot"][i+"_air"][0:10,:].T, color="green")

        #plt.ylim(0,3000)
        plt.grid(True)
        #plt.savefig(f"ResCO2_timeseries_{i}.png")
        plt.show()
        print()
