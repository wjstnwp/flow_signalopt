from flow.controllers import IDMController, RLController
from flow.core.params import SumoParams, EnvParams, InitialConfig, NetParams
from flow.core.params import VehicleParams, SumoLaneChangeParams
from flow.envs import TestEnv
from flow.core.params import TrafficLightParams
from nets.single_lane import SingleLane
from nets.single_lane import ADDITIONAL_NET_PARAMS
from envs.single_lane import SingleLaneEnv, ADDITIONAL_ENV_PARAMS, TestEnv

vehicles = VehicleParams()

# Human vehicle
# vehicles.add(
#     veh_id="human",
#     acceleration_controller=(IDMController, {}),
#     lane_change_params=SumoLaneChangeParams(
#          model="SL2015",
#          lc_sublane=2.0,
#          ),
#     num_vehicles=1
#     )

# RL vehicle
vehicles.add(
    veh_id="rl",
    acceleration_controller=(RLController, {}),
    lane_change_params=SumoLaneChangeParams(
         model="SL2015",
         lc_sublane=2.0,
         ),
    num_vehicles=1
    )

sim_params = SumoParams(sim_step=0.1, render=True, lateral_resolution=0.1)
env_params = EnvParams(horizon=2000, additional_params=ADDITIONAL_ENV_PARAMS.copy())
net_params = NetParams(additional_params=ADDITIONAL_NET_PARAMS.copy())

tl_logic = ADDITIONAL_ENV_PARAMS["tl_logic"]

flow_params = dict(
    exp_tag='single_lane',
    env_name=SingleLaneEnv,
    network=SingleLane,
    simulator='traci',
    sim=sim_params,
    env=env_params,
    net=net_params,
    veh=vehicles,
    initial=InitialConfig(),
    tls = tl_logic
)

