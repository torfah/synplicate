import importlib
import math
import os

# utils
from utils import logger
import timeit



def execute(benchmark_path, synthesizer, delta, epsilon,name,samples={}):
    print("Executing ERM procedure...")
    # determine number of samples based on the values of delta and epsilon 
    synthesizer.initialize(benchmark_path)

    # =================================================================================================
    # Sampler:
    # =================================================================================================
    # import sampler
    sampler = importlib.import_module(f".sampler",benchmark_path.replace("/",".").rstrip('.'))

    # Compute number of samples according to emprirical risk minimization 
    class_size = synthesizer.compute_class_size()
    num_of_samples = math.ceil(math.log((1+class_size)/delta)/epsilon)
    print(f"Using {num_of_samples} samples ...")
    
    if samples == {}:
        samples.update(sampler.uniform(num_of_samples))

    # =================================================================================================
    # =================================================================================================


    # =================================================================================================
    # Synthesizer:
    # =================================================================================================
    # Execute synthesizer

    
    

    # dump input samples
    logger.dump_samples(samples,benchmark_path,f"erm_syn_samples")

    # initialize
    os.system(f"rm -r {benchmark_path}program")
    Gamma = []
    W = [(0,100,0)]

    while W != []:
        expl_lower_bound, expl_upper_bound, corr_bound = W.pop(0)
        synthesis_time = 0
        precision = 7
        
        # Explore in current_region
        start = timeit.default_timer()
        print("=================================")
        print(f" Exploring solution in region [{expl_lower_bound},{expl_upper_bound},{corr_bound}]")
        print("=================================")
        program_path, dot_path, corr, explainability = synthesizer.synthesize(benchmark_path,samples,expl_lower_bound,expl_upper_bound,precision,f"{name}_{expl_lower_bound}_{expl_upper_bound}_{corr_bound}_erm")
        print(f"Synthesized program: {program_path}\nVisualization: {dot_path}")
        stop = timeit.default_timer()
        synthesis_time = stop-start
        print(f"Synthesis time:{synthesis_time}")

        if corr>0 and explainability>0:
            print(f"Accuracy:{corr}")
            print(f"Explainabilty: {explainability}")

            if corr> corr_bound:
                Gamma.append((program_path,corr,explainability))
                print(f"Adding region ({expl_lower_bound},{int(explainability*100)},{corr})")
                W.append((expl_lower_bound,int(explainability*100),corr))
                print(f"Adding region ({int(explainability*100)},{expl_upper_bound},{corr_bound})")
                W.append((int(explainability*100),expl_upper_bound,corr_bound))
            else:
                print(f"Not Pareto-optimal. Adding only region ({expl_lower_bound},{int(explainability*100)},{corr_bound})")
                W.append((expl_lower_bound,int(explainability*100),corr_bound))
        
        print("=================================")
        
        

    return samples, Gamma
        