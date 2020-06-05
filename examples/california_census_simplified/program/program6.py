import sys
sys.path.insert(0,"examples/california_census_simplified/")
import feature_defs

def execute(inputs):
	program_nodes ={}
	program_nodes["0"]= "median_income"

	program_edges ={}
	program_edges[("0",1)]= "Class_1"
	program_edges[("0",0)]= "Class_1"

	features = feature_defs.retrieve_feature_defs()

	value_map = {} 
	value_map["median_income"] = features["median_income"]([("population",inputs[0]),("median_income",inputs[1])])

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

