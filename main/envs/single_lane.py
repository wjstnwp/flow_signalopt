from flow.envs import Env
from gym.spaces.box import Box
from flow.core import rewards
from gym.spaces import Tuple
from flow.core.params import TrafficLightParams
import numpy as np
import random

duration1 = 30
duration2 = 10
offset = random.randint(0, duration1+duration2+1)

ADDITIONAL_ENV_PARAMS = {
    "max_accel" : 1,
    "max_decel" : 1,
    "tl_logic" : None,
}

def set_tllogic():
    tl_logic =  TrafficLightParams(baseline = False)
    phases = [{"duration": "{0}".format(duration1), "state": "GrGr"},
              {"duration": "{0}".format(duration2), "state": "yryr"},
              {"duration": "{0}".format(duration1), "state": "rGrG"},
              {"duration": "{0}".format(duration2), "state": "ryry"}]

    tl_logic.add("t.l.", phases=phases, offset=offset)

    return tl_logic

ADDITIONAL_ENV_PARAMS["tl_logic"] = set_tllogic()

class SingleLaneEnv(Env):
    def __init__(self, env_params, sim_params, network, simulator='traci'):
        for p in ADDITIONAL_ENV_PARAMS.keys():
            if p not in env_params.additional_params:
                raise KeyError(
                    'Environment parameter \'{}\' not supplied'.format(p))

        super().__init__(env_params, sim_params, network, simulator)
        if env_params.additional_params['tl_logic'] is not None:
            self.tl_logic = env_params.additional_params['tl_logic']
        else:
            self.tl_logic = None

    @property
    def action_space(self):
        num_actions = self.initial_vehicles.num_rl_vehicles
        accel_ub = self.env_params.additional_params["max_accel"]
        accel_lb = - abs(self.env_params.additional_params["max_decel"])

        return Box(low = accel_lb,
                   high = accel_ub,
                   shape = (num_actions,),)

    @property
    def observation_space(self):
        return Box(low = -0, 
                   high = float("inf"),
                   shape = (4*self.initial_vehicles.num_vehicles,),)

    def _apply_rl_actions(self, rl_actions):
        rl_ids = self.k.vehicle.get_rl_ids()
        self.k.vehicle.apply_acceleration(rl_ids, rl_actions)

    def get_state(self, **kwargs):
        ids = self.k.vehicle.get_ids()
        # speed = [self.k.vehicle.get_speed(veh_id) for veh_id in ids]
        # pos_to_tl = [(self.k.network.edge_length("before_tl") - self.k.vehicle.get_x_by_id(veh_id)) for veh_id in ids]
        # pos_to_tl1 = list(map(lambda x: max(x,0), pos_to_tl))
        if len(ids) != 0:
            current_time = self.k.vehicle.get_timestep(ids[0])/1000
            speed = [self.k.vehicle.get_speed(veh_id) for veh_id in ids]
            pos_to_tl = [(self.k.network.edge_length("before_tl") - self.k.vehicle.get_x_by_id(veh_id)) for veh_id in ids]
            pos_to_tl1 = list(map(lambda x: max(x,0), pos_to_tl))
        else:
            current_time = 0
            speed = [0]
            pos_to_tl1 = [0]

        time_to_greenstart = [(duration1+duration2-offset-current_time)%(duration1+duration2)]
        time_to_greenend = [(duration1-offset-current_time)%(duration1+duration2)]

        return np.concatenate((speed, pos_to_tl1, time_to_greenstart, time_to_greenend))

    def compute_reward(self, rl_actions, **kwargs):
        # reward = rewards.rl_forward_progress(self) + rewards.energy_consumption(self)
        reward = rewards.rl_forward_progress(self)
        return reward
            
  
# class TestEnv(Env):
#     def action_space(self):
#         return Box(low=0, high=0, shape=(0,), dtype=np.float32)

#     def observation_space(self):
#         return Box(low=0, high=0, shape=(0,), dtype=np.float32)

#     def _apply_rl_actions(self, rl_actions):
#         return

#     def compute_reward(self, rl_actions, **kwargs):
#         if "reward_fn" in self.env_params.additional_params:
#             return self.env_params.additional_params["reward_fn"](self)
#         else:
#             return 0

#     def get_state(self, **kwargs):
#         return np.array([])