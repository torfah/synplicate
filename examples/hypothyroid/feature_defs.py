# inputs: [longitude, latitude, population, median_income]
# features: population, median_income, location
# output: [median_house_price]
# labels: median_house_price

def check_num_of_inputs(inputs):
    return len(inputs)==2

def age(inputs):
    assert(check_num_of_inputs(inputs))
    value = inputs[0][1]
    if value<30:
        return 0
    elif value < 50:
        return 1
    elif value <70:
        return 2
    else:
        return 3

def TSH(inputs):
    assert(check_num_of_inputs(inputs))
    value = inputs[1][1] 
    if value<=4.0:
        return 0
    elif value<5.0:
        return 1
    elif value<9.0:
        return 2
    else:
        return 3 


def Class(outputs):
    value = outputs[0][1]   
    return value


def retrieve_feature_defs():
    feature_defs = {}
    feature_defs["age"] = age
    feature_defs["TSH"] = TSH
    feature_defs["Class"] = Class

    return feature_defs