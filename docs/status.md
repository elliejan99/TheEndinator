---
layout: default
title: Status
---
## Video Summary

<iframe width="560" height="315" src="https://www.youtube.com/watch?v=5POyuojgjSk&feature=youtu.be" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>

## Project Summary

On the quest to defeat the final boss of Minecraft, players must first destroy all the ender crystals that lie atop large 
pillars in the dragon’s arena. To simulate this, the goal of our project is to use reinforcement learning in order to train 
our agent to accurately shoot objects at varying heights and distances with a bow. This process involves having the agent look 
for objects to shoot, as well as adjusting the vertical and horizontal angle of their arrow in order to hit their targets. 

## Approach

The main algorithm that we’re using to train our agent is reinforcement learning. Our agent begins their mission in the center 
of a flat area surrounded by entities at varying heights and distances and is given a bow and several arrows. The agent mainly 
uses ObservationFromRay, to detect whether or not there’s an entity to shoot at in the center of their screen. We also utilize 
ObervationFromFullStats in order to keep track of the number of arrows that our agent has used.

There are an infinite number of states as our agent utilizes continuous movement. To transition from one state to another, the agent
takes three actions. The actions are changing pitch (looking up and down), changing turn (looking left and right), and deciding whether
or not to use their bow. The agent will always change their pitch and turn, but whether or not they use their bow is dependent on 
the observations received from ObservationFromRay. If there’s no entity to shoot in the agent’s line of sight, the agent will simply 
change their pitch and turn in order to look for an entity to shoot. However, if there is an entity in the agent’s line of sight, then 
the agent is permitted to shoot. Our agent freezes itself, adjusts the angle of its arrow vertically and horizontally, and releases its 
arrow. The sleep time for the agent is set to 1.2 in order to ensure that the agent has enough time to pull back its arrow and release 
it in the correct direction.

If the agent misses the target, they’re given a penalty of 1, and if the agent hits the target, they’re given a reward of 10. To implement
this, we penalized the agent for every arrow they used (ie. discarded) and rewarded it based on whether or not it did damage to an entity. 
Based on the rewards or punishments our agent receives, it updates its policy accordingly and slowly learns the best vertical and horizontal 
angle needed to hit its target. Our project utilizes the PPOtrainer from Rllib in order to maximize the number of entities damaged in a single run. 

## Evaluation

## Remaining Goals and Challenges

One of the most critical goals we have going forward is to change the primary algorithm that we’re using to train our agent from 
reinforcement learning to deep Q-learning. We believe that deep Q-learning would allow our agent to develop a better policy and allow 
for more ambitiously placed targets. Our prototype has only been trained on targets at the same low height, so we hope to give it 
more experience with targets at varying heights and distances. This ties in to our ultimate goal of having our agent be able to shoot 
targets on top of the tall and far pillars in the ender dragon’s domain. To test that, another goal we have is to create more fine-tuned 
maps that will enable us to systematically test our agent’s aim as each mission we currently trainour agent on is randomized. Lastly, 
we hope to experiment with different hand-coded policies in order to figure out which yield the best results.

Some challenges we anticipate that we’ll face in the near future include finding more ways to evaluate our agent’s performance as well as 
figuring out what major changes will be needed in order to change the primary algorithm we use to train our agent. To begin with, we currently
evaluate our agent based on the number of hits and misses that result from the agent shooting its bow, but we’d like to be able to see the 
entire trajectory of our agent’s arrow as well as how well the agent is accounting for height and distance when aiming its arrow. We currently 
haven’t implemented a way to obtain such data, but by creating less-randomized maps as well as setting up a second agent to observe the trajectory 
of the first agent’s arrow, we may be able to gather this data. Furthermore, changing our primary training algorithm may require large changes to 
our code and research which may prove to be time-consuming.  But we hope to look into various libraries and other resources in order to make the 
change to deep Q-learning as smooth as possible.

## Resources Used

Deep Q Learning - https://keras-rl.readthedocs.io/en/latest/agents/overview/
