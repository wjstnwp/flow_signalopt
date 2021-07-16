from flow.envs import Env
from gym.spaces.box import Box
from flow.core import rewards
from gym.spaces import Tuple
import numpy as np

ADDITIONAL_ENV_PARAMS = {
    "max_accel" : 1,
    "max_decle" : 1,
    "target_speed" : 20,
    "tl_logic" : None,
}

def set_tllogic():
    tl_logic = TrafficLightParams

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
        pos_to_tl = [self.k.network.edge_length("befoer_tl") - pos(veh_id) for veh_id in ids]

        self.k.traffic_light


        return np.concatenate((speed, pos, pos_to_tl))

    def compute_reward(self, rl_actions, **kwargs):
        ids = self.k.vehicle.get_ids()
        speeds = self.k.vehicle.get_speed(ids)

        return np.mean(speeds)

