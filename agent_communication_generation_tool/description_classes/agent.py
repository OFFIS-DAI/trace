"""
Defines agent types for generation of agent communication pattern.
"""
from abc import ABC
from enum import Enum


class Agent(ABC):
    """
    Abstract class of an agent.
    """

    def __init__(self, omnet_name: str, omnet_port: int, coordinates=(0, 0)):
        self.omnet_name = omnet_name
        self.omnet_port = omnet_port
        self.coordinates = coordinates

        self.node_id = None
        self.agent_type = None


class LeafAgent(Agent):
    """
    A LeafAgent implements the class Agent and is located at the lowest hierarchy level.
    """

    class LeafAgentType(Enum):
        """
        The type of LeafAgent.
        """
        DEVICE_AGENT = 0
        HOUSEHOLD_AGENT = 1
        GENERATION_AGENT = 2
        GRID_INFRASTRUCTURE_AGENT = 3
        STORAGE_AGENT = 4

    def __init__(self,
                 omnet_name,
                 omnet_port,
                 agent_type: LeafAgentType,
                 coordinates=(0, 0)):
        super().__init__(omnet_name, omnet_port, coordinates)
        self.agent_type = agent_type


class AggregatorAgent(Agent):
    """
    An AggregatorAgent implements the class Agent and is located at the middle hierarchy level.
    """

    class AggregatorAgentType(Enum):
        """
        The type of AggregatorAgent.
        """
        AGGREGATOR_AGENT = 0
        PDC_AGENT = 1
        SUBSTATION_AGENT = 2

    def __init__(self,
                 omnet_name,
                 omnet_port,
                 agent_type: AggregatorAgentType,
                 coordinates=(0, 0)):
        super().__init__(omnet_name, omnet_port, coordinates)
        self.agent_type = agent_type


class CentralAgent(Agent):
    """
    A CentralAgent implements the class Agent and is located at the highest hierarchy level.
    """

    class CentralAgentType(Enum):
        """
        The type of CentralAgent.
        """
        GRID_OPERATOR_AGENT = 0
        CONTROL_CENTER_AGENT = 1
        MARKET_AGENT = 2

    def __init__(self,
                 omnet_name,
                 omnet_port,
                 agent_type: CentralAgentType,
                 coordinates=(0, 0)):
        super().__init__(omnet_name, omnet_port, coordinates)
        self.agent_type = agent_type
