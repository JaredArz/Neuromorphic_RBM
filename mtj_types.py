import numpy as np

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
