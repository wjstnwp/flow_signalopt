from flow.core.params import InitialConfig
from flow.core.params import TrafficLightParams
from flow.networks import Network
import random

net_len = random.randint(200, 1000)
ADDITIONAL_NET_PARAMS = {
    "length" : net_len,
    "lanes" : 1,
    # nodes: start, tl, stop  ->  edges: before_tl, after_tl
    "num_edges" : 2,
    "num_nodes" : 3, 
    "speed_limit" : 20,
    "position_tl" : net_len - 100
}

class SingleLane(Network):
    def __init__(self,
                 name,
                 vehicles,
                 net_params,
                 initial_config=InitialConfig(),
                 traffic_lights=TrafficLightParams()):

        for p in ADDITIONAL_NET_PARAMS.keys():
            if p not in net_params.additional_params:
                raise KeyError('Network parameter "{}" not supplied'.format(p))

        super().__init__(name, vehicles, net_params, initial_config, traffic_lights)
    
    def specify_nodes(self, net_params):
        length = net_params.additional_params["length"]
        seg_length1 = net_params.additional_params["position_tl"]

        nodes = [{
            "id": "start",
            "x": 0,
            "y": 0
        }, {
           "id": "t.l.",
            "x": seg_length1,
            "y": 0
        }, {
            "id": "stop",
            "x": length,
            "y": 0
        }]

        return nodes

    def specify_edges(self, net_params):
        length = net_params.additional_params["length"]
        seg_length1 = net_params.additional_params["position_tl"]
        seg_length2 = length-seg_length1

        edges = [{
            "id": "before_tl",
            "type": "highwayType",
            "from": "start",
            "to": "t.l.",
            "length": seg_length1
        }, {
            "id": "after_tl",
            "type": "highwayType",
            "from": "t.l.",
            "to": "stop",
            "length": seg_length2
        }]

        return edges

    def specify_types(self, net_params):
        lanes = net_params.additional_params["lanes"]
        speed_limit = net_params.additional_params["speed_limit"]

        types = [{
            "id": "highwayType",
            "numLanes": lanes,
            "speed": speed_limit
        }]

        return types

    def specify_routes(self, net_params):
        rts = {
            "before_tl": ["before_tl", "after_tl"]
        }

        return rts

    def specify_edge_starts(self):
        junction_length = 0.1
        seg_length1 = self.net_params.additional_params["position_tl"]

        edge_starts = [
            ("before_tl", 0+junction_length),
            ("after_tl", seg_length1+junction_length),
            ]

        return edge_starts

    def specify_internal_edge_starts(self):
        junction_length = 0.1

        return super().specify_internal_edge_starts()