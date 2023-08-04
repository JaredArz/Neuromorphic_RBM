import matplotlib.pyplot as plt
import random as rnd
import numpy as np
from pathlib import Path

from   mtj_types import SHE_MTJ_rng
import RRAM_types
import helper_funcs as h
import SA_funcs  as s
import parallelism as p

from re import S
import time
from datetime import datetime
import os

#REFERENCES: [1] Random Bitstream Generation using Voltage
#-Controlled Magnetic Anisotropy and Spin Orbit Torque Magnetic Tunnel Junctions 

dev_iter = 50
def main():
    batch_size = 3*os.cpu_count() 
    # =======================================================================
    prob = "Max Sat"
    #NOTE: these values are found to work well --jared, 3,50-150
    total_iters = 10000  #Number of Simulations to Run
    iter_per_temp = 1
    Jsot_steps = [5,10,25,64,100,200,300,400,500,750,1000]

    cb_array = RRAM_types.HfHfO2

    #None uses default values
    #0.1, 0.25 works nicely for RRAM HfHfO2
    g_dev_sig   = 0       # device to device variation
    g_cyc_sig   = 0       # cycle to cycle variation 
    mag_dev_sig = 0
    single_overwrite_flag = False
    multi_overwrite_flag = False
    # =======================================================================
    # =======================================================================
    # =======================================================================

    out_path = h.get_out_path(prob)

    sim_wrapper = choose_wrapper(multi_overwrite_flag,single_overwrite_flag,\
                            bool(g_dev_sig == 0 and mag_dev_sig == 0))
    if sim_wrapper is None:
        print("flag error")
        exit()

    total_start_time = time.time()
    for i in range(len(Jsot_steps)):
        a = {"total_iters": total_iters,"prob":prob,
             "g_dev_sig": g_dev_sig, "g_cyc_sig":g_cyc_sig,
             "mag_dev_sig":mag_dev_sig,"cb_array":cb_array,
             "iter_per_temp":iter_per_temp,"Jsot_steps":Jsot_steps[i]}
        sim_setup = h.get_simulation_setup(batch_size, a)
        print(sim_setup)
        h.write_setup(sim_setup,out_path)
        sim_wrapper(batch_size,a,out_path)
    print("--- total program time: %s seconds ---" % (time.time() - total_start_time))

def sim_with_dev_var(batch_size,a,out_path):
    print(f"--- running {dev_iter} device samples... ---")
    print("--- this will take a while... ---")
    success_rate_list = []
    for i in range(dev_iter):
        sols,all_sols,all_e = p.run_in_batch(SA,batch_size,a)
        success_rate = h.get_success_rate(all_sols,a["prob"])
        success_rate_list.append(success_rate)
        print(f"--- success rate {i}: {success_rate}% ---")
        plot_wrapper(sols, a, out_path, i)
        h.write_data(all_e,all_sols,out_path)
        h.write_success(success_rate,out_path)
    std_dev = np.std(success_rate_list)
    mean = np.average(success_rate_list)
    dev_file = "device_iterations.txt"
    f = open( Path( out_path / dev_file ), 'w' )
    f.write(f"success rates are across {dev_iter} sims with MTJ or CB array dev-to-dev variation\n")
    f.write(f"mean: {mean}\n")
    f.write(f"std dev. {std_dev}\n")
    f.close()

def sim_no_dev_var(batch_size,a,out_path):
    sols,all_sols,all_e = p.run_in_batch(SA,batch_size,a)
    success_rate = h.get_success_rate(all_sols,a["prob"])
    print(f"--- success rate: {success_rate}% ---")
    plot_wrapper(sols,a,out_path)
    h.write_data(all_e,all_sols,out_path)
    h.write_success(success_rate,out_path)

def choose_wrapper(m_flag,s_flag,not_dev_var):
    if ( not_dev_var and not m_flag ) or (s_flag and not m_flag):
        sim = sim_no_dev_var
    elif (not not_dev_var and not s_flag ) or (m_flag and not s_flag):
        sim = sim_with_dev_var
    else:
        sim = None
    return sim

def SA(a, sol_queue,sol_hist_queue,e_hist_queue):
    # ========================= Problem definition =========================
    total_iters,prob,g_dev_sig,g_cyc_sig,mag_dev_sig,\
            cb_array,scale,iter_per_temp,Jsot_steps = h.unpack(a)

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
        print("bad problem")
        exit()
    # =======================================================================
   
   
    # ========================== device init  ===============================

    #   map abstract weights to conductances
    gmin = 1.0/cb_array.HRS
    gmax = 1.0/cb_array.LRS
    Edges = (( (Edges-np.min(Edges)/(np.max(Edges)-np.min(Edges)))*(gmax-gmin))+gmin )
    Edges_base = s.inject_add_dev_var(Edges,cb_array,g_dev_sig)

    thetas    = np.full(6,np.pi/2)
    phis      = np.ones_like(thetas)*np.random.uniform(0,2*np.pi,size=np.shape(thetas))
    devs = [ SHE_MTJ_rng(thetas[i], phis[i], mag_dev_sig) for i in range(6)]
    # ===============================================================================


    # ================ annealing schedule ====================
    # === values from [1] ===
    Jsot_max    = 5e11      #
    Jsot_min    = 1e11      #
    # =======================
    Jsot_delta = ( Jsot_max - Jsot_min ) / Jsot_steps 
    # limit current according to [1]
    limit_current = lambda J: -6e9 if(J < -6e9) else( 6e9 if(J > 6e9) else J)
    # ========================================================


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
    Vertices = s.sample_neurons(devs,0,0,0)
    weighted = np.dot(Vertices, Edges) 

    energy_history = []
    solution_history = []

    Teff = Jsot_max #Set effective temperature
    while(Teff >= Jsot_min): 
        for g in range(iter_per_temp):
            weighted_scaled_limited = s.lmap(limit_current,weighted * scale)
            input_J = weighted_scaled_limited
            Vertices = (s.sample_neurons(devs,input_J,Teff,0))

            #============================
            #   weighted arr is the result of VMM --
            #   once scaled, it's used as input for the array of MTJs
            #============================
            weighted = np.dot(Vertices, Edges)
            Edges = s.inject_add_cyc_noise(Edges_base,cb_array,g_cyc_sig)
        energy_history.append(Vertices @ Edges @ np.array(Vertices).T)
        solution_history.append(s.convertToDec(Vertices)) 
        Teff -= Jsot_delta
    solution = s.convertToDec(Vertices)
    sol_queue.put(solution)
    sol_hist_queue.put(solution_history)
    e_hist_queue.put(energy_history)

def plot_wrapper(sols,a,out_path,dev_i=None):
    total_iters,prob,g_dev_sig,g_cyc_sig,mag_dev_sig,\
            cb_array,scale,iter_per_temp,Jsot_steps = h.unpack(a)
    h.my_hist(sols,total_iters,prob,g_dev_sig,g_cyc_sig,mag_dev_sig,\
                              cb_array,scale,iter_per_temp,Jsot_steps,out_path,dev_i)

if __name__ == "__main__":
    main()
