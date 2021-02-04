import sys
sys.path.insert(0,"experiments/ICML/AutoTaxi/")
import feature_defs

def execute(inputs):
	program_nodes ={}
	program_nodes["2"]= "init_pos"
	program_nodes["1"]= "clouds"
	program_nodes["0"]= "clouds"

	program_edges ={}
	program_edges[("2",3)]= "alert_1"
	program_edges[("2",2)]= "alert_0"
	program_edges[("2",1)]= "alert_0"
	program_edges[("2",0)]= "alert_0"
	program_edges[("1",5)]= "2"
	program_edges[("1",4)]= "alert_1"
	program_edges[("1",3)]= "alert_1"
	program_edges[("1",2)]= "alert_1"
	program_edges[("1",1)]= "2"
	program_edges[("1",0)]= "2"
	program_edges[("0",5)]= "2"
	program_edges[("0",4)]= "2"
	program_edges[("0",3)]= "alert_1"
	program_edges[("0",2)]= "2"
	program_edges[("0",1)]= "1"
	program_edges[("0",0)]= "1"

	features = feature_defs.retrieve_feature_defs()

	value_map = {} 
	value_map["init_pos"] = features["init_pos"]([("clouds",inputs[0]),("day_time",inputs[1]),("init_pos",inputs[2])])
	value_map["clouds"] = features["clouds"]([("clouds",inputs[0]),("day_time",inputs[1]),("init_pos",inputs[2])])
	value_map["clouds"] = features["clouds"]([("clouds",inputs[0]),("day_time",inputs[1]),("init_pos",inputs[2])])

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

