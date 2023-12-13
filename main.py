import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

import RRAM_types
import helper_funcs as h
from SA_funcs  import SA,SetMTJs,SetCBA
from parallelism import run_in_batch,run_serial
from tqdm import tqdm
import time
import os

#REFERENCES: [1] Random Bitstream Generation using Voltage
#-Controlled Magnetic Anisotropy and Spin Orbit Torque Magnetic Tunnel Junctions 

# Global ==================
total_iters = 1000
num_devs    = 10
CBA_is_dev    = False
MTJs_is_dev   = False
parallel_flag = True
batch_size = 32
prob = "Max Sat"
cb_array  = RRAM_types.HfHfO2
iter_per_temp = 3  # 3 works well
Jsot_steps    = 150  # 150 works well -- jared
# ====================

def main():
    # sweeping parameters
    g_dev_sig   = [0.0,0.05,0.1,0.15,0.2,0.25,0.3,0.4,0.5]
    g_cyc_sig   = [0.0,0.05,0.1,0.15,0.2,0.25,0.3,0.4,0.5]
    mag_dev_sig = [0.0,0.05,0.1]
    scale = [1.25e14]

    #  constants, named list 
    c = {"total_iters":total_iters, "num_devs": num_devs,
         "cb_array":cb_array,"iter_per_temp":iter_per_temp,
         "Jsot_steps":Jsot_steps,"prob":prob,"batch_size": batch_size}
    out_path = h.get_out_path(c)
    run_strings = set()
    repeat_run = lambda r: False if(r not in run_strings) else( True )

    # ========================== sweep ==================================
    total_start_time = time.time()


    Gdd = 0.0
    Gcc = 0.0
    for Mdd in mag_dev_sig:
        for s in scale:
            r_str = (str(Gdd)+str(Gcc)+str(Mdd)+str(s))
            if(repeat_run(r_str)): continue
            else:run_strings.add(r_str)
            p = {"g_dev_sig": Gdd, "g_cyc_sig":Gcc,"mag_dev_sig":Mdd,"scale":s}
            param_path = h.get_param_path(out_path,p)
            sim_setup  = h.get_simulation_setup(p,c)
            h.write_setup(sim_setup,param_path)
            sim_wrapper(p,c,param_path)

    Gdd = 0.0
    Mdd = 0.0
    for Gcc in g_cyc_sig:
        for s in scale:
            r_str = (str(Gdd)+str(Gcc)+str(Mdd)+str(s))
            if(repeat_run(r_str)): continue
            else:run_strings.add(r_str)
            p = {"g_dev_sig": Gdd, "g_cyc_sig":Gcc,"mag_dev_sig":Mdd,"scale":s}
            param_path = h.get_param_path(out_path,p)
            sim_setup  = h.get_simulation_setup(p,c)
            h.write_setup(sim_setup,param_path)
            sim_wrapper(p,c,param_path)

    Gcc = 0.0
    Mdd = 0.0
    for Gdd in g_dev_sig:
        for s in scale:
            r_str = (str(Gdd)+str(Gcc)+str(Mdd)+str(s))
            if(repeat_run(r_str)): continue
            else:run_strings.add(r_str)
            p = {"g_dev_sig": Gdd, "g_cyc_sig":Gcc,"mag_dev_sig":Mdd,"scale":s}
            param_path = h.get_param_path(out_path,p)
            sim_setup  = h.get_simulation_setup(p,c)
            h.write_setup(sim_setup,param_path)
            sim_wrapper(p,c,param_path)
    Gcc = 0.2
    Mdd = 0.05
    for Gdd in g_dev_sig:
        for s in scale:
            r_str = (str(Gdd)+str(Gcc)+str(Mdd)+str(s))
            if(repeat_run(r_str)): continue
            else:run_strings.add(r_str)
            p = {"g_dev_sig": Gdd, "g_cyc_sig":Gcc,"mag_dev_sig":Mdd,"scale":s}
            param_path = h.get_param_path(out_path,p)
            sim_setup  = h.get_simulation_setup(p,c)
            h.write_setup(sim_setup,param_path)
            sim_wrapper(p,c,param_path)
    Gdd = 0.2
    Mdd = 0.05
    for Gcc in g_cyc_sig:
        for s in scale:
            r_str = (str(Gdd)+str(Gcc)+str(Mdd)+str(s))
            if(repeat_run(r_str)): continue
            else:run_strings.add(r_str)
            p = {"g_dev_sig": Gdd, "g_cyc_sig":Gcc,"mag_dev_sig":Mdd,"scale":s}
            param_path = h.get_param_path(out_path,p)
            sim_setup  = h.get_simulation_setup(p,c)
            h.write_setup(sim_setup,param_path)
            sim_wrapper(p,c,param_path)

    Gcc = 0.2
    Gdd = 0.2
    Mdd = 0.05
    scale = [1e14,1.1e14,1.2e14,1.3e14,1.4e14,1.5e14]
    for s in scale:
        r_str = (str(Gdd)+str(Gcc)+str(Mdd)+str(s))
        if(repeat_run(r_str)): continue
        else:run_strings.add(r_str)
        p = {"g_dev_sig": Gdd, "g_cyc_sig":Gcc,"mag_dev_sig":Mdd,"scale":s}
        param_path = h.get_param_path(out_path,p)
        sim_setup  = h.get_simulation_setup(p,c)
        h.write_setup(sim_setup,param_path)
        sim_wrapper(p,c,param_path)

    # ===============================================================================

    print("--- total program time: %s seconds ---" % (time.time() - total_start_time))
    # ===============================================================================
    # //////////////////////////////////////////////////////////////////////////////


### dives into a parallelism script which will spawn SA processes with all 
### the necessary parameters
def sim_wrapper(p,c,parent_path):
    #NOTE: debug: print(f"--- running {num_devs} device samples... ---")
    success_rate_list = []
    ### redundant iff. CBA and MTJ are both device
    Edges = SetCBA(p["g_dev_sig"],c["prob"],c["cb_array"])
    devs = SetMTJs(p["mag_dev_sig"])
    for dev_i in range(num_devs):
        if CBA_is_dev:
            Edges = SetCBA(p["g_dev_sig"],c["prob"],c["cb_array"])
        if MTJs_is_dev:
            devs = SetMTJs(p["mag_dev_sig"])
        if parallel_flag:
            sols,all_sols,all_e = run_in_batch(SA,p,c,Edges,devs)
        else:
            sols,all_sols,all_e = run_serial(SA,p,c,Edges,devs)
        success_rate_list.append(h.get_success_rate(all_sols,c["prob"]))
        #NOTE: debug: print(f"--- success rate {dev_i}: {success_rate}% ---")
        h.write_data(all_e,all_sols,parent_path,dev_i)
    std_dev = np.std(success_rate_list)
    mean = np.average(success_rate_list)
    #==================================

    f = open( Path( parent_path / "device_iterations.txt" ), 'w' )
    w_str = (f"success rates are across {num_devs} devices)\n"
             f"In this sim ==============================\n"
             f"MTJ varied across these rates: {MTJs_is_dev}\n"
             f"CBA varied across these rates': {CBA_is_dev}\n"
             f"Mean: {mean}\n"
             f"Std. dev: {std_dev}\n"
             f"High: {np.max(success_rate_list)}\n"
             f"Low: {np.min(success_rate_list)}\n===== rates per device ======\n"
            )
    for dev_i in range(num_devs):
        w_str += f"Dev {dev_i}: {success_rate_list[dev_i]}\n"
        for dev in devs:
            del dev
    f.write(w_str)
    f.close()
    return 0

if __name__ == "__main__":
    main()
