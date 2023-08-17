import numpy as np
import re
import os
import glob
import time

class data:
    def __init__(self,m,s,h,l):
        self.means   = m
        self.stddevs = s
        self.highs   = h
        self.lows    = l

to_float = lambda val: float( val )
get_slice_attrs = lambda sliced, attr: [getattr(elem, attr) for elem in sliced]

def main():
    # y is implicitly success rate
    data_file = "device_iterations.txt"
    root_dir = "../outputs/RBM_sims_08-10/MaxSat_1000_Memristor_19:02:54"
    # x axis to sweep over
    gdd = [0.0,0.05,0.1,0.15,0.2,0.25,0.3,0.4,0.5]
    gcc = [0.0,0.05,0.1,0.15,0.2,0.25,0.3,0.4,0.5]
    #each should make a new line on the plot, overlayed
    mdd = [0.0,0.05,0.1]
    scale = [0.75e14,1e14,1.25e14]

    all_data = np.empty((len(mdd),len(scale),len(gdd),len(gcc)),dtype=object)
    for i in range(len(mdd)):
        for j in range(len(scale)):
            for k in range(len(gdd)):
                for l in range(len(gdd)):
                    # using file globbing in the data directory, need each pertinent value
                    #FIXME: i had intended to get slices back by globbing, but now im doing this individually.... maybe easier hthis way???
                    glob = {"gdd":gdd[k], "gcc":gcc[l], "mdd":mdd[i], "s":scale[j]}

                    dir_path = select_dir(root_dir,const_params)
                    means,stddevs,highs,lows = map(to_float, get_file_data(dir_path,data_file))
                    all_data[i,j,k,l] = data(means,stddevs,highs,lows)

    print("save data file as (.npy):")
    fname = input()
    np.save(fname, all_data)


def get_file_data(dir_path, data_file):
    #dir_path = sorted(select_dir(root_dir,const_params))
    with open(os.path.join(dir_path,data_file), 'r') as f:
        for line in f:
            match   = re.search(r"Mean: (\d+\.\d+)", line)
            if match:
                mean = match.group(1)
                continue
            match = re.search(r"Std. dev: (\d+\.\d+)", line)
            if match:
                stddev = match.group(1)
                continue
            match   = re.search(r"High: (\d+\.\d+)", line)
            if match:
                high = match.group(1)
                continue
            match    = re.search(r"Low: (\d+\.\d+)" , line)
            if match:
                low = match.group(1)
                break
    return mean,stddev,high,low

def select_dir(root_dir,c):
    if c is not None:
        dir_path = glob.glob(f'{root_dir}/*Gdd{c["gdd"]}_Gcc{c["gcc"]}_Ndd{c["mdd"]}_s{c["s"]:.2e}*')
    else:
        dir_path = glob.glob(f'{root_dir}/*')
    for d in dir_path:
        if os.path.isfile(d):
            i = dir_path.index(d)
            dir_path.pop(i)

    if len(dir_path) == 0:
        print(f"Directory:\n{dir_path}\nNot found -- The sweep is incomplete. Pointing program to null data.")
        return "../outputs/null_data"
    return dir_path[0]

if __name__ == "__main__":
    main()
