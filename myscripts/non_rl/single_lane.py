from flow.controllers import IDMController, RLController
from flow.core.params import SumoParams, EnvParams, InitialConfig, NetParams
from flow.core.params import VehicleParams, SumoCarFollowingParams, SumoLaneChangeParams
from flow.envs import TestEnv
from flow.core.params import TrafficLightParams
from myscripts.nets.single_lane import SingleLane
from myscripts.nets.single_lane import ADDITIONAL_NET_PARAMS
from flow.envs.ring.accel import ADDITIONAL_ENV_PARAMS
import random
from myscripts.envs.single_lane import SingleLaneEnv
from myscripts.envs import single_lane

vehicles = VehicleParams()
dur1 = single_lane.duration1
dur2 = single_lane.duration2

# Human vehicle
vehicles.add(
    veh_id="human",
    acceleration_controller=(IDMController, {}),
    lane_change_params=SumoLaneChangeParams(
         model="SL2015",
         lc_sublane=2.0,
         ),
    num_vehicles=1
    )

# RL vehicle
# vehicles.add(
#     veh_id="rl",
#     acceleration_controller=(RLController, {}),
#     lane_change_params=SumoLaneChangeParams(
#          model="SL2015",
#          lc_sublane=2.0,
#          ),
#     num_vehicles=1
#     )

sim_params = SumoParams(sim_step=0.1, render=True, lateral_resolution=0.1)
env_params = EnvParams(horizon=2000, additional_params=ADDITIONAL_ENV_PARAMS.copy())
net_params = NetParams(additional_params=ADDITIONAL_NET_PARAMS.copy())

tl_logic =  TrafficLightParams(baseline = False)
phases = [{"duration": "{0}".format(dur1), "state": "GrGr"},
          {"duration": "{0}".format(dur2), "state": "yryr"},
          {"duration": "{0}".format(dur1), "state": "rGrG"},
          {"duration": "{0}".format(dur2), "state": "ryry"}]

offset = random.randint(0, dur1+dur2+1)
tl_logic.add("t.l.", phases=phases, offset=offset)

flow_params = dict(
    exp_tag='single_lane',
    env_name=TestEnv,
    network=SingleLane,
    simulator='traci',
    sim=sim_params,
    env=env_params,
    net=net_params,
    veh=vehicles,
    initial=InitialConfig(),
    tls = tl_logic
)

