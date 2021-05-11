import os



def extract_soft_variables(dimacs):
    print("|---Extracting soft variables...")  
    soft_vars = []
    text_file = open(dimacs)

    for line in text_file.readlines():
        if not line.startswith("c"):
            break
        
        current_num = ""
        if ("match_0" in line or " lam_" in line or "used_node_" in line):
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
            if "used_node_" in line:
                if(("-",current_num,1) not in soft_vars):
                    soft_vars.append(("-",current_num,1))
            else:
                if (("",current_num,1) not in soft_vars):
                    soft_vars.append(("",current_num,1))

    text_file.close()    
    return soft_vars

def dimacs_to_wcnf(wcnf_file, dimacs_path, soft_vars):
    print("|---Writing WCNF File...")  
    text_file = open(dimacs_path)

    # print(pi_vars)
    hard_limit = len(soft_vars) + 1
    for line in text_file.readlines():
        if  line.startswith("c"):
            wcnf_file.write(line)
            continue
           
        if line.startswith('p cnf'):
            #print (line)
            var = line.split(' ')[2]
            numClauses=int(line.split(' ')[3])
            # print (var, numClauses)
            wcnf_file.write("p wcnf ")
            wcnf_file.write(var)
            wcnf_file.write(" ")
            wcnf_file.write(str(numClauses+ len(soft_vars))) 
            wcnf_file.write(f" {hard_limit}  \n")  #limit for hard clauses
            # add soft clauses
            for sign,var,weight in soft_vars:
                wcnf_file.write(f"{weight} {sign}{var} {0}\n")
        else: 
            # words = line.split()
            # first_var = words[0]
            # second_var = words[1]
            # if ((first_var in soft_vars) and (int(second_var) == 0)):
            #     wcnf_file.write(f"1 {first_var} {second_var}\n") 
            # else:
            wcnf_file.write(f"{hard_limit} {line}")

    text_file.close()    





def encode(encoder, output_dir_path,samples,num_of_feature_nodes,feature_partition,label_partition,feature_defs,lower_bound, upper_bound, precision, weights_map, file_name):

    # create max#sat file
    os.system(f"mkdir -p {output_dir_path}")
    sat_file_path = output_dir_path+file_name
    sat_file = open(sat_file_path,"w")
    sat_file.write("BC1.1\n")

    # phi_E
    encoder.phi_E(sat_file,num_of_feature_nodes,feature_partition,label_partition)
    sat_file.write("\n")

    # phi_sim 
    encoder.phi_sim(sat_file,num_of_feature_nodes,feature_partition,label_partition,samples,feature_defs)
    sat_file.write("\n")

    # phi_corr
    encoder.phi_corr(sat_file,samples)
    sat_file.write("\n") 

    # phi_expl
    encoder.phi_expl(sat_file,num_of_feature_nodes,feature_partition,label_partition)
    sat_file.write("\n")   

    # phi_region
    for node in range(num_of_feature_nodes):
        weights_map[f"used_node_{node:d}"]= 1
        for feature, bucket in feature_partition.items():
            weights_map[f"lam_{node:d}_{feature}"] = 1
    encoder.phi_region(sat_file,num_of_feature_nodes,feature_partition,lower_bound,upper_bound,weights_map,precision)


    sat_file.write("FORMULA :=  phi_E & phi_sim & phi_corr & phi_expl & phi_region;\n")
    

    sat_file.write("ASSIGN FORMULA;")
    sat_file.close()


    # create dimacs file
    dimacs_path = output_dir_path+"encoding_temp.dimacs"

    print("Translating to dimacs...")
    os.system(f"./synthesizer/max_sat/bc2cnf -all  {sat_file_path} {dimacs_path}")


    print("Translating to wcnfdimacs...")
    wcnf_path = output_dir_path+file_name+".wcnf"
    soft_vars = extract_soft_variables(dimacs_path)
    wcnf_file = open(wcnf_path,"w")
    dimacs_to_wcnf(wcnf_file, dimacs_path, soft_vars)
    wcnf_file.close()

    return wcnf_path

