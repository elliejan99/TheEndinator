import numpy as np


# P0: Same height, increasing distances
# P1: Increasing height, same distance
# P2: Various height, various distance
# Distance based on num_mobs_killed
def build_pillar(mobs_killed, p0_mobs_killed, phase):
    res = []

    height = ((mobs_killed - p0_mobs_killed) // 3) + 1
    distance = (mobs_killed // 3) + 2

    # MAX limit
    if distance > 29:
        distance = 29

    if height > 29:
        height = 29
    x = np.random.randint(-2, 3)
    if phase == 0:
        s = "<DrawBlock x='{x}'  y='60' z='{z}' type='glowstone'/>".format(z=distance, x=x)
        res.append(s)

        s = "<DrawEntity x='{x}'  y='61' z='{z}' type='Pig'/>".format(z=distance, x=x)
        res.append(s)

    elif phase == 1:
        y = 60 + height
        for i in range(60, y):
            s = "<DrawBlock x='1'  y='{y}' z='10' type='glowstone'/>".format(y=i)
            res.append(s)

        s = "<DrawEntity x='1'  y='{y}' z='10' type='Pig'/>".format(y=y)
        res.append(s)

    else:
        z = np.random.randint(1, distance)
        y = np.random.randint(60, 60 + height)

        for i in range(60, y + 1):
            s = "<DrawBlock x='1'  y='{y}' z='{z}' type='glowstone'/>".format(y=i, z=z)
            res.append(s)

        s = "<DrawEntity x='1'  y='{y}' z='{z}' type='Pig'/>".format(y=y + 1, z=z)
        res.append(s)

    return res


def get_mission_xml(mobs_killed, p0_mobs_killed, size, phase, max_episode_steps):
    return '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
            <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

                <About>
                    <Summary>TheEndinator</Summary>
                </About>

                <ServerSection>
                    <ServerInitialConditions>
                        <Time>
                            <StartTime>1000</StartTime>
                            <AllowPassageOfTime>false</AllowPassageOfTime>
                        </Time>
                        <AllowSpawning> true </AllowSpawning>
                        <AllowedMobs> Pig </AllowedMobs>
                        <Weather>clear</Weather>
                    </ServerInitialConditions>
                    <ServerHandlers>
                        <FlatWorldGenerator generatorString="3;7,2;1;"/>
                        <DrawingDecorator>
                            <DrawCuboid x1="-40" y1="50" z1="-40" x2="99" y2="100" z2="40" type="stone"/>
                            <DrawCuboid x1="-39" y1="51" z1="-39" x2="39" y2="99" z2="39" type="air"/>
                            <DrawBlock x='0'  y='60' z='0' type='air' />
                            <DrawBlock x='0'  y='59' z='0' type='glowstone' />
                         ''' + \
           "".join(build_pillar(mobs_killed, p0_mobs_killed, phase)) + \
           '''
           </DrawingDecorator>
           <ServerQuitWhenAnyAgentFinishes/>
       </ServerHandlers>
   </ServerSection>

   <AgentSection mode="Survival">
       <Name>TheEndinator</Name>
       <AgentStart>
           <Placement x="1" y="60" z="0" pitch="0" yaw="0"/>
           <Inventory>
               <InventoryItem slot="0" type="bow"/>
               <InventoryItem slot="1" type="arrow" quantity="64"/>
           </Inventory>
       </AgentStart>
       <AgentHandlers>
           <RewardForDamagingEntity>
               <Mob reward="15" type="Pig"/>
           </RewardForDamagingEntity>            
           <RewardForDiscardingItem>
               <Item reward="-1" type="arrow"/>
           </RewardForDiscardingItem>
           <RewardForTimeTaken initialReward="0" delta="-0.1" density="PER_TICK"/>
           <ContinuousMovementCommands/>
           <ObservationFromFullStats/>
           <ObservationFromFullInventory/>
           <ObservationFromRay/>
           <ObservationFromNearbyEntities>
                   <Range name="NearbyEntities" xrange="40" yrange="40" zrange="40" />
           </ObservationFromNearbyEntities>
           <MissionQuitCommands/>
           <AgentQuitFromReachingCommandQuota total="''' + str(max_episode_steps * 6) + '''" />
                        <AgentQuitFromTouchingBlockType>
                            <Block type="bedrock" />
                        </AgentQuitFromTouchingBlockType>
                    </AgentHandlers>
                </AgentSection>
            </Mission>'''
