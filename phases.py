import numpy as np

#P0: Same height, various distances
#P1: Various height, same distance
#P2: Various height, various distance
def build_pillar(low, high, phase):
    res = []

    if phase == 0:
        x = np.random.randint(low,high)
        z = np.random.randint(low,high)
        dist = np.sqrt( np.square(x) + (np.square(z)))
        
        for y in range(60, 65):
            s = "<DrawBlock x='{x}'  y='{y}' z='{z}' type='glowstone'/>".format(x=x, y=y, z=z)
            res.append(s)

        s = "<DrawEntity x='{x}'  y='65' z='{z}' type='Pig'/>".format(x=x, z=z)
        res.append(s)
        
    elif phase == 1:
        y = np.random.randint(60, 70)
        dist = np.sqrt( np.square(x) + (np.square(z)))
        
        for y in range(y):
            s = "<DrawBlock x='5'  y='{y}' z='5' type='glowstone'/>".format(y=y)
            res.append(s)

        s = "<DrawEntity x='5'  y='{y}' z='5' type='Pig'/>".format(y=y+1)
        res.append(s)
        
    else:
        x = np.random.randint(low,high)
        z = np.random.randint(low,high)
        y = np.random.randint(60, 70)
        dist = np.sqrt( np.square(x) + (np.square(z)))
        
        for y in range(5):
            s = "<DrawBlock x='{x}'  y='{y}' z='{z}' type='glowstone'/>".format(x=x, y=y, z=z)
            res.append(s)

        s = "<DrawEntity x='{x}'  y='{y}' z='{z}' type='Pig'/>".format(x=x, y=y+1, z=z)
        res.append(s)

    return res


def get_mission_xml(low, high, size, phase, max_episode_steps):
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
                            <DrawSphere x="0" y="60" z="0" radius="40" type="stone"/>
                            <DrawSphere x="0" y="60" z="0" radius="38" type="air"/>
                            <DrawBlock x='0'  y='60' z='0' type='air' />
                            <DrawBlock x='0'  y='59' z='0' type='glowstone' />
                         ''' + \
                        "".join(build_pillar(low, high, phase)) + \
                        '''
                        </DrawingDecorator>
                        <ServerQuitWhenAnyAgentFinishes/>
                    </ServerHandlers>
                </ServerSection>

                <AgentSection mode="Survival">
                    <Name>TheEndinator</Name>
                    <AgentStart>
                        <Placement x="0.5" y="60" z="0.5" pitch="0" yaw="0"/>
                        <Inventory>
                            <InventoryItem slot="0" type="bow"/>
                            <InventoryItem slot="1" type="arrow" quantity="64"/>
                        </Inventory>
                    </AgentStart>
                    <AgentHandlers>
                        <RewardForDamagingEntity>
                            <Mob reward="10" type="Pig"/>
                        </RewardForDamagingEntity>            
                        <RewardForDiscardingItem>
                            <Item reward="-1" type="arrow"/>
                        </RewardForDiscardingItem>
                        <ContinuousMovementCommands/>
                        <ObservationFromFullStats/>
                        <ObservationFromRay/>
                        <ObservationFromNearbyEntities>
                                <Range name="NearbyEntities" xrange="30" yrange="30" zrange="30" />
                        </ObservationFromNearbyEntities>
                        <AgentQuitFromReachingCommandQuota total="''' + str(max_episode_steps * 3) + '''" />
                        <AgentQuitFromTouchingBlockType>
                            <Block type="bedrock" />
                        </AgentQuitFromTouchingBlockType>
                    </AgentHandlers>
                </AgentSection>
            </Mission>'''
