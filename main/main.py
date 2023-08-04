import matplotlib.pyplot as plt
import random as rnd
import numpy as np
from pathlib import Path

import RRAM_types
import helper_funcs as h
from SA_funcs  import SA,SetDevice
import parallelism as parallel

import time
from datetime import datetime
import os

#REFERENCES: [1] Random Bitstream Generation using Voltage
#-Controlled Magnetic Anisotropy and Spin Orbit Torque Magnetic Tunnel Junctions 

# Global ==================
total_iters = 10
dev_iter = 1
batch_size = os.cpu_count() 
prob = "Max Sat"
cb_array  = RRAM_types.HfHfO2
# == ==================

def main():
    # ========================= sweeping parameters ==============================
    iter_per_temp = [1]  # 3 works well
    Jsot_steps    = [10]  # 150 works well -- jared
    # None uses default values fpr g_dev and g_cyc
    #0.1, 0.25 works nicely for RRAM HfHfO2
    g_dev_sig   = [0]       # device to device variation
    g_cyc_sig   = [0]       # cycle to cycle variation 
    mag_dev_sig = [1]


    # =============================================================================
    # total_iters will define how many simulations to run with the same device.
    # these flags can be set to force single or multiple device operation
    single_flag = False
    multi_flag = False


    # ====================  constants, named list  =============================
    c = {"total_iters":total_iters, "dev_iter": dev_iter,
            "cb_array":cb_array,"scale": h.get_scale(prob,cb_array), "prob":prob,"batch_size": batch_size}



    # ==================== set single or multi device operation ======================
    # ==================== i.e. nest the entire simulation across devices or not
    dev_var_bool = bool(g_dev_sig != 0 or mag_dev_sig != 0)
    if ( not dev_var_bool and not multi_flag ) or (single_flag and not multi_flag):
        sim_wrapper = sim_single_dev
    elif (dev_var_bool and not single_flag ) or (multi_flag and not single_flag):
        sim_wrapper = sim_multi_dev
    else:
        print("flag error")
        exit()

    # ========================== sweep ==================================
    out_path = h.get_out_path(c)
    total_start_time = time.time()
    for Gdd in g_dev_sig:
        for Gcc in g_cyc_sig:
            for Mdd in mag_dev_sig:
                for i in iter_per_temp:
                    for Js in Jsot_steps:
                        p = {"g_dev_sig": Gdd, "g_cyc_sig":Gcc,
                             "mag_dev_sig":Mdd,"iter_per_temp":i,"Jsot_steps":Js}
                        param_path = h.get_param_path(out_path,p)
                        sim_setup  = h.get_simulation_setup(p,c)
                        print(sim_setup)
                        h.write_setup(sim_setup,param_path)
                        sim_wrapper(p,c,param_path)
    print("--- total program time: %s seconds ---" % (time.time() - total_start_time))
    # ===============================================================================
    # //////////////////////////////////////////////////////////////////////////////


def sim_multi_dev(p,c,parent_path):
    print(f"--- running {dev_iter} device samples... ---")
    print("--- this will take a while... ---")
    success_rate_list = []
    d = SetDevice(p["g_dev_sig"],p["g_cyc_sig"],p["mag_dev_sig"],c["prob"],c["cb_array"])
    for dev_i in range(dev_iter):
        dev_path = h.get_dev_path(parent_path,dev_i)
        sols,all_sols,all_e = parallel.run_in_batch(SA,p,c,d)
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
    f.write(f"success rates are across one device simulated {dev_iter} times (either MTJ or CB array dev-to-dev variation enabled)\n")
    f.write(f"mean: {mean}\n")
    f.write(f"std dev. {std_dev}\n")
    f.close()

def sim_single_dev_(p,c,parent_path):
    d = SetDevice(p["g_dev_sig"],p["g_cyc_sig"],p["mag_dev_sig"],c["prob"],c["cb_array"])
    sols,all_sols,all_e = parallel.run_in_batch(SA,p,c,d)
    success_rate = h.get_success_rate(all_sols,c["prob"])
    print(f"--- success rate: {success_rate}% ---")
    h.my_hist(sols,p,c,parent_path)
    h.write_data(all_e,all_sols,parent_path)
    h.write_success(success_rate,parent_path)


if __name__ == "__main__":
    main()
