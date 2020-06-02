import tensorflow as tf
from synthesizer.max_sharp_sat import mmc_synthesizer
from evaluator.recall_evaluator import evaluator
import importlib


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
samples.update(sampler.sample(num_of_samples))


# main loop
done = False
while not done: 

    newsamples = {}
    # Synthesizer
    program_path, dot_path = mmc_synthesizer.synthesize(synthesis_benchmark_path,samples,iteration)
    print(f"Synthesized program: {program_path}\nVisualization: {dot_path}")

    # Evaluator
    print("Evaluating program against model...")
    done = evaluator.evaluate(sampler,program_path,samples)

    if not done :
        print("Refining sample set...")
        newsamples = evaluator.refine(sampler,program_path,samples)
        if len(newsamples.items())==0:
            done = True
        # print(samples)
        # print(newsamples)
        samples.update(newsamples)
   
    iteration +=1
    print(f"{len(samples)}")
    # break

print(f"Synthesis complete after {iteration} iterations!")


    