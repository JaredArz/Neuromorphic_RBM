import matplotlib.pyplot as plt

import random as rnd
import numpy as np
from pathlib import Path

import RRAM_types
import helper_funcs as h
from SA_funcs  import SA,SetMTJs,SetCBA
import parallelism as parallel

import time
from datetime import datetime
import os

#REFERENCES: [1] Random Bitstream Generation using Voltage
#-Controlled Magnetic Anisotropy and Spin Orbit Torque Magnetic Tunnel Junctions 

# Global ==================
total_iters = 1000
num_devs = 100
CBA_is_dev  = True
MTJs_is_dev = True
batch_size = 3*os.cpu_count()
prob = "Max Sat"
cb_array  = RRAM_types.HfHfO2
# sweeping manually
# scale = cb_array.Amps[prob]
# ====================

def main():
    # ========================= sweeping parameters ==============================
    iter_per_temp = [3]  # 3 works well
    Jsot_steps    = [150]  # 150 works well -- jared
    # None uses default values fpr g_dev and g_cyc
    #0.1, 0.25 works nicely for RRAM HfHfO2
    g_dev_sig   = [0.0,0.05,0.1,0.15,0.2,0.25,0.3,0.35,0.4,0.45,0.5]      
    g_cyc_sig   = [0.0,0.05,0.1,0.15,0.2,0.25,0.3,0.35,0.4,0.45,0.5]
    mag_dev_sig = [0.0,0.05,0.1]
    scale = [0.5e14,0.75e14,1e14,1.25e14,1.5e14]

    # ====================  constants, named list  =============================
    c = {"total_iters":total_iters, "num_devs": num_devs,
           "cb_array":cb_array,"prob":prob,"batch_size": batch_size}


    # ========================== sweep ==================================
    out_path = h.get_out_path(c)
    total_start_time = time.time()
    for Gdd in g_dev_sig:
        for Gcc in g_cyc_sig:
            for Mdd in mag_dev_sig:
                for i in iter_per_temp:
                    for Js in Jsot_steps:
                        for s in scale:
                            p = {"g_dev_sig": Gdd, "g_cyc_sig":Gcc,
                                    "mag_dev_sig":Mdd,"iter_per_temp":i,"Jsot_steps":Js,"scale":s}
                            param_path = h.get_param_path(out_path,p)
                            sim_setup  = h.get_simulation_setup(p,c)
                            print(sim_setup)
                            h.write_setup(sim_setup,param_path)
                            sim_wrapper(p,c,param_path)
    print("--- total program time: %s seconds ---" % (time.time() - total_start_time))
    # ===============================================================================
    # //////////////////////////////////////////////////////////////////////////////


# dives into a parallelism script which will spawn SA processes with all 
# the necessary parameters
def sim_wrapper(p,c,parent_path):
    print(f"--- running {num_devs} device samples... ---")
    success_rate_list=[]
    # redundant iff. CBA and MTJ are both device
    Edges = SetCBA(p["g_dev_sig"],c["prob"],c["cb_array"])
    devs = SetMTJs(p["mag_dev_sig"])
    for dev_i in range(num_devs):
        if CBA_is_dev:
            Edges = SetCBA(p["g_dev_sig"],c["prob"],c["cb_array"])
        if MTJs_is_dev:
            devs = SetMTJs(p["mag_dev_sig"])
        dev_path = h.get_dev_path(parent_path,dev_i)
        sols,all_sols,all_e = parallel.run_in_batch(SA,p,c,Edges,devs)
        success_rate = h.get_success_rate(all_sols,c["prob"])
        success_rate_list.append(success_rate)
        print(f"--- success rate {dev_i}: {success_rate}% ---")
        h.my_hist(sols, p,c, dev_path)
        h.write_data(all_e,all_sols,dev_path)
        h.write_success(success_rate,dev_path)
    std_dev = np.std(success_rate_list)
    mean = np.average(success_rate_list)
    dev_file = "device_iterations.txt"
    f = open( Path( parent_path / dev_file ), 'w' )
    w_str = (f"success rates are across {num_devs} devices)\n"
             f"In this sim ==============================\n"
             f"MTJ varied across these rates: {MTJs_is_dev}\n"
             f"CBA varied across these rates': {CBA_is_dev}\n"
             f"Mean: {mean}\n"
             f"Std. dev: {std_dev}\n"
             f"High: {np.max(success_rate_list)}\n"
             f"Low: {np.min(success_rate_list)}\n"
            )
    f.write(w_str)
    f.close()


if __name__ == "__main__":
    main()
