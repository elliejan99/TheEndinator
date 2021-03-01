# Rllib docs: https://docs.ray.io/en/latest/rllib.html

try:
    from malmo import MalmoPython
except:
    import MalmoPython

import sys
import time
import json
import matplotlib.pyplot as plt
import numpy as np
from numpy.random import randint

import gym, ray
from gym.spaces import Discrete, Box
from ray.rllib.agents import ppo

from phases import get_mission_xml

class TheEndinator(gym.Env):

    def __init__(self, env_config):
        # Static Parameters
        self.size = 50
        self.reward_density = .1
        self.penalty_density = .02
        self.obs_size = 4
        self.max_episode_steps = 100
        self.log_frequency = 10

        self.low = -10
        self.high = 10
        self.phase = 0
        
        # Rllib Parameters #pitch, turn, use
        self.action_space = Box(-1, 1, shape=(3,), dtype=np.float32)
        self.observation_space = Box(-360, 360, shape=(self.obs_size,), dtype=np.float32)

        # Malmo Parameters
        self.agent_host = MalmoPython.AgentHost()
        try:
            self.agent_host.parse(sys.argv)
        except RuntimeError as e:
            print('ERROR:', e)
            print(self.agent_host.getUsage())
            exit(1)

        # TheEndinator Parameters
        self.obs = None
        self.allow_shoot = False
        self.pitch = 0
        self.yaw = 0
        self.episode_step = 0
        self.episode_return = 0
        self.returns = []
        self.steps = []
        self.tick = 30
        self.episode_reward_mean = 0

    def reset(self):
        """
        Resets the environment for the next episode.

        Returns
            observation: <np.array> flattened initial obseravtion
        """
        # Reset Malmo
        world_state = self.init_malmo()

        # Reset Variables
        self.returns.append(self.episode_return)
        current_step = self.steps[-1] if len(self.steps) > 0 else 0
        self.steps.append(current_step + self.episode_step)
        self.episode_return = 0
        self.episode_step = 0

        # Log
        if len(self.returns) > self.log_frequency + 1 and \
            len(self.returns) % self.log_frequency == 0:
            self.log_returns()

        # Get Observation
        self.obs, self.allow_shoot = self.get_observation(world_state)

        return self.obs

    def step(self, action):
        """
        Take an action in the environment and return the results.

        Args
            action: <int> index of the action to take

        Returns
            observation: <np.array> flattened array of obseravtion
            reward: <int> reward from taking action
            done: <bool> indicates terminal state
            info: <dict> dictionary of extra information
        """
        # return action to be performed and the reward
        # this function can get the action, perform it, and calculate the reward that it gives

        # Get Action
        shoot = 0
        if action[2] >= 0:
            shoot = 1

        if shoot != 1 or self.allow_shoot:
            if shoot == 1:
                self.agent_host.sendCommand('turn 0')
                self.agent_host.sendCommand('use {}'.format(shoot))
                self.agent_host.sendCommand('pitch {}'.format(action[0]))
                time.sleep(0.1)

                self.agent_host.sendCommand('pitch 0')
                time.sleep(1.1)

                self.agent_host.sendCommand('use 0')
                
            else:
                self.agent_host.sendCommand('use {}'.format(shoot))
                self.agent_host.sendCommand('pitch {}'.format(action[0]))
                self.agent_host.sendCommand('turn {}'.format(action[1]))
                time.sleep(.1)

        self.episode_step += 1

        # Get Observation
        world_state = self.agent_host.getWorldState()
        for error in world_state.errors:
            print("Error:", error.text)
        self.obs, self.allow_shoot = self.get_observation(world_state)

        # Get Done
        done = not world_state.is_mission_running

        # Get Reward
        reward = 0
        for r in world_state.rewards:
            reward += r.getValue()
        self.episode_return += reward
        if reward > 0:
            self.agent_host.sendCommand("quit")

        return self.obs, reward, done, dict()

    def init_malmo(self):
        """
        Initialize new malmo mission.
        """
        #TODO change which get_mission_xml is called based on a measure for success 

        my_mission = MalmoPython.MissionSpec(get_mission_xml(self.low, self.high, self.size, self.phase, self.max_episode_steps), True)
        my_mission_record = MalmoPython.MissionRecordSpec()
        my_mission.requestVideo(800, 500)
        my_mission.setViewpoint(0)

        max_retries = 3
        my_clients = MalmoPython.ClientPool()
        my_clients.add(MalmoPython.ClientInfo('127.0.0.1', 10000)) # add Minecraft machines here as available

        for retry in range(max_retries):
            try:
                self.agent_host.startMission( my_mission, my_clients, my_mission_record, 0, 'TheEndinator' )
                break
            except RuntimeError as e:
                if retry == max_retries - 1:
                    print("Error starting mission:", e)
                    exit(1)
                else:
                    time.sleep(2)

        world_state = self.agent_host.getWorldState()
        while not world_state.has_mission_begun:
            time.sleep(0.1)
            world_state = self.agent_host.getWorldState()
            for error in world_state.errors:
                print("\nError:", error.text)

        return world_state

    def get_observation(self, world_state):
        """
        Use the agent observation API to get a flattened 2 x 5 x 5 grid around the agent.
        The agent is in the center square facing up.

        Args
            world_state: <object> current agent world state

        Returns
            observation: <np.array> the state observation
            allow_break_action: <bool> whether the agent is facing a diamond
        """
        obs = np.zeros((self.obs_size, ))
        allow_shoot = False

        while world_state.is_mission_running:
            time.sleep(0.1)
            world_state = self.agent_host.getWorldState()
            if len(world_state.errors) > 0:
                raise AssertionError('Could not load grid.')

            if world_state.number_of_observations_since_last_state > 0:
                # First we get the json from the observation API
                msg = world_state.observations[-1].text
                observations = json.loads(msg)

                # Get observation


                # Rotate observation with orientation of agent
                yaw = observations['Yaw']
                distance = -1
                obs = obs.flatten()
                try:
                    allow_shoot = observations['LineOfSight']['type'] == 'Pig'
                    distance = observations['LineOfSight']['distance']
                except:
                    pass

                self.pitch = observations['Pitch']
                self.yaw = observations['Yaw']
                obs[0] = self.pitch
                obs[1] = self.yaw
                obs[2] = distance
                obs[3] = allow_shoot
                print(obs)

                break

        return obs, allow_shoot

    def log_returns(self):
        """
        Log the current returns as a graph and text file

        Args:
            steps (list): list of global steps after each episode
            returns (list): list of total return of each episode
        """
        box = np.ones(self.log_frequency) / self.log_frequency
        returns_smooth = np.convolve(self.returns[1:], box, mode='same')
        plt.clf()
        plt.plot(self.steps[1:], returns_smooth)
        plt.title('The Endinator')
        plt.ylabel('Return')
        plt.xlabel('Steps')
        plt.savefig('returns.png')

        with open('returns.txt', 'w') as f:
            for step, value in zip(self.steps[1:], self.returns[1:]):
                f.write("{}\t{}\n".format(step, value)) 

    def set_phase(self, phase):
        self.phase = phase

if __name__ == '__main__':
    ray.init()
    trainer = ppo.PPOTrainer(env=TheEndinator, config={
        'env_config': {},           # No environment parameters to configure
        'framework': 'torch',       # Use pyotrch instead of tensorflow
        'num_gpus': 0,              # We aren't using GPUs
        'num_workers': 0,            # We aren't using parallelism
        'optimizer': {}
    })

    #import the model from file
    try:
        trainer.import_model("my_weights.h5")
    except:
        print("No preview weights recorded")
    
    for i in range(1000):
        # Perform one iteration of training the policy with PPO
        result = trainer.train()
        if result["episode_reward_mean"] > 100:
            phase = 2
        elif result["episode_reward_mean"] > 50:
            phase = 1
        else:
            phase = 0

        trainer.workers.foreach_worker(
            lambda ev: ev.foreach_env(
                lambda env: env.set_phase(phase)))

        #every 100 episodes we save the data
        if i % 100 == 0:
            checkpoint = trainer.save()
            print("checkpoint saved at", checkpoint)