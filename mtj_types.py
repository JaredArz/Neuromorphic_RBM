import sys
sys.path.append("./fortran_source")
import sampling as f90
import os
import numpy as np
# Format must be consistent with fortrn, do not change
# File ID of length seven with 0's to the left
def format_file_ID(pid) -> str:
    str_pid = str(pid)
    while len(str_pid) < 7:
        str_pid = '0' + str_pid
    return str_pid

def draw_norm(x,psig):
    return x*np.random.normal(1,psig,1)

def draw_const(x,csig):
    return x + np.random.normal(-1*csig,csig,1)

class SHE_MTJ_rng():
    def __init__(self,init_theta,phi_init,sig):
        if init_theta == 0:
            print('Init theta cannot be 0, defaulted to pi/100')
            self.theta = np.pi/100
        else:
            self.theta = init_theta
        self.phi = phi_init
        # default sig is 0.05
        self.Ki  = draw_norm(1.0056364e-3,sig/2)  # The anisotropy energy in J/m2
        self.TMR = draw_norm(1.2,sig)             # TMR ratio at V=0,120%  
        self.Rp  = draw_norm(5e3,sig)             # Magenetoresistance at parallel state, 8000 Ohm
        self.energy_usage = 0.0e0
        self.sample_count = 1
        self.thetaHistory = []
        self.phiHistory   = []

    def mtj_sample(self, Jstt, Jshe, dump_mod=1, view_mag_flag=0, file_ID=1) -> (int,float):
        # fortran call
        energy, bit, theta_end, phi_end = f90.sampling.sample_she(Jstt,\
                Jshe, self.theta, self.phi, self.Ki, self.TMR, self.Rp,\
                dump_mod, view_mag_flag, self.sample_count, file_ID)
        # Need to update device objects and put together time evolution data after return.
        self.phi = phi_end
        self.theta = theta_end
        if( view_mag_flag and (sample_count % dump_mod == 0)):
            # These file names are determined by fortran subroutine single_sample.
            phi_from_txt   = np.loadtxt("phi_time_evol_"+ format_file_ID(file_ID) + ".txt", dtype=float, usecols=0, delimiter=None)
            theta_from_txt = np.loadtxt("theta_time_evol_"+ format_file_ID(file_ID) + ".txt", dtype=float, usecols=0, delimiter=None)
            os.remove("phi_time_evol_"   + format_file_ID(file_ID) + ".txt")
            os.remove("theta_time_evol_" + format_file_ID(file_ID) + ".txt")
            dev.thetaHistory = list(theta_from_txt)
            dev.phiHistory   = list(phi_from_txt)
        if(view_mag_flag):
            self.sample_count+=1
        self.energy_usage += energy
        return bit
