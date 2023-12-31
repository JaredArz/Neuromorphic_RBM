import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path
import os
import plotting_funcs as pf
from sim_class import sim

debug = False

def main() -> None:
    this_sim = sim()
    data = this_sim.get_interactive()
    my_hist( (data["sols"])[0], 500, "Max Sat", "./")

def my_hist(sols,total_iters,prob,out_path) -> None:
    # =================================
    # ===== Graphing of Histogram =====
    # =================================

    fig,ax = pf.plot_init()
    plot_w_file = (f'Hist_RBM_{prob}.svg').replace(" ","")
    w_path = os.path.join(out_path, plot_w_file)

    bar_col = 'cadetblue'
    format_hist_for_prob(fig,ax,prob)
    #======================================================================
    ax.set_yticks(range(0, total_iters, int(total_iters/10)))
    ax.hist(sols,bins=64,facecolor=bar_col)
    ax.set_xlabel('Value')
    ax.set_ylabel('Frequency')
    ax.set_title(prob + ' Solution Frequency Over ' + str(total_iters) + ' Iterations')
    if debug:
        ax.annotate(f"Amplification: {(scale):.2e}",xy = (275,280), xycoords='figure points')
        ax.annotate(f"Num steps {Jsot_steps}   ", xy = (275,270),xycoords='figure points')
        ax.annotate(f"Iters per step {iter_per_temp}", xy = (275,260),xycoords='figure points')
        ax.annotate(f"MTJ dev-to-dev  σ {mag_dev_sig}", xy = (275,250),xycoords='figure points')
        ax.annotate(f"CBA dev-to-dev σ {g_dev_sig}", xy = (275,240),xycoords='figure points')
        ax.annotate(f"CBA cyc-to-cyc  σ {g_cyc_sig}", xy = (275,230),xycoords='figure points')
    pf.prompt_save_svg(fig,w_path)

def format_hist_for_prob(fig,ax,prob):
    sol_highlight = "red"
    #=====================================================================
    #   define x ticks and solution-tick highlighting unique for each problem
    if prob == "Max Cut":
        ticks = [0,5,11,12,13,20,25,30,35,40,45,50,51,52,60,68]
        labels = [0,5,' ',12,' ',20,25,30,35,40,45,' ',51,' ',60,68]
        ax.set_xticks(ticks=ticks,labels=labels)
        fig.gca().get_xticklabels()[3].set_color(sol_highlight)
        fig.gca().get_xticklabels()[-4].set_color(sol_highlight)
    elif prob == "Max Sat":
        ticks = [0,5,10,20,21,22,27,28,29,35,40,45,50,55,60,68]
        labels = [0,5,10,' ',21,' ',' ',28,' ',35,40,45,50,55,60,68]
        ax.set_xticks(ticks=ticks,labels=labels)
        fig.gca().get_xticklabels()[4].set_color(sol_highlight)
        fig.gca().get_xticklabels()[7].set_color(sol_highlight)
    elif prob == "Ind Set":
        ticks = [0,5,10,15,20,25,30,36,37,38,40,45,50,55,60,68]
        labels = [0,5,10,15,20,25,30,'',37,'',40,45,50,55,60,68]
        ax.set_xticks(ticks=ticks,labels=labels)
        fig.gca().get_xticklabels()[7].set_color(sol_highlight)

if __name__ == "__main__":
    main()
