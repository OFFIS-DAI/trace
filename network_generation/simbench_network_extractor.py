import math
import random
import warnings
import os
from abc import ABC, abstractmethod
from enum import Enum
from os.path import abspath
from pathlib import Path
import simbench as sb
import utm
from sklearn.cluster import KMeans
import numpy as np

from agent_communication_generation_tool.description_classes.agent import LeafAgent, CentralAgent, AggregatorAgent, \
    Agent

warnings.filterwarnings('ignore')

ROOT = str(Path(abspath(__file__)).parent.parent)


class SystemState(Enum):
    NORMAL = 0
    LIMITED = 1
    FAILED = 2


class CommunicationInfrastructure:
    def __init__(self, class_name: str, identifier: str, position: tuple):
        self.class_name = class_name
        self.identifier = identifier
        self.position = position


class CommunicationConnection:
    def __init__(self, connector_1: tuple,
                 connector_2: tuple, conn_type: str):
        self.connector_1 = connector_1
        self.connector_2 = connector_2
        self.conn_type = conn_type

    def get_connection_string(self) -> str:
        name_1 = name_2 = ''
        if isinstance(self.connector_1[0], Agent):
            name_1 = self.connector_1[0].omnet_name
        elif isinstance(self.connector_1[0], CommunicationInfrastructure):
            name_1 = self.connector_1[0].identifier
        if isinstance(self.connector_2[0], Agent):
            name_2 = self.connector_2[0].omnet_name
        elif isinstance(self.connector_2[0], CommunicationInfrastructure):
            name_2 = self.connector_2[0].identifier
        return f'{name_1}.{self.connector_1[1]} <--> {self.conn_type} <--> {name_2}.{self.connector_2[1]}'


def delete_old_config_section():
    # Open the file and read its contents
    with open('omnet_project_files/omnetpp.ini', 'r') as file:
        content = file.read()

    # Create the pattern string to search for
    pattern = f'[Config SimbenchNetwork]'

    # Check if the pattern exists in the file
    start_index = content.find(pattern)
    if start_index != -1:
        # Find the next occurrence of '[' after the pattern
        end_index = content.find('[Config', start_index + len(pattern))

        # If another '[' is found, delete everything from the pattern to the '['
        if end_index != -1:
            modified_content = content[:start_index] + content[end_index:]
        else:  # If no further '[' is found, delete everything from the pattern to the end of the file
            modified_content = content[:start_index]

        # Write the modified content back to the file
        with open('omnet_project_files/omnetpp.ini', 'w') as file:
            file.write(modified_content)
        print("File modified successfully.")
    else:
        print("Pattern not found in the file.")


class SimbenchNetworkExtractor(ABC):
    def __init__(self, simbench_code, system_state=SystemState.NORMAL):
        self.simbench_code = simbench_code
        self.simbench_network = None
        self.system_state = system_state

        self.port = 1000

        # communication infrastructure for OMNeT++ network definition
        self.communication_infrastructure = list()
        # communication connections for OMNeT++ network definition
        self.communication_connections = list()

        self.agents = list()
        self.traffic_devices = list()

        self.network_size = (0, 0)

        # agents from simbench power network
        self.household_agents = list()
        self.grid_infrastructure_agents = list()
        self.storage_agents = list()
        self.generation_agents = list()

        self.substation_agents = list()

        # generated agents
        self.control_center_agent = None
        self.market_agent = None
        self.aggregator_agent = None
        self.pdc_agent = None
        self.grid_operator_agent = None

    def initialize_network(self):
        config_name = 'SimbenchNetwork' + self.simbench_code.replace('-', '_')
        self.simbench_network = sb.get_simbench_net(self.simbench_code)

        self.get_agents_from_simbench_network()

        self.agents = (self.household_agents +
                       self.grid_infrastructure_agents +
                       self.storage_agents +
                       self.generation_agents +
                       self.substation_agents)

        self.rescale_network()
        self.add_control_agents()

        if self.system_state == SystemState.LIMITED or self.system_state == SystemState.FAILED:
            self.add_traffic_devices()
        self.place_communication_infrastructure()

        os.chdir(ROOT)

        delete_old_config_section()

        network_description = self.get_omnet_network_description()
        ini_config = self.get_omnet_ini_config()

        with open(f'omnet_project_files/networks/SimbenchNetwork.ned', 'w') as f:
            f.write(network_description)
            f.close()

        with open(f'omnet_project_files/omnetpp.ini', 'a') as config:
            config.write(ini_config)
            config.close()

        # save as result
        directory = "agent_communication_generation_tool/results/ned_files"

        ned_file_path = os.path.join(directory, f"{config_name}.ned")
        ini_file_path = os.path.join(directory, f"{config_name}.ini")

        # Check if the .ned file does not exist, then write
        if not os.path.exists(ned_file_path):
            with open(ned_file_path, 'w') as f:
                f.write(network_description)
        if not os.path.exists(ini_file_path):
            with open(ini_file_path, 'w') as f:
                f.write(ini_config)

    def get_network_area(self, agents=None):
        if not agents:
            agents = self.agents
        min_x = math.inf
        max_x = 0
        min_y = math.inf
        max_y = 0
        for agent in agents:
            if agent.coordinates[0] < min_x:
                min_x = agent.coordinates[0]
            if agent.coordinates[1] < min_y:
                min_y = agent.coordinates[1]
            if agent.coordinates[0] > max_x:
                max_x = agent.coordinates[0]
            if agent.coordinates[1] > max_y:
                max_y = agent.coordinates[1]
        return (min_x, min_y), (max_x, max_y)

    def rescale_network(self):
        (min_x, min_y), (max_x, max_y) = self.get_network_area()
        self.network_size = (max_x - min_x, max_y - min_y)
        for agent in self.agents:
            new_coords = (agent.coordinates[0] - min_x + 10, agent.coordinates[1] - min_y + 10)
            agent.coordinates = new_coords

    def get_port(self):
        port = self.port
        self.port += 1
        return port

    def get_agents_from_simbench_network(self):
        # grid infrastructure agents
        bus_measurements = self.simbench_network.measurement[self.simbench_network.measurement['element_type'] == 'bus']
        measurement_bus_ids = bus_measurements['element']
        unique_measurement_bus_ids = measurement_bus_ids.unique()
        measurement_bus_coordinates = self.simbench_network.bus_geodata.loc[unique_measurement_bus_ids]
        measurements_with_coordinates = (
            self.simbench_network.measurement.join(measurement_bus_coordinates, on='element', how='left',
                                                   rsuffix='_geo'))
        i = 0

        for index, row in measurements_with_coordinates.iterrows():
            self.grid_infrastructure_agents.append(
                LeafAgent(
                    omnet_name=f'grid_infrastructure_agent_{i}',
                    omnet_port=self.get_port(),
                    agent_type=LeafAgent.LeafAgentType.GRID_INFRASTRUCTURE_AGENT,
                    coordinates=utm.from_latlon(row['x'], row['y'])
                )
            )
            i += 1

        # load agents
        load_bus_ids = self.simbench_network.load['bus']
        load_bus_coordinates = self.simbench_network.bus_geodata.loc[load_bus_ids]
        loads_with_coordinates = (
            self.simbench_network.load.join(load_bus_coordinates, on='bus', how='left', rsuffix='_geo'))
        i = 0
        for index, row in loads_with_coordinates.iterrows():
            self.household_agents.append(
                LeafAgent(
                    omnet_name=f'household_agent_{i}',
                    omnet_port=self.get_port(),
                    agent_type=LeafAgent.LeafAgentType.HOUSEHOLD_AGENT,
                    coordinates=utm.from_latlon(row['x'], row['y'])
                )
            )
            i += 1

        # generation agents
        gen_bus_ids = self.simbench_network.sgen['bus']
        gen_bus_coordinates = self.simbench_network.bus_geodata.loc[gen_bus_ids]
        gens_with_coordinates = (
            self.simbench_network.sgen.join(gen_bus_coordinates, on='bus', how='left', rsuffix='_geo'))
        i = 0
        for index, row in gens_with_coordinates.iterrows():
            self.generation_agents.append(
                LeafAgent(
                    omnet_name=f'generation_agent_{i}',
                    omnet_port=self.get_port(),
                    agent_type=LeafAgent.LeafAgentType.GENERATION_AGENT,
                    coordinates=utm.from_latlon(row['x'], row['y'])
                )
            )
            i += 1

        # storage agents
        storage_bus_ids = self.simbench_network.storage['bus']
        storage_bus_coordinates = self.simbench_network.bus_geodata.loc[storage_bus_ids]
        storages_with_coordinates = (
            self.simbench_network.storage.join(storage_bus_coordinates, on='bus', how='left', rsuffix='_geo'))
        i = 0
        for index, row in storages_with_coordinates.iterrows():
            self.storage_agents.append(
                LeafAgent(
                    omnet_name=f'storage_agent_{i}',
                    omnet_port=self.get_port(),
                    agent_type=LeafAgent.LeafAgentType.STORAGE_AGENT,
                    coordinates=utm.from_latlon(row['x'], row['y'])
                )
            )
            i += 1
        """
        # substation agents
        substation_bus_ids = net.substation['bus']
        substation_bus_coordinates = net.bus_geodata.loc[substation_bus_ids]
        substation_with_coordinates = (
            net.storage.join(substation_bus_coordinates, on='bus', how='left', rsuffix='_geo'))
        i = 0
        for index, row in substation_with_coordinates.iterrows():
            self.substation_agents.append(
                AggregatorAgent(
                    omnet_name=f'substation_agent_{i}',
                    omnet_port=port,
                    agent_type=AggregatorAgent.AggregatorAgentType.SUBSTATION_AGENT,
                    coordinates=(row['x'], row['y'])
                )
            )
            port += 1
            i += 1"""

    def add_traffic_devices(self):
        num_traffic_devices = 0
        if self.system_state == SystemState.LIMITED:
            num_traffic_devices = 100
        elif self.system_state == SystemState.FAILED:
            num_traffic_devices = 500
        self.traffic_devices.extend([CommunicationInfrastructure(
            class_name='StandardHost',
            identifier=f'traffic_device_{i}',
            position=(random.randint(10, 100), random.randint(10, 100))
        ) for i in range(num_traffic_devices)])

    def add_aggregator_level_agents(self, centroid: tuple, cluster_id: int):
        new_agents = []
        # per cluster
        self.pdc_agent = (
            AggregatorAgent(omnet_name=f'pdc_agent_{cluster_id}', omnet_port=self.get_port(),
                            agent_type=AggregatorAgent.AggregatorAgentType.PDC_AGENT, coordinates=centroid)
        )
        new_agents.append(self.pdc_agent)

        if len(self.substation_agents) == 0:
            substation_agent = AggregatorAgent(omnet_name=f'substation_agent_{cluster_id}', omnet_port=self.get_port(),
                                               agent_type=AggregatorAgent.AggregatorAgentType.SUBSTATION_AGENT,
                                               coordinates=centroid)
            self.substation_agents.append(substation_agent)
            new_agents.append(substation_agent)
        self.agents.extend(new_agents)
        return new_agents

    def add_control_agents(self):
        # generated agents
        self.aggregator_agent = (
            AggregatorAgent(omnet_name='aggregator_agent', omnet_port=self.get_port(),
                            agent_type=AggregatorAgent.AggregatorAgentType.AGGREGATOR_AGENT,
                            coordinates=(100, 100))
        )
        self.agents.append(self.aggregator_agent)
        self.control_center_agent = (
            CentralAgent(omnet_name='control_center_agent', omnet_port=self.get_port(),
                         agent_type=CentralAgent.CentralAgentType.CONTROL_CENTER_AGENT, coordinates=(100, 100))
        )
        self.agents.append(self.control_center_agent)

        self.market_agent = (
            CentralAgent(omnet_name='market_agent', omnet_port=self.get_port(),
                         agent_type=CentralAgent.CentralAgentType.MARKET_AGENT, coordinates=(100, 100)))
        self.agents.append(self.market_agent)

        self.grid_operator_agent = (
            CentralAgent(omnet_name='grid_operator_agent', omnet_port=self.get_port(),
                         agent_type=CentralAgent.CentralAgentType.GRID_OPERATOR_AGENT, coordinates=(100, 100)))
        self.agents.append(self.grid_operator_agent)

        if not isinstance(self, SimbenchEthernetNetworkExtractor):
            position_middle = int(self.network_size[0]) / 2, int(self.network_size[1]) / 2
            self.add_aggregator_level_agents(position_middle, 0)

    @abstractmethod
    def place_communication_infrastructure(self):
        """
        Method that fills the following lists: self.communication_infrastructure and self.communication_connections.
        """
        pass

    @abstractmethod
    def get_omnet_network_description(self) -> str:
        """
        Bilds string for the OMNeT++ .ned network description file.
        :return: file as string.
        """
        pass

    def get_omnet_ini_config(self) -> str:
        pass


class Simbench5GNetworkExtractor(SimbenchNetworkExtractor):
    def __init__(self, simbench_code, system_state):
        super().__init__(simbench_code, system_state)

    def place_communication_infrastructure(self):
        # place channel control
        self.communication_infrastructure.append(
            CommunicationInfrastructure(
                class_name='LteChannelControl',
                identifier='channelControl',
                position=(100, 100)
            )
        )
        # place routing table recorder
        self.communication_infrastructure.append(
            CommunicationInfrastructure(
                class_name='RoutingTableRecorder',
                identifier='routingRecorder',
                position=(100, 100)
            )
        )
        # place configurator
        self.communication_infrastructure.append(
            CommunicationInfrastructure(
                class_name='Ipv4NetworkConfigurator',
                identifier='configurator',
                position=(100, 100)
            )
        )
        # place binder
        self.communication_infrastructure.append(
            CommunicationInfrastructure(
                class_name='Binder',
                identifier='binder',
                position=(100, 100)
            )
        )
        # place carrier aggregation
        self.communication_infrastructure.append(
            CommunicationInfrastructure(
                class_name='CarrierAggregation',
                identifier='carrierAggregation',
                position=(100, 100)
            )
        )
        # place server
        server = CommunicationInfrastructure(
            class_name='StandardHost',
            identifier='server',
            position=(100, 100)
        )
        self.communication_infrastructure.append(server)
        # place router
        router = CommunicationInfrastructure(
            class_name='Router',
            identifier='router',
            position=(100, 100)
        )
        self.communication_infrastructure.append(router)
        # place upf
        upf = CommunicationInfrastructure(
            class_name='Upf',
            identifier='upf',
            position=(100, 100)
        )
        self.communication_infrastructure.append(upf)
        # place iupf
        iupf = CommunicationInfrastructure(
            class_name='Upf',
            identifier='iUpf',
            position=(100, 100)
        )
        self.communication_infrastructure.append(iupf)
        # place gNodeBs
        gNodeB = CommunicationInfrastructure(
            class_name='gNodeB',
            identifier='gNB',
            position=(int(self.network_size[0]) / 2, int(self.network_size[1]) / 2)
        )  # TODO: maybe add multiple gNodeBs
        self.communication_infrastructure.append(gNodeB)

        # place background cell
        bgc = CommunicationInfrastructure(
            class_name='BackgroundCell',
            identifier='bgCell',
            position=(int(self.network_size[0]) / 2 - 10, int(self.network_size[1]) / 2 - 10)
        )
        self.communication_infrastructure.append(bgc)

        """
        Define connections
        """
        self.communication_connections.append(
            CommunicationConnection(
                connector_1=(server, 'pppg++'),
                connector_2=(router, 'pppg++'),
                conn_type='Eth10G'
            )
        )

        self.communication_connections.append(
            CommunicationConnection(
                connector_1=(router, 'pppg++'),
                connector_2=(upf, 'filterGate'),
                conn_type='Eth10G'
            )
        )

        self.communication_connections.append(
            CommunicationConnection(
                connector_1=(upf, 'pppg++'),
                connector_2=(iupf, 'pppg++'),
                conn_type='Eth10G'
            )
        )

        self.communication_connections.append(
            CommunicationConnection(
                connector_1=(iupf, 'pppg++'),
                connector_2=(gNodeB, 'ppp'),
                conn_type='Eth10G'
            )
        )

        central_agents = [agent for agent in self.agents if isinstance(agent, CentralAgent)]
        for central_agent in central_agents:
            self.communication_connections.append(
                CommunicationConnection(
                    connector_1=(router, 'pppg++'),
                    connector_2=(central_agent, 'pppg++'),
                    conn_type='Eth10G'  # TODO: maybe change
                )
            )

    def get_omnet_network_description(self):
        imports = ('import inet.networklayer.configurator.ipv4.Ipv4NetworkConfigurator;\n'
                   'import inet.networklayer.ipv4.RoutingTableRecorder\n;'
                   'import inet.node.ethernet.Eth10G;\n'
                   'import inet.node.inet.Router;\n'
                   'import inet.node.inet.StandardHost;\n'
                   'import simu5g.common.binder.Binder;\n'
                   'import simu5g.common.carrierAggregation.CarrierAggregation;\n'
                   'import simu5g.nodes.Upf;\n'
                   'import simu5g.nodes.NR.gNodeB;\n'
                   'import simu5g.nodes.NR.NRUe;\n'
                   'import simu5g.nodes.backgroundCell.BackgroundCell;\n'
                   'import simu5g.world.radio.LteChannelControl;\n')

        network = f'network SimbenchNetwork5G ' + '{\n'

        parameters = 'parameters: @display("i=block/network2;bgb=' + f'{self.network_size[0]},{self.network_size[1]}");\n'

        submodules = 'submodules:\n\n'

        for module in self.communication_infrastructure:
            submodules += (f'\t{module.identifier}: {module.class_name}' + '{' +
                           f'@display("p={int(module.position[0])},{int(module.position[1])}");' + '}\n')

        for module in self.traffic_devices:
            submodules += (f'\t{module.identifier}: NRUe' + '{' +
                           f'@display("p={int(module.position[0])},{int(module.position[1])}");' + '}\n')
        for agent in self.agents:
            if isinstance(agent, CentralAgent):
                submodules += (
                        f'\t{agent.omnet_name}: StandardHost ' +
                        '{@display("p=' + f'{int(agent.coordinates[0])},{int(agent.coordinates[1])}' + '");}\n')
            else:
                submodules += (f'\t{agent.omnet_name}: NRUe ' +
                               '{@display("p=' + f'{int(agent.coordinates[0])},{int(agent.coordinates[1])}' + '");}\n')

        connections = 'connections:\n'
        for connection in self.communication_connections:
            connections += '\t' + connection.get_connection_string() + ';\n'

        return imports + network + parameters + submodules + connections + '}'

    def get_omnet_ini_config(self):
        config_string = (f'[Config SimbenchNetwork]\n'
                         f'network = SimbenchNetwork5G\n'
                         f'extends = Net5G\n')

        for i, agent in enumerate(self.agents):  # TODO: if multiple agents: assign to antenna
            config_string += f'**.{agent.omnet_name}.app[0].localPort = {agent.omnet_port}\n'
            config_string += \
                (f'**.{agent.omnet_name}.app[0].trafficConfigPath = '
                 f'"modules/traffic_configurations/traffic_config_{agent.omnet_name}.json"\n')
        config_string += '*.server.numApps=0\n'

        for traffic_device in self.traffic_devices:
            config_string += f'*.{traffic_device.identifier}.app[*].destAddress = "{random.choice(self.agents).omnet_name}"\n'
        return config_string


class SimbenchEthernetNetworkExtractor(SimbenchNetworkExtractor):

    def __init__(self, simbench_code, system_state):
        super().__init__(simbench_code, system_state)

    def place_communication_infrastructure(self):
        non_central_agents = [agent for agent in self.agents if not isinstance(agent, CentralAgent)]

        agent_coordinates = np.array([agent.coordinates for agent in non_central_agents])

        central_agents = [agent for agent in self.agents if isinstance(agent, CentralAgent)]

        # Place a router at the centroid of the cluster
        router_central = CommunicationInfrastructure(
            class_name='Router',
            identifier=f'router_central',
            position=(100, 100)
        )
        self.communication_infrastructure.append(router_central)

        # place configurator
        self.communication_infrastructure.append(
            CommunicationInfrastructure(
                class_name='Ipv4NetworkConfigurator',
                identifier='configurator',
                position=(100, 100)
            )
        )

        for agent in central_agents:
            self.communication_connections.append(
                CommunicationConnection(
                    connector_1=(router_central, 'pppg++'),
                    connector_2=(agent, 'pppg++'),
                    conn_type='Eth10M'
                )
            )

        # Step 1: Cluster agents with similar coordinates
        num_clusters = 3  # This can be dynamic or based on some heuristics
        kmeans = KMeans(n_clusters=num_clusters, random_state=0).fit(agent_coordinates)
        labels = kmeans.labels_

        # Store clusters information
        clusters = {}
        for i in range(num_clusters):
            clusters[i] = []

        for idx, label in enumerate(labels):
            clusters[label].append(non_central_agents[idx])

        # Step 2: Place one router per cluster at the centroid
        for cluster_id, agents_in_cluster in clusters.items():
            # Calculate the centroid of the cluster
            cluster_coordinates = np.array([agent.coordinates for agent in agents_in_cluster])
            centroid = cluster_coordinates.mean(axis=0)

            new_agents = self.add_aggregator_level_agents(tuple(centroid), cluster_id)

            # Place a router at the centroid of the cluster
            router = CommunicationInfrastructure(
                class_name='Router',
                identifier=f'router_{cluster_id}',
                position=tuple(centroid)
            )
            self.communication_infrastructure.append(router)

            # connect router to central router
            self.communication_connections.append(
                CommunicationConnection(
                    connector_1=(router, 'pppg++'),
                    connector_2=(router_central, 'pppg++'),
                    conn_type='Eth10M'
                )
            )

            # Step 3: Define connections between agents and the router
            for agent in agents_in_cluster + new_agents:
                self.communication_connections.append(
                    CommunicationConnection(
                        connector_1=(router, 'pppg++'),
                        connector_2=(agent, 'pppg++'),
                        conn_type='Eth10M'
                    )
                )

    def get_omnet_network_description(self) -> str:
        imports = ('import inet.networklayer.configurator.ipv4.Ipv4NetworkConfigurator;\n'
                   'import inet.networklayer.ipv4.RoutingTableRecorder;\n'
                   'import inet.node.ethernet.Eth10M;\n'
                   'import inet.node.inet.Router;\n'
                   'import inet.node.inet.StandardHost;\n')

        network = f'network SimbenchNetwork ' + '{\n'

        # add some margin (10m) in network display
        parameters = ('parameters: @display("i=block/network2;bgb=' +
                      f'{self.network_size[0] + 10},{self.network_size[1] + 10}");\n')

        submodules = 'submodules:\n\n'

        for module in self.communication_infrastructure:
            submodules += (f'\t{module.identifier}: {module.class_name}' + '{' +
                           f'@display("p={int(module.position[0])},{int(module.position[1])}");' + '}\n')
        for agent in self.agents:
            submodules += (
                    f'\t{agent.omnet_name}: StandardHost ' +
                    '{@display("p=' + f'{int(agent.coordinates[0])},{int(agent.coordinates[1])}' + '");}\n')

        for traffic_device in self.traffic_devices:
            submodules += (f'\t{traffic_device.identifier}: Ue ' +
                           '{@display("p=' + f'{int(traffic_device.position[0])},{int(traffic_device.position[1])}' + '");}\n')
        connections = 'connections:\n'
        for connection in self.communication_connections:
            connections += '\t' + connection.get_connection_string() + ';\n'

        return imports + network + parameters + submodules + connections + '}'

    def get_omnet_ini_config(self):
        config_string = (f'[Config SimbenchNetwork]\n'
                         f'network = SimbenchNetwork\n'
                         f'extends = Ethernet\n')

        for i, agent in enumerate(self.agents):
            config_string += f'**.{agent.omnet_name}.app[0].localPort = {agent.omnet_port}\n'
            config_string += \
                (f'**.{agent.omnet_name}.app[0].trafficConfigPath = '
                 f'"modules/traffic_configurations/traffic_config_{agent.omnet_name}.json"\n')
        config_string += '*.server.numApps=0\n'
        for traffic_device in self.traffic_devices:
            config_string += (f'*.{traffic_device.identifier}.app[*].destAddress = '
                              f'"{random.choice(self.agents).omnet_name}"\n')
        return config_string


class SimbenchLTENetworkExtractor(SimbenchNetworkExtractor):

    def __init__(self, simbench_code, system_state, specification):
        self.specification = specification
        super().__init__(simbench_code, system_state)

    def place_communication_infrastructure(self):
        # place channel control
        self.communication_infrastructure.append(
            CommunicationInfrastructure(
                class_name='LteChannelControl',
                identifier='channelControl',
                position=(100, 100)
            )
        )
        # place routing table recorder
        self.communication_infrastructure.append(
            CommunicationInfrastructure(
                class_name='RoutingTableRecorder',
                identifier='routingRecorder',
                position=(100, 100)
            )
        )
        # place configurator
        self.communication_infrastructure.append(
            CommunicationInfrastructure(
                class_name='Ipv4NetworkConfigurator',
                identifier='configurator',
                position=(100, 100)
            )
        )
        # place binder
        self.communication_infrastructure.append(
            CommunicationInfrastructure(
                class_name='Binder',
                identifier='binder',
                position=(100, 100)
            )
        )
        # place carrier aggregation
        self.communication_infrastructure.append(
            CommunicationInfrastructure(
                class_name='CarrierAggregation',
                identifier='carrierAggregation',
                position=(100, 100)
            )
        )
        # place server
        server = CommunicationInfrastructure(
            class_name='StandardHost',
            identifier='server',
            position=(100, 100)
        )
        self.communication_infrastructure.append(server)
        # place router
        router = CommunicationInfrastructure(
            class_name='Router',
            identifier='router',
            position=(100, 100)
        )
        self.communication_infrastructure.append(router)
        # place pgw
        pgw = CommunicationInfrastructure(
            class_name='PgwStandard',
            identifier='pgw',
            position=(100, 100)
        )
        self.communication_infrastructure.append(pgw)
        # place eNodeBs
        eNodeB = CommunicationInfrastructure(
            class_name='eNodeB',
            identifier='eNB',
            position=(int(self.network_size[0]) / 2, int(self.network_size[1]) / 2)
        )  # TODO: maybe add multiple eNodeBs
        self.communication_infrastructure.append(eNodeB)

        """
        Define connections
        """
        self.communication_connections.append(
            CommunicationConnection(
                connector_1=(server, 'pppg++'),
                connector_2=(router, 'pppg++'),
                conn_type='Eth10G'
            )
        )

        self.communication_connections.append(
            CommunicationConnection(
                connector_1=(router, 'pppg++'),
                connector_2=(pgw, 'filterGate'),
                conn_type='Eth10G'
            )
        )

        self.communication_connections.append(
            CommunicationConnection(
                connector_1=(pgw, 'pppg++'),
                connector_2=(eNodeB, 'ppp'),
                conn_type='Eth10G'
            )
        )
        central_agents = [agent for agent in self.agents if isinstance(agent, CentralAgent)]
        for central_agent in central_agents:
            self.communication_connections.append(
                CommunicationConnection(
                    connector_1=(router, 'pppg++'),
                    connector_2=(central_agent, 'pppg++'),
                    conn_type='Eth10G'  # TODO: maybe change
                )
            )

    def get_omnet_network_description(self):
        imports = ('import inet.networklayer.configurator.ipv4.Ipv4NetworkConfigurator;\n'
                   'import inet.networklayer.ipv4.RoutingTableRecorder;\n'
                   'import inet.node.ethernet.Eth10G;\n'
                   'import inet.node.inet.Router;\n'
                   'import inet.node.inet.StandardHost;\n'
                   'import simu5g.common.binder.Binder;\n'
                   'import simu5g.common.carrierAggregation.CarrierAggregation;\n'
                   'import simu5g.nodes.Ue;\n'
                   'import simu5g.nodes.eNodeB;\n'
                   'import simu5g.nodes.PgwStandard;\n'
                   'import simu5g.world.radio.LteChannelControl;\n')

        network = f'network SimbenchNetwork ' + '{\n'

        # add some margin (10m) in network display
        parameters = ('parameters: @display("i=block/network2;bgb=' +
                      f'{self.network_size[0] + 10},{self.network_size[1] + 10}");\n')

        submodules = 'submodules:\n\n'

        for module in self.communication_infrastructure:
            submodules += (f'\t{module.identifier}: {module.class_name}' + '{' +
                           f'@display("p={int(module.position[0])},{int(module.position[1])}");' + '}\n')
        for agent in self.agents:
            if isinstance(agent, CentralAgent):
                submodules += (
                        f'\t{agent.omnet_name}: StandardHost ' +
                        '{@display("p=' + f'{int(agent.coordinates[0])},{int(agent.coordinates[1])}' + '");}\n')
            else:
                submodules += (f'\t{agent.omnet_name}: Ue ' +
                               '{@display("p=' + f'{int(agent.coordinates[0])},{int(agent.coordinates[1])}' + '");}\n')

        for traffic_device in self.traffic_devices:
            submodules += (f'\t{traffic_device.identifier}: Ue ' +
                           '{@display("p=' + f'{int(traffic_device.position[0])},{int(traffic_device.position[1])}' + '");}\n')
        connections = 'connections:\n'
        for connection in self.communication_connections:
            connections += '\t' + connection.get_connection_string() + ';\n'

        return imports + network + parameters + submodules + connections + '}'

    def get_omnet_ini_config(self):
        config_string = (f'[Config SimbenchNetwork]\n'
                         f'network = SimbenchNetwork\n'
                         f'extends = {self.specification.name}\n')

        for i, agent in enumerate(self.agents):  # TODO: if multiple agents: assign to antenna
            config_string += f'**.{agent.omnet_name}.app[0].localPort = {agent.omnet_port}\n'
            config_string += \
                (f'**.{agent.omnet_name}.app[0].trafficConfigPath = '
                 f'"modules/traffic_configurations/traffic_config_{agent.omnet_name}.json"\n')
        config_string += '*.server.numApps=0\n'
        for traffic_device in self.traffic_devices:
            config_string += (f'*.{traffic_device.identifier}.app[*].destAddress = '
                              f'"{random.choice(self.agents).omnet_name}"\n')
        return config_string
