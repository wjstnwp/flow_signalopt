from flow.core.params import SumoParams, EnvParams, InitialConfig, NetParams
from flow.core.params import VehicleParams, SumoCarFollowingParams
from flow.controllers import RLController, IDMController, ContinuousRouter
from flow.envs import WaveAttenuationPOEnv
from flow.networks import RingNetwork

HORIZON = 1500
N_CPUS = 2
N_ROLLOUTS = 1

vehicles = VehicleParams()
vehicles.add(
    veh_id="human",
    acceleration_controller=(IDMController, {}),
    car_following_params=SumoCarFollowingParams(),
    routing_controller=(ContinuousRouter, {}),
    num_vehicles=21)
vehicles.add(
    veh_id="rl",
    acceleration_controller=(RLController, {}),
    routing_controller=(ContinuousRouter, {}),
    num_vehicles=1)

sim_params = SumoParams(sim_step=0.1, render=False)

ADDITIONAL_ENV_PARAMS = {
    "max_accel": 1,
    "max_decel": 1,
    "ring_length": [220, 270],
}
env_params = EnvParams(horizon=HORIZON, additional_params=ADDITIONAL_ENV_PARAMS)

ADDITIONAL_NET_PARAMS = {
    "length": 250,
    "lanes": 1,
    "speed_limit": 30,
    "resolution": 40,
}
net_params = NetParams(additional_params=ADDITIONAL_NET_PARAMS)

flow_params = dict(
    exp_tag='hw1-2',
    env_name=WaveAttenuationPOEnv,
    network=RingNetwork,
    simulator='traci',
    sim=sim_params,
    env=env_params,
    net=net_params,
    veh=vehicles,
    initial=InitialConfig(),
)

import json

import ray
try:
    from ray.rllib.agents.agent import get_agent_class
except ImportError:
    from ray.rllib.agents.registry import get_agent_class
from ray.tune import run_experiments
from ray.tune.registry import register_env

from flow.utils.registry import make_create_env
from flow.utils.rllib import FlowParamsEncoder

ray.init(num_cpus=N_CPUS, ignore_reinit_error = True)

alg_run = "PPO"

agent_cls = get_agent_class(alg_run)
config = agent_cls._default_config.copy()
config["num_workers"] = N_CPUS - 1  # number of parallel workers
config["train_batch_size"] = HORIZON * N_ROLLOUTS  # batch size
config["gamma"] = 0.999  # discount rate
config["model"].update({"fcnet_hiddens": [16, 16]})  # size of hidden layers in network
config["use_gae"] = True  # using generalized advantage estimation
config["lambda"] = 0.97  
config["sgd_minibatch_size"] = min(16 * 1024, config["train_batch_size"])  # stochastic gradient descent
config["kl_target"] = 0.02  # target KL divergence
config["num_sgd_iter"] = 10  # number of SGD iterations
config["horizon"] = HORIZON  # rollout horizon

flow_json = json.dumps(flow_params, cls=FlowParamsEncoder, sort_keys=True, indent=4)

config['env_config']['flow_params'] = flow_json
config['env_config']['run'] = alg_run

create_env, gym_name = make_create_env(params=flow_params, version=0)

register_env(gym_name, create_env)

trials = run_experiments({
    flow_params["exp_tag"]: {
        "run": alg_run,
        "env": gym_name,
        "config": {
            **config
        },
        "checkpoint_freq": 1,  # number of iterations between checkpoints
        "checkpoint_at_end": True,  # generate a checkpoint at the end
        "max_failures": 999,
        "stop": {  # stopping conditions
            "training_iteration": 300,  # number of iterations to stop after
        },
    },
})