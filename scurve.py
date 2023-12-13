import sys
sys.path.append("./data_proc")
import plotting_funcs as pf
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.style as style
import scienceplots
import os
import time
import numpy as np
import glob
import re
from tqdm import tqdm

from mtj_types import SHE_MTJ_rng

j_steps = 50 #was 250
J_lut = np.linspace(-6e9,6e9,j_steps)
J_SHEs = [3e11, 5e11, 4.85e12]
num_to_avg = 1000
#num_to_avg = 10000
dev_variations = 2 #was 100

def gen():
  start_time = time.time()
  out_path = get_out_path()

  devices = []
  for _ in range(dev_variations):
    dev = SHE_MTJ_rng(np.pi/2, np.random.uniform(0,2*np.pi), 0.05)
    devices.append(dev)

  pbar = tqdm(total=len(devices)*len(J_SHEs))
  for J_SHE in J_SHEs:
    for dev_num,dev in enumerate(devices):
        weights = []
        for j in range(j_steps):
          avg_wght = 0
          for _ in range(num_to_avg):
            J_stt = J_lut[j]
            out, _ = dev.mtj_sample(J_stt,J_SHE)
            avg_wght = avg_wght + out
          avg_wght = avg_wght/num_to_avg
          weights.append(avg_wght)
        w_file = f"{out_path}/weight_data_{J_SHE:.0e}_{dev_num}.txt"
        f = open(w_file,'w')
        for i in range(j_steps):
          f.write(str(weights[i]))
          f.write('\n')
        f.close()
        pbar.update(1)
  pbar.close()
  print("--- %s seconds ---" % (time.time() - start_time))

def get_out_path():
  make_dir = lambda d: None if(os.path.isdir(d)) else(os.mkdir(d))
  #create dir and write path
  date = datetime.now().strftime("%H:%M:%S")
  out_path = (f"./outputs/weight_dataset_{date}")
  make_dir("./outputs")
  make_dir(f"{out_path}")
  return out_path

CB_color_cycle = ['#377eb8', '#ff7f00', '#4daf4a',
                '#f781bf', '#a65628', '#984ea3',
                '#999999', '#e41a1c', '#dede00']
def plot(path):
  fig, ax = pf.plot_init()
  slash_re = r'\/$'
  date_re = r'\d{2}:\d{2}:\d{2}'
  lines=[]

  for i,J_SHE in enumerate(J_SHEs):
    if re.search(slash_re, path):
      files = glob.glob(f"{path}*{J_SHE:.0e}*.txt")
    else:
      files = glob.glob(f"{path}/*{J_SHE:.0e}*.txt")
    weights_2d = []

    for f in files:
      weights = np.loadtxt(f, usecols=0);
      weights_2d.append(weights)
    average = np.average(weights_2d,axis=0)
    line, = plt.plot(J_lut,average,color=CB_color_cycle[i], alpha=1, linewidth=2, linestyle='-')
    lines.append(line)
    stddevs = np.std(weights_2d, axis=0, ddof=1)
    minus = average[:] - stddevs[:]
    plus = average[:] + stddevs[:]
    # takes average of all devices and plots that scurve
    # uses the standard deviation calculated from all the devices 
    # to plot error bands
    # note that each device weight curve is itself averaged over a few times to get
    # a solid line
    ax.fill_between(J_lut,minus,plus,interpolate=True,alpha=0.2)

  ax.set_xlabel(r'$J_{STT}$ ($A/m^{2}$)')
  ax.set_ylabel('Weight')
  ax.set_ylim([-0.05, 1.05])
  ax.legend([lines[0],lines[1],lines[2]], [r'$3*10^{11}$', r'$5*10^{11}$', r'$5*10^{12}$'], title=r'$J_{SOT}(A/m^2)$',loc='upper right',prop={'size':16})


  match = re.search(date_re, path)
  if match:
    date=match.group(0)
  else:
    print("No date associated with dataset, fix paths manually, exiting")
    return 0

  pf.prompt_show(fig)
  pf.prompt_save_svg(fig, f"./outputs/weight_dataset_{date}/scurve.svg")

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
