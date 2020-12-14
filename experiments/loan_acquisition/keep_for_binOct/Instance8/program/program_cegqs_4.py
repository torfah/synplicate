import sys
sys.path.insert(0,"experiments/loan_acquisition/")
import feature_defs

def execute(inputs):
	program_nodes ={}
	program_nodes["9"]= "age"
	program_nodes["8"]= "credit_score"
	program_nodes["7"]= "monthly_income"
	program_nodes["6"]= "credit_score"
	program_nodes["5"]= "credit_score"
	program_nodes["4"]= "dependents"
	program_nodes["3"]= "age"
	program_nodes["2"]= "dependents"
	program_nodes["1"]= "age"
	program_nodes["0"]= "monthly_income"

	program_edges ={}
	program_edges[("9",3)]= "approved_0"
	program_edges[("9",2)]= "approved_1"
	program_edges[("9",1)]= "approved_0"
	program_edges[("9",0)]= "approved_1"
	program_edges[("8",2)]= "approved_0"
	program_edges[("8",1)]= "approved_1"
	program_edges[("8",0)]= "approved_0"
	program_edges[("7",1)]= "8"
	program_edges[("7",0)]= "9"
	program_edges[("6",2)]= "approved_0"
	program_edges[("6",1)]= "approved_0"
	program_edges[("6",0)]= "7"
	program_edges[("5",2)]= "approved_1"
	program_edges[("5",1)]= "8"
	program_edges[("5",0)]= "approved_0"
	program_edges[("4",1)]= "5"
	program_edges[("4",0)]= "6"
	program_edges[("3",3)]= "approved_1"
	program_edges[("3",2)]= "approved_1"
	program_edges[("3",1)]= "8"
	program_edges[("3",0)]= "approved_0"
	program_edges[("2",1)]= "3"
	program_edges[("2",0)]= "approved_1"
	program_edges[("1",3)]= "approved_1"
	program_edges[("1",2)]= "2"
	program_edges[("1",1)]= "2"
	program_edges[("1",0)]= "4"
	program_edges[("0",1)]= "1"
	program_edges[("0",0)]= "1"

	features = feature_defs.retrieve_feature_defs()

	value_map = {} 
	value_map["age"] = features["age"]([("age",inputs[0]),("monthly_income",inputs[1]),("dependents",inputs[2]),("credit_score",inputs[3])])
	value_map["credit_score"] = features["credit_score"]([("age",inputs[0]),("monthly_income",inputs[1]),("dependents",inputs[2]),("credit_score",inputs[3])])
	value_map["monthly_income"] = features["monthly_income"]([("age",inputs[0]),("monthly_income",inputs[1]),("dependents",inputs[2]),("credit_score",inputs[3])])
	value_map["credit_score"] = features["credit_score"]([("age",inputs[0]),("monthly_income",inputs[1]),("dependents",inputs[2]),("credit_score",inputs[3])])
	value_map["credit_score"] = features["credit_score"]([("age",inputs[0]),("monthly_income",inputs[1]),("dependents",inputs[2]),("credit_score",inputs[3])])
	value_map["dependents"] = features["dependents"]([("age",inputs[0]),("monthly_income",inputs[1]),("dependents",inputs[2]),("credit_score",inputs[3])])
	value_map["age"] = features["age"]([("age",inputs[0]),("monthly_income",inputs[1]),("dependents",inputs[2]),("credit_score",inputs[3])])
	value_map["dependents"] = features["dependents"]([("age",inputs[0]),("monthly_income",inputs[1]),("dependents",inputs[2]),("credit_score",inputs[3])])
	value_map["age"] = features["age"]([("age",inputs[0]),("monthly_income",inputs[1]),("dependents",inputs[2]),("credit_score",inputs[3])])
	value_map["monthly_income"] = features["monthly_income"]([("age",inputs[0]),("monthly_income",inputs[1]),("dependents",inputs[2]),("credit_score",inputs[3])])

	flag = True
	current_node = "0"
	while flag:
		current_feature = program_nodes[current_node]
		next_node = program_edges[current_node,value_map[current_feature]]
		if next_node.isdigit():
			current_node = next_node
		else:
			current_node = next_node
			flag = False
	return current_node

