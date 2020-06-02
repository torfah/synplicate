import numpy as np
import pandas as pd
import tensorflow as tf 

import random
import math

model_path = "examples/loan_acquisition/model"
model = tf.keras.models.load_model(model_path) # load model 


def truncate(number, digits) -> float:
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper

def sample(num_of_samples):

    samples = {}

    # create 100 (features, Label) samples
    feature1_name = 'age'
    feature2_name = 'monthly_income'


    print("----------------------")
    for i in range(num_of_samples):

        feature1_value = random.randint(18,80)
        print(feature1_name, ": ", feature1_value,end =" | ")

        feature2_value = truncate(abs(random.uniform(10000,4000)),2)
        print(feature2_name, ": ", feature2_value,end =" | ")

        prediction = model.predict({feature1_name: np.array([feature1_value]), 
                                    feature2_name: np.array([feature2_value])})
        print(prediction)
        

        prediction_value = 1
        if prediction[0][0] > prediction[0][1]:
            prediction_value = 0
        print(prediction_value)
        print("----------------------")
        
        samples[(feature1_name,feature1_value),(feature2_name,feature2_value)] = [("approved",prediction_value)]


    return samples


def predict(inputs):

    feature1_name = 'age'
    feature2_name = 'monthly_income'

    prediction = model.predict({feature1_name: np.array([inputs[0]]), 
                                    feature2_name: np.array([inputs[1]])})

    prediction_value = 1
    if prediction[0][0] > prediction[0][1]:
        prediction_value = 0

    return [("approved",prediction_value)]
