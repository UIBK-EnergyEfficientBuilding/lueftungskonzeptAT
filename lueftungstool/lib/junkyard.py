    jj=1
    tt=(t_air_end<t_obs)
    tt2=np.any(t_air_end<t_obs)
    while np.any(t_air_end<t_obs):
        jj +=1
        t_air_start=t_air_start*jj
        t_air_end=t_air_end*jj
        tidx_when_airing = tidx_when_airing | (t_i>=t_air_start) & (t_i<=t_air_end)
        t_i_mat=t_i[0,tidx_when_airing[0,:]]
        if jj>1000:
            print(f"Warning: stopped calculation after {jj} airing events")       #xxx message for frontend?
            break


###
        # instant concentration and ideal airing
    t_instC_idealC0_a=t_until_th_anaSol(c_threshold,c_amb,c_stat,ACH,t_obs)

    c_instC_idealC0 = c_inst(c_amb,c_stat,ACH,t_i)
    c_instC_idealC0_qua = np.quantile(c_instC_idealC0, quantiles, axis=0)
    t_instC_idealC0=t_until_th_numSol(c_threshold,c_instC_idealC0,t_i)

    eval_qua=0.5    #xxx tbd better defintion
    c_instC_idealC0_med=np.quantile(c_instC_idealC0,eval_qua,axis=0)
    #t_i_mat=np.broadcast_to(t_i,c_instC_idealC0.shape)
    t_i_mat=np.tile(t_i,(c_instC_idealC0.shape[0],1))
    n_max_air=25
    t_i_air = np.linspace(0,t_airing.flatten(),n_max_air+1,axis=1)[:,1:]
    t_air_start=t_instC_idealC0
    t_air_end=t_instC_idealC0+t_airing
    #idx_air = (t_i>=t_air_start) & (t_i<=t_air_end)
    #c_air = c_inst(c_instC_idealC0[:,t_air_start],c_amb,Vdot_airing,t_i[0,idx_air])
    c_instC_idealC0_air = c_instC_idealC0
    jj=1
    tt=(t_air_end<t_obs)
    tt2=np.any(t_air_end<t_obs)
    while np.any(t_air_end<t_obs):
        t_air_end=t_air_start+t_airing

        idx_air = (t_i>=t_air_start) & (t_i<=t_air_end)
        idx_air_st = (t_i==t_air_start)
        idx_nonair=np.invert(idx_air)
        test4=t_i_mat[idx_air]
        test5=t_i_mat
        #c_instC_idealC0_air[idx_nonair]=0
        #test5[idx_nonair]=0
        #test6=np.argmax(test5!=0,axis=1,keepdims=True)
        #test6a=test5[:,test6.flatten()]
        test6=test5[idx_air_st]
        test6a=test6[:,np.newaxis]
        test7a=test5-test6[:,np.newaxis]
        test7=test5-test5[idx_air_st].reshape(-1,1)
        test7[test7<0]=0

        c_air = c_inst(c_instC_idealC0[t_i==t_air_start].reshape(-1,1),c_stat_air,ACH_airing,test7)
        test=t_i<=t_air_start
        test2=c_instC_idealC0[t_i<=t_air_start]
        test3=c_instC_idealC0_air[idx_air]
        c_instC_idealC0_air[idx_air]=c_air[idx_air]
        t_air_start=t_air_end
        jj +=1
        if jj>1:
            print(f"Warning: stopped calculation after {jj} airing events")       #xxx message for frontend?
            break

    tt=(t_air_end<t_obs)
    tt2=np.any(t_air_end<t_obs)

