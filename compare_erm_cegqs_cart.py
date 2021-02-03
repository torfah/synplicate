import os
import importlib
import sys
sys.path.append('../../')
sys.path.append('../')
from subprocess import STDOUT, PIPE, run

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


def experiment(dd_size, delta, epsilon, dir_name,depth,num_eva):

    synthesis_benchmark_path = f"experiments/ICML/loan_acquisition/"
    test = synthesis_benchmark_path.replace("/",".").rstrip('.')

    ################################################################################################################
    #                                    GLOBAL PERFORMANCE-PARAMETER VARIABLES                                    #
    ################################################################################################################
    
    #TIME
    erm_synthesis_time = 0
    erm_mmc_synthesis_time = 0
    
    cart_depth_synthesis_time = 0
    cart_unbounded_synthesis_time = 0
    
    inferdt_synthesis_time = 0
    inferdt_depth_synthesis_time = 0
    binoct_synthesis_time = 0
   
    cegqs_synthesis_time = 0
    cegqs_mmc_synthesis_time = 0
    

    ################################################################################################################
    #                         SYNTHESIZE USING SYNPLICATE-ERM, CART, INFERDT, AND BINOCT                           #
    ################################################################################################################

    # SYNTHESIZE USING SYNPLICTAE AND USE PRODUCED SAMPLES FOR INFERDT AND BINOCT
    print("Executing Synplicate's erm procedure ...")
    # USING MS
    start = timeit.default_timer()
    erm_samples, erm_program_path = erm.execute(synthesis_benchmark_path,ms_synthesizer,delta,epsilon,"ms")
    stop = timeit.default_timer()
    erm_synthesis_time = stop-start

    # # USING MMC
    # start = timeit.default_timer()
    # erm_mmc_samples, erm_mmc_program_path = erm.execute(synthesis_benchmark_path,mmc_synthesizer,delta,epsilon,"mmc")
    # stop = timeit.default_timer()
    # erm_mmc_synthesis_time = stop-start

    samples_file = f"{synthesis_benchmark_path}samples/erm_syn_samples.csv"
    
    # USING SKLEARN CART
    print("Executing CART unbounded depth ...")
    ## UNBOUNDED DEPTH 
    start = timeit.default_timer()
    cart_unbounded_tree = cart_tree_synthesizer.synthesize(samples_file,["0","1","2","3"], synthesis_benchmark_path,-1,"unbounded")
    cart_unbounded_depth = cart_unbounded_tree.get_depth()
    cart_unbounded_nodes = cart_unbounded_tree.get_n_leaves()
    stop = timeit.default_timer()
    cart_unbounded_synthesis_time = stop-start

    ## BOUNDED DEPTH 
    print("Executing CART bounded depth ...")
    start = timeit.default_timer()
    cart_depth_tree = cart_tree_synthesizer.synthesize(samples_file,["0","1","2","3"], synthesis_benchmark_path,depth,"depth")
    cart_bounded_depth = cart_depth_tree.get_depth()
    cart_bounded_nodes = cart_depth_tree.get_n_leaves()
    stop = timeit.default_timer()
    cart_depth_synthesis_time = stop-start

    # USING INFERDT
    ## AUX
    def parse_inferdt(tree_text,out_file_path):
        program = open(out_file_path,"w")
        tokens  = (tree_text.stdout).split("\n")

        indent = "   "
        program.write("def execute(in_map):\n")
        depth = 0
        nodes = 0
        for token in tokens:
            if "Depth:" in token:
                temp = token.split(":")
                depth = int(temp[1])
            if "Number of nodes:" in token:
                temp = token.split(":")
                nodes = int(temp[1])
            if ">" in token:
                tabs = token.count("|")+1
                temp = token.replace("|","").strip().split(">")
                if not "!" in token:
                    if ":" in temp[1]:
                        tempp = temp[1].split(":")
                        program.write(f"{indent*tabs}if in_map['{temp[0]}']>{tempp[0]}:\n{indent*(tabs+1)}return {tempp[1]}\n")
                    else:    
                        program.write(f"{indent*tabs}if in_map['{temp[0]}']>{temp[1]}:\n")
                else:
                    temp = token.replace("!","").replace("|","").strip().split(">")
                    if ":" in temp[1]:
                        tempp = temp[1].split(":")
                        program.write(f"{indent*tabs}else:\n{indent*(tabs+1)}return {tempp[1]}\n")
                    else:    
                        program.write(f"{indent*tabs}else:\n")

    
        program.close()
        return depth, nodes, out_file_path

    os.system(f"mkdir {synthesis_benchmark_path}inferdt")
    ## OPTIMAL DEPTH AND SIZE
    print("Executing InferDT depth + size ...")
    start = timeit.default_timer()
    inferdt_depth_size_tree = run(f"./synthesizer/InferDT/InferDT {samples_file} -v -x infer", stdout=PIPE, stderr=STDOUT, universal_newlines=True, shell=True, timeout=300)
    inferdt_depth_size_depth, inferdt_depth_size_nodes, inferdt_depth_size_path = parse_inferdt(inferdt_depth_size_tree,f"{synthesis_benchmark_path}inferdt/dt_d_s.py")
    inferdt_synthesis_time = stop-start

    print(inferdt_depth_size_depth,inferdt_depth_size_nodes)

    ## OPTIMAL DEPTH
    print("Executing InferDT depth ...")
    start = timeit.default_timer()
    inferdt_depth_tree = run(f"./synthesizer/InferDT/InferDT {samples_file} -d -v -x infer", stdout=PIPE, stderr=STDOUT, universal_newlines=True, shell=True, timeout=300)
    inferdt_depth_depth, inferdt_depth_nodes, inferdt_depth_path = parse_inferdt(inferdt_depth_size_tree,f"{synthesis_benchmark_path}inferdt/dt_d.py")
    inferdt_depth_synthesis_time = stop-start
    print(inferdt_depth_depth,inferdt_depth_nodes)


    # USING BINOCT
    # AUX
    def parse_binoct(tree_text,out_file_path):
        program = open(out_file_path,"w")
        tokens  = (tree_text.stdout).split("\n")

        
        program.write("def execute(in_map):\n")
        nodes = 0
        for token in tokens:
            if "if" in token:
                temp = token.replace("{",":").split(" <= ")
                tempp = temp[0].split("( ")
                program.write("\n   ")
                program.write(f"{tempp[0]} ( in_map['{tempp[1]}'] <= {temp[1]}")
                nodes += 1
            if "examples" in token:
                temp = token.split("return")
                tempp = temp[1].split()
                program.write("\n   ")
                program.write(f"{temp[0]} return {tempp[0]}")
                nodes += 1
            if "else" in token:
                temp = token.replace("{",":")
                program.write("\n   ")
                program.write(temp)
            

        program.close()
        return nodes, out_file_path

    os.system(f"mkdir {synthesis_benchmark_path}binoct")
    # USES DEPTH FORM INFERDT DEPTH
    print("Executing BinOct with maxdepth from InferDT ...")
    binoct_tree = run(f"python3 ./synthesizer/binoct/run_exp.py {samples_file} {inferdt_depth_depth}",stdout=PIPE, stderr=STDOUT, universal_newlines=True, shell=True, timeout=300)
    print(binoct_tree.stdout)
    binoct_nodes, binoct_path = parse_binoct(binoct_tree,f"{synthesis_benchmark_path}binoct/dt.py")
    print("Number of nodes for binoct tree: ",binoct_nodes)


    ################################################################################################################
    #                                       SYNTHESIZE USING SYNPLICATE-CEGS                                       #
    ################################################################################################################
    
    # USING MMC
    start = timeit.default_timer()
    cegqs_mmc_program_path, cegqs_best_mmc  = cegqs.execute(synthesis_benchmark_path,mmc_synthesizer, delta, epsilon, 10, 5, 0.01, 5, "ttf", 10,"mmc")
    stop = timeit.default_timer()
    cegqs_mmc_synthesis_time = stop-start

    # USING MS
    start = timeit.default_timer()
    cegqs_program_path, cegqs_best_ms  = cegqs.execute(synthesis_benchmark_path,ms_synthesizer, delta, epsilon, 10, 5, 0.01, 5, "ttf", 10,"ms")
    stop = timeit.default_timer()
    cegqs_synthesis_time = stop-start


    ################################################################################################################

    ################################################################################################################
    #                                                   EVALUATION                                                 #
    ################################################################################################################

    # CREATE EVALUATION SETS 

    
    


    # print("----------------------------")
    # print("Creating evaluation set...")
    # sampler = importlib.import_module(f".sampler",synthesis_benchmark_path.replace("/",".").rstrip('.'))

    # erm_rate, erm_mmc_rate, cegqs_rate, cegqs_mmc_rate  = cochran.just_evaluate(sampler,synthesis_benchmark_path,erm_program_path, erm_mmc_program_path, cegqs_program_path, cegqs_mmc_program_path,delta, epsilon, "dt_samples")

    # dt_depth_rate = cart_tree_synthesizer.evaluate(f"{synthesis_benchmark_path}samples/dt_samples.csv",dt_depth)

    # dt_unbounded_rate = cart_tree_synthesizer.evaluate(f"{synthesis_benchmark_path}samples/dt_samples.csv",dt_unbounded)
    
    
    # print("****************************************************")
    # print(f"ERM ms rate: {erm_rate}. Time: {erm_synthesis_time}. Size: {depth}")
    # print(f"ERM mmc rate: {erm_mmc_rate}. Time: {erm_mmc_synthesis_time}. Size: {depth}")
    # print(f"CeGQS rate: {cegqs_rate}. Time: {cegqs_synthesis_time}. Size {depth}. Best: {cegqs_best_ms}" )
    # print(f"CeGQS mmc rate: {cegqs_mmc_rate}. Time: {cegqs_mmc_synthesis_time}. Size {depth}. Best: {cegqs_best_mmc}")
    # print(f"dt depth rate: {dt_depth_rate}. Time: {dt_depth_synthesis_time}. Depth: {depth}. Size: {dt_depth.get_n_leaves()}")
    # print(f"dt unbounded rate: {dt_unbounded_rate}. Time: {dt_unbounded_synthesis_time}. Depth: {dt_unbounded.get_depth()}. Size: {dt_unbounded.get_n_leaves()}")
    # print("****************************************************")







dd_size = 1
delta = 0.05
epsilon = 0.05
benchmark_name = "la"
synthesizer = ms_synthesizer
dir_name = f"{benchmark_name}_{dd_size}_{delta}_{epsilon}"
num_eva = 5

experiment(dd_size,delta,epsilon,dir_name,dd_size,num_eva)