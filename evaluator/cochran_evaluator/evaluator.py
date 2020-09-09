import importlib
import itertools
import random



def evaluate(sampler,program_path,samples,delta, epsilon, refinement_size):

   misclassification_rate = 1.0
   refinement = {}

   return refinement, misclassification_rate