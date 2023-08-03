# =================================================================
# July 7,2023
#
# Various helper functions used in the simulated annealing scripts
# ==================================================================

import matplotlib.pyplot as plt

from datetime import datetime
from pathlib import Path
import time
import os
import math
import numpy as np

def get_out_path(prob):
    #create dir and write path
    date_fine = datetime.now().strftime("%m-%d_%H:%M:%S")
    date_session = datetime.now().strftime("%m-%d")
    session_dir = Path(f"./outputs/RBM_sims_{date_session}")
    out_dir = (prob + "_run_" + f"{date_fine}").replace(" ","")
    out_path =  session_dir / out_dir   
    if not os.path.isdir(session_dir):
        os.mkdir(session_dir)
    if not os.path.isdir(out_path):
        os.mkdir(out_path)
    return(out_path)

def write_data(all_e,all_sols,out_dir) -> None:
    data_w_file = 'RBM_energy_and_sols.npy' 
    f = open( Path( out_dir / data_w_file ) , "ab")
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


def get_simulation_setup(batch_size, a) -> None:
    total_iters,prob,g_dev_sig,g_cyc_sig,mag_dev_sig,\
            cb_array,scale,iter_per_temp,Jsot_steps = unpack(a)
    single_sample_time = 0.0002182
    est_run_time = (total_iters * single_sample_time * iter_per_temp * Jsot_steps)/((batch_size)/2.5 * 60)
    if est_run_time < 1:
        run_time_str = "< 1 minute"
    else:
        run_time_str = f"{math.ceil(est_run_time)} minutes"
        
    sim_setup = (f"========================================\n\
--- starting parallel {prob} SA sim with:\n\
{cb_array.device_type} CB array\n\
Amplif. factor {scale:3.0e}\n\
{total_iters} total iterations\n\
{iter_per_temp} iteration(s) per temp\n\
{Jsot_steps} temp steps\n\
MTJ device deviation = {mag_dev_sig}\n\
G device deviation   = {g_dev_sig}\n\
G cycle deviation    = {g_cyc_sig}\n\
--- estimated run time:  {run_time_str}\n\
===============================\n")
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

def my_hist(sols,num_iter,prob,g_dev_sig,g_cyc_sig,mag_dev_sig,cb_array,scale,iter_per_temp,Jsot_steps,out_path, dev_i=None) -> str:
    # =================================
    # ===== Graphing of Histogram =====
    # =================================
    if dev_i is None:
        plot_w_file = (f'Hist_{prob}_Gdd{g_dev_sig}_Gcc{g_cyc_sig}_Ndd{mag_dev_sig}_Js{Jsot_steps}_i{iter_per_temp}.svg').replace(" ","") 
    else:
        plot_w_file = (f'Hist_dev{dev_i}_{prob}_Gdd{g_dev_sig}_Gcc{g_cyc_sig}_Ndd{mag_dev_sig}_Js{Jsot_steps}_i{iter_per_temp}.svg').replace(" ","") 
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
    plt.yticks(range(0, num_iter, int(num_iter/10)))
    plt.hist(sols,bins=64,facecolor=bar_col)
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.title(prob + ' Solution Frequency Over ' + str(num_iter) + ' Iterations')
    plt.annotate(f"Amplification: {(scale):3.0e}",xy = (275,280), xycoords='figure points')
    plt.annotate(f"Num steps {Jsot_steps}", xy = (275,270),xycoords='figure points')
    plt.annotate(f"Iters per step {iter_per_temp}", xy = (275,260),xycoords='figure points')
    plt.annotate(f"MTJ dev-to-dev  σ {mag_dev_sig}", xy = (275,250),xycoords='figure points')
    plt.annotate(f"CBA dev-to-dev σ {g_dev_sig}", xy = (275,240),xycoords='figure points')
    plt.annotate(f"CBA cyc-to-cyc  σ {g_cyc_sig}", xy = (275,230),xycoords='figure points')
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

def unpack(a):
    total_iters = a["total_iters"]
    prob        = a["prob"]
    g_dev_sig   = a["g_dev_sig"]
    g_cyc_sig   = a["g_cyc_sig"]
    mag_dev_sig = a["mag_dev_sig"]
    cb_array    = a["cb_array"]
    iter_per_temp = a["iter_per_temp"]
    Jsot_steps  = a["Jsot_steps"]
    g_dev_out = (cb_array.base_dev_stdd if(g_dev_sig is None) else(g_dev_sig))
    g_cyc_out = (cb_array.base_cyc_stdd if(g_cyc_sig is None) else(g_cyc_sig))
    if prob == "Max Sat":
        scale  = cb_array.Max_Sat_amp
    elif prob == "Max Cut":
        scale  = cb_array.Max_Cut_amp 
    return total_iters,prob,g_dev_out,g_cyc_out,mag_dev_sig,cb_array,scale,iter_per_temp,Jsot_steps
