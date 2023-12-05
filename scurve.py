import sys
sys.path.append('./fortran_source')
# ===== handles fortran interface and batch parallelism =====
# ===========================================================
import os
import time
import numpy as np
import glob
from datetime import datetime
import matplotlib.pyplot as plt
from mtj_types import SHE_MTJ_rng, draw_norm
import re
from tqdm import tqdm

j_steps = 5 #FIXME increase to 100
J_lut = np.linspace(-6e9,6e9,j_steps)

num_to_avg = 1000 #FIXME increase to 10000
dev_variations = 10

def gen():
  start_time = time.time()
  out_path = get_out_path()
  dump_flag = 0
  devices = []

  for _ in range(dev_variations):
    dev = SHE_MTJ_rng()
    devices.append(dev)

  #FIXME add bounds for dev-dev var
  #FIXME add extra loop to check 3 different SHES
  pbar = tqdm(total=len(devices))
  for dev_num,dev in enumerate(devices):
    weights = []
    for j in range(j_steps):
      avg_wght = 0
      for _ in range(num_to_avg):
        _, out, theta_end, phi_end = f90.single_sample.pulse_then_relax(J_lut[j],5e11,
                                                      dev.theta,dev.phi,
                                                      dev.Ki,dev.TMR,dev.Rp,dump_flag)
        dev.theta = theta_end
        dev.phi = phi_end
        #out,energy = mtj_sample(dev,J_lut[j])
        avg_wght = avg_wght + out
      avg_wght = avg_wght/num_to_avg
      weights.append(avg_wght)
    w_file = f"{out_path}/weight_data_{dev_num}.txt"
    f = open(w_file,'w')
    for i in range(j_steps):
      f.write(str(weights[i]))
      f.write('\n')
    f.close
    pbar.update(1)
  pbar.close()
  print("--- %s seconds ---" % (time.time() - start_time))

def get_out_path():
  make_dir = lambda d: None if(os.path.isdir(d)) else(os.mkdir(d))
  #create dir and write path
  date = datetime.now().strftime("%H:%M:%S")
  out_path = (f"./results/weight_dataset_{date}")
  make_dir("./results")
  make_dir(f"{out_path}")
  return out_path

def plot(path):
  slash_re = r'\/$'
  date_re = r'\d{2}:\d{2}:\d{2}'
  if re.search(slash_re, path):
    files = glob.glob(f"{path}*.txt")
  else:
    files = glob.glob(f"{path}/*.txt")
  colormap = plt.cm.get_cmap('viridis', len(files))
  weights_2d = []
  for i,f in enumerate(files):
    weights = np.loadtxt(f, usecols=0);
    weights_2d[i] = weights
    plt.plot(J_lut,weights,color=colormap(i), alpha=0.7)
  stddevs = compute_stddevs(weights_2d)
  plt.xlabel('J [A/m^2]')
  plt.ylabel('weight')
  plt.title('Coin Bias')
  print("save figure? (y/n)")
  user_bool = input()
  if user_bool == 'y' or user_bool == 'Y':
    match = re.search(date_re, path)
    if match:
      date=match.group(0)
      plt.savefig(f"./results/weight_dataset_{date}/scurve.png",format='png',dpi=1200)
    else:
      print("No date associated with dataset, enter a string to save ./results/scurve_<your input>.png")
      user_tag = input()
      plt.savefig(f"./results/scurve_{user_tag}.png",format='png',dpi=1200)
  plt.show()

def compute_stddevs(weights_2d):
  weights_2d = np.array(weights_2d)
  means = [np.average(arr,axis=0) for arr in weights_2d]
  sums = []
  for i in range(len(weights_2d)):
      weights_2d[:, i] = pow(weights_2d[:, i] - means[i],2)
      sums[i] = np.sum(weights_2d, axis=0)
  stddevs = pow(sums[i] / len(weights_2d), 0.5)
  return stddevs

if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("Call with task:\n'-g':generate scurve,\n'-p <path>': plot existing scurve with data from path")
    raise(IndexError)
  task = sys.argv[1]
  if task == '-g':
      gen()
  elif task == '-p':
      path = sys.argv[2]
      plot(path)
  else:
      print("can't do the task you've asked for")
      raise(NotImplementedError)
