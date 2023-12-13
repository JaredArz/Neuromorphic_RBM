import sys
from   mtj_types import SHE_MTJ_rng
import numpy as np
import copy
import os
import time
import itertools as it
import helper_funcs as h


debug = False

Max_Sat_Weights = np.array([[-5, -1, -1, 10, -1, -1],
                          [-1, -7, -2, -2, 10, -1],
                          [-1, -2, -7, -2, -1, 10],
                          [10, -2, -2, -7, -1, -1],
                          [-1, 10, -1, -1, -5, -1],
                          [-1, -1, 10, -1, -1, -5]])
#Example Graph:
#  0  1
#  |/\|
#  2  3     
#  |/\|
#  4  5
#Solution is 110011/001100 = 51/12
Max_Cut_Weights = np.array([[10,10,-1,-1,10,10],
                          [10,10,-1,-1,10,10],
                          [-1,-1,10,10,-1,-1],
                          [-1,-1,10,10,-1,-1],
                          [10,10,-1,-1,10,10],
                          [10,10,-1,-1,10,10]])

#Example Graph:
#            0
#           / \
#          1   2 
#         /\   /\
#        /  \ /  \  
#        \   4   /
#         \ / \ /
#          3   5
#Solution is 100101 = 37
Ind_Set_Weights = np.array([[-10,10,10,-1,-1,-1],
                          [10,-10,-1,10,10,-1],
                          [10,-1,-10,-1,10,10],
                          [-1,10,-1,-10,10,-1],
                          [-1,10,10,10,-10,10],
                          [-1,-1,10,-1,10,-10]])

def SetMTJs(mag_dev_sig):
    thetas    = np.full(6,np.pi/2)
    phis      = np.ones_like(thetas)*np.random.uniform(0,2*np.pi,size=np.shape(thetas))
    devs = [ SHE_MTJ_rng(thetas[i], phis[i], mag_dev_sig) for i in range(6)]
    return devs


def SetCBA(g_dev_sig,prob,cb_array):
    if prob == "Max Sat":
        Edges = Max_Sat_Weights
    elif prob == "Max Cut":
        Edges = Max_Cut_Weights
    elif prob == "Ind Set":
        Edges = Ind_Set_Weights
    else:
        print("bad problem")
        exit()

    # ========================== device init  ===============================
    gmin = 1.0/cb_array.HRS
    gmax = 1.0/cb_array.LRS
    Edges = (( (Edges-np.min(Edges)/(np.max(Edges)-np.min(Edges)))*(gmax-gmin))+gmin )
    Edges = inject_add_dev_var(Edges,cb_array,g_dev_sig)
    return Edges

limit_current = lambda J: -6e9 if(J < -6e9) else( 6e9 if(J > 6e9) else J)
def SA(p,c, Edges,devs, sol_queue,sol_hist_queue,e_hist_queue,parallel_flag):
    g_cyc_sig  = p["g_cyc_sig"]
    scale      = p["scale"]
    cb_array   = c["cb_array"]
    Jsot_steps = c["Jsot_steps"]
    iter_per_temp = c["iter_per_temp"]

    Edges_base = copy.deepcopy(Edges)

    #   all forked process inherit the same prng seed. 
    #   manually setting with a mostly unique seed to avoid this determinism
    np.random.seed((os.getpid() * int(time.time())) % 123456789)

    # ================ annealing schedule ====================
    # === values from [1] ===
    Jsot_max    = 5e11      #
    Jsot_min    = 1e11      #
    # =======================
    Jsot_delta = ( Jsot_max - Jsot_min ) / Jsot_steps
    # limit current according to [1]
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
    Vertices = sample_neurons(devs,0,0,0)
    weighted = np.dot(Vertices, Edges)

    energy_history = []
    solution_history = []

    if debug:
        f = open("weighted_inputs.txt", "w")

    Teff = Jsot_max #Set effective temperature
    while(Teff >= Jsot_min):
        for g in range(iter_per_temp):
            weighted_scaled_limited = lmap(limit_current,weighted * scale)
            if debug:
                for j in weighted_scaled_limited:
                    f.write(str(j))
                    f.write("  ")
                f.write("\n")
            Vertices = (sample_neurons(devs,weighted_scaled_limited,Teff,0))

            #============================
            #   weighted arr is the result of VMM --
            #   once scaled, it's used as input for the array of MTJs
            #============================
            weighted = np.dot(Vertices, Edges)
            if g != iter_per_temp-1:
                Edges = inject_add_cyc_noise(Edges_base,cb_array,g_cyc_sig)
        energy_history.append(Vertices @ Edges @ np.array(Vertices).T)
        solution_history.append(convertToDec(Vertices))
        Edges = inject_add_cyc_noise(Edges_base,cb_array,g_cyc_sig)
        Teff -= Jsot_delta
    solution = convertToDec(Vertices)
    if debug:
        f.close()
    if parallel_flag:
        sol_queue.put(solution)
        sol_hist_queue.put(solution_history)
        e_hist_queue.put(energy_history)
    else:
        return [],[],[]

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
        out, _ = devs[h].mtj_sample(neurons_dot_W_scaled[h],J_step)
        bits.append( out )
    return bits

get_Log10R      = lambda G: np.log10(1.0/G)
sample_noise    = lambda logR,std_dev: np.random.normal(logR,std_dev)
to_G            = lambda noisy_logR: 1.0/pow(10,noisy_logR)
abs_arr         = lambda e: abs(e)
lmap = lambda func, *iterable: list(map(func, *iterable))
# The resistance is experimentally observed to be approximately log-normal (both cycle-to-cycle and device-to-device)
# From Intrinsic Switching Variability in HfO2 RRAM, A.Fantini
def inject_add_cyc_noise(G_in,cbarr,std_dev) -> np.ndarray:
    if std_dev == 0:
        return G_in
    #//////////////////
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

def inject_add_dev_var(G_in,cbarr,std_dev) -> np.ndarray:
    if std_dev == 0:
        return G_in
    #//////////////////
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
