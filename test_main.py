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
total_iters = 1 #5000
num_dev_configs  = 1 #100
CBA_is_dev    = True
MTJs_is_dev   = True
parallel_flag = True
batch_size = 4 #FIXME
prob = "Max Sat"
cb_array  = RRAM_types.HfHfO2
scale = 1e14
iter_per_temp = 1  # 3 works well
Jsot_steps    = 10  # 150 works well -- jared
# ====================

def main():
    # sweeping parameters
    g_dev_sig   = [0.0]
    g_cyc_sig   = [0.0]
    mag_dev_sig = [0.0]

    #  constants, named list 
    c = {"total_iters":total_iters, "num_devs": num_dev_configs,
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
            r_str = (str(Gdd)+str(Gcc)+str(Mdd))
            if(repeat_run(r_str)): continue
            else:run_strings.add(r_str)
            p = {"g_dev_sig": Gdd, "g_cyc_sig":Gcc,"mag_dev_sig":Mdd,"scale":scale}
            param_path = h.get_param_path(out_path,p)
            sim_setup  = h.get_simulation_setup(p,c)
            h.write_setup(sim_setup,param_path)
            sim_wrapper(p,c,param_path)

    Gdd = 0.0
    Mdd = 0.0
    for Gcc in g_cyc_sig:
            r_str = (str(Gdd)+str(Gcc)+str(Mdd))
            if(repeat_run(r_str)): continue
            else:run_strings.add(r_str)
            p = {"g_dev_sig": Gdd, "g_cyc_sig":Gcc,"mag_dev_sig":Mdd,"scale":scale}
            param_path = h.get_param_path(out_path,p)
            sim_setup  = h.get_simulation_setup(p,c)
            h.write_setup(sim_setup,param_path)
            sim_wrapper(p,c,param_path)

    Gcc = 0.0
    Mdd = 0.0
    for Gdd in g_dev_sig:
            r_str = (str(Gdd)+str(Gcc)+str(Mdd))
            if(repeat_run(r_str)): continue
            else:run_strings.add(r_str)
            p = {"g_dev_sig": Gdd, "g_cyc_sig":Gcc,"mag_dev_sig":Mdd,"scale":scale}
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
    Neurons = SetMTJs(p["mag_dev_sig"])
    for dev_i in range(num_dev_configs):
        if CBA_is_dev:
            Edges = SetCBA(p["g_dev_sig"],c["prob"],c["cb_array"])
        if MTJs_is_dev:
            Neurons = SetMTJs(p["mag_dev_sig"])
        if parallel_flag:
            sols,all_sols,all_e = run_in_batch(SA,p,c,Edges,Neurons)
        else:
            sols,all_sols,all_e = run_serial(SA,p,c,Edges,Neurons)
        total_energy_usage = 0
        for mtj in Neurons:
            total_energy_usage += mtj.energy_usage
        average_energy_usage_per_device = total_energy_usage / len(Neurons)
        success_rate_list.append(h.get_success_rate(all_sols,c["prob"]))
        #NOTE: debug: print(f"--- success rate {dev_i}: {success_rate}% ---")
        h.write_data(all_e,all_sols,parent_path,dev_i)
        h.write_energy_usage(average_energy_usage_per_device, parent_path,dev_i)
    std_dev = np.std(success_rate_list)
    mean = np.average(success_rate_list)
    #==================================

    f = open( Path( parent_path / "device_iterations.txt" ), 'w' )
    w_str = (f"Success rates are across {total_iters} iterations of SA.\n"
             f"In this sim ==============================\n"
             f"MTJ varied across these rates: {MTJs_is_dev}\n"
             f"CBA varied across these rates': {CBA_is_dev}\n"
             f"Mean: {mean}\n"
             f"Std. dev: {std_dev}\n"
             f"High: {np.max(success_rate_list)}\n"
             f"Low: {np.min(success_rate_list)}\n===== rates per device ======\n"
            )
    for dev_i in range(num_dev_configs):
        w_str += f"Device config {dev_i}: {success_rate_list[dev_i]}\n"
    f.write(w_str)
    f.close()
    return 0

if __name__ == "__main__":
    main()
