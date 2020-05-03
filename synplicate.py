
import tensorflow as tf
from synthesizer.max_sharp_sat import mmc_synthesizer
import importlib


# Read arguments
threshold = True
num_of_samples = 4
# synthesis_config_path = "examples/california_census_simplified/config.mmc"
synthesis_benchmark_path = "examples/california_census_simplified/"
model_path = "examples/california_census_simplified/model"
model = tf.keras.models.load_model(model_path) # load model 


# main loop 
while threshold:
    # Sampler:
    # import sampler
    sampler = importlib.import_module(f".sampler",synthesis_benchmark_path.replace("/",".").rstrip('.'))
    # Input: model: model of a deep neural network.
    #        num_of_samples: sampling rate
    # Output: samples: Map {tuple of ordered inputs -> tuple of ordered lables}
    print(f"Sampling {num_of_samples} new samples ...")
    samples = sampler.sample(model,num_of_samples)

    # Bucket check
    # TODO

    # Synthesizer
    program_path, dot_path = mmc_synthesizer.synthesize(synthesis_benchmark_path,samples)
    print(f"Synthesized program: {program_path}\nVisualization: {dot_path}")

    # Evaluator

    break

print("Synthesis complete!")


    