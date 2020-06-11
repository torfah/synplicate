import numpy as np
import pandas as pd
import tensorflow as tf 

import random
from random import choice
import math

model_path = "examples/hypothyroid/model"
model = tf.keras.models.load_model(model_path) # load model 


def truncate(number, digits) -> float:
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper

def representative_sample():
     
    samples = {}

    # create 100 (features, Label) samples
    feature1_name = 'age'
    feature2_name = 'TSH'


    print("----------------------")
    for i in [18,25,30,35,40,55,60,65,70,75,80]:
        for j in [2000.0,2500.0,3000.0,5000.0,6000.0,7000.0,8000.0,10000.0]:

            feature1_value = i
            print(feature1_name, ": ", feature1_value,end =" | ")

            feature2_value = j
            print(feature2_name, ": ", feature2_value,end =" | ")

            prediction = model.predict({feature1_name: np.array([feature1_value]), 
                                        feature2_name: np.array([feature2_value])})
            print(prediction)
            

            prediction_value = 1
            if prediction[0][0] > prediction[0][1]:
                prediction_value = 0
            print(prediction_value)
            print("----------------------")
        
            samples[(feature1_name,feature1_value),(feature2_name,feature2_value)] = [("H1",prediction_value)]


    return samples

def uniform(num_of_samples):

    samples = {}

    # create 100 (features, Label) samples
    feature1_name = 'age'
    feature2_name = 'TSH'


    # print("----------------------")
    for i in range(num_of_samples):

        feature1_value = random.choice([random.randint(10,90)])
        feature1_value = feature1_value/100.0
        # print(feature1_name, ": ", feature1_value,end =" | ")

        feature2_value = random.choice([truncate(abs(random.uniform(5,2)),2),truncate(abs(random.uniform(5,2)),2),truncate(abs(random.uniform(5,2)),2),truncate(abs(random.uniform(20,10)),2),truncate(abs(random.uniform(100,5)),2)])
        # print(feature2_name, ": ", feature2_value,end =" | ")

        prediction = model.predict({feature1_name: np.array([feature1_value]), 
                                    feature2_name: np.array([feature2_value])})
        # print(prediction)
        

        prediction_value = prediction[0][0]
        c = 0
        for i in range(3):
            if prediction[0][i] > prediction_value:
                prediction_value = prediction[0][i]
                c = i

        # print(prediction_value)
        # print("----------------------")
        
        samples[(feature1_name,feature1_value),(feature2_name,feature2_value)] = [("Class",c)]


    return samples

def sample(num_of_samples):

    samples = {}

    # create 100 (features, Label) samples
    feature1_name = 'age'
    feature2_name = 'TSH'


    print("----------------------")
    for i in range(num_of_samples):

        feature1_value = random.choice([random.randint(10,100)])
        print(feature1_name, ": ", feature1_value,end =" | ")

        feature2_value = random.choice([truncate(abs(random.uniform(5,2)),2),truncate(abs(random.uniform(5,2)),2),truncate(abs(random.uniform(5,2)),2),truncate(abs(random.uniform(20,9)),2),truncate(abs(random.uniform(100,10)),2)])
        # feature2_value = feature2_value/10.0
        print(feature2_name, ": ", feature2_value,end =" | ")

        prediction = model.predict({feature1_name: np.array([feature1_value]), 
                                    feature2_name: np.array([feature2_value])})
        print(prediction)
        

        prediction_value = prediction[0][0]
        c = 0
        for i in range(3):
            if prediction[0][i] > prediction_value:
                prediction_value = prediction[0][i]
                c = i
        print(prediction_value)
        print("----------------------")
        
        samples[(feature1_name,feature1_value),(feature2_name,feature2_value)] = [("Class",c)]


    return samples


def predict(inputs):

    feature1_name = 'age'
    feature2_name = 'TSH'

    prediction = model.predict({feature1_name: np.array([inputs[0]]), 
                                    feature2_name: np.array([inputs[1]])})

    prediction_value = prediction[0][0]
    c = 0
    for i in range(3):
        if prediction[0][i] > prediction_value:
            prediction_value = prediction[0][i]
            c = i

    return [("Class",c)]
