import numpy as np

def build_pillar():
    res = []

    #End pillars height (6,37)
    #End pillars distance 47 blocks in a circle
    distance = [(0,30), (25,25), (30,0), (25,-25), (0,-30), (-25,-25), (-30,0), (-25,25)]

    for (x,z) in distance:
        height = 60 + np.random.randint(6, 30)
        for y in range(60, height):
            s = "<DrawBlock x='{x}'  y='{y}' z='{z}' type='glowstone'/>".format(x=x, y=y, z=z)
            res.append(s)

        s = "<DrawEntity x='{x}'  y='{y}' z='{z}' type='Pig'/>".format(x=x, y=height, z=z)
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
                        "".join(build_pillar()) + \
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

