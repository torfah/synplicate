
import tensorflow as tf
import sys
import os
sys.path.append('../../')
from sampler import sampler



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


def extract_max_variables(dimacs):
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
        
    return vars


def extract_ind_variables(dimacs):    
    vars = []
    text_file = open(dimacs)

    for line in text_file.readlines():
        if not line.startswith("c"):
            break
        
        current_num = ""
       
        if ("c f" in line) or ("c l " in line):
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
        
    return vars


def encode(model,num_of_samples,num_of_nodes):
    debug = "\n"
    # Create file
    text_file = open("encoding.sat","w")
    text_file.write("BC1.1\n")
    
    # Get Samples
    samples = sampler.sample(model,num_of_samples)

    # Create phi_Gamma
    text_file.write("phi_Gamma :=")
    counter = 0
    feature_var_id ={} # maps feature number and sample number to variable 
    num_of_features = 0 
   
    for features, lables in samples.items():
        text_file.write("(")
        num_of_features = len(features)
        for i in range(len(features)):
            text_file.write(f"f{i:d}_")
            text_file.write(create_feature_string(features[i]))
            feature_var_id[(i,counter)] = f"f{i:d}_{create_feature_string(features[i])}"
            if i < len(features)-1:
                text_file.write(" & ")
        if lables:
            text_file.write(" => l")
        else:
            text_file.write(" => !l")
        text_file.write(")")
        if counter < num_of_samples-1:
            text_file.write(" & ")
        text_file.write(debug)
        counter += 1 

    text_file.write(" & ")
    text_file.write(debug)
    # Only one feature vector can be true
    text_file.write("(")
    for i in range(num_of_samples):
        text_file.write("(")
        for f in range(num_of_features):
            text_file.write(feature_var_id[(f,i)])
            if f<num_of_features-1:
                    text_file.write("& ")
        text_file.write(")")
        text_file.write(" & ")
        for j in range(num_of_samples):
            if i!=j :
                text_file.write("!(")
                for f in range(num_of_features):
                    text_file.write(feature_var_id[(f,j)])
                    if f<num_of_features-1:
                        text_file.write("& ")
                text_file.write(")")
                if j<num_of_samples-2 or (j==num_of_samples-2 and i!=num_of_samples-1): 
                    text_file.write(" & ")
        if i<num_of_samples-1:
            text_file.write("|")
        text_file.write(debug)
    text_file.write(")")
    
    text_file.write(" & ")
    text_file.write(debug)
    for f in range(num_of_features):
        text_file.write("(")
        for i in range(num_of_samples):
            text_file.write("(")
            text_file.write(feature_var_id[(f,i)])
            text_file.write("& ")
            for j in range(num_of_samples):
                if (feature_var_id[(f,j)]!=feature_var_id[(f,i)]):
                    text_file.write("!")
                    text_file.write(feature_var_id[(f,j)])
                    if j<num_of_samples-2 or (j==num_of_samples-2 and i!=num_of_samples-1): 
                        text_file.write(" & ")
            if i<num_of_samples-1:
                text_file.write(")| ")
                text_file.write(debug)
            else:
                text_file.write(")")
        text_file.write(")")
        if f<num_of_features-1:
            text_file.write("& ")
        text_file.write(debug)
    text_file.write(";\n")
   
    # Create phi_T for template 
    text_file.write("phi_T := ")
    # Assign nodes to features 
    for i in range(num_of_nodes):
        text_file.write("(")
        for f in range(num_of_features):
            text_file.write(f"lam_{i:d}_{f:d}")
            for ff in range(num_of_features):
                if ff!=f:
                    text_file.write(" & ")
                    text_file.write(f"!lam_{i:d}_{ff:d}")
            if f<num_of_features-1:
                text_file.write(" | ")
        text_file.write(")")
        if i<num_of_nodes-1:
            text_file.write(" & ")
        text_file.write(debug)
    # Determine allowed transitions according to feature in node
    text_file.write(" & ")
    for i in range(num_of_nodes):
        for f in range(num_of_features):
            text_file.write("(")
            text_file.write(f"lam_{i:d}_{f:d} => ")
            for j in range(num_of_nodes):
                for ff in range(num_of_features):
                    if j!=i and ff!=f:
                        for s in range(num_of_samples):
                            text_file.write(f"   !tau_{i:d}_{feature_var_id[(ff,s)]}_{j:d}")
                            if not ((ff==num_of_features-1 or (ff==num_of_features-2 and f==num_of_features-1)) and (j==num_of_nodes-1 or (j==num_of_nodes-2 and i==num_of_nodes-1)) and s==num_of_samples-1):
                                text_file.write(" & ")
                            text_file.write(debug)
            text_file.write(")")
            if not(i==num_of_nodes-1 and f==num_of_features-1):
                text_file.write(" & ")
            text_file.write(debug)
    # Rules for label nodes: label nodes can only be reached from non-label nodes
    text_file.write(" & ")
    for i in range(num_of_nodes):
        for f in range(num_of_features):
            text_file.write("(")
            text_file.write(f"lam_{i:d}_{f:d} => ")
            for j in [True,False]:
                for ff in range(num_of_features):
                    if ff!=f:
                        for s in range(num_of_samples):
                            text_file.write(f"   !tau_{i:d}_{feature_var_id[(ff,s)]}_{j}")
                            if not ((ff==num_of_features-1 or (ff==num_of_features-2 and f==num_of_features-1)) and (j==False) and s==num_of_samples-1):
                                text_file.write(" & ")
                            text_file.write(debug)
            text_file.write(")")
            if not(i==num_of_nodes-1 and f==num_of_features-1):
                text_file.write(" & ")
            text_file.write(debug)

    text_file.write(";\n")

    # Create phi_R: relation between and Gamma: valid instantiation of T if it accepts one sample. 
    # Maximize then over number of accepted samples
    text_file.write("phi_R := ")
    # Path encoding: at each position on node of T is determined and only one node. Two nodes are connected via a transition in T
    for i in range(num_of_nodes+1): 
        text_file.write("(")
        for j in range(num_of_nodes+2): # +2 for true and false nodes
            text_file.write("(")
            if j==num_of_nodes:
                tempnode = True
            elif j==num_of_nodes+1:
                tempnode = False
            if j<num_of_nodes:
                text_file.write(f"P{i:d}{j:d}")
            else:
                text_file.write(f"P{i:d}{tempnode}")
            for jj in range(num_of_nodes+2):
                if jj!=j:
                    text_file.write(" & ")
                    if jj==num_of_nodes:
                        tempnode = True
                    elif jj==num_of_nodes+1:
                        tempnode = False
                    if jj<num_of_nodes:
                        text_file.write(f"!P{i:d}{jj:d}")
                    else:
                        text_file.write(f"!P{i:d}{tempnode}")

            text_file.write(")")
            if j<num_of_nodes+1:
                text_file.write(" | ")
        text_file.write(")")
        if i<num_of_nodes:
            text_file.write(" & ")
        text_file.write(debug)
    # if end node reach then repeated until end
    text_file.write("&")
    text_file.write(debug)
    for i in range(num_of_nodes+1):
        text_file.write("(")
        text_file.write(f"P{i:d}True => P{i+1:d}True")
        text_file.write(" & ")
        text_file.write(f"P{i:d}False => P{i+1:d}False")
        text_file.write(")")
        if i<num_of_nodes:
            text_file.write(" & ")
    
    text_file.write(debug)
    text_file.write("&")
    text_file.write(debug)
    # between two nodes on the path there must be a transition
    for p in range(1,num_of_nodes+1):
        text_file.write("(")
        for i in range(num_of_nodes):
            for f in range(num_of_features):
                for s in range(num_of_samples):
                    for j in range(num_of_nodes+2):
                        if j!=i:
                            if j==num_of_nodes:
                                tempnode = True
                            elif j==num_of_nodes+1:
                                tempnode = False
                            if j<num_of_nodes:
                                text_file.write(f"delta_{p:d}_{i:d}_{feature_var_id[(f,s)]}_{j:d}")
                            else:
                                text_file.write(f"delta_{p:d}_{i:d}_{feature_var_id[(f,s)]}_{tempnode}")
                            
                            text_file.write(" | ")
                            text_file.write(debug)
        text_file.write(f"delta_{p:d}_End")
        text_file.write(")")
        text_file.write(debug)
        if p<num_of_nodes:
            text_file.write(" & ")
    
    # transition must be valid
    text_file.write(" & ")
    text_file.write(debug)
    for p in range(1,num_of_nodes+1):
        for i in range(num_of_nodes):
            for f in range(num_of_features):
                for s in range(num_of_samples):
                    for j in range(num_of_nodes+2):
                        if j!=i:
                            text_file.write("(")
                            if j<num_of_nodes:
                                text_file.write(f"delta_{p:d}_{i:d}_{feature_var_id[(f,s)]}_{j:d} => P{p-1:d}{i:d} & P{p:d}{j:d} & {feature_var_id[(f,s)]}")
                            elif j==num_of_nodes:
                                text_file.write(f"delta_{p:d}_{i:d}_{feature_var_id[(f,s)]}_True => P{p-1:d}{i:d} & P{p:d}{True} & {feature_var_id[(f,s)]}")
                            else:
                                text_file.write(f"delta_{p:d}_{i:d}_{feature_var_id[(f,s)]}_False => P{p-1:d}{i:d} & P{p:d}{False} & {feature_var_id[(f,s)]}")
                            text_file.write(")")
                            text_file.write(debug)
                            text_file.write("&")

    text_file.write("True")    
   

    text_file.write(";\n")
    text_file.write("FORMULA := phi_Gamma & phi_T & phi_R;\n")
    text_file.write("ASSIGN FORMULA;")
    text_file.close()


    

########## testing ###########
