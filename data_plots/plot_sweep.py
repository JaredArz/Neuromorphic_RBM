import matplotlib.pyplot as plt
import scienceplots
import numpy as np
from data_class import data

def main():
    colors = [
             '#648FFF',
             '#DC267F',
             '#FFB000',
             ]
    plot_init()
    print("file to load:")
    data_fname = input()
    x = [0.0,0.05,0.1,0.15,0.2,0.25,0.3,0.4,0.5]
    D = np.load(data_fname,allow_pickle=True)
    plot_sweep_slice(x,D[0,0,5,:],colors[0])
    plot_sweep_slice(x,D[0,0,5,:],colors[1])
    plot_sweep_slice(x,D[0,0,5,:],colors[2])
    print("save plot as (.svg):")
    fname = input()
    plt.savefig(f"./plots/{fname}.svg", format = 'svg')

def plot_init():
    #fig, ax1 = plt.subplots()
    #FIXME: no tacc sad
    #plt.rc('text', usetex=True)
    #plt.style.use(['science','ieee'])
    plt.title("Success Rate Parameter Sweep")
    plt.ylabel("Percent Success Rate")
    #FIXME: no tacc sad
    #plt.xlabel(r'Standard Deviation [$\Omega$] = 1/2\ \mu*10^x$')
    plt.xlabel('Standard Deviation')
    plt.ylim((0,100))
    #fig.tight_layout()
    #return fig,ax1

get_slice_attrs = lambda sliced, attr: [getattr(elem, attr) for elem in sliced]
def plot_sweep_slice(x,sliced,color):
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
    plt.axhline(y=highest, color=color, linestyle="--",alpha=0.15)
    plt.axhline(y=lowest, color=color, linestyle="--",alpha=0.15)
    plt.errorbar(x, y, yerr=yerror, fmt='',data=None, marker='s')
    plt.fill_between(x, y_minus,y_plus,interpolate=True,alpha=0.1)

'''Deprecated
def plot_sweep(x,means,stddevs,highs,lows):
    colors = [
             '#648FFF',
             '#DC267F',
             '#FFB000',
             ]
    #FIXME: highest and lowest will get messy with so many godman overlayed plots
    highest = max(highs)
    lowest  = min(lows)
    y = means
    yerror = stddevs
    plt.axhline(y=highest, color="black", linestyle="--",alpha=0.15)
    plt.axhline(y=lowest, color="black", linestyle="--",alpha=0.15)
    plt.errorbar(x, y, yerr=yerror, fmt='',data=None, marker='s')
'''

if __name__ == "__main__":
    main()
