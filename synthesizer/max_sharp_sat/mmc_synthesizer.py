
from synthesizer.max_sharp_sat import encoder


def config(path):
    config_file = open(path,"r")
    # initialize 
    size = 0
    feature_partition = {}
    label_partition = {}
    extend = False
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
        else:
            raise Exception("Config file syntax error!")
        # print(word_list[0])

    return (size,feature_partition,label_partition,extend)


def synthesize(output_path,samples,config):

    num_of_feature_nodes = config[0]
    feature_partition = config[1]
    label_partition = config[2]

    

    # create max#sat encoding
    encoding_path = encoder.encode(output_path,samples,num_of_feature_nodes,feature_partition,label_partition)

    # maximum model counting 

    # translate witness to program 
    program_path = ""

    return program_path