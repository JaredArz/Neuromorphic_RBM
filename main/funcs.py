# =================================================================
# July 7,2023
#
# Various helper functions used in the simulated annealing scripts
# ==================================================================
import sys
sys.path.append('./fortran_source')
import single_sample as ss

import matplotlib.pyplot as plt
import itertools as it
import numpy as np

from datetime import datetime
from pathlib import Path
import time
import os

def handle_w_path(prob):
    #create dir and write path
    date = datetime.now().strftime("%m-%d_%H:%M:%S")
    out_dir = Path("./outputs")
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
    w_file = ("RBM_Sim_" + prob + '_' + date + '_Hist.png').replace(" ","") 
    
    #pathlib POSIX path creation
    w_path = Path( out_dir / w_file)
    return(w_path,date)

def my_hist(prob,num_iter,sols,scale,iter_per_temp,Jsot_steps,mag_dev_sig,g_dev_sig,g_cyc_sig) -> str:
    # =================================
    # ===== Graphing of Histogram =====
    # =================================
    w_path,date = handle_w_path(prob)
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
    plt.annotate(f"Amplification: {scale:1.0e}",xy = (275,280), xycoords='figure points')
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
        plt.savefig(w_path,format='png',dpi=1200)
    elif user_input == 'n' or user_input == 'N':
        pass
    else:
        print("invalid input... saving figure just in case")
        plt.savefig(w_path,format='png',dpi=1200)
    return date

def convertToDec(args) -> int:
    #can take optionally a list or a numpy 2D matrix
    sum = 0
    if type(args) == np.ndarray:
        for k in range(0, len(args[0])):
            sum += (args[0][k] * (2**(len(args[0])-k-1)))
    else:
        for k in range(0, len(args)):
            sum += (args[k] * (2**(len(args)-k-1)))
    return sum


#   NOTE: Fortran in here
def sample_neurons(devs,neurons_dot_W_scaled,J_step,dump_flag) -> list:
    bits = []
    #   initial setting will be initialized here
    if type(neurons_dot_W_scaled) is int:
        neurons_dot_W_scaled = np.zeros(6)
    for h in range(6): 
        #   NOTE: python-fortran interface
        #   f90 call looks like import.module_name.function(args)
        _, out, theta_end, phi_end = ss.single_sample.pulse_then_relax(neurons_dot_W_scaled[h],J_step,\
                                                      devs[h].theta,devs[h].phi,                     \
                                                      devs[h].Ki,devs[h].TMR,devs[h].Rp,dump_flag)
        devs[h].theta = theta_end
        devs[h].phi = phi_end
        bits.append( out )
    return bits

get_Log10R      = lambda G: np.log10(1.0/G)
sample_noise    = lambda logR,std_dev: np.random.normal(logR,std_dev)
to_G            = lambda noisy_logR: 1.0/pow(10,noisy_logR)
abs_arr         = lambda e: abs(e)
lmap = lambda func, *iterable: list(map(func, *iterable))
# The resistance is experimentally observed to be approximately log-normal (both cycle-to-cycle and device-to-device)
# From Intrinsic Switching Variability in HfO2 RRAM, A.Fantini
def inject_add_cyc_noise(G_in,cbarr,std_dev=None) -> np.ndarray:
    if std_dev == 0:
        return G_in
    #//////////////////
    if std_dev is None:
        stdd = cbarr.base_cyc_stdd
    else:
        stdd = std_dev
    #//////////////////
    if cbarr.device_type == "Memristor":
        sign_matrix   = np.reshape([-1 if element < 0 else 1 for element in G_in.flatten()],(6,6))
        abs_G_in      = lmap(abs_arr,G_in)
        R_log         = lmap(get_Log10R, abs_G_in)
        R_log_w_noise = lmap(sample_noise, R_log, it.repeat(stdd))
        abs_G_out     = lmap(to_G, R_log_w_noise)
        G_out         = np.multiply(abs_G_out, sign_matrix)
        return G_out
    elif cbarr.device_type == "MTJ":
        diff = (1.0/cbarr.LRS) - (1.0/cbarr.HRS) 
        scaled_stdd = diff*stdd
        noise = np.random.normal(0,scaled_stdd,6)
        return G_in + noise

def inject_add_dev_var(G_in,cbarr,std_dev=None) -> np.ndarray:
    if std_dev == 0:
        return G_in
    #//////////////////
    if std_dev == None:
        stdd = cbarr.base_dev_stdd
    else:
        stdd = std_dev
    #//////////////////
    if cbarr.device_type == "Memristor":
        sign_matrix  = np.reshape([-1 if element < 0 else 1 for element in G_in.flatten()],(6,6))
        abs_G_in      = lmap(abs_arr,G_in)
        R_log         = lmap(get_Log10R, abs_G_in)
        R_log_w_noise = lmap(sample_noise, R_log, it.repeat(stdd))
        abs_G_out     = lmap(to_G, R_log_w_noise)
        G_out         = np.multiply(abs_G_out, sign_matrix)
        return G_out
    elif cbarr.device_type == "MTJ":
        diff = (1.0/cbarr.LRS) - (1.0/cbarr.HRS) 
        scaled_stdd = diff*stdd
        noise = np.random.normal(0,scaled_stdd,6)
        return G_in + noise

