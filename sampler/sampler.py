import numpy as np
import pandas as pd
import tensorflow as tf 

import random
import math


def truncate(number, digits) -> float:
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper

def sample(model,num_of_samples):

    samples = {}

    # test_df = pd.read_csv("https://download.mlcc.google.com/mledu-datasets/california_housing_test.csv")
    # # Calculate the Z-scores of each column in the test set.
    # test_df_mean = test_df.mean()
    # test_df_std = test_df.std()
    # test_df_norm = (test_df - test_df_mean)/test_df_std
    # label_name = "median_house_value"
    # test_features = {name:np.array(value) for name, value in test_df_norm.items()}
    # test_label = np.array(test_features.pop(label_name)) # isolate the label

    # Normalization factors
    train_df = pd.read_csv("https://download.mlcc.google.com/mledu-datasets/california_housing_train.csv")
    train_df_mean = train_df.mean()
    train_df_std = train_df.std()

    # print(train_df_mean)
    # print(train_df_std)

    # create 100 (features, Label) samples
    feature1_name = 'longitude'
    feature2_name = 'latitude'
    feature3_name = 'population'
    feature4_name = 'median_income'

    print("----------------------")
    for i in range(num_of_samples):
        print("Sample", i,end =": ")
        # Feature 1
        feature1_value = random.uniform(-124.3,-114.3)
        print(feature1_name, ": ", feature1_value,end =" | ")
        feature1_value_norm = truncate((feature1_value - train_df_mean[feature1_name])/train_df_std[feature1_name],2)
        print(feature1_name, "_norm: ", feature1_value_norm,end =" | ")

        # Feature 2
        feature2_value = random.uniform(32.5,42.5)
        print(feature2_name, ": ", feature2_value,end =" | ")
        feature2_value_norm = truncate((feature2_value - train_df_mean[feature2_name])/train_df_std[feature2_name],2)
        print(feature2_name, "_norm: ", feature2_value_norm,end =" | ")

        # Feature 3
        feature3_value = random.uniform(3.0,35682.0)
        print(feature3_name, ": ", feature3_value,end =" | ")
        feature3_value_norm = truncate((feature3_value - train_df_mean[feature3_name])/train_df_std[feature3_name],2)
        print(feature3_name, "_norm: ", feature3_value_norm,end =" | ")

        # Feature 4
        feature4_value = random.uniform(0.5,15.0)
        print(feature4_name, ": ", feature4_value, end =" | ")
        feature4_value_norm = truncate((feature4_value - train_df_mean[feature4_name])/train_df_std[feature4_name],2)
        print(feature4_name, "_norm: ", feature4_value_norm, end =" =>  ")

        prediction = model.predict({feature1_name: np.array([feature1_value_norm]), 
                                feature2_name: np.array([feature2_value_norm]), 
                                feature3_name:np.array([feature3_value_norm]),
                                feature4_name:np.array([feature4_value_norm])})


        print(prediction)
        print("----------------------")
        # label = True
        # if (prediction[0][0])> 0: 
        #     label = True 
        # else:
        #     label = False
        samples[(feature1_name,feature1_value),(feature2_name,feature2_value),(feature3_name,feature3_value),(feature4_name,feature4_value)] = [("median_house_price",prediction)]
    
    return samples



############## testing #############
# Load model 
# path = "../examples/california_census_simplified/model"
# model = tf.keras.models.load_model(path)

# sample(model,10)

