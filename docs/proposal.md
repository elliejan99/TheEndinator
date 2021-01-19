---
layout: default
title: Proposal
---
##Summary of the Project
For our project, our goal is to build an AI that can defeat the ender dragon. This will require the agent to find and shoot stationary
end crystals, shoot a moving target, and avoid the dragon’s attacks. The input will be the position of the agent relative to the dragon
and end crystals. The output will be the agent’s determined movements and actions such as shooting an arrow after using a learned policy.

##AI/ML Algorithms
We’re planning to use Q-learning and neural networks to implement this agent.

##Evaluation Plan
Since the goal of our agent is to defeat the ender dragon, we can measure its level of success by counting the number of end crystals 
it’s able to destroy as well as the percentage of health the dragon still has before the player dies. At first, the agent won’t be able 
to aim their bow correctly, resulting in no end crystals being destroyed but by the end of the training, we expect our agent to be able 
to destroy most of the end crystals and take a portion of the dragon’s health. 

Over time, we should be able to watch our agent improve at using the bow, such as by the degree that it pulls back the arrow and the 
angle at which it shoots. Additionally, we hope to see it eventually avoid the dragon’s attacks, such as stepping out of the range of 
its fireball. Every time it’s able to damage the dragon or avoid dying to its attacks, the agent will update its policy and should 
gradually become more successful. 

##Appointment with the Instructor
January 27th - 3 PM
