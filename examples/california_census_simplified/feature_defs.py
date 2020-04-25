# inputs: [longitude, latitude, population, median_income]
# features: population, median_income, location
# output: [median_house_price]
# labels: median_house_price

def check_num_of_inputs(inputs):
    return len(inputs)==4

def population(inputs):
    assert(check_num_of_inputs(inputs))
    value = inputs[2][1]
    if value<3000.0:
        return 1
    if value<10000.0:
        return 2
    if value<20000.0:
        return 3
    else:
        return 0

def median_income(inputs):
    assert(check_num_of_inputs(inputs))
    value = inputs[3][1] 
    if value<2000.0:
        return 1
    else:
        return 0

def location(inputs):
    assert(check_num_of_inputs(inputs))
    longitude = inputs[0][1]
    latitude = inputs[1][1]
    if -114.0>=longitude and longitude>-118.0:
        if 36.0<=latitude and latitude<39:
            return 1
    if -118.0>= longitude and longitude>=-124.3:
        if 39<=latitude and latitude<=42.5:
            return 2    
    return 0

def median_house_price(outputs):
    value = outputs[0][1]
    if value<-3.0:
        return 1
    if value<-1.5:
        return 2
    if value<0.0:
        return 3
    if value<1.5:
        return 4    
    return 0

def test(outputs):
    return 0

def retrieve_feature_defs():
    feature_defs = {}
    feature_defs["population"] = population
    feature_defs["medianIncome"] = median_income
    feature_defs["location"] = location
    feature_defs["medianHousePrice"] = median_house_price
    feature_defs["test"] = test

    return feature_defs