import sys
sys.path.append("./fortran_source")
import sampling as f90
import os
import signal
import numpy as np

def mtj_sample(dev,Jstt,Jshe,dump_mod=1,view_mag_flag=0,file_ID=1,config_check=0) -> (int,float):
    energy, bit, theta_end, phi_end = f90.sampling.sample_she(Jstt,\
            Jshe, dev.theta, dev.phi, dev.Ki, dev.TMR, dev.Rp,\
            dump_mod, view_mag_flag, 0, file_ID, config_check)
    # Need to update device objects and put together time evolution data after return.
    dev.phi = phi_end
    dev.theta = theta_end
    #if( (view_mag_flag and (dev.sample_count % dump_mod == 0)) or config_check):
    #    # These file names are determined by fortran subroutine single_sample.
    #    phi_from_txt   = np.loadtxt("phi_time_evol_"+ format_file_ID(file_ID) + ".txt", dtype=float, usecols=0, delimiter=None)
    #    theta_from_txt = np.loadtxt("theta_time_evol_"+ format_file_ID(file_ID) + ".txt", dtype=float, usecols=0, delimiter=None)
    #    os.remove("phi_time_evol_"   + format_file_ID(file_ID) + ".txt")
    #    os.remove("theta_time_evol_" + format_file_ID(file_ID) + ".txt")
    #    dev.thetaHistory = list(theta_from_txt)
    #    dev.phiHistory   = list(phi_from_txt)
    #if(view_mag_flag):
    #    dev.sample_count+=1
    return bit,energy

# Format must be consistent with fortrn, do not change
# File ID of length seven with 0's to the left
def format_file_ID(pid) -> str:
    str_pid = str(pid)
    while len(str_pid) < 7:
        str_pid = '0' + str_pid
    return str_pid
