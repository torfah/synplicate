
import importlib
import os
from synthesizer.max_sharp_sat import encoder




def config(path):
    config_file = open(f"{path}config.mmc","r")
    # initialize 
    size = 0
    feature_partition = {}
    label_partition = {}
    extend = False
    feature_defs = {}
    # parse config file
    for line in config_file:
        word_list = line.split()
        if word_list[0]=="size":
            size = int(word_list[2])
        elif word_list[0]=="features":
            for feature in word_list[2:]:
                name = feature.split(':')[0] 
                num_of_partitions = feature.split(':')[1].split(',')[0] 
                feature_partition[name] = int(num_of_partitions)
        elif word_list[0]=="labels":
            for label in word_list[2:]:
                name = label.split(':')[0] 
                num_of_partitions = label.split(':')[1].split(',')[0] 
                label_partition[name] = int(num_of_partitions)
        elif word_list[0]=="extend":
            if word_list[2] == "True":
                extend = True
        elif word_list[0]=="feature_defs":
            module = importlib.import_module(f".{word_list[2]}",path.replace("/",".").rstrip('.'))
            feature_defs = module.retrieve_feature_defs()
        else:
            raise Exception("Config file syntax error!")
        # print(word_list[0])

    return (size,feature_partition,label_partition,feature_defs,extend)


def synthesize(output_path,samples,config):

    num_of_feature_nodes = config[0]
    feature_partition = config[1]
    label_partition = config[2] 
    feature_defs = config[3]
    

    # create max#sat encoding
    encoding_path = encoder.encode(output_path,samples,num_of_feature_nodes,feature_partition,label_partition,feature_defs)

    # maximum model counting 
    print("Maximum model counting...")
    os.system(f"python synthesizer/max_sharp_sat/maxcount.py --scalmc synthesizer/max_sharp_sat/scalmc {encoding_path} 3")

    # translate witness to program 
    program_path = ""

    return program_path