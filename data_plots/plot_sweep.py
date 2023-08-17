import matplotlib.pyplot as plt
import scienceplots

def main():
    plot_init()
    plot_sweep_slice(gdd,all_data[0,0,:])
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

def plot_sweep_slice(x,sliced):
    means   = get_slice_attrs(sliced,"means")
    stddevs = get_slice_attrs(sliced,"stddevs")
    highs   = get_slice_attrs(sliced,"highs")
    lows    = get_slice_attrs(sliced,"lows")
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
