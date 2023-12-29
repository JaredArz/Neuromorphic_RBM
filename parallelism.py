import multiprocessing as mp
from tqdm import tqdm

def run(func,p,c,Edges,devs,parallel_flag):
    sols      = []
    all_sols  = []
    all_e     = []

    #   not to the best way to parallelize since
    #   batches are sequential, that is, even if an open
    #   core is available, it wont run till the slowest
    #   process finishes. good enough for now though.
    sims_to_run = c["total_iters"]
    if not parallel_flag:
        # overwrite batchsize if serial
        batch_size  = 1
    else:
        batch_size  = c["batch_size"]
    while sims_to_run  >= 1:
        if sims_to_run < batch_size:
            batch_size = sims_to_run
        sol_queue      = mp.Queue()  # parallel-safe queue
        all_e_queue    = mp.Queue()  # parallel-safe queue
        all_sols_queue = mp.Queue()  # parallel-safe queue
        processes = []

        #   create processes and start them
        for _ in range(batch_size):
            if parallel_flag:
                sim = mp.Process(target=func, args=(p,c,Edges,devs,sol_queue,all_sols_queue,all_e_queue))
                processes.append(sim)
                sim.start()
            else:
                func(p,c,Edges,devs,sol_queue,all_sols_queue,all_e_queue)

        #   waits for solution to be available
        num_procs = len(processes)
        while True:
            sol = sol_queue.get()  #will block
            sol_list = all_sols_queue.get()  #will block
            e_list = all_e_queue.get()  #will block
            sols.append(sol)
            all_sols.append(sol_list)
            all_e.append(e_list)
            num_procs -= 1
            if num_procs <= 0:
                break

        #   wait for all processes to wrap-up before continuing
        #   skips if serial, None in processes
        for sim in processes:
            sim.join()

        for sim in processes:
            sim.close()

        del sol_queue
        del all_e_queue
        del all_sols_queue
        sims_to_run -= batch_size

    return sols, all_sols, all_e
