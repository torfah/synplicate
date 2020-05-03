import os

def create_feature_string(feature):
    name = ""
    value = feature
    if feature<0:
        name += "N"
        value = -1*value
    else:
        name += "P"
    
    name += str(int(value*100))
    return name

def phi_Gamma(sat_file,samples):
    sat_file.write("phi_Gamma := \n")
   
    counter = 0
    feature_var_id ={} # maps feature number and sample number to variable 
    num_of_inputs = len(list(samples)[0])
    num_of_samples = len(samples)
    num_of_labels = len(samples[list(samples)[0]])
   
    sat_file.write("(\n")
    for inputs, labels in samples.items():
        sat_file.write("(")
        for i in range(len(inputs)):
            sat_file.write(f"{inputs[i][0]}_")
            sat_file.write(create_feature_string(inputs[i][1]))
            feature_var_id[(i,counter)] = f"{inputs[i][0]}_{create_feature_string(inputs[i][1])}"
            if i < len(inputs)-1:
                sat_file.write(" & ")
        sat_file.write(" & ")
        for i in range(len(labels)):
            sat_file.write(f"{labels[i][0]}_")
            sat_file.write(create_feature_string(labels[i][1]))
            feature_var_id[(i+num_of_inputs,counter)] = f"{labels[i][0]}_{create_feature_string(labels[i][1])}"
            if i < len(labels)-1:
                sat_file.write(" & ")
        sat_file.write(")")
        if counter < len(samples)-1:
            sat_file.write(" | ")
        sat_file.write("\n")
        counter += 1 
    sat_file.write(")\n")
    sat_file.write(" & ")
    sat_file.write("\n")
    for f in range(num_of_inputs + num_of_labels):
        sat_file.write("(")
        for i in range(num_of_samples):
            sat_file.write("(")
            sat_file.write(feature_var_id[(f,i)])
            sat_file.write(" => ")
            flag = False
            for j in range(num_of_samples):
                if (feature_var_id[(f,j)]!=feature_var_id[(f,i)]):
                    if flag: 
                        sat_file.write(" & ")
                    flag = True
                    sat_file.write("!")
                    sat_file.write(feature_var_id[(f,j)])
            if i<num_of_samples-1:
                sat_file.write(") & ")
            else:
                sat_file.write(")")
        sat_file.write(")")
        if f<(num_of_inputs + num_of_labels)-1:
            sat_file.write("& ")
        sat_file.write("\n")

    sat_file.write(";\n")

def phi_T(sat_file,num_of_feature_nodes,feature_partition,label_partition):
    num_of_features = len(feature_partition)
    sat_file.write("phi_T :=\n")
    # assign feature nodes to unique features
    sat_file.write("(\n")
    for i in range(num_of_feature_nodes):
        sat_file.write("(")
        for h, f in enumerate(list(feature_partition.keys())):
            sat_file.write("(")
            sat_file.write(f"lam_{i:d}_{f}")
            for ff in list(feature_partition.keys()):
                if ff!=f:
                    sat_file.write(" & ")
                    sat_file.write(f"!lam_{i:d}_{ff}")
            sat_file.write(")")
            if h<num_of_features-1:
                sat_file.write(" | ")
        sat_file.write(")")
        if i<num_of_feature_nodes-1:
            sat_file.write(" & ")
        sat_file.write("\n")
    sat_file.write(")")

    # uniquness per feature and determinism of transition relation 
    # uniquness feature nodes
    sat_file.write(" \n& \n")
    
    if (num_of_feature_nodes>1):
        sat_file.write("(\n")
        for i in range(num_of_feature_nodes):
            for fid, f in enumerate(feature_partition.keys()):
                sat_file.write("(")
                sat_file.write(f"lam_{i:d}_{f} => T ")
                for j in range(i+1,num_of_feature_nodes):
                    ffid = 0
                    for  ff, ffbu in feature_partition.items():
                        if j!=i and ff!=f:
                            for s in range(ffbu):
                                sat_file.write(f"  & !tau_{i:d}_{ff}_{s:d}_{j:d}")
                                # if not ((ffid==num_of_features-1 or (ffid==num_of_features-2 and fid==num_of_features-1)) and (j==num_of_feature_nodes-1 or (j==num_of_feature_nodes-2 and i==num_of_feature_nodes-1)) and s==ffbu-1):
                                #     sat_file.write(" & ")
                        ffid += 1
                sat_file.write(")")
                if not(i==num_of_feature_nodes-1 and fid==num_of_features-1):
                    sat_file.write(" & ")
                sat_file.write("\n")
        sat_file.write(" ) \n& \n")
    # uniquness label nodes
    sat_file.write("(")
    for i in range(num_of_feature_nodes):
        for fid, f in enumerate(feature_partition.keys()):
            sat_file.write("(")
            sat_file.write(f"lam_{i:d}_{f} => ")
            lid = 0
            for l, lbu in label_partition.items():
                for h in range(lbu):
                    ffid = 0
                    for  ff, ffbu in feature_partition.items():
                        if ff!=f:
                            for s in range(ffbu):
                                sat_file.write(f"   !tau_{i:d}_{ff}_{s:d}_{l}_{h}")
                                if not ((ffid==num_of_features-1 or (ffid==num_of_features-2 and fid==num_of_features-1)) and (lid==len(label_partition)-1 and h==lbu-1) and s==ffbu-1):
                                    sat_file.write(" & ")
                        ffid += 1
                lid += 1
            sat_file.write(")")
            if not(i==num_of_feature_nodes-1 and fid==num_of_features-1):
                sat_file.write(" & ")
            sat_file.write("\n")
    sat_file.write(")\n")
    # determinism
    num_of_label_nodes = 0
    lable_node_id = {}
    for l, lbu in label_partition.items():
        for j in range(lbu):
            lable_node_id[num_of_label_nodes+j]= (l,j)
        num_of_label_nodes += lbu

    
    # if num_of_feature_nodes>1:
    sat_file.write("& \n")
    sat_file.write("(\n")
    for i in range(num_of_feature_nodes):
        sat_file.write("(\n")
        fid = 0 
        for f,fbu in feature_partition.items():
            for b in range(fbu):
                sat_file.write("(")
                for j in range(i+1,num_of_feature_nodes+num_of_label_nodes):
                    if j < num_of_feature_nodes:
                        if j!=i:
                            sat_file.write("(")
                            sat_file.write(f"tau_{i:d}_{f}_{b:d}_{j:d} & ")
                            for jj in range(i+1,num_of_feature_nodes+num_of_label_nodes):
                                if j!=jj and jj!=i:
                                    if jj<num_of_feature_nodes:
                                        sat_file.write(f"!tau_{i:d}_{f}_{b:d}_{jj:d}")
                                    else:
                                        sat_file.write(f"!tau_{i:d}_{f}_{b:d}_{lable_node_id[jj-num_of_feature_nodes][0]}_{lable_node_id[jj-num_of_feature_nodes][1]}")
                                    if not(jj==num_of_feature_nodes+num_of_label_nodes-1 or (jj==num_of_feature_nodes+num_of_label_nodes-2 and j==num_of_feature_nodes+num_of_label_nodes-1)):
                                        sat_file.write(" & ")
                            sat_file.write(")")
                            sat_file.write("  | ")
                    else:
                        sat_file.write("(")
                        sat_file.write(f"tau_{i:d}_{f}_{b:d}_{lable_node_id[j-num_of_feature_nodes][0]}_{lable_node_id[j-num_of_feature_nodes][1]} ")
                        for jj in range(i+1,num_of_feature_nodes+num_of_label_nodes):
                            if jj<num_of_feature_nodes:
                                if jj!=j and jj!=i:
                                    sat_file.write(" & ")
                                    sat_file.write(f"!tau_{i:d}_{f}_{b:d}_{jj:d} ")                                            
                            else:
                                if (lable_node_id[j-num_of_feature_nodes][0]==lable_node_id[jj-num_of_feature_nodes][0] and jj!=j):
                                    sat_file.write(" & ")     
                                    sat_file.write(f"!tau_{i:d}_{f}_{b:d}_{lable_node_id[jj-num_of_feature_nodes][0]}_{lable_node_id[jj-num_of_feature_nodes][1]}")                                               
                        sat_file.write(")")
                        if not (j==num_of_feature_nodes+num_of_label_nodes-1):
                                sat_file.write("  | ")
                sat_file.write(")")
                if not (fid==num_of_features-1 and b==fbu-1):
                    if b==fbu-1:
                        sat_file.write("\n | \n")
                    else:
                        sat_file.write("&\n")
            fid += 1 
        sat_file.write("\n)")   
        if not (i==num_of_feature_nodes-1):
            sat_file.write("\n&\n")
    sat_file.write("\n)")
    sat_file.write(";\n")

def phi_sim(sat_file,num_of_feature_nodes,feature_partition,label_partition,samples,feature_defs):

    # path encoding
    sat_file.write("phi_sim := pi_0_0 &\n")
    sat_file.write("T ")
    for p in range(num_of_feature_nodes):
        sat_file.write("\n &")
        sat_file.write("(")
        sat_file.write(" F \n")
        for i in range(num_of_feature_nodes):
            for f, fbu in feature_partition.items():
                for b in range(fbu):
                    for j in range(i+1,num_of_feature_nodes):
                        if(j!=i):
                            sat_file.write("   | ")
                            sat_file.write("(")
                            sat_file.write(f"del_{p:d}_{i:d}_{f}_{b:d}_{j:d} & ")
                            sat_file.write(f"pi_{p:d}_{i:d} & pi_{p+1:d}_{j:d} & ")
                            sat_file.write(f"tau_{i:d}_{f}_{b:d}_{j:d} & ")
                            sat_file.write("(")
                            sat_file.write("F")
                            for inputs in samples.keys():
                                feature_def = feature_defs[f]
                                if feature_def(inputs) == b:
                                    sat_file.write(" | ")
                                    sat_file.write("(")
                                    sat_file.write("T ")
                                    for name, val in inputs:
                                        sat_file.write(" & ")
                                        sat_file.write(f"{name}_{create_feature_string(val)}")
                                    sat_file.write(")")
                            sat_file.write(")")
                            sat_file.write(")")
                            sat_file.write("\n")
                    for l, lbu in label_partition.items():
                        for lb in range(lbu):
                            sat_file.write("   | ")
                            sat_file.write("(")
                            sat_file.write(f"del_{p:d}_{i:d}_{f}_{b:d}_{l}_{lb:d} & ")
                            sat_file.write(f"pi_{p:d}_{i:d} & pi_{p+1:d}_{l}_{lb:d} & ")
                            sat_file.write(f"tau_{i:d}_{f}_{b:d}_{l}_{lb:d} & ")
                            sat_file.write("(")
                            sat_file.write("F")
                            for inputs in samples.keys():
                                feature_def = feature_defs[f]
                                if feature_def(inputs) == b:
                                    sat_file.write(" | ")
                                    sat_file.write("(")
                                    sat_file.write("T ")
                                    for name, val in inputs:
                                        sat_file.write(" & ")
                                        sat_file.write(f"{name}_{create_feature_string(val)}")
                                    sat_file.write(")")
                            sat_file.write(")")
                            sat_file.write(")")
                            sat_file.write("\n")
        sat_file.write(")")

    sat_file.write(" & \n")

    # label condition
    sat_file.write("(")
    sat_file.write("F")
    for p in range(num_of_feature_nodes+1):
        for l, lbu in label_partition.items():
            for b in range(lbu):
                sat_file.write("\n")
                sat_file.write(" | ")
                sat_file.write("(")
                sat_file.write(f"pi_{p:d}_{l}_{b:d} & ")
                sat_file.write("(")
                sat_file.write("F")
                for outputs in list(samples.values()):
                    label_def = feature_defs[l]
                    if label_def(outputs) == b:
                        sat_file.write(" | ")
                        sat_file.write("(")
                        sat_file.write("T ")
                        for name, val in outputs:
                            if name == l:
                                sat_file.write(" & ")
                                sat_file.write(f"{name}_{create_feature_string(val)}")
                        sat_file.write(")")
                sat_file.write(")")
                sat_file.write(")")
    sat_file.write(")")

    # uniqueness of labels and nodes in path
    sat_file.write("\n&\n")
    sat_file.write("(")
    sat_file.write("T \n")
    for p in range(num_of_feature_nodes+1):
        for i in range(num_of_feature_nodes):
            sat_file.write(" & ")
            sat_file.write("(")
            sat_file.write(f"pi_{p:d}_{i:d} => ")
            sat_file.write("( T")
            for j in range(num_of_feature_nodes): 
                if j!=i:
                    sat_file.write(f" & !pi_{p:d}_{j:d}")
            for l, lbu in label_partition.items():
                for b in range(lbu):
                    sat_file.write(f" & !pi_{p:d}_{l}_{b:d}")
            sat_file.write(")")
            sat_file.write(")")
            sat_file.write("\n")
    sat_file.write(")")

    sat_file.write("\n&\n")
    sat_file.write("(")
    sat_file.write("T \n")
    for p in range(num_of_feature_nodes+1):
        for l, lbu in label_partition.items():
            for b in range(lbu):
                sat_file.write(" & ")
                sat_file.write("(")
                sat_file.write(f"pi_{p:d}_{l}_{b:d} =>")
                sat_file.write("( T ")
                for bb in range(lbu):
                    if bb!=b:
                        sat_file.write(f" & !pi_{p:d}_{l}_{bb:d}")
                sat_file.write(")")
                sat_file.write(")")
                sat_file.write("\n")
    sat_file.write(")")
    sat_file.write(";\n")   

def extract_max_variables(dimacs):
    print("|---Extracting maximization variables...")  
    vars = []
    text_file = open(dimacs)

    for line in text_file.readlines():
        if not line.startswith("c"):
            break
        
        current_num = ""
       
        if ("tau" in line) or ("lam" in line):
            flag = False
            
            for letter in line:
                if letter=='\n':
                    break
                if flag:
                    if letter.isdigit():
                        current_num += letter
                if letter == '>':
                    flag = True
        
        if current_num!="":
            vars.append(current_num)
    print(f"   {len(vars)} max variables")
    text_file.close()    
    return vars

def extract_ind_variables(dimacs,name_list): 
    print("|---Extracting counting variables...")   
    vars = []
    text_file = open(dimacs)

    for line in text_file.readlines():
        # print(line)
        if not line.startswith("c"):
            break
        
        current_num = ""
        flag = False
        for name in name_list:
            if (f"c {name}") in line:
                # print(name)
                flag = True
       
        if flag:
            flag2= False
            for letter in line:
                if letter=='\n':
                    break
                if flag2:
                    if letter.isdigit():
                        current_num += letter
                if letter == '>':
                    flag2 = True
        
        if current_num!="":
            vars.append(current_num)
    print(f"   {len(vars)} ind variables")
    text_file.close()
    return vars


def encode(output_path,samples,num_of_feature_nodes,feature_partition,label_partition,feature_defs):

    # create max#sat file
    os.system(f"mkdir -p {output_path}")
    sat_file_path = output_path+"encoding.sat"
    sat_file = open(sat_file_path,"w")
    sat_file.write("BC1.1\n")

    # phi_Gamma 
    phi_Gamma(sat_file,samples)

    # phi_T
    phi_T(sat_file,num_of_feature_nodes,feature_partition,label_partition)

    # phi_sim 
    # compute mapping between (feature,bucket) -> sample
    phi_sim(sat_file,num_of_feature_nodes,feature_partition,label_partition,samples,feature_defs)


    sat_file.write("FORMULA := phi_Gamma & phi_T & phi_sim;\n")
    sat_file.write("ASSIGN FORMULA;")
    sat_file.close()

    # create dimac file with mmc parameters 
    dimacs_tempfile_path = output_path+"encoding_temp.dimacs"

    print("Translating to dimacs...")
    os.system(f"./synthesizer/max_sharp_sat/bc2cnf -all {sat_file_path} {dimacs_tempfile_path}")
    

    print("Translating to maxdimacs...")
    dimacs_file_path = output_path+"encoding.dimacs"
    maximization_vars = extract_max_variables(dimacs_tempfile_path)
    name_list = []
    for k,v in samples.items():
        for i in range(len(k)):
            name_list.append(k[i][0])
        for j in range(len(v)):
            name_list.append(v[j][0])
        break
    counting_vars = extract_ind_variables(dimacs_tempfile_path,name_list)
    dimacs_file = open(dimacs_file_path,"w")
    dimacs_file.write("c max")
    for s in maximization_vars:
        dimacs_file.write(f" {s} ")
    dimacs_file.write("0\n")    

    dimacs_file.write("c ind")
    for s in counting_vars:
        dimacs_file.write(f" {s} ")
    dimacs_file.write("0\n") 

    dimacs_temp_file = open(dimacs_tempfile_path,"r")
    temp_string = dimacs_temp_file.read()
    dimacs_file.write(temp_string)
    dimacs_temp_file.close()
    dimacs_file.close()

    # os.system(f"rm {output_path}encoding_temp.dimacs")

    return dimacs_file_path