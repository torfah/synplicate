import sys
sys.path.insert(0,"examples/loan_acquisition/")
import feature_defs

def execute(inputs):
	program_nodes ={}

	program_edges ={}

	features = feature_defs.retrieve_feature_defs()

	value_map = {} 

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

