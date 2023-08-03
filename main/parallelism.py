import multiprocessing as mp
from tqdm import tqdm

def run_in_batch(func,batch_size, a):
    sols      = []
    all_sols  = []
    all_e     = []

    #   not to the best way to parallelize since
    #   batches are sequential, that is, even if an open
    #   core is available, it wont run till the slowest
    #   process finishes. good enough for now though.
    sims_to_run = a["total_iters"]
    pbar = tqdm(total=sims_to_run,ncols=80)
    while sims_to_run >= 1:        
        if sims_to_run < batch_size:
            batch_size = sims_to_run
        sol_queue = mp.Queue()  # parallel-safe queue
        all_e_queue = mp.Queue()  # parallel-safe queue
        all_sols_queue = mp.Queue()  # parallel-safe queue
        processes = []
        #   create processes and start them
        for _ in range(batch_size):
            sim = mp.Process(target=func, args=(a,sol_queue,all_sols_queue,all_e_queue))
            processes.append(sim)
            sim.start()
        #   waits for solution to be available
        for sim in processes:
            sol = sol_queue.get()  #will block
            sol_list = all_sols_queue.get()  #will block
            e_list = all_e_queue.get()  #will block
            sols.append(sol)
            all_sols.append(sol_list)
            all_e.append(e_list)
        #   wait for all processes to wrap-up before continuing
        for sim in processes:
            sim.join()
        pbar.update(batch_size)
        sims_to_run -= batch_size 
    pbar.close()
    return sols, all_sols, all_e
