---
layout: default
title: Proposal
---
## Summary of the Project
For our project, our goal is to build an AI that can perform the first step in defeating the ender dragon. This will require the agent to find and shoot stationary
end crystals. Our AI needs to be able to utilize a bow to hit targets at varying heights and distances. This will require the agent to learn how much strength to utilize when drawing back the bow and what angle to aim their arrow in order to hit the targets. The input will be the position and angle of the agent relative to the targets. The output will be the agent’s strength used to draw back the bow and the angle and direction at which they aim it based on a learned policy.The input will be the position of the agent relative to the entities the agents are trying to shoot. The output will be the agent’s determined movements and actions such as shooting an arrow after using a learned policy.

## AI/ML Algorithms
We’re planning to use deep Q-learning and reinforcement learning to implement this agent.

## Evaluation Plan
Although our goal is to be able to destroy all of the end crystals as a first step to killing the ender dragon, we are having the agent train in a more controlled environment with pigs placed on blocks at certain heights and distances. Since the goal of our agent is to hit various targets at different angles and distances, we can measure its level of success by counting the number targets it’s able to hit within a certain number of arrows. At first, the agent won’t know how much to draw back their bow as well as where the arrow needs to be fired in order to hit the target, resulting in a majority of missed shots. But by the end of the training, we expect our agent to be able to hit most of the targets. Over time, we should be able to watch our agent improve at using the bow, such as by the degree that it pulls back the arrow and the angle at which it shoots. Every time it’s able to hit the target, the agent will update its policy and should gradually become more successful.

## Appointment with the Instructor
January 27th - 3 PM

## Weekly Team Meetings
Thursdays at 3 PM
