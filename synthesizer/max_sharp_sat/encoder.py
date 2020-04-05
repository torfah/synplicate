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
            for j in range(num_of_samples):
                if (feature_var_id[(f,j)]!=feature_var_id[(f,i)]):
                    sat_file.write("!")
                    sat_file.write(feature_var_id[(f,j)])
                    if j<num_of_samples-2 or (j==num_of_samples-2 and i!=num_of_samples-1): 
                        sat_file.write(" & ")
            if i<num_of_samples-1:
                sat_file.write(")& ")
                sat_file.write("\n")
            else:
                sat_file.write(")")
        sat_file.write(")")
        if f<(num_of_inputs + num_of_labels)-1:
            sat_file.write("& ")
        sat_file.write("\n")

    sat_file.write(";\n")

def phi_T(sat_file,num_of_feature_nodes,feature_partition,label_partition):
    sat_file.write("phi_T :=")

    sat_file.write(";\n")

def encode(output_path,samples,num_of_feature_nodes,feature_partition,label_partition):

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


    sat_file.write("FORMULA := phi_Gamma & phi_T;\n")
    sat_file.write("ASSIGN FORMULA;")
    sat_file.close()

    # create dimac file with mmc parameters 
    dimacs_tempfile_path = output_path+"encoding_temp.dimacs"

    os.system(f"./synthesizer/max_sharp_sat/bc2cnf -all {sat_file_path} {dimacs_tempfile_path}")

    dimacs_file_path = output_path+"encoding.dimacs"
    return dimacs_file_path