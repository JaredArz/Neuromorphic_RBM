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
    total_iters = c["total_iters"]
    prob = c["prob"]
    cb_array = c["cb_array"]
    #create dir and write path
    date_fine = datetime.now().strftime("%H:%M:%S")
    date_session = datetime.now().strftime("%m-%d")
    session_dir = Path(f"./outputs/RBM_sims_{date_session}")
    out_dir = (f"{prob}_{cb_array.device_type}_{total_iters}_{date_fine}").replace(" ","")
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
    g_dev_sig,g_cyc_sig,mag_dev_sig,scale = unpack_params(p)
    param_dir = f'p_Gdd{g_dev_sig}_Gcc{g_cyc_sig}_Ndd{mag_dev_sig}_s{scale:.2e}'
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

def write_energy_usage(energy,out_dir,dev_i) -> None:
    data_w_file = f'nrg_and_sols_d{dev_i}.npy.gz'
    f = gzip.GzipFile(Path( out_dir / data_w_file ) , "a")
    np.save(f,energy)
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
    g_dev_sig,g_cyc_sig,mag_dev_sig,scale = unpack_params(p)
    total_iters,dev_iter,iter_per_temp,Jsot_steps,batch_size,prob,cb_array = unpack_consts(c)
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
        sol_one = 51
        sol_two = 12
    elif prob == "Ind Set":
        sol_one = 37
        sol_two = 37
    for s in final_sols:
        if (s == sol_one) or (s == sol_two):
            correct += 1
    return (correct/len(final_sols))*100


def unpack_params(p):
    g_dev_sig     = p["g_dev_sig"]
    g_cyc_sig     = p["g_cyc_sig"]
    mag_dev_sig   = p["mag_dev_sig"]
    scale         = p["scale"]
    return g_dev_sig,g_cyc_sig,mag_dev_sig,scale

def unpack_consts(c):
    total_iters = c["total_iters"]
    num_devs    = c["num_devs"]
    batch_size  = c["batch_size"]
    prob        = c["prob"]
    cb_array    = c["cb_array"]
    Jsot_steps  = c["Jsot_steps"]
    iter_per_temp = c["iter_per_temp"]
    return total_iters,num_devs,iter_per_temp,Jsot_steps,batch_size,prob,cb_array
