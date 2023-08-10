import multiprocessing as mp
from tqdm import tqdm

def run_in_batch(func,p,c,Edges,devs):
    sols      = []
    all_sols  = []
    all_e     = []

    #   not to the best way to parallelize since
    #   batches are sequential, that is, even if an open
    #   core is available, it wont run till the slowest
    #   process finishes. good enough for now though.
    sims_to_run = c["total_iters"]
    batch_size = c["batch_size"]
    #pbar = tqdm(total=sims_to_run,ncols=80)
    while sims_to_run >= 1:        
        if sims_to_run < batch_size:
            batch_size = sims_to_run
        sol_queue      = mp.Queue()  # parallel-safe queue
        all_e_queue    = mp.Queue()  # parallel-safe queue
        all_sols_queue = mp.Queue()  # parallel-safe queue
        processes = []
        #   create processes and start them
        for _ in range(batch_size):
            sim = mp.Process(target=func, args=(p,c,Edges,devs,sol_queue,all_sols_queue,all_e_queue))
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
        #pbar.update(batch_size)
        sims_to_run -= batch_size 
        for sim in processes:
            sim.close()
        del sol_queue
        del all_e_queue
        del all_sols_queue
    #pbar.close()
    #del pbar
    return sols, all_sols, all_e


def run_serial(func,p,c,Edges,devs):
    sims_to_run = c["total_iters"]
    batch_size = c["batch_size"]
    while sims_to_run >= 1:
        func(p,c,Edges,devs,[],[],[],0)
        sims_to_run-=1
    sols      = [1,2,3,4,5,6,7,8,9,10]
    all_sols  = [[1,2,3,4,5,6,7,8,9,10] for i in  range(10)]
    all_e  = [[1,2,3,4,5,6,7,8,9,10] for i in  range(10)]
    return sols,all_sols,all_e

