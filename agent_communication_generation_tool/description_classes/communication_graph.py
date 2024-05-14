"""
Implementation of communication graph representation to indicate neighborhoods between agents.
"""
import random
from abc import ABC, abstractmethod

import networkx as nx

from agent_communication_generation_tool.description_classes.agent import Agent, CentralAgent, AggregatorAgent, \
    LeafAgent


class CommunicationGraph(ABC):
    """
    Abstract class of a communication graph.
    """

    def __init__(self,
                 agents: list[Agent], max_number_of_agents_per_type=None):
        if max_number_of_agents_per_type:
            agents = reduce_number_of_leaf_agents_in_graph(max_number_of_agents_per_type=max_number_of_agents_per_type,
                                                           agents=agents)
        self.agents = agents
        self.node_agent_mapping = {idx: agent for idx, agent in enumerate(self.agents)}
        self.graph = self.initialize_graph()
        self.relabeled_graph = None

    def relabel_graph(self):
        if len(self.node_agent_mapping) == len(self.agents):
            mapping = {}
            for node, agent in self.node_agent_mapping.items():
                mapping[node] = agent.omnet_name
            self.relabeled_graph = self.graph.copy()
            self.relabeled_graph = nx.relabel_nodes(self.relabeled_graph, mapping)

    def get_agents_by_type(self,
                           agent_type):
        return [agent for agent in self.agents if agent.agent_type == agent_type]

    def get_agents_by_class(self,
                            agent_class):
        return [agent for agent in self.agents if isinstance(agent, agent_class)]

    @abstractmethod
    def initialize_graph(self) -> nx.Graph:
        pass

    def get_neighbors(self,
                      agent: Agent):
        """
        Gets neighbors from topology graph.
        :param agent: node to get neighbors for.
        :return: list of agent objects.
        """
        l = 0
        for node_id, cur_agent in self.node_agent_mapping.items():
            if agent == cur_agent:
                neighbor_ids = [n for n in nx.neighbors(self.graph, l)]
                return [self.node_agent_mapping[i] for i in neighbor_ids]
            l += 1

    @abstractmethod
    def get_description(self):
        pass


class RingOverlayGraph(CommunicationGraph):
    def __init__(self, agents: list[Agent],
                 central_agent: CentralAgent,
                 max_number_of_agents_per_type=None):
        self.central_agent = central_agent
        super().__init__(agents, max_number_of_agents_per_type)

    def initialize_graph(self) -> nx.Graph:
        """
        Initializes topology as networkx graph.
        :return: generated graph.
        """
        graph = nx.Graph()
        for node in self.node_agent_mapping.keys():
            graph.add_node(node)

        agents_without_central_agent = {idx: agent for idx, agent in self.node_agent_mapping.items()
                                        if not isinstance(agent, CentralAgent)}

        for idx, agent in agents_without_central_agent.items():
            graph.add_edge(idx,
                           idx + 1 if idx < len(agents_without_central_agent) - 1
                           else list(agents_without_central_agent.keys())[0])

        return graph

    def get_description(self):
        return f'Ring Overlay Topology with {len(self.agents)} agents'


class SmallWorldOverlayGraph(CommunicationGraph):
    def __init__(self, agents: list[Agent],
                 central_agent: CentralAgent,
                 p: float,
                 max_number_of_agents_per_type=None):
        self.central_agent = central_agent
        self.p = p
        super().__init__(agents, max_number_of_agents_per_type)

    def initialize_graph(self) -> nx.Graph:
        """
        Initializes topology as networkx graph.
        :return: generated graph.
        """
        graph = nx.Graph()

        for node in self.node_agent_mapping.keys():
            graph.add_node(node)

        leaf_agents = {idx: agent for idx, agent in self.node_agent_mapping.items()
                       if isinstance(agent, LeafAgent)}

        for idx, agent in leaf_agents.items():
            graph.add_edge(idx,
                           idx + 1 if idx < len(leaf_agents) - 1
                           else list(leaf_agents.keys())[0])
            if random.random() < self.p:
                others = {i: a for i, a in leaf_agents.items() if a != agent}
                choice = random.choice(list(others.keys()))
                graph.add_edge(idx, choice)
        return graph

    def get_description(self):
        return f'Small World Overlay Topology with {len(self.agents)} agents and p = {self.p}'


class CompleteOverlayGraph(CommunicationGraph):
    def __init__(self, agents: list[Agent],
                 central_agent: CentralAgent,
                 max_number_of_agents_per_type=None):
        self.central_agent = central_agent
        super().__init__(agents, max_number_of_agents_per_type)

    def initialize_graph(self) -> nx.Graph:
        """
        Initializes topology as networkx graph.
        :return: generated graph.
        """
        graph = nx.Graph()
        for node in self.node_agent_mapping.keys():
            graph.add_node(node)

        leaf_agents = {idx: agent for idx, agent in self.node_agent_mapping.items()
                       if isinstance(agent, LeafAgent)}

        for idx, agent in leaf_agents.items():
            graph.add_edge(idx,
                           idx + 1 if idx < len(leaf_agents) - 1
                           else list(leaf_agents.keys())[0])
            others = {i: a for i, a in leaf_agents.items() if a != agent}
            for o in others.keys():
                graph.add_edge(idx, o)
        return graph

    def get_description(self):
        return f'Complete Overlay Topology with {len(self.agents)} agents'


def reduce_number_of_leaf_agents_in_graph(max_number_of_agents_per_type: int, agents: list[Agent]):
    reduced_agents = list()
    for agent_type in LeafAgent.LeafAgentType:
        agents_of_type = [agent for agent in agents if agent.agent_type == agent_type]
        if len(agents_of_type) > max_number_of_agents_per_type:
            reduced_agents.extend(random.sample(agents_of_type, max_number_of_agents_per_type))
        else:
            reduced_agents.extend(agents_of_type)
    reduced_agents.extend([agent for agent in agents if not isinstance(agent, LeafAgent)])
    return reduced_agents


class StarCommunicationGraph(CommunicationGraph):
    def __init__(self,
                 agents: list[Agent],
                 central_agent: CentralAgent,
                 aggregator_agent=None,
                 max_number_of_agents_per_type=None):
        self.central_agent = central_agent
        self.aggregator_agent = aggregator_agent
        super().__init__(agents, max_number_of_agents_per_type)

    def initialize_graph(self) -> nx.Graph:
        """
        Initializes topology as networkx graph.
        :return: generated graph.
        """
        central_agent_id = [key for key, value in self.node_agent_mapping.items() if value == self.central_agent][0]
        leaf_agents = {idx: agent for idx, agent in self.node_agent_mapping.items()
                       if isinstance(agent, LeafAgent) and agent != self.central_agent}

        graph = nx.Graph()

        if self.aggregator_agent:
            aggregator_id = [key for key, value in self.node_agent_mapping.items() if value == self.aggregator_agent][0]
            graph.add_edge(central_agent_id, aggregator_id)

            for l_agent_id in leaf_agents:
                graph.add_edge(l_agent_id, aggregator_id)
        else:
            for l_agent_id in leaf_agents:
                graph.add_edge(l_agent_id, central_agent_id)
        return graph

    def get_description(self):
        return f'Star Overlay Topology with {len(self.agents)} agents'
