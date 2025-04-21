import sys
sys.path.insert(0,"examples/loan_acquisition/")
import feature_defs

def execute(inputs):
	program_nodes ={}
	program_nodes["2"]= "age"
	program_nodes["1"]= "age"
	program_nodes["0"]= "monthly_income"

	program_edges ={}
	program_edges[("2",3)]= "approved_0"
	program_edges[("2",2)]= "approved_0"
	program_edges[("2",1)]= "approved_0"
	program_edges[("2",0)]= "approved_0"
	program_edges[("1",3)]= "approved_1"
	program_edges[("1",2)]= "approved_1"
	program_edges[("1",1)]= "approved_1"
	program_edges[("1",0)]= "approved_0"
	program_edges[("0",1)]= "1"
	program_edges[("0",0)]= "approved_1"

	features = feature_defs.retrieve_feature_defs()

	value_map = {} 
	value_map["age"] = features["age"]([("age",inputs[0]),("monthly_income",inputs[1])])
	value_map["age"] = features["age"]([("age",inputs[0]),("monthly_income",inputs[1])])
	value_map["monthly_income"] = features["monthly_income"]([("age",inputs[0]),("monthly_income",inputs[1])])

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

