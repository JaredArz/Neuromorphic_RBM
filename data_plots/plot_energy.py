import numpy as np
import sys
output_path = "../outputs"
session_dir = "RBM_sims_08-10"
data_dir = "MaxSat_1000_Memristor_19:02:54"
param_dir = "params_Gdd0.2_Gcc0.05_NddTrue_Js150_i3"
dev_dir = "Dev_4"
sys.path.append('{output_path}/{session_dir}/{data_dir}/{param_dir}/{dev_dir}/')
import matplotlib.pyplot as plt
import scienceplots
import gzip
from pathlib import Path
import os

data_file = 'RBM_energy_and_sols.npy.gz'
path_to_data = Path(Path( output_path)\
                    /Path(session_dir)\
                    /Path(data_dir)   \
                    /Path(param_dir)  \
                    /Path(dev_dir)    \
                    /Path(data_file))
Jsot_max    = 5e11 
Jsot_min    = 1e11   
Jsot_steps = 150
def main():
    arr = []
    with gzip.open(path_to_data, 'rb') as f:
        f_content = f.read()
    with open("temp.npy", 'ab') as f:
        f.write(f_content)
    with open("temp.npy", 'rb') as f:
        all_e = np.load(f)
        all_s = np.load(f)
    os.remove("temp.npy")

    avg_e = list(np.average(all_e,axis=0))
    end_sols = [ elem[-1] for elem in all_s]

    #4 is incredibly good
    #5 is demonstrative, high to low
    #6 is demonstrative, low to high
    sing_i = 5
    s_single = all_s[sing_i]
    #es = (all_e[12], all_e[18], all_e[5])
    ind=11
    es = (all_e[ind])

    x = np.linspace(Jsot_min,Jsot_max,Jsot_steps)


    fig, ax1 = plot_init()
    plot_single_energy(x,fig,ax1,es)
    plt.savefig("s.svg", format="svg")

def plot_init():
    fig, ax1 = plt.subplots()
    ax1.set_xlabel(r'Current Density $A/m^3$')
    plt.rc('text', usetex=True)
    plt.style.use(['science','ieee'])
    fig.tight_layout()
    return fig,ax1

def plot_avg_energy(x,y,fg,ax1):
    ax1.plot(x,y,'#648FFF')
    ax1.axhline(y=y[-1], color="black", linestyle="--",alpha=0.15)
    ax1.set_title('Average Energy Across SA Iterations')
    ax1.set_ylabel('System Energy')

def plot_single_energy(x,fg,ax1,es):
    colors = [  
             '#648FFF',
             '#DC267F',
             '#FFB000',
             ]
    for y in enumerate(es):
        i = y[0]
        y = y[1]
        ax1.plot(x,y,color=colors[i],alpha=0.9)
        if i == 0:
            ax1.axhline(y=y[-1], color='0', linestyle="--",alpha=0.6)
    ax1.set_title('Energy Over SA Iterations')
    ax1.set_ylabel('System Energy')

def plot_single_energy_and_sol(x,y):
    # =======================
    ax1.plot(x,sols_sample,color="#3976af")
    ax1.axhline(y=sols_sample[25], color="black", linestyle="--",alpha=0.15)

    ax2 = ax1.twinx()
    ax2.plot(x,sample,alpha=0.5,color="#ef8536")
    ax2.axhline(y=sample[25], color="black", linestyle="--",alpha=0.15)
    #plt.plot(x,avg)
    ax1.set_ylim(-15,69)
    ax2.set_ylim(-0.00144,0.00025)
    ax1.set_xlabel('Current Density A/m³')
    ax1.set_ylabel('Solution in Decimal')
    ax2.set_ylabel('System Energy')


if __name__ == "__main__":
    main()
