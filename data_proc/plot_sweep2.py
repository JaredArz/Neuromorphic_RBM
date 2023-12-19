import matplotlib.pyplot as plt
import scienceplots
import numpy as np
from data_class import data
import plotting_funcs as pf
from sim_class import sim

colors = [
         '#648FFF',
         '#DC267F',
         '#FFB000',
         ]

def main():
    fig,ax  = pf.plot_init()
    ax.title("Success Rate Parameter Sweep")
    ax.set_ylabel("Percent Success Rate")
    ax.set_xlabel('Standard Deviation')
    ax.set_ylim((0,100))

    this_sim = sim()
    data = this_sim.get_interactive()
    #=========== mdd,s,gdd,gcc
    # GOAL: plot all Ndd,Gcc constant and just vary Gdd
    #plot_sweep_slice(ax,x,D[0,0,:,0],colors[0])
    #plot_sweep_slice(ax,x,D[0,1,:,0],colors[1])
    #plot_sweep_slice(ax,x,D[0,2,:,0],colors[2])
    # need to get mean, high, low, data for varying values in range... need full sweep of data to actually test
    sweep = data["sols"]

    pf.prompt_save_svg("./test_sweep.svg")

get_slice_attrs = lambda sliced, attr: [getattr(elem, attr) for elem in sliced]
def plot_sweep_slice(ax,x,sliced,color):
    means   = get_slice_attrs(sliced,"means")
    stddevs = get_slice_attrs(sliced,"stddevs")
    highs   = get_slice_attrs(sliced,"highs")
    lows    = get_slice_attrs(sliced,"lows")
    #FIXME: highest and lowest will get messy with so many godman overlayed plots
    highest = max(highs)
    lowest  = min(lows)+0.25
    y = means
    yerror = stddevs
    y_minus = [y[i]-yerror[i] for i in range(len(y))]
    y_plus = [y[i]+yerror[i] for i in range(len(y))]
    ax.axhline(y=highest, color=color, linestyle="--",alpha=0.15)
    ax.axhline(y=lowest, color=color, linestyle="--",alpha=0.15)
    ax.errorbar(x, y, yerr=yerror, fmt='',data=None, marker='s')
    ax.fill_between(x, y_minus,y_plus,interpolate=True,alpha=0.1)

if __name__ == "__main__":
    main()
