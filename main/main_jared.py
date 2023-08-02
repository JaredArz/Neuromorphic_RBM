import matplotlib.pyplot as plt
import random as rnd
import numpy as np
import math

from   mtj_types import SHE_MTJ_rng
import RRAM_types
import funcs

import multiprocessing as mp
from tqdm import tqdm
from re import S
import time
from datetime import datetime
import os

#REFERENCES: [1] Random Bitstream Generation using Voltage
#-Controlled Magnetic Anisotropy and Spin Orbit Torque Magnetic Tunnel Junctions 

# limit current according to [1]
def SA(sol_queue,sol_hist_queue,e_hist_queue,get_run_data_flag):
    # ========================== Problem definition =========================
    prob = "Max Sat"

    if prob == "Max Sat":
        Edges = np.array([[-5, -1, -1, 10, -1, -1], 
                          [-1, -7, -2, -2, 10, -1],
                          [-1, -2, -7, -2, -1, 10], 
                          [10, -2, -2, -7, -1, -1],
                          [-1, 10, -1, -1, -5, -1], 
                          [-1, -1, 10, -1, -1, -5]])
    elif prob == "Max Cut":
        #Example Graph:
        #  0  1
        #  |/\|
        #  2  3     
        #  |/\|
        #  4  5
        #Solution is 110011/001100 = 51/12
        Edges = np.array([[10,10,-1,-1,10,10], 
                          [10,10,-1,-1,10,10], 
                          [-1,-1,10,10,-1,-1], 
                          [-1,-1,10,10,-1,-1], 
                          [10,10,-1,-1,10,10], 
                          [10,10,-1,-1,10,10]])
    else:
        # dummy Edges for call with get_run_data_flag
        Edges = np.zeros((6,6))
    # =======================================================================
    
   
   
    # ========================== device init  ===============================
    cb_array = RRAM_types.HfHfO2

    mag_dev_sig = 1
    #None uses default values

    #works nicely for RRAM
    g_dev_sig  = 0.1       # device to device variation
    g_cyc_sig  = 0.25       # cycle to cycle variation 

    if prob == "Max Sat":
        scale  = cb_array.Max_Sat_amp
    elif prob == "Max Cut":
        scale  = cb_array.Max_Cut_amp 
    gmin = 1.0/cb_array.HRS
    gmax = 1.0/cb_array.LRS
    
    #   map abstract weights to conductances
    Edges = (( (Edges-np.min(Edges)/(np.max(Edges)-np.min(Edges)))*(gmax-gmin))+gmin )
    Edges_base = funcs.inject_add_dev_var(Edges,cb_array,g_dev_sig)

    thetas    = np.full(6,np.pi/2)
    phis      = np.ones_like(thetas)*np.random.uniform(0,2*np.pi,size=np.shape(thetas))
    devs = [ SHE_MTJ_rng(thetas[i], phis[i], mag_dev_sig) for i in range(6)]
    # ===============================================================================


    # ================ annealing schedule ====================
    total_iters = 1000   #Number of Simulations to Run
    iter_per_temp = 3
    # === values from [1] ===
    Jsot_max    = 5e11      #
    Jsot_min    = 1e11      #
    # =======================
    Jsot_steps = 100
    Jsot_delta = ( Jsot_max - Jsot_min ) / Jsot_steps 
    limit_current = lambda J: -6e9 if(J < -6e9) else( 6e9 if(J > 6e9) else J)
    # ========================================================
    #   simple way to get run data for parallel process while keeping all variables contained within this function
    if get_run_data_flag == 0:
        pass
    else:
        g_dev_out = (cb_array.base_dev_stdd if(g_dev_sig is None) else(g_dev_sig))
        g_cyc_out = (cb_array.base_cyc_stdd if(g_cyc_sig is None) else(g_cyc_sig))
        return prob,total_iters,iter_per_temp, Jsot_steps, mag_dev_sig, g_dev_out, g_cyc_out,scale


    # ////////////
    # ////////////
    # ////////////
    # ================================== Exexcute SA ==================================
    #   uncomment if analyzing evolution of algorithm across annealing schedule
    #sols_across_temp   = [] 
    #energy_across_temp = []
    # =================================================
    #   Random state to start
    # =================================================
    Vertices = funcs.sample_neurons(devs,0,0,0)
    weighted = np.dot(Vertices, Edges) 

    energy_history = []
    solution_history = []

    Teff = Jsot_max #Set effective temperature
    while(Teff >= Jsot_min): 
        for g in range(iter_per_temp):
            weighted_scaled_limited = funcs.lmap(limit_current,weighted * scale)
            input_J = weighted_scaled_limited
            Vertices = (funcs.sample_neurons(devs,input_J,Teff,0))

            #============================
            #   weighted arr is the result of VMM --
            #   once scaled, it's used as input for the array of MTJs
            #============================
            weighted = np.dot(Vertices, Edges)
            Edges = funcs.inject_add_cyc_noise(Edges_base,cb_array,g_cyc_sig)
        energy_history.append(Vertices @ Edges @ np.array(Vertices).T)
        solution_history.append(funcs.convertToDec(Vertices)) 
        Teff -= Jsot_delta
    solution = funcs.convertToDec(Vertices)
    sol_queue.put(solution)
    sol_hist_queue.put(solution_history)
    e_hist_queue.put(energy_history)


def print_simulation_setup(batch_size) -> None:
    prob,total_iters,iter_per_temp, Jsot_steps, mag_dev_sig, g_dev_sig, g_cyc_sig,scale  = SA([],[],[],1)
    single_sample_time = 0.0002182
    print("====================================================")
    print(f"---------- starting parallel {prob} SA sim with:\n\
            parallel batch size of {batch_size}\n\
            {total_iters} total iterations\n\
            {iter_per_temp} iteration(s) per temp\n\
            {Jsot_steps} temp steps\n\
            MTJ device deviation = {mag_dev_sig}\n\
            G device deviation   = {g_dev_sig}\n\
            G cycle deviation    = {g_cyc_sig}\n\
          \r---------- estimated run time: {math.ceil((total_iters * single_sample_time * iter_per_temp * Jsot_steps)/((batch_size)/2.5 * 60))} minutes")
    print("====================================================")
    return prob, total_iters

def plot():
    prob,total_iters,iter_per_temp, Jsot_steps, mag_dev_sig, g_dev_sig, g_cyc_sig,scale  = SA([],[],[],1)
    date = funcs.my_hist(prob,total_iters,sols,scale,iter_per_temp,Jsot_steps,mag_dev_sig,g_dev_sig,g_cyc_sig)
    return date

if __name__ == "__main__":
    total_start_time = time.time()
    # ================================================================
    #  parallelized wrapper for SA(), 
    #  run paramters are only accesible from the function body
    # ================================================================
    
    sols      = []
    all_sols = []
    all_e = []
    #NOTE: fine if personal, change if lab puter
    batch_size = os.cpu_count() 
    #   function call to get run data for job creation and for user to see
    prob, total_iters = print_simulation_setup(batch_size)

    #   not to the best way to parallelize since
    #   batches are sequential, that is, even if an open
    #   core is available, it wont run till the slowest
    #   process finishes. good enough for now though.
    sims_to_run = total_iters
    pbar = tqdm(total=total_iters,ncols=80)
    while sims_to_run >= 1:        
        if sims_to_run < batch_size:
            batch_size = sims_to_run
        sol_queue = mp.Queue()  # parallel-safe queue
        all_e_queue = mp.Queue()  # parallel-safe queue
        all_sols_queue = mp.Queue()  # parallel-safe queue
        processes = []
        #   create processes and start them
        for _ in range(batch_size):
            sim = mp.Process(target=SA, args=(sol_queue,all_sols_queue,all_e_queue,0))
            processes.append(sim)
            sim.start()
        #   waits for solution to be available
        for sim in processes:
            sol = sol_queue.get()  #will block
            sol_list = all_sols_queue.get()  #will block
            e_list = all_e_queue.get()  #will block
            sols.append(sol)
            all_sols.append(sol_list)
            all_e.append(e_list)
        #   wait for all processes to wrap-up before continuing
        for sim in processes:
            sim.join()
        pbar.update(batch_size)
        sims_to_run -= batch_size 
    pbar.close()

    print("--- total program time: %s seconds ---" % (time.time() - total_start_time))
    #   plot
    print("--- saving plot... ----")
    date = plot()
    print("-------- done ---------")
    f = open(f"./outputs/energy_data/energy_data_{date}.py", "w")
    f.write("e = " + str(all_e) + "\n")
    f.write("s = " + str(all_sols))
    f.close()
