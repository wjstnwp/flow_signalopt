from flow.envs import Env
from gym.spaces.box import Box
from flow.core import rewards
from gym.spaces import Tuple
from flow.core.params import TrafficLightParams
import numpy as np
import random

offset = random.randint(0,41)
duration1 = 40
duration2 = 10

ADDITIONAL_ENV_PARAMS = {
    "max_accel" : 2,
    "max_decel" : 1,
    "target_speed" : 20,
    "tl_logic" : None,
}

def set_tllogic():
    tl_logic =  TrafficLightParams(baseline = False)
    phases = [{"duration": "{0}".format(duration1), "state": "GrGr"},
              {"duration": "{0}".format(duration2), "state": "yryr"},
              {"duration": "{0}".format(duration1), "state": "rGrG"},
              {"duration": "{0}".format(duration2), "state": "ryry"}]

    offset = random.randint(0, duration1+duration2+1)
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
        
        self.time = 0

    def action_space(self):
        num_actions = self.initial_vehicles.num_rl_vehicles
        accel_ub = self.env_params.additional_params["max_accel"]
        accel_lb = - abs(self.env_params.additional_params["max_decel"])

        return Box(low=accel_lb,
                   high=accel_ub,
                   shape=(num_actions,))

    def observation_space(self):
        speed = Box(
            low = 0,
            high = 1,
            shape = (self.initial_vehicles.num_vehicles,),
            dtype = np.float32)

        pos = Box(
            low = 0,
            high = np.inf,
            shape = (self.initial_vehicles.num_vehicles,),
            dtype = np.float32)
        
        return Tuple((speed, pos))

    def _apply_rl_actions(self, rl_actions):
        rl_ids = self.k.vehicle.get_rl_ids()
        self.k.vehicle.apply_acceleration(rl_ids, rl_actions)

    def get_state(self, **kwargs):
        ids = self.k.vehicle.get_ids()
        speed = [self.k.vehicle.get_speed(veh_id) for veh_id in ids]
        pos = [self.k.vehicle.get_x_by_id(veh_id) for veh_id in ids]
        pos_to_tl = [self.k.network.edge_length("before_tl") - pos(veh_id) for veh_id in ids]

        


        return np.concatenate((speed, pos, pos_to_tl))

    def compute_reward(self, rl_actions, **kwargs):
        ids = self.k.vehicle.get_ids()
        speeds = self.k.vehicle.get_speed(ids)

        return np.mean(speeds)

    def timer(self):
        self.time += self.sim_step
            

