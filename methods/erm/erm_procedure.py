import importlib
import math

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
    
    synthesis_time = 0
    upper_bound = 50
    lower_bound = 0
    precision = 7

    # dump input samples
    logger.dump_samples(samples,benchmark_path,f"erm_syn_samples")

    start = timeit.default_timer()
    program_path, dot_path, count = synthesizer.synthesize(benchmark_path,samples,lower_bound,upper_bound,precision,f"{name}_erm")
    print(f"Synthesized program: {program_path}\nVisualization: {dot_path}")
    stop = timeit.default_timer()
    synthesis_time = stop-start
    print(f"Synthesis time:{synthesis_time}")

    if count>0:
        print(f"Accuracy:{count/num_of_samples}")

    return samples, program_path
        