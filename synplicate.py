import tensorflow as tf
from synthesizer.max_sharp_sat import mmc_synthesizer
from evaluator.recall_evaluator import evaluator
import importlib
import timeit
import os


def dump_samples(samples,path,file_name):

    os.system(f"mkdir -p {path}samples/")
    samples_file = open(f"{path}samples/{file_name}.csv","w")

    inputs = list(samples.keys())[0]
    outputs = list(samples.values())[0]
    for name, val in inputs:
        samples_file.write(f"{name},")
    for name, val in outputs:
        samples_file.write(f"{name},")

    size = samples_file.tell()               # the size...
    samples_file.truncate(size-1) 

    samples_file.write("\n")
    
    for inputs, outputs in samples.items():
        for name, val in inputs:
            samples_file.write(f"{val},")
        for name, val in outputs:
            samples_file.write(f"{val},")
        size = samples_file.tell()               # the size...
        samples_file.truncate(size-1) 
        samples_file.write("\n")

    



    samples_file.close()


# Read arguments
num_of_samples = 20
# synthesis_config_path = "examples/california_census_simplified/config.mmc"
# synthesis_benchmark_path = "examples/california_census_simplified/"
# model_path = "examples/california_census_simplified/model"

synthesis_benchmark_path = "examples/loan_acquisition/"

# Sampler:
# import sampler
sampler = importlib.import_module(f".sampler",synthesis_benchmark_path.replace("/",".").rstrip('.'))
samples = {}
iteration = 0
threshold = 0.5

# Initial set of samples (S0 in paper)
# Input: model: model of a deep neural network.
#        num_of_samples: size of initial set of samples
# Output: samples: Map {tuple of ordered inputs -> tuple of ordered lables}
print(f"Sampling initial {num_of_samples} samples ...")
# random samples
samples.update(sampler.sample(num_of_samples))

# representative samples 
# samples.update(sampler.representative_sample())





# main loop
done = False
global_synthesis_time = 0
global_evaluation_time = 0
while not done and iteration<10: 

    newsamples = {}
    synthesis_time = 0
    evluation_time = 0

    # dump input samples
    dump_samples(samples,synthesis_benchmark_path,f"samples_{iteration}")

    # Synthesizer
    start = timeit.default_timer()
    program_path, dot_path = mmc_synthesizer.synthesize(synthesis_benchmark_path,samples,iteration)
    print(f"Synthesized program: {program_path}\nVisualization: {dot_path}")
    stop = timeit.default_timer()
    synthesis_time = stop-start
    print(f"Synthesis time:{synthesis_time}")

    # Evaluator
    start = timeit.default_timer()
    print("Evaluating program against model...")
    done, test_samples = evaluator.evaluate(sampler,program_path,samples)
    dump_samples(test_samples,synthesis_benchmark_path,f"test_samples_{iteration}")

    if not done :
        print("Refining sample set...")
        newsamples = evaluator.refine(sampler,program_path,samples)
        if len(newsamples.items())==0:
            done = True
        # print(samples)
        # print(newsamples)
        # dump new input samples
        samples.update(newsamples)
        dump_samples(newsamples,synthesis_benchmark_path,f"newsamples_{iteration}")

    
    stop = timeit.default_timer()
    evaluation_time = stop-start
    print(f"Evaluation time:{evaluation_time}")
    
    global_synthesis_time += synthesis_time
    global_evaluation_time += evaluation_time
    iteration +=1
    print(f"Size of sample set: {len(samples)}")
    print("--------------------------------------------------")
    # break

print("================================================")
print(f"Synthesis complete after {iteration} iterations!")
print(f"Time: {global_evaluation_time+global_synthesis_time}")


    