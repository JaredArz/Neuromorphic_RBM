import sys
# import functions to test directly
sys.path.append('../')
sys.path.append('../fortran_source')
import mtj_types as mtj
import numpy as np

th_init = np.pi/2
ph_init = np.pi/2
dev = mtj.SHE_MTJ_rng(th_init,ph_init,0)

J_she = 5e11
Jappl = 0
print(dev.energy_usage)
_ = dev.mtj_sample(Jappl,J_she)
print(dev.energy_usage)
_ = dev.mtj_sample(Jappl,J_she)
print(dev.energy_usage)
_ = dev.mtj_sample(Jappl,J_she)
print(dev.energy_usage)
_ = dev.mtj_sample(Jappl,J_she)
print(dev.energy_usage)
