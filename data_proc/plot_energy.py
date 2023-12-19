import sys
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np
import gzip
import os

import plotting_funcs as pf
from sim_class import sim

Jsot_max    = 5e11
Jsot_min    = 1e11
Jsot_steps  = 150

colors = [
         '#648FFF',
         '#DC267F',
         '#FFB000',
         ]

def main():
    this_sim = sim()
    data = this_sim.get_interactive()
    es = data["costs"]
    sols  = data["sols"]

    J_sot = np.linspace(Jsot_min,Jsot_max,Jsot_steps)

    fig, ax = pf.plot_init()
    ax.set_xlabel(r'Current Density $A/m^3$')
    init_energys_plot(J_sot,es,ax)
    pf.prompt_save_svg(fig, "./test.svg")

def init_avg_energy_plot(x,y,ax):
    ax.plot(x,y,colors[0])
    ax.axhline(y=y[-1], color="black", linestyle="--",alpha=0.15)
    ax.set_title('Average Energy Across SA Iterations')
    ax.set_ylabel('System Energy')

def init_energys_plot(x,es,ax):
    min_e = es[0,0]
    for array in es:
        current = np.amin(array)
        if (current < min_e):
            min_e = current
    ax.axhline( min_e , color='0', linestyle="--",alpha=0.6)
    for i,e in enumerate(es):
        ax.plot(x,e,color=colors[i % len(colors)],alpha=0.9)
    ax.set_title('Energy Over SA Iterations')
    ax.set_ylabel('System Energy')

""" FIXME
def init_single_energy_and_sol(x,y):
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
"""

if __name__ == "__main__":
    main()
