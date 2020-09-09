import importlib
import math

# import synthesizers
from synthesizer.max_sharp_sat import mmc_synthesizer
from synthesizer.max_sat import ms_synthesizer
from synthesizer.omt import omt_synthesizer

# import evaluators
from evaluator.recall_evaluator import evaluator as recall
from evaluator.cochran_evaluator import evaluator as cochran 

# import utils
from utils import logger
import timeit


def execute(benchmark_path, synthesizer, delta, epsilon, init_num_of_samples, step_bound, termination_threshold, stability_factor, terminiation_condition, refinement_size):
    print("Executing CeGQS procedure...")
    # Determine number of samples based on the values of delta and epsilon 
    synthesizer.initialize(benchmark_path)
    
    # Compute termination map 
    termination_map = {}
    termination_map["ttt"] = lambda steps, rate, stability_count: steps >= step_bound or rate <= termination_threshold  or stability_count >= stability_factor
    termination_map["ftt"] = lambda steps, rate, stability_count: rate <= termination_threshold  or stability_count >= stability_factor
    termination_map["tft"] = lambda steps, rate, stability_count: steps >= step_bound or stability_count >= stability_factor
    termination_map["ttf"] = lambda steps, rate, stability_count: steps >= step_bound or rate <= termination_threshold
    termination_map["fft"] = lambda steps, rate, stability_count: stability_count >= stability_factor
    termination_map["ftf"] = lambda steps, rate, stability_count: rate <= termination_threshold
    termination_map["tff"] = lambda steps, rate, stability_count: steps >= step_bound


    # =================================================================================================
    # Iniital samples: S0
    # =================================================================================================
    # import sampler
    sampler = importlib.import_module(f".sampler",benchmark_path.replace("/",".").rstrip('.'))
    samples = {}
    # Initial set of samples (S0 in paper)
    # Input: model: model of a deep neural network.
    #        num_of_samples: size of initial set of samples
    # Output: samples: Map {tuple of ordered inputs -> tuple of ordered lables}
    print(f"Sampling initial {init_num_of_samples} samples ...")
    # random samples
    samples.update(sampler.sample(init_num_of_samples))

    # =================================================================================================
    # =================================================================================================


    # =================================================================================================
    # CeGQS main loop: 
    # =================================================================================================
    
    # Utils
    global_synthesis_time = 0
    global_evaluation_time = 0
    
    # Output
    program_path = ""
    dot_path = ""
    count = 0
    steps = 0
    misclassification_rate = 1.0
    stability_count = 0
    num_of_samples = len(samples)


    # Termination condition
    terminate = termination_map[terminiation_condition]

    while not terminate(steps, misclassification_rate, stability_count):

        # Reset for iteration
        newsamples = {}
        synthesis_time = 0
        evaluation_time = 0

        # dump input samples
        logger.dump_samples(samples,benchmark_path,f"samples_{steps}")

        # Synthesize
        print("---------------------------------------------")
        start = timeit.default_timer()
        program_path, dot_path, count = synthesizer.synthesize(benchmark_path,samples,f"encoding_{steps}")
        print(f"Synthesized program: {program_path}\nVisualization: {dot_path}")
        stop = timeit.default_timer()
        synthesis_time = stop-start
        print(f"Synthesis time:{synthesis_time}")

        # Evaluate and refine
        start = timeit.default_timer()
        print("Evaluating program against model...")
        refinement, misclassification_rate = cochran.evaluate(sampler,program_path,samples,delta,epsilon, refinement_size)

        samples.update(refinement)
        num_of_samples = len(samples)
        logger.dump_samples(refinement,benchmark_path,f"newsamples_{steps}")

        stop = timeit.default_timer()
        evaluation_time = stop-start
        print(f"Evaluation time:{evaluation_time}")


        
        # Increment for next iteration 
        steps += 1
        global_synthesis_time += synthesis_time
        global_evaluation_time += evaluation_time

        print("---------------------------------------------")


        if count>0:
            print(f"Misclassification rate: {misclassification_rate}")
        
        print("*********************************************")
    

    print("================================================")
    print(f"Synthesis complete after {steps} refinement steps!")
    print(f"Total time: {global_evaluation_time+global_synthesis_time}")
    print("================================================")
    print("================================================")

    # =================================================================================================
    # =================================================================================================
    # =================================================================================================

