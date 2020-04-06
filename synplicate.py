
import tensorflow as tf
from sampler import sampler
from synthesizer.max_sharp_sat import mmc_synthesizer


# Read arguments
threshold = True
num_of_samples = 6
synthesis_config_path = "examples/california_census_simplified/config.mmc"
model_path = "examples/california_census_simplified/model"
output_path = "examples/california_census_simplified/mmc_encoding/"
model = tf.keras.models.load_model(model_path) # load model 


# main loop 
while threshold:
    # Sampler:
    # Input: model: model of a deep neural network.
    #        num_of_samples: sampling rate
    # Output: samples: Map {tuple of ordered inputs -> tuple of ordered lables}
    print(f"Sampling {num_of_samples} new samples ...")
    samples = sampler.sample(model,num_of_samples)

    # Bucket check
    # TODO

    # Synthesizer
    print("Extracting synthesis configuration... ") 
    config = mmc_synthesizer.config(synthesis_config_path) 
    print(f"Synthesizing program with {config[0]:d} states, features {config[1]}, and labels {config[2]} ...")
    program_path = mmc_synthesizer.synthesize(output_path,samples,config)

    # Evaluator

    break

print("Synthesis complete!")


    