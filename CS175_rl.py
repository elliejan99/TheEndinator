try:
    from malmo import MalmoPython
except:
    import MalmoPython

import os
import shutil

import sys
import time
import json
import matplotlib.pyplot as plt
import numpy as np
from numpy.random import randint
import math

import gym, ray
from gym.spaces import Discrete, Box
from ray.rllib.agents import ppo, dqn

from phases import get_mission_xml

class TheEndinator(gym.Env):

    def __init__(self, env_config):
        self.size = 50
        self.obs_size = 5
        self.max_episode_steps = 100
        self.log_frequency = 2

        self.action_space = Box(-1 / 3, 1 / 3, shape=(3,), dtype=np.float32)
        self.observation_space = Box(-360, 360, shape=(self.obs_size,), dtype=np.float32)

        self.agent_host = MalmoPython.AgentHost()
        try:
            self.agent_host.parse(sys.argv)
        except RuntimeError as e:
            print('ERROR:', e)
            print(self.agent_host.getUsage())
            exit(1)

        self.obs = None
        self.allow_shoot = False
        self.pitch = 0
        self.yaw = 0
        self.num_mobs_killed = 0
        self.p0_mobs_killed = 0
        self.phase = 0

        self.steps = []
        self.returns = []
        self.episode_step = 0
        self.episode_return = 0
        self.episode_reward_mean = 0
        self.distance = []
        self.start_time = 0
        self.end_time = 0
        self.time_taken = [] 
        self.num_arrows = 0
        self.last_normal = 0
        
    def reset(self):
        world_state = self.init_malmo()

        if self.end_time < self.start_time:
            self.end_time = time.time()
        self.time_taken.append(self.end_time - self.start_time)

        self.returns.append(self.episode_return)
        current_step = self.steps[-1] if len(self.steps) > 0 else 0
        self.steps.append(current_step + self.episode_step)

        if len(self.time_taken) > self.log_frequency + 1 and \
                len(self.time_taken) % self.log_frequency == 0:
            self.log_time_taken()

        if len(self.returns) > self.log_frequency + 1 and \
                len(self.returns) % self.log_frequency == 0:
            self.log_returns()

        if len(self.steps) > 1 and len(self.distance) > 1:
            with open('distanceTime.txt', 'a') as f:
                f.write("{}\t{}\t{}\t{}\t{}\n".format(self.steps[-1], self.distance[-1], self.start_time, self.end_time,
                                                      self.end_time - self.start_time))

            with open('distanceArrows.txt', 'a') as f:
                f.write(
                    "{}\t{}\t{}\t{}\n".format(self.steps[-1], self.distance[-1], self.num_arrows, self.episode_return))

            with open('distanceYaw.txt', 'a') as f:
                f.write("{}\t{}\t{}\t{}\t{}\n".format(self.steps[-1], self.phase, self.distance[-1], self.obs[3],
                                                      self.episode_return))

        self.episode_return = 0
        self.episode_step = 0

        self.obs, self.allow_shoot, _ = self.get_observation(world_state)
        self.distance.append(self.obs[1])
        self.start_time = time.time()

        return self.obs

    def step(self, action):
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
                pitch_condition = self.pitch >= 60 and action[0] > 0 or self.pitch <= -60 and action[0] < 0
                yaw_condition = self.yaw >= 60 and action[1] > 0 or self.yaw <= -60 and action[1] < 0
                if pitch_condition and yaw_condition:
                    self.agent_host.sendCommand('pitch 0')
                    self.agent_host.sendCommand('turn 0')
                    self.agent_host.sendCommand('use {}'.format(shoot))
                elif pitch_condition:
                    self.agent_host.sendCommand('pitch 0')
                    self.agent_host.sendCommand('turn {}'.format(action[1]))
                    self.agent_host.sendCommand('use {}'.format(shoot))
                elif yaw_condition:
                    self.agent_host.sendCommand('turn 0')
                    self.agent_host.sendCommand('pitch {}'.format(action[0]))
                    self.agent_host.sendCommand('use {}'.format(shoot))
                else:
                    self.agent_host.sendCommand('pitch {}'.format(action[0]))
                    self.agent_host.sendCommand('turn {}'.format(action[1]))
                    self.agent_host.sendCommand('use {}'.format(shoot))

                time.sleep(.02)

        self.episode_step += 1

        # Get Observation
        world_state = self.agent_host.getWorldState()
        for error in world_state.errors:
            print("Error:", error.text)
        self.obs, self.allow_shoot, norm = self.get_observation(world_state)

        # Get Done
        done = not world_state.is_mission_running

        # Get Reward
        reward = 0
        if not self.allow_shoot:
            reward += norm - 0.6
        elif self.allow_shoot:
            reward += 0.5
        for r in world_state.rewards:
            reward += r.getValue()
        self.episode_return += reward

        self.last_normal = norm
        return self.obs, reward, done, dict()

    def init_malmo(self):
        my_mission = MalmoPython.MissionSpec(
            get_mission_xml(self.num_mobs_killed, self.p0_mobs_killed, self.size, self.phase, self.max_episode_steps),
            True)
        my_mission_record = MalmoPython.MissionRecordSpec()
        my_mission.requestVideo(800, 500)
        my_mission.setViewpoint(0)

        max_retries = 3
        my_clients = MalmoPython.ClientPool()
        my_clients.add(MalmoPython.ClientInfo('127.0.0.1', 10000))  

        for retry in range(max_retries):
            try:
                self.agent_host.startMission(my_mission, my_clients, my_mission_record, 0, 'TheEndinator')
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
        obs = np.zeros((self.obs_size,))
        allow_shoot = False

        while world_state.is_mission_running:
            time.sleep(0.1)
            world_state = self.agent_host.getWorldState()
            if len(world_state.errors) > 0:
                raise AssertionError('Could not load grid.')

            if world_state.number_of_observations_since_last_state > 0:
                msg = world_state.observations[-1].text
                observations = json.loads(msg)

                self.num_mobs_killed = observations['MobsKilled']
                self.pitch = observations['Pitch']
                self.yaw = observations['Yaw']
                self.num_arrows = observations['InventorySlot_1_size']
                
                obs = obs.flatten()

                try:
                    allow_shoot = observations['LineOfSight']['type'] == 'Pig'
                except:
                    pass

                obs[2] = allow_shoot

                try:
                    agent_pos = np.array([observations['XPos'], observations['YPos'], observations['ZPos']])
                    agent_dir = np.array([observations['LineOfSight']['x'], observations['LineOfSight']['y'],
                                          observations['LineOfSight']['z']]) - agent_pos
                    pig_pos = np.array([0, 0, 0])
                    found_pig = False
                    for entity in observations['NearbyEntities']:
                        if entity['name'] == 'Pig':
                            found_pig = True
                            pig_pos = np.array([entity['x'], entity['y'], entity['z']])
                            obs[0] = self.dot_agent_pig(pig_pos - agent_pos, agent_dir)
                            break

                    if not found_pig:
                        self.end_time = time.time()
                        self.agent_host.sendCommand("quit")

                    obs[1] = np.linalg.norm(pig_pos - agent_pos)
                    obs[3] = self.yaw
                    obs[4] = self.pitch
                except:
                    pass

                break
        return obs, allow_shoot, obs[0]

    def dot_agent_pig(self, pig_dir, agent_dir):
        pig_norm = np.linalg.norm(pig_dir)
        agent_norm = np.linalg.norm(agent_dir)
        if agent_norm == 0:
            return np.dot(pig_dir / pig_norm, agent_dir)

        return np.dot(pig_dir / pig_norm, agent_dir / agent_norm)

    def log_time_taken(self):
        box = np.ones(self.log_frequency) / self.log_frequency
        time_taken_smooth = np.convolve(self.time_taken[1:], box, mode='same')
        plt.clf()
        plt.plot(self.steps[1:], time_taken_smooth)
        plt.title('The Endinator')
        plt.ylabel('Time Taken')
        plt.xlabel('Steps')
        plt.savefig('timeTaken.png')

    def log_returns(self):
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

        if phase == 1:
            self.p0_mobs_killed = self.num_mobs_killed


if __name__ == '__main__':
    checkpoint_root = "tmp/exa"
    shutil.rmtree(checkpoint_root, ignore_errors=True, onerror=None)

    ray_results = "{}/ray_result/".format(os.getenv("HOME"))
    shutil.rmtree(ray_results, ignore_errors=True, onerror=None)

    ray.init()
    trainer = ppo.PPOTrainer(env=TheEndinator, config={
        'env_config': {},  # No environment parameters to configure
        'framework': 'torch',  # Use pyotrch instead of tensorflow
        'num_gpus': 0,  # We aren't using GPUs
        'num_workers': 0,  # We aren't using parallelism
        'optimizer': {}
    })
    
    try:
        trainer.import_model("my_weights.h5")
    except:
        print("No preview weights recorded")

    for i in range(1000):
        result = trainer.train()

        if i % 100 == 0:
            checkpoint_file = trainer.save(checkpoint_root)
            print(i + 1, result["episode_reward_min"],
                  result["episode_reward_mean"],
                  result["episode_reward_max"],
                  checkpoint_file)

        if result["episode_reward_mean"] > 120:
            phase = 2
        elif result["episode_reward_mean"] > 70:
            phase = 1
        else:
            phase = 0

        trainer.workers.foreach_worker(
            lambda ev: ev.foreach_env(
                lambda env: env.set_phase(phase)))

