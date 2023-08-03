import sys
sys.path.append('./fortran_source')
import single_sample as f90
import numpy as np

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
        _, out, theta_end, phi_end = f90.single_sample.pulse_then_relax(neurons_dot_W_scaled[h],J_step,\
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
