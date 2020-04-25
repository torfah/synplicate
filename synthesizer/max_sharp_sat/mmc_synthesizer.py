
import importlib
import os
from synthesizer.max_sharp_sat import encoder




def configure(path):
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

def extract_program(encoding_path,witness_path,target_path):

    
    os.system(f"mkdir -p {target_path}program")
    witness_file = open(witness_path,"r")
    dot_file_path = target_path+"program/program.dot"
    dot_file = open(dot_file_path,"w")
    python_file_path = target_path+"program/program.py"
    python_file = open(python_file_path,"w") 

    var_ids = []
    count = 0
    for line in witness_file.readlines():
        if line.startswith("v "):
            # extract variable id 
            current_var_id = ""
            for letter in line:
                if letter == '\n':
                    break
                elif letter.isdigit() or letter=='-':
                    current_var_id += letter
                else:
                    if current_var_id!="":
                         var_ids.append(current_var_id)
                    current_var_id = ""
            print("Witness found! ",end='')
        if line.startswith("c Estimated max-count"):
            words = line.split()
            count = words[3]+words[4]+words[5]
            print("Count: ", count)
        
    if var_ids == []:
        print("No witness found!")
        exit
            
    # match witness values 
    print("Extracting program from witness...")
    program_nodes = {} # state -> feature
    program_edges = {} # state, partition -> state 
    encoding_file = open(encoding_path,"r")
    for line in encoding_file.readlines():
        if line.startswith("p "):
            break
        if line.startswith("c tau"):
            words = line.split()
            # retrieve var name 
            name = words[1]
            # retrieve var id
            id = words[3]
            if id in var_ids:
                # extract origin state, partition, successor state 
                attributes = name.split('_')
                program_edges[(attributes[1],attributes[3])] = attributes[4]
                print(f"({attributes[1]},{attributes[3]}) -> {attributes[4]}")
        if line.startswith("c lam"):
            words = line.split()
            # retrieve var name 
            name = words[1]
            # retrieve var id
            id = words[3]
            if id in var_ids:
                # extract  state, feature
                attributes = name.split('_')
                program_nodes[attributes[1]] = attributes[2]
                print(f"{attributes[1]}: {attributes[2]}")

    
    # print(program_edges)
    # print(program_nodes)

    dot_file.close()
    python_file.close()
    witness_file.close()
    return python_file_path

def synthesize(benchmark_path,samples):
    
    print("Extracting synthesis configuration... ") 
    config = configure(benchmark_path) 

    print(f"Synthesizing program with {config[0]:d} states, features {config[1]}, and labels {config[2]} ...")

    output_path = benchmark_path+"mmc_encoding/"

    
    num_of_feature_nodes = config[0]
    feature_partition = config[1]
    label_partition = config[2] 
    feature_defs = config[3]
    
   

    # create max#sat encoding
    encoding_path = encoder.encode(output_path,samples,num_of_feature_nodes,feature_partition,label_partition,feature_defs)

    # maximum model counting 
    print("Maximum model counting...")
    witness_path = output_path + "witness.txt"
    os.system(f"python synthesizer/max_sharp_sat/maxcount.py --scalmc synthesizer/max_sharp_sat/scalmc {encoding_path} 1 > {witness_path}")

    # translate witness to program: extract program from mmc witness
    program_path = extract_program(encoding_path,witness_path,benchmark_path)

    return program_path