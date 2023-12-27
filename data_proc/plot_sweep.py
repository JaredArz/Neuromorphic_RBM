import matplotlib.pyplot as plt
import numpy as np
import plotting_funcs as pf
from sim_class import sim

colors = [
         '#648FFF',
         '#DC267F',
         '#FFB000',
         ]

def main():
    fig,ax  = pf.plot_init()
    ax.set_title("Success Rate Parameter Sweep")
    ax.set_ylabel("Percent Success Rate")
    ax.set_xlabel('Standard Deviation')
    ax.set_ylim((0,100))

    this_sim = sim("../outputs/RBM_sims_12-19/MaxSat_Memristor_500_15:30:47")

    x = this_sim.get_Gdds()
    plot_sweep(x, this_sim, "Gdd", ax)
    pf.prompt_save_svg(fig, "./test_sweep.svg")

#duplicate = lambda a,l : [a[0] for _ in range(l)]

def plot_sweep(x,sim,key,ax):
    means   = sim.slice(key,"mean")
    stddevs = sim.slice(key,"stddev")
    highs   = sim.slice(key,"high")
    lows    = sim.slice(key,"low")
    #dummy = map(lambda l: duplicate(l,len(x)) if len(l) < len(x) else l, dummy)
    highest = max(highs)
    lowest  = min(lows)+0.25
    lower_bound = [means[i]-stddevs[i] for i in range(len(means))]
    upper_bound = [means[i]+stddevs[i] for i in range(len(means))]
    ax.axhline(highest, color='b', linestyle="--",alpha=0.15)
    ax.axhline(lowest, color='b', linestyle="--",alpha=0.15)
    ax.errorbar(x, means, yerr=stddevs, fmt='',data=None, marker='s')
    ax.fill_between(x, lower_bound, upper_bound, interpolate=True,alpha=0.1)


if __name__ == "__main__":
    main()
