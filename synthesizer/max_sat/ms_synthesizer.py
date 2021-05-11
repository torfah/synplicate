import importlib
import os
import pandas
import sys
#import csv
from  synthesizer.max_sat import encoder, dd_encoder
from  synthesizer.max_sat import smallencoder
from pysat.examples.rc2 import RC2
#from pysat.examples.fm import FM
from pysat.formula import WCNF

# global variables 
num_of_feature_nodes = 0
feature_partition = {}
label_partition = {}
feature_defs = {}
output_path = ""
weights_map = {}


## Copied from ../max_sharp_sat/mmc_synthesizer.py 
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
            print(path)
            module = importlib.import_module(f".{word_list[2]}", path.replace("/",".").rstrip('.'))
            feature_defs = module.retrieve_feature_defs()
        else:
            raise Exception("Config file syntax error!")
        # print(word_list[0])

    return (size,feature_partition,label_partition,feature_defs,extend)

def synthesize_python_code(target_path,program_edges,program_nodes,input_names,file_name):
    python_file_dir_path = target_path+ f"program/"
    program_file_name = f"program_{file_name}.py"
    python_file = open(python_file_dir_path+program_file_name,"w") 

    # target_path_modified = target_path.replace("/",".").rstrip('.')
    python_file.write("import sys\n")
    python_file.write(f"sys.path.insert(0,\"{target_path}\")\n")
    python_file.write(f"import feature_defs\n\n")

    # python_file.write(f"def execute({input_names[0]}")
    # for i in range(1,len(input_names)):
    #     python_file.write(f", {input_names[i]}")
    # python_file.write("):\n")


    python_file.write(f"def execute(inputs):\n")

    # create flowchart edges and nodes maps
    python_file.write(f"\tprogram_nodes ={{}}\n")
    for node,feature in program_nodes.items():
        python_file.write(f"\tprogram_nodes[\"{node}\"]= \"{feature}\"\n")

    python_file.write(f"\n\tprogram_edges ={{}}\n")
    for (source,partition), dest in program_edges.items():
        python_file.write(f"\tprogram_edges[(\"{source}\",{partition})]= \"{dest}\"\n")

    python_file.write("\n\tfeatures = feature_defs.retrieve_feature_defs()\n\n")

    # compute backets for each feature
    input_string = "["
    input_idx = 0
    for name in input_names:
        input_string += f"(\"{name}\",inputs[{input_idx}]),"
        input_idx +=1
    input_string = input_string.rstrip(',')
    input_string += "]"
    
    python_file.write(f"\tvalue_map = {{}} \n")
    for node, feature in program_nodes.items():
        python_file.write(f"\tvalue_map[\"{feature}\"] = features[\"{feature}\"]({input_string})")
        python_file.write("\n")

    python_file.write("\n")
    python_file.write("\tflag = True\n")
    python_file.write("\tcurrent_node = \"0\"\n")
    # python_file.write("\tlabel=\"\"\n")
    python_file.write(f"\twhile flag:\n")
    python_file.write(f"\t\tcurrent_feature = program_nodes[current_node]\n")
    python_file.write(f"\t\tnext_node = program_edges[current_node,value_map[current_feature]]\n")
    python_file.write(f"\t\tif next_node.isdigit():\n")
    python_file.write(f"\t\t\tcurrent_node = next_node\n")
    python_file.write(f"\t\telse:\n")
    python_file.write(f"\t\t\tcurrent_node = next_node\n")
    python_file.write(f"\t\t\tflag = False\n")

    # python_file.write("\tprint(current_node)\n")
    python_file.write(f"\treturn current_node\n\n")

    # python_file.write(f"print(f\"first result {{flowchart(-120.0,32.2,23222.9,1.6)}}\")")


    python_file.close()

    python_file_path = python_file_dir_path+program_file_name

    return python_file_path

def extract_program_map(encoding_path, model):
## Copied from ../max_sharp_sat/mmc_synthesizer.py and suitably modified
    print("Extracting program from witness...")
    # print(model);
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
            if int(id) in model:
                # extract origin state, partition, successor state 
                attributes = name.split('_')
                source  = attributes[1]
                partition = attributes[2]
                index = 2
                while (not partition.isdigit()):
                    index += 1
                    partition = attributes[index]
                index += 1
                dest = attributes[index]
                for att in attributes[index+1:]:
                    dest += "_"+ att
                program_edges[(source,partition)] = dest
                print(f"({source},{partition}) -> {dest}")
        if line.startswith("c lam"):
            words = line.split()
            # retrieve var name 
            name = words[1]
            # retrieve var id
            id = words[3]
            if int(id) in model:
                # extract  state, feature
                attributes = name.split('_')
                node = attributes[1]
                feature = attributes[2]
                for att in attributes[3:]:
                    feature += "_"+att
                program_nodes[node] = feature
                print(f"{node}: {feature}")
    
    return program_edges,program_nodes

def synthesize_dot_code(target_path,program_edges,program_nodes,file_name):
    dot_file_path = target_path+ f"program/program_{file_name}.dot"

    #print(program_edges)
    #print(program_nodes)
    #print(iteration)
    dot_file = open(dot_file_path,"w")

    dot_file.write("digraph {\n")
    for value in program_edges.values():
        # print(value)
        if not value.isdigit():
            dot_file.write(f"node [label={value},style=\"\"] {value}\n")
    
    for node, feature in program_nodes.items():
        # print(node)
        # print(feature)
        dot_file.write(f"node [label={feature},shape=\"diamond\",style=\"\"] {node}\n")

    dot_file.write("\n")

    for (source, partition) , dest in program_edges.items():
        dot_file.write(f"{source} -> {dest} [label=\"{partition}\"]\n")

    dot_file.write("}")

    dot_file.close()

    png_path = target_path + f"program/program_{file_name}.png"

    os.system(f"dot -Tpng {dot_file_path} -o {png_path}")
    return dot_file_path, png_path


def extract_program(encoding_path,model,target_path,input_names,file_name):

    print(target_path)

    os.system(f"mkdir -p {target_path}program")
    program_edges, program_nodes = extract_program_map(encoding_path,model)

    dot_file_path, png_path = synthesize_dot_code(target_path, program_edges, program_nodes,file_name)
    python_file_path = synthesize_python_code(target_path,program_edges,program_nodes,input_names,file_name)

    return python_file_path,dot_file_path,png_path


def initialize(benchmark_path):
    
    global num_of_feature_nodes, feature_partition, label_partition, feature_defs, output_path

    print("Extracting synthesis configuration... ") 
    config = configure(benchmark_path) 
    print(config)

    num_of_feature_nodes = config[0]
    feature_partition = config[1]
    label_partition = config[2] 
    feature_defs = config[3]

    output_path = benchmark_path+"maxsat_encoding/"


def compute_class_size():
    size = 0

    num_of_features = len(feature_partition)
    max_num_of_partition = 0
    for b in feature_partition.values():
        if b>max_num_of_partition:
            max_num_of_partition=b
    
    num_of_label_combinations = 1
    for b in label_partition.values():
        num_of_label_combinations *=b

    size = num_of_feature_nodes*max_num_of_partition*(num_of_feature_nodes+num_of_label_combinations)*(num_of_features**num_of_feature_nodes)

    # print(f"Class Size:{size}, number of nodes:{num_of_feature_nodes}, feature partitions: {max_num_of_partition}, labels: {num_of_label_combinations}")
    return size


def synthesize(benchmark_path,samples,lower_bound, upper_bound, precision,file_name):

    global num_of_feature_nodes, feature_partition, label_partition, feature_defs, output_path, weights_map
    
    # create max#sat encoding
    encoding_file_name = f"{file_name}"
    
    # config = configure(benchmark_path) 
    # num_of_feature_nodes = config[0]
    # feature_partition = config[1]
    # label_partition = config[2] 
    # feature_defs = config[3]

    encoding_path = encoder.encode(dd_encoder,output_path,samples,num_of_feature_nodes,feature_partition,label_partition,feature_defs,lower_bound,upper_bound,precision,weights_map,encoding_file_name)
    # encoding_path, pi_vars= smallencoder.encode(output_path,samples,num_of_feature_nodes,feature_partition,label_partition,feature_defs,encoding_file_name)
    #encoding_path = "" # TODO call encoder. use output path as directory to store encoding 
    
    #print (pi_vars)
    #print (tau_vars)
    #print (lam_vars)
    # maxsat 
    print("Max Sat...")
        
    wcnf = WCNF(from_file=encoding_path)
#    fm = FM(wcnf, verbose=1)
#    fm.compute()  # set of hard clauses should be satisfiable
    witness_path = output_path + f"witness_{file_name}.txt"
#    os.system(f"python3 /home/shetal/pysat/examples/fm.py -vv {encoding_path} > {witness_path}")
## Run the RC2 MaxSat solver
    witness_file = open(witness_path,"w")

    pfound = True
    with RC2(wcnf) as rc2:
        x =  rc2.compute()
        # print (x)
        cost = rc2.cost
        print(f"Cost:{cost}")
        try:
            model = rc2.model
            s1=str(model)
            #print(s1)
            witness_file.write(s1)
        except:
            print("No program found. Instance is Unsatisfiable ")
            pfound = False

    witness_file.close()

    program_path = ""
    dot_path = ""
    if not pfound:
        return program_path, dot_path, 0
##TODO: Create a dot file from the tau and lam variables

    # TODO safe program into witness file 

    # translate witness to program: extract program from maxsat witness
    # extract program signature 
    input_names = []
    for s in samples.keys():
        for i in range(len(s)):
            input_names.append(s[i][0])
        break
    program_path = ""
    dot_path = ""
    # TODO extract program from witness

    print(input_names)
    sat_samples=len(samples) - cost
    print(f"SatSamples :{sat_samples}")
    program_path, dot_path, png_path = extract_program(encoding_path,model,benchmark_path,input_names,file_name)

    return program_path, dot_path, sat_samples
 
# samples={}
# #sample_file = '/home/shetal/Synthesis-Interpretable-Programs-for-DNNs/Experiments/loan_acquisition/age_bias_guided/Bench1/run1/samples/newsamples_0.csv'

# #data=pandas.read_csv(sample_file, 'series')
# #print(data.values)

# #with open(sample_file) as csvfile:
# #    data = list(csv.reader(csvfile))

# #for s in data.columns:
# #    print(s)
# #for s in data.values:
# #    for j in s.enumerate:
# #        print(f"First row: {j}")

# #print(data)
# samples[('age', 20), ('monthly_income', 5000)] = [("approved", 0)]
# samples[('age', 40), ('monthly_income', 8000)] = [("approved", 1)]
# samples[('age', 60), ('monthly_income', 4000)] = [("approved", 1)]
# samples[('age', 49), ('monthly_income', 9000)] = [("approved", 1)]
# samples[('age', 49), ('monthly_income', 9000)] = [("approved", 0)]
# samples[('age', 29), ('monthly_income', 4000)] = [("approved", 0)]
# benchmark_path="examples/loan_acquisition/"

# synthesize(benchmark_path, samples, 0)


