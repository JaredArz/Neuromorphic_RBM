import numpy as np
import matplotlib.pyplot as plt
import itertools
import sys
sys.path.append('../')
sys.path.append('../fortran_source')
import funcs as f
# import functions to test directly
import RRAM_types as rram


def main():
    # ======================
    plot_select = "hist"    #hist, cdf
    # ======================
    dev = rram.MTJ_INC
    G_LRS = 1.0/dev.LRS
    std_dev = dev.base_dev_stdd
    G_LRS_mat = np.full((6,6),G_LRS)
    sample_num = 2700

    y = []
    for i in range(sample_num):
        G_w_noise = f.inject_add_cyc_noise(G_LRS_mat, dev, std_dev)
        for elem in G_w_noise.flatten():
            y.append(elem)
    
    count, bins_count = np.histogram(y, bins=64)
    pdf = count / sum(count)
    cdf = np.cumsum(pdf)

    if plot_select == "cdf":
        plt.plot((bins_count[1:]), (cdf))
    elif plot_select == "hist":
        plt.hist(y,100,facecolor="cadetblue")
    plt.xlabel(f'mtj_G')
    plt.ylabel('Frequency')
    plt.title('mtj G LRS distribution around mean (100,000 samples)')

    plt.savefig(f"./noise_test_mtj_g_{plot_select}.png", dpi=1200)

if __name__ == "__main__":
    main()

