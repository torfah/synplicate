import importlib
import os
import pandas
import sys
import copy

#import csv
from synthesizer.max_sat import encoder, dd_encoder

from imaxhs import Solver

# global variables 
num_of_feature_nodes = 0
feature_partition = {}
feature_weights ={}
label_partition = {}
feature_defs = {}
output_path = ""
weights_map = {}
base_wcnf = {}
threshold_vars = {}
corr_soft_vars =[]
expl_soft_vars = []
encoding_path = ""
hard_weight = 0
current_rc2 = ""
threshold_weight = 0

solver = Solver()
core_vars = 0
total_vars = 0
global_counter = 0
core_hard_weight = 0


## Copied from ../max_sharp_sat/mmc_synthesizer.py 
def configure(path):
    config_file = open(f"{path}dd.config","r")
    # initialize 
    size = 0
    feature_partition = {}
    feature_weights = {}
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
                num_of_partitions = feature.split(':')[1]
                weight = feature.split(':')[2].split(',')[0]
                # print(f"{name} -- {num_of_partitions} -- {weight}")
                feature_partition[name] = int(num_of_partitions)
                feature_weights[name] = int(weight)
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
   

    return (size,feature_partition,feature_weights,label_partition,feature_defs,extend)

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
        if line.startswith("c lamp"):
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


def initialize(benchmark_path):#TODO move to specialized encoder
    
    global num_of_feature_nodes, feature_partition, feature_weights, label_partition, feature_defs, output_path

    print("Extracting synthesis configuration... ") 
    config = configure(benchmark_path) 
    print(config)

    num_of_feature_nodes = config[0]
    feature_partition = config[1]
    feature_weights = config[2]
    label_partition = config[3] 
    feature_defs = config[4]

    output_path = benchmark_path+"maxsat_encoding/"
    os.system(f"rm -r {output_path}")


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

# prepare binary encoding of thresholds
def get_binary(num,precision):
    count = 0
    nump = num
    binary = []
    while nump//2 != 0:
        if count>=precision:
            raise Exception(f"Num not encodable in {precision} bits!")

        if nump%2==1:
            binary.append(1)
        else:
            binary.append(0)
        count += 1
        nump = nump//2

    if num>0:
        binary.append(1)
        count +=1

    while count<precision:
        binary.append(0)
        count +=1

    return binary

def synthesize(benchmark_path,samples,lower_bound, upper_bound, precision, file_name, first = True):

    global current_rc2, threshold_weight, num_of_feature_nodes, feature_partition, label_partition, feature_defs, output_path, feature_weights, base_wcnf,corr_soft_vars, expl_soft_vars, threshold_vars, encoding_path, hard_weight, global_counter, core_vars, total_vars, core_hard_weight
    
    # create max#sat encoding
    encoding_file_name = f"{file_name}"
    
    
    # Compute core encoding just one time
    if first:
        encoding_path, corr_soft_vars, expl_soft_vars, corr_vars, hard_weight = encoder.encode_base(dd_encoder,output_path,samples,num_of_feature_nodes,feature_partition,feature_weights,label_partition,feature_defs,lower_bound,upper_bound,precision,weights_map,encoding_file_name)
        core_wcnf = open(encoding_path, 'r')
        core_hard_weight = hard_weight

        for line in core_wcnf.readlines():
            if line.startswith("c"):
                pass

            else if line.startswith("p wcnf "):
                num_vars, num_clauses, hard_limit = [int(w) for w in line.split()[2:]]
                core_vars = num_vars

            else:
                clause_weight = int(line.split()[0])
                if clause_weight == hard_limit:
                    solver.add_clause([int(w) for w in line.split()[1:-1]])

                else:
                    solver.add_soft_lit(int(line.split()[1]), clause_weight)

        core_wcnf.close()



    encoding_path_thres, threshold_vars, hard_weight_thres = encoder.encode_base(dd_encoder, output_path, lower_bound, upper_bound, precision, encoding_file_name)
    thres_wcnf = open(encoding_path_thres, 'r')
    global_counter = global_counter + 1

    for line in thres_wcnf.readlines():
        if line.startswith("c"):
                pass

        else if line.startswith("p wcnf "):
            num_vars, num_clauses, hard_limit = [int(w) for w in line.split()[2:]]
            total_vars = core_vars + num_vars

        else:
            clause = [int(w) for w in line.split()[1:-1]]
            clause.append(total_vars + global_counter)
            solver.add_clause(clause)

    thres_wcnf.close()


    threshold_weight = core_hard_weight + hard_weight_thres + 1

    # maxsat 
    print("Max Sat...")
    witness_path = output_path + f"witness_{file_name}.txt"
    witness_file = open(witness_path,"w")
    
    ## Run the MaxSat solver
    pfound = True
    assumptions = [total_vars + i for i in range(1, global_counter)]
    assumptions.append(-(total_vars + global_counter))
    status = solver.solve(assumptions)

    if status not in [20, 30]:
        print("No program found. Instance is Unsatisfiable ")
        pfound = False
        return "", "", 0, 0

    cost = solver.get_obj_val()
    print(f"Total cost:{cost}")
    corr_reward = 0
    expl_reward = 0

    try:
        model = solver.get_model
        s1=str(model)
        # print(s1)
        witness_file.write(s1)
        for v in model:
            for num, weight in corr_vars:
                # print(f"Check: {v} , {num}")
                if str(v)==num:
                    corr_reward += 1 
                    # print(f"|-----------------------------: {v} , {num}")
            for num, weight in expl_soft_vars:
                if str(v)==num:
                    expl_reward += weight
                    # print(num)

    witness_file.close()

    program_path = ""
    dot_path = ""

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
    sat_samples = corr_reward
    explainability = (expl_reward)/100
    print(f"SatSamples :{sat_samples}")
    program_path, dot_path, png_path = extract_program(encoding_path,model,benchmark_path,input_names,file_name)
    
    current_rc2.delete()
    return program_path, dot_path, sat_samples/len(samples), explainability
 
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


