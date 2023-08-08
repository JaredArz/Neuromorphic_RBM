import matplotlib.pyplot as plt
import numpy as np
import re
import os
import glob
import scienceplots


def main():
    data_file = "device_iterations.txt"
    #root_dir =  "../outputs/RBM_sims_08-07/MaxSat_10000_Memristor_08-07_13:45:40"
    #root_dir = "../outputs/RBM_sims_08-07/MaxSat_1000_Memristor_08-07_14:41:23"
    root_dir = "../outputs/RBM_sims_08-07/MaxSat_1000_Memristor_08-07_15:12:58" 
    const_param = "Gdd0.2"
    #const_param = "Gcc0.2"

    means,stddevs,highs,lows = [  [float( e ) for e in elem ] for elem in get_device_iter_data(root_dir,data_file,const_param)]
    x = [0.05,0.1,0.2,0.375,0.4,0.5]
    print(means)
    plot(x,means,stddevs,highs,lows)

def plot(x,means,stddevs,highs,lows):
    highest = max(highs)
    lowest  = min(lows)
    y = means
    yerror = stddevs
    #FIXME: may conflict with style
    A = 6
    plt.rc('figure', figsize=[46.82 * .5**(.5 * A), 33.11 * .5**(.5 * A)])
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')

    plt.axhline(y=highest, color="black", linestyle="--",alpha=0.15)
    plt.axhline(y=lowest, color="black", linestyle="--",alpha=0.15)
    
    plt.errorbar(x, y, yerr=yerror, fmt='',data=None, marker='s')

    plt.ylim( (0,100) )

    plt.title("Success Rate Parameter Sweep")
    plt.ylabel("Percent Success Rate")
    plt.xlabel(r'Noise,$\ \sigma= 1/2\ \mu*10^x$')
    #FIXME: may need to check this style
    plt.style.use('science')
    print("file to save as (no extension): ")
    f_name = input()
    plt.savefig(f"./plots/{f_name}.svg", format = 'svg')

def get_device_iter_data(root_dir, data_file,const_param=None):
    means = []
    stddevs = []
    highs = []
    lows = []
    dirs = sorted(select_dirs(root_dir,const_param))
    for d in dirs:
        with open(os.path.join(d,data_file), 'r') as f:
            for line in f:
                match   = re.search(r"mean: (\d+\.\d+)", line)
                if match:
                    mean = match.group(1)
                    continue
                match = re.search(r"std dev. (\d+\.\d+)", line)
                if match:
                    stddev = match.group(1)
                    continue
                match   = re.search(r"High: (\d+\.\d+)", line)
                if match:
                    high = match.group(1)
                    continue
                match    = re.search(r"Low:  (\d+\.\d+)" , line)
                if match:
                    low = match.group(1)
                    continue
        means.append(mean)
        stddevs.append(stddev)
        highs.append(high)
        lows.append(low)
    return means,stddevs,highs,lows

def select_dirs(root_dir,const_param):
    if const_param is not None:
        dirs = glob.glob(f'{root_dir}/*{const_param}*')
    else:
        dirs = glob.glob(f'{root_dir}/*')
    for d in dirs:
        if os.path.isfile(d):
            i = dirs.index(d)
            dirs.pop(i)
    return dirs

    
if __name__ == "__main__":
    main()
