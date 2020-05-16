import numpy as np
import pandas as pd
# import tensorflow as tf 

import random
import math


def truncate(number, digits) -> float:
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper

def sample(model,num_of_samples):

    samples = {}

    # create 100 (features, Label) samples
    feature1_name = 'age'
    feature2_name = 'monthly_income'


    print("----------------------")
    for i in range(num_of_samples):

        feature1_value = random.randint(18,30)
        print(feature1_name, ": ", feature1_value,end =" | ")

        feature2_value = truncate(abs(random.uniform(10000,4000)),2)
        print(feature2_name, ": ", feature2_value,end =" | ")

        prediction = model.predict({feature1_name: np.array([feature1_value]), 
                                    feature2_name: np.array([feature2_value])})
        print(prediction)
        print("----------------------")

        samples[(feature1_name,feature1_value),(feature2_name,feature2_value)] = [("approved",prediction[0][0])]

    return samples
