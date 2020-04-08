# inputs: longitude, latitude, population, median_income
# features: population, median_income, location

def check_num_of_inputs(inputs):
    return len(inputs)==4

def population(inputs):
    assert(check_num_of_inputs(inputs))
    return 0

def median_income(inputs):
    assert(check_num_of_inputs(inputs))
    return 0

def location(inputs):
    assert(check_num_of_inputs(inputs))
    return 0

def retrieve_feature_defs():
    feature_defs = {}
    feature_defs["population"] = population
    feature_defs["median_income"] = median_income
    feature_defs["location"] = location

    return feature_defs