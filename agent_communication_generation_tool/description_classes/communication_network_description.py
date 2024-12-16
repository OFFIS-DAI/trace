"""
Descriptions of communication networks in OMNeT++.
"""
from abc import ABC
from enum import Enum

from network_generation.simbench_network_extractor import SimbenchNetworkExtractor, SimbenchLTENetworkExtractor, \
    Simbench5GNetworkExtractor, SystemState, SimbenchEthernetNetworkExtractor

import warnings

warnings.filterwarnings('ignore')

from agent_communication_generation_tool.description_classes.agent import (Agent, LeafAgent,
                                                                           AggregatorAgent, CentralAgent)


class CommunicationNetworkDescription(ABC):
    """
    Abstract class that describes a communication network model in OMNeT++.
    """

    def __init__(self, comm_network_description_id,
                 agents: list[Agent],
                 config_name: str,
                 speed_mbps=0):
        self.id = comm_network_description_id
        self.agents = agents
        self.config_name = config_name
        self.speed_mbps = speed_mbps


class HANDescription(CommunicationNetworkDescription, ABC):
    """
    Home Area Network description.
    """

    def __init__(self, config_name):
        self.household_agent = (
            LeafAgent(omnet_name='household_agent', omnet_port=1000,
                      agent_type=LeafAgent.LeafAgentType.HOUSEHOLD_AGENT))
        self.device_agents = [
            LeafAgent(omnet_name=f'device_agent_{i}', omnet_port=1001 + i,
                      agent_type=LeafAgent.LeafAgentType.DEVICE_AGENT)
            for i in range(0, 10)]
        super().__init__(comm_network_description_id=f'{config_name}',
                         agents=self.device_agents + [self.household_agent],
                         config_name=config_name)

    def get_central_agent(self):
        return self.household_agent


class EthernetDescription(HANDescription):
    """
    Home Area Network description for Ethernet connection.
    """

    def __init__(self, speed_mbps=10):
        self.speed_mbps = speed_mbps
        super().__init__(config_name=f'HAN_Ethernet_{speed_mbps}Mbps')


class WifiDescription(HANDescription):
    """
    Home Area Network description for Wi-Fi connection.
    """

    class Specification(Enum):
        Wifi_802_11 = 0
        Wifi_802_11_ac = 1

    def __init__(self, specification):
        super().__init__(config_name=f'{specification.name}')


class SimbenchNetworkDescription(CommunicationNetworkDescription, ABC):
    """
    Communication network based on simbench power network.
    Reference for simbench networks: https://simbench.de/de/datensaetze/
    Mapping:
        - load: Household Agent
        - generator: Generation Agent
        - storage: Storage Agent
        - measurement: Grid Infrastructure Agent

        - substation: Substation Agent
    """

    def __init__(self, network_extractor: SimbenchNetworkExtractor,
                 technology: str, simbench_code):
        config_name = 'SimbenchNetwork'
        self.technology = technology
        network_extractor.initialize_network()

        self.household_agents = network_extractor.household_agents
        self.grid_infrastructure_agents = network_extractor.grid_infrastructure_agents
        self.storage_agents = network_extractor.storage_agents
        self.generation_agents = network_extractor.generation_agents
        self.substation_agents = network_extractor.substation_agents
        self.control_center_agent = network_extractor.control_center_agent
        self.market_agent = network_extractor.market_agent
        self.aggregator_agent = network_extractor.aggregator_agent
        self.pdc_agent = network_extractor.pdc_agent
        self.grid_operator_agent = network_extractor.grid_operator_agent

        super().__init__(config_name=config_name,
                         agents=network_extractor.agents,
                         comm_network_description_id=f'{config_name}_{self.technology}_{simbench_code}')

    def get_central_agent(self):
        return self.control_center_agent


class SimbenchLTENetworkDescription(SimbenchNetworkDescription):
    class Specification(Enum):
        LTE = 0
        LTE450 = 1

    def __init__(self, simbench_code, specification=Specification.LTE, system_state=SystemState.NORMAL,
                 max_number_of_agents_per_type=None):
        self.system_state = system_state
        self.simbench_code = simbench_code
        network_extractor = SimbenchLTENetworkExtractor(simbench_code, system_state, specification,
                                                        max_number_of_agents_per_type)
        super().__init__(network_extractor, technology=specification.name, simbench_code=simbench_code)


class Simbench5GNetworkDescription(SimbenchNetworkDescription):
    def __init__(self, simbench_code, specification=None, system_state=SystemState.NORMAL,
                 max_number_of_agents_per_type=None):
        self.system_state = system_state
        self.simbench_code = simbench_code
        network_extractor = Simbench5GNetworkExtractor(simbench_code, system_state, max_number_of_agents_per_type)
        super().__init__(network_extractor, technology='5G', simbench_code=simbench_code)


class SimbenchEthernetNetworkDescription(SimbenchNetworkDescription):
    def __init__(self, simbench_code, specification=None, system_state=SystemState.NORMAL,
                 max_number_of_agents_per_type=None):
        network_extractor = SimbenchEthernetNetworkExtractor(simbench_code, system_state, max_number_of_agents_per_type)
        self.simbench_code = simbench_code
        self.system_state = SystemState.NORMAL
        super().__init__(network_extractor, technology='Ethernet', simbench_code=simbench_code)

