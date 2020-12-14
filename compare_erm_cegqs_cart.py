import os
import importlib
import sys
sys.path.append('../../')
sys.path.append('../')

#import procedures
from methods.erm import erm_procedure as erm
from methods.cegqs import cegqs_procedure as cegqs

# import synthesizers
from synthesizer.max_sharp_sat import mmc_synthesizer
from synthesizer.max_sat import ms_synthesizer
from synthesizer.omt import omt_synthesizer
from synthesizer.decision_trees import cart_tree_synthesizer


from evaluator.recall_evaluator import evaluator
from evaluator.cochran_evaluator import evaluator as cochran

import timeit



def experiment(dd_size, delta, epsilon, dir_name,depth):

    synthesis_benchmark_path = f"experiments/california_census/"
    test = synthesis_benchmark_path.replace("/",".").rstrip('.')

    erm_synthesis_time = 0
    erm_mmc_synthesis_time = 0
    cegqs_synthesis_time = 0
    cegqs_mmc_synthesis_time = 0
    dt_depth_synthesis_time = 0
    dt_unbounded_synthesis_time = 0

    
 

    # Execute ERM
    # importlib.import_module(f".feature_defs", test)

    start = timeit.default_timer()
    erm_mmc_samples, erm_mmc_program_path = erm.execute(synthesis_benchmark_path,mmc_synthesizer,delta,epsilon,"mmc")
    stop = timeit.default_timer()
    erm_mmc_synthesis_time = stop-start
    
    start = timeit.default_timer()
    erm_samples, erm_program_path = erm.execute(synthesis_benchmark_path,ms_synthesizer,delta,epsilon,"ms")
    stop = timeit.default_timer()
    erm_synthesis_time = stop-start

    

    # Execute CART with ERM syn_sample_set
    start = timeit.default_timer()
    dt_depth = cart_tree_synthesizer.synthesize(f"{synthesis_benchmark_path}samples/erm_syn_samples.csv",["0","1","2","3"], synthesis_benchmark_path,depth,"depth")
    stop = timeit.default_timer()
    dt_depth_synthesis_time = stop-start

    start = timeit.default_timer()
    dt_unbounded = cart_tree_synthesizer.synthesize(f"{synthesis_benchmark_path}samples/erm_syn_samples.csv",["0","1","2","3"], synthesis_benchmark_path,-1,"unbounded")
    stop = timeit.default_timer()
    dt_unbounded_synthesis_time = stop-start

    # Execute CeGQS

    start = timeit.default_timer()
    cegqs_mmc_program_path, cegqs_best_mmc  = cegqs.execute(synthesis_benchmark_path,mmc_synthesizer, delta, epsilon, 10, 5, 0.01, 5, "ttf", 10,"mmc")
    stop = timeit.default_timer()
    cegqs_mmc_synthesis_time = stop-start

    start = timeit.default_timer()
    cegqs_program_path, cegqs_best_ms  = cegqs.execute(synthesis_benchmark_path,ms_synthesizer, delta, epsilon, 10, 5, 0.01, 5, "ttf", 10,"ms")
    stop = timeit.default_timer()
    cegqs_synthesis_time = stop-start

    


    print("----------------------------")
    print("Creating evaluation set...")
    sampler = importlib.import_module(f".sampler",synthesis_benchmark_path.replace("/",".").rstrip('.'))

    erm_rate, erm_mmc_rate, cegqs_rate, cegqs_mmc_rate  = cochran.just_evaluate(sampler,synthesis_benchmark_path,erm_program_path, erm_mmc_program_path, cegqs_program_path, cegqs_mmc_program_path,delta, epsilon, "dt_samples")

    dt_depth_rate = cart_tree_synthesizer.evaluate(f"{synthesis_benchmark_path}samples/dt_samples.csv",dt_depth)

    dt_unbounded_rate = cart_tree_synthesizer.evaluate(f"{synthesis_benchmark_path}samples/dt_samples.csv",dt_unbounded)
    
    
    print("****************************************************")
    print(f"ERM ms rate: {erm_rate}. Time: {erm_synthesis_time}. Size: {depth}")
    print(f"ERM mmc rate: {erm_mmc_rate}. Time: {erm_mmc_synthesis_time}. Size: {depth}")
    print(f"CeGQS rate: {cegqs_rate}. Time: {cegqs_synthesis_time}. Size {depth}. Best: {cegqs_best_ms}" )
    print(f"CeGQS mmc rate: {cegqs_mmc_rate}. Time: {cegqs_mmc_synthesis_time}. Size {depth}. Best: {cegqs_best_mmc}")
    print(f"dt depth rate: {dt_depth_rate}. Time: {dt_depth_synthesis_time}. Depth: {depth}. Size: {dt_depth.get_n_leaves()}")
    print(f"dt unbounded rate: {dt_unbounded_rate}. Time: {dt_unbounded_synthesis_time}. Depth: {dt_unbounded.get_depth()}. Size: {dt_unbounded.get_n_leaves()}")
    print("****************************************************")







dd_size = 3
delta = 0.05
epsilon = 0.01
benchmark_name = "la"
synthesizer = ms_synthesizer
dir_name = f"{benchmark_name}_{dd_size}_{delta}_{epsilon}"

experiment(dd_size,delta,epsilon,dir_name,dd_size)