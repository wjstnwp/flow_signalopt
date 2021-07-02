from flow.controllers import IDMController, ContinuousRouter
from flow.core.params import SumoParams, EnvParams, InitialConfig, NetParams
from flow.core.params import VehicleParams, InFlows, SumoCarFollowingParams, SumoLaneChangeParams
from flow.envs.ring.accel import ADDITIONAL_ENV_PARAMS
from flow.networks.traffic_light_grid import TrafficLightGridNetwork
from flow.envs import TestEnv
from flow.core.params import TrafficLightParams
from flow.networks import Network
import numpy as np
import random
from flow.core.experiment import Experiment

ADDITIONAL_NET_PARAMS = {
    "length" : 1000,
    "lanes" : 1,
    # nodes: start, tl, stop  ->  edges: before_tl, after_tl
    "num_edges" : 1,
    "num_nodes" : 3, 
    "speed_limit" : 30,
    "position_tl" : random.randint(100, 900)
}

class myNetwork(Network):
    def __init__(self,
                 name,
                 vehicles,
                 net_params,
                 initial_config=InitialConfig(),
                 traffic_lights=TrafficLightParams()):

        for p in ADDITIONAL_NET_PARAMS.keys():
            if p not in net_params.additional_params:
                raise KeyError('Network parameter "{}" not supplied'.format(p))

        super().__init__(name, vehicles, net_params, initial_config,
                         traffic_lights)
    
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
        seg_length1 = net_params.additional_params["position_tl"]

        edge_starts = [
            ("before_tl", 0+junction_length),
            ("after_tl", seg_length1+junction_length),
            ]

        return edge_starts

    def specify_internal_edge_starts(self):
        junction_length = 0.1


        return super().specify_internal_edge_starts()

vehicles = VehicleParams()
vehicles.add(
    veh_id="human",
    acceleration_controller=(IDMController, {}),
    car_following_params=SumoCarFollowingParams(min_gap=0.5),
    lane_change_params=SumoLaneChangeParams(
        model="SL2015",
        lc_sublane=2.0,
    ),
    )

inflow = InFlows()
inflow.add(
    veh_type="human",
    edge="before_tl",
    vehs_per_hour=1000,
    depart_lane="free",
    depart_speed=20
)

sim_params = SumoParams(sim_step=0.1, render=True, lateral_resolution=0.1)
env_params = EnvParams(additional_params=ADDITIONAL_ENV_PARAMS)

net_params = NetParams(inflows=inflow, additional_params=ADDITIONAL_NET_PARAMS.copy())

tl_logic =  TrafficLightParams(baseline = False)
phases = [{"duration": "31", "minDur": "8", "maxDur": "45", "state": "GrGr"},
          {"duration": "6", "minDur": "3", "maxDur": "6", "state": "yryr"},
          {"duration": "31", "minDur": "8", "maxDur": "45", "state": "rGrG"},
          {"duration": "6", "minDur": "3", "maxDur": "6", "state": "ryry"}]

tl_logic.add("t.l.", phases=phases)

flow_params = dict(
    exp_tag='hw1-2',
    env_name=TestEnv,
    network=myNetwork,
    simulator='traci',
    sim=sim_params,
    env=env_params,
    net=net_params,
    veh=vehicles,
    initial=InitialConfig(),
    tls = tl_logic
)

flow_params['env'].horizon = 3000
exp = Experiment(flow_params)

# run the sumo simulation
_ = exp.run(1, convert_to_csv=False)