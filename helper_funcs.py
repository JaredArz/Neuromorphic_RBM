# =================================================================
# July 7,2023
#
# Various helper functions used in the simulated annealing scripts
# ==================================================================

import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path
import numpy as np
import gzip
import time
import os
import math

def get_out_path(c):
    total_iters,_,_,prob,cb_array = unpack_consts(c)
    #create dir and write path
    date_fine = datetime.now().strftime("%H:%M:%S")
    date_session = datetime.now().strftime("%m-%d")
    session_dir = Path(f"./outputs/RBM_sims_{date_session}")
    out_dir = (f"{prob}_{total_iters}_{cb_array.device_type}_{date_fine}").replace(" ","")
    out_path =  session_dir / out_dir   
    if not os.path.isdir("./outputs"):
        os.mkdir("./outputs")
    if not os.path.isdir(session_dir):
        os.mkdir(session_dir)
    if not os.path.isdir(out_path):
        os.mkdir(out_path)
    return out_path

def get_dev_path(param_path,dev_i):
    dev_dir = (f"Dev_{dev_i}")
    dev_path =  param_path / Path(dev_dir)
    if not os.path.isdir(dev_path):
        os.mkdir(dev_path)
    return dev_path

def get_param_path(out_path,p):
    g_dev_sig,g_cyc_sig,mag_dev_sig,iter_per_temp,Jsot_steps,scale = unpack_params(p)
    param_dir = f'p_Js{Jsot_steps}_i{iter_per_temp}_Gdd{g_dev_sig}_Gcc{g_cyc_sig}_Ndd{mag_dev_sig}_s{scale:.2e}'
    param_path =  out_path / Path(param_dir)
    if not os.path.isdir(param_path):
        os.mkdir(param_path)
    return param_path

def write_data(all_e,all_sols,out_dir,dev_i) -> None:
    data_w_file = f'nrg_and_sols_d{dev_i}.npy.gz' 
    f = gzip.GzipFile(Path( out_dir / data_w_file ) , "a")
    np.save(f,all_e)
    np.save(f,all_sols)
    f.close()

def write_setup(sim_setup,out_dir) -> None:
    metadata_w_file = 'RBM_metadata.txt'
    f = open( Path( out_dir / metadata_w_file)  ,'a')
    f.write(sim_setup)
    f.close()

def write_success(success_rate,out_dir):
    metadata_w_file = 'RBM_success_rates.txt'
    f = open( Path( out_dir / metadata_w_file)  ,'a')
    f.write(f"success rate: {success_rate}%\n" )
    f.write(f"#####\n" )
    f.close()

def get_simulation_setup(p,c) -> None:
    g_dev_sig,g_cyc_sig,mag_dev_sig,iter_per_temp,Jsot_steps,scale = unpack_params(p)
    total_iters,dev_iter,batch_size,prob,cb_array = unpack_consts(c)
    single_sample_time = 0.0002182
    est_run_time = (total_iters * single_sample_time * iter_per_temp * Jsot_steps)/((batch_size)/3 * 60)
    if est_run_time < 1:
        run_time_str = "< 1 minute"
    else:
        run_time_str = f"{math.ceil(est_run_time)} minutes"
        
    sim_setup = (
        f"========================================\n"
        f"--- starting parallel {prob} SA sim with:\n"
        f"{cb_array.device_type} CB array\n"
        f"Amplif. factor {scale:.2e}\n"
        f"{total_iters} total iterations\n"
        f"{iter_per_temp} iteration(s) per temp\n"
        f"{Jsot_steps} temp steps\n"
        f"MTJ device deviation = {mag_dev_sig}\n"
        f"G device deviation   = {g_dev_sig}\n"
        f"G cycle deviation    = {g_cyc_sig}\n"
        f"--- estimated run time:  {run_time_str}\n"
        f"===============================\n"
        )
    return sim_setup

def get_success_rate(all_sols, prob) -> float:
    final_sols = [ elem[-1] for elem in all_sols ]
    correct = 0
    if prob == "Max Sat":
        sol_one = 28
        sol_two = 21
    elif prob == "Max Cut":
        pass
        #FIXME
    for s in final_sols:
        if (s == sol_one) or (s == sol_two):
            correct += 1
    return (correct/len(final_sols))*100

def my_hist(sols,p,c,out_path) -> str:
    # =================================
    # ===== Graphing of Histogram =====
    # =================================
    #g_dev_sig,g_cyc_sig,mag_dev_sig,iter_per_temp,Jsot_steps,scale = unpack_params(p)
    #total_iters,dev_iter,batch_size,prob,cb_array = unpack_consts(c)
    total_iters = c["total_iters"]
    prob = c["prob"]

    plot_w_file = (f'Hist_RBM_{prob}.svg').replace(" ","") 
    w_path = Path( out_path / plot_w_file)

    bar_col = 'cadetblue' # burnt orange lol
    sol_highlight = "red"
    #=====================================================================
    #   define x ticks and solution-tick highlighting unique for each problem
    if prob == "Max Cut":
        ticks = [0,5,11,12,13,20,25,30,35,40,45,50,51,52,60,68]
        labels = [0,5,' ',12,' ',20,25,30,35,40,45,' ',51,' ',60,68]
        plt.xticks(ticks=ticks,labels=labels)
        plt.gca().get_xticklabels()[3].set_color(sol_highlight)
        plt.gca().get_xticklabels()[-4].set_color(sol_highlight)
    elif prob == "Max Sat":
        ticks = [0,5,10,20,21,22,27,28,29,35,40,45,50,55,60,68]
        labels = [0,5,10,' ',21,' ',' ',28,' ',35,40,45,50,55,60,68]
        plt.xticks(ticks=ticks,labels=labels)
        plt.gca().get_xticklabels()[4].set_color(sol_highlight)
        plt.gca().get_xticklabels()[7].set_color(sol_highlight)
    #======================================================================
    plt.yticks(range(0, total_iters, int(total_iters/10)))
    plt.hist(sols,bins=64,facecolor=bar_col)
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.title(prob + ' Solution Frequency Over ' + str(total_iters) + ' Iterations')
    #plt.annotate(f"Amplification: {(scale):.2e}",xy = (275,280), xycoords='figure points')
    #plt.annotate(f"Num steps {Jsot_steps}   ", xy = (275,270),xycoords='figure points')
    #plt.annotate(f"Iters per step {iter_per_temp}", xy = (275,260),xycoords='figure points')
    #plt.annotate(f"MTJ dev-to-dev  σ {mag_dev_sig}", xy = (275,250),xycoords='figure points')
    #plt.annotate(f"CBA dev-to-dev σ {g_dev_sig}", xy = (275,240),xycoords='figure points')
    #plt.annotate(f"CBA cyc-to-cyc  σ {g_cyc_sig}", xy = (275,230),xycoords='figure points')
    #plt.show()
    #print("Save figure? y/n")
    #user_input = input()
    user_input='y'
    if user_input == 'y' or user_input == 'Y':
        plt.savefig(w_path,format='svg')
    elif user_input == 'n' or user_input == 'N':
        pass
    else:
        print("invalid input... saving figure just in case")
        plt.savefig(w_path,format='svg')

def unpack_params(p):
    g_dev_sig     = p["g_dev_sig"]
    g_cyc_sig     = p["g_cyc_sig"]
    mag_dev_sig   = p["mag_dev_sig"]
    iter_per_temp = p["iter_per_temp"]
    Jsot_steps    = p["Jsot_steps"]
    scale         = p["scale"]
    g_dev_out = (cb_array.base_dev_stdd if(g_dev_sig is None) else(g_dev_sig))
    g_cyc_out = (cb_array.base_cyc_stdd if(g_cyc_sig is None) else(g_cyc_sig))
    return g_dev_out,g_cyc_out,mag_dev_sig,iter_per_temp,Jsot_steps,scale

def unpack_consts(c):
    total_iters = c["total_iters"]
    num_devs    = c["num_devs"]
    batch_size  = c["batch_size"]
    prob        = c["prob"]
    cb_array    = c["cb_array"]
    return total_iters,num_devs,batch_size,prob,cb_array
