"""
All agent communication pattern are implemented in this file.
"""
import json
import os
import random
from abc import ABC, abstractmethod
from enum import Enum

import pandas as pd

from agent_communication_generation_tool.description_classes.agent import CentralAgent, LeafAgent, Agent, \
    AggregatorAgent
from agent_communication_generation_tool.description_classes.communication_graph import CommunicationGraph
from agent_communication_generation_tool.description_classes.data_size_generator import (DataSizeGenerator,
                                                                                         FixedDataSizeGenerator,
                                                                                         InIntervalDataSizeGenerator)


class TriggerType(Enum):
    """
    Communication might be event or time triggered.
    """
    EVENT_TRIGGERED = 1
    TIME_TRIGGERED = 2


class CommunicationMode(Enum):
    """
    The communication mode.
    """
    UNICAST = 1
    MULTICAST = 2
    BROADCAST = 3
    MANY_TO_ONE = 4
    COMPLEX = 5


class OrganizationalStructure(Enum):
    """
    The structure of the agent system.
    """
    CENTRALIZED = 1
    HIERARCHICAL = 2
    DECENTRALIZED = 3


def write_config_to_file(end_device, config):
    """
    Writes json-network configuration to file in OMNeT++ project.
    :param end_device: name of end device.
    :param config: traffic configuration file (json).
    :return: writes file
    """
    directory = 'omnet_project_files/modules/traffic_configurations/'
    os.makedirs(directory, exist_ok=True)  # Create directory if it doesn't exist

    with open(os.path.join(directory, f'traffic_config_{end_device}.json'), 'w') as f:
        json.dump(config, f, indent=2)


def get_initial_config(agent: Agent):
    """
    Generates initial configuration dict for OMNeT++.
    :param agent: sender.
    :return: dictionary with config.
    """
    return {
        "sender": agent.omnet_name,
        "messageList": []
    }


class AgentCommunicationPattern(ABC):
    """
    Abstract class that represents the communication pattern of an agent-based application.
    """

    def __init__(self,
                 simulation_duration_ms: int,
                 communication_graph: CommunicationGraph,
                 trigger: TriggerType,
                 frequency_ms: int,
                 data_size_generator: DataSizeGenerator,
                 communication_mode: CommunicationMode):
        directory = 'omnet_project_files/modules/traffic_configurations/'
        try:
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
        except Exception as e:
            print('Failed to delete: ', e)

        self.simulation_duration_ms = simulation_duration_ms
        self.communication_graph = communication_graph
        self.data_size_generator = data_size_generator
        self.trigger = trigger
        self.frequency_ms = frequency_ms
        self.communication_mode = communication_mode

        self.message_id_counter = 0
        self.traffic_configurations = {}

    @abstractmethod
    def generate_traffic_configuration_files(self):
        """
        This method should be implemented by child classes to generate configuration files for OMNeT++.
        """
        pass

    def get_inputs(self):
        """
        Get inputs (traffic configuration) as pandas DataFrame.
        :return: DataFrame.
        """
        dfs = []
        for client, data in self.traffic_configurations.items():
            df = pd.DataFrame(data['messageList'])
            df['sender'] = client
            dfs.append(df)
        if len(dfs) == 0:
            return None
        return pd.concat(dfs)

    def get_control_center_agent(self):
        control_center_agents = (
            self.communication_graph.get_agents_by_type(CentralAgent.CentralAgentType.CONTROL_CENTER_AGENT))
        if len(control_center_agents) == 0:
            raise ValueError('No control agent implemented.')
        if len(control_center_agents) > 1:
            raise ValueError('More than one control agent.')
        return control_center_agents[0]

    def get_aggregator_agent(self):
        aggregator_agents = (
            self.communication_graph.get_agents_by_type(AggregatorAgent.AggregatorAgentType.AGGREGATOR_AGENT))
        if len(aggregator_agents) == 0:
            raise ValueError('No aggregator agent implemented.')
        if len(aggregator_agents) > 1:
            raise ValueError('More than one aggregator agent.')
        return aggregator_agents[0]

    def get_market_agent(self):
        market_agents = (
            self.communication_graph.get_agents_by_type(CentralAgent.CentralAgentType.MARKET_AGENT))
        if len(market_agents) == 0:
            raise ValueError('No market agent implemented.')
        if len(market_agents) > 1:
            raise ValueError('More than one market agent.')
        return market_agents[0]

    def get_grid_operator_agent(self):
        grid_operator_agents = (
            self.communication_graph.get_agents_by_type(CentralAgent.CentralAgentType.GRID_OPERATOR_AGENT))
        if len(grid_operator_agents) == 0:
            raise ValueError('No grid operator agent implemented.')
        if len(grid_operator_agents) > 1:
            raise ValueError('More than one grid operator agent.')
        return grid_operator_agents[0]

    def add_message_to_config(self,
                              config: dict,
                              time_send_ms: int,
                              receiver: Agent,
                              packet_size_bytes: int,
                              expect_reply=False,
                              reply_after_ms_range=(0, 0)
                              ):
        new_msg = {
            "msgId": self.message_id_counter,
            "timeSend_ms": time_send_ms,
            "receiver": receiver.omnet_name,
            "receiverPort": receiver.omnet_port,
            "packetSize_B": packet_size_bytes
        }
        if expect_reply:
            new_msg['reply'] = True
            new_msg['replyAfter_ms'] = random.randint(reply_after_ms_range[0],
                                                      reply_after_ms_range[1])
        config['messageList'].append(new_msg)
        self.message_id_counter += 1
        return config

    def fill_config_for_non_sending_agents(self):
        non_sending_agents = [agent for agent in self.communication_graph.agents
                              if agent.omnet_name not in self.traffic_configurations.keys()]
        for agent in non_sending_agents:
            config = {
                "sender": agent.omnet_name,
                "messageList": []
            }
            write_config_to_file(agent.omnet_name, config)
            self.traffic_configurations[agent.omnet_name] = config

    def generate_to_neighbor_communication(self,
                                           agents: list[Agent]):
        for agent in agents:
            config = get_initial_config(agent)
            data_size = self.data_size_generator.get_data_size()
            current_time = self.frequency_ms
            while current_time < self.simulation_duration_ms:
                neighbors = self.communication_graph.get_neighbors(agent)
                assert all(isinstance(neighbor, Agent) for neighbor in neighbors)
                for receiver in neighbors:
                    config = self.add_message_to_config(config, time_send_ms=current_time, receiver=receiver,
                                                        packet_size_bytes=data_size)
                current_time += self.frequency_ms
            write_config_to_file(agent.omnet_name, config)
            self.traffic_configurations[agent.omnet_name] = config
        self.fill_config_for_non_sending_agents()

    def generate_many_to_one_communication(self,
                                           one: Agent,
                                           many: list[Agent],
                                           send_only_once=False
                                           ):
        send_time = random.randint(0, self.simulation_duration_ms)

        for agent in many:
            config = {
                "sender": agent.omnet_name,
                "messageList": []
            }
            data_size = self.data_size_generator.get_data_size()
            if not send_only_once:
                current_time = self.frequency_ms
                while current_time < self.simulation_duration_ms:
                    neighbors = self.communication_graph.get_neighbors(agent)
                    assert all(isinstance(neighbor, Agent) for neighbor in neighbors)
                    for receiver in neighbors:
                        config = self.add_message_to_config(config, time_send_ms=current_time, receiver=receiver,
                                                            packet_size_bytes=data_size)
                    current_time += self.frequency_ms
            else:
                neighbors = self.communication_graph.get_neighbors(agent)
                assert all(isinstance(neighbor, Agent) for neighbor in neighbors)
                for receiver in neighbors:
                    config = self.add_message_to_config(config, time_send_ms=send_time, receiver=receiver,
                                                        packet_size_bytes=data_size)
            write_config_to_file(agent.omnet_name, config)
            self.traffic_configurations[agent.omnet_name] = config
        self.fill_config_for_non_sending_agents()

    def generate_event_triggered_communication(self,
                                               one: Agent,
                                               many: list[Agent],
                                               multiple_events=False,
                                               event_frequency_range=(0, 0),
                                               send_time=0,
                                               expect_reply=False,
                                               reply_after_range=(0, 0)):
        config = {
            "sender": one.omnet_name,
            "messageList": []
        }
        data_size = self.data_size_generator.get_data_size()
        neighbors = self.communication_graph.get_neighbors(one)
        assert all(isinstance(neighbor, Agent) for neighbor in neighbors)
        if multiple_events:
            sending_times = []
            new_sending_time = 0
            while True:
                new_sending_time += random.randint(event_frequency_range[0], event_frequency_range[1])
                if new_sending_time < self.simulation_duration_ms:
                    sending_times.append(new_sending_time)
                else:
                    break
        else:
            sending_times = [send_time]
        for s_time in sending_times:
            possible_receivers = []
            if self.communication_mode == CommunicationMode.BROADCAST:
                possible_receivers = neighbors
            elif self.communication_mode == CommunicationMode.MULTICAST:
                # sample half of the neighbors as receiver of multicast
                possible_receivers = random.sample(neighbors, int(len(neighbors) / 2))
            elif self.communication_mode == CommunicationMode.UNICAST:
                possible_receivers = random.sample(many, 1)

            for receiver in possible_receivers:
                if receiver in many:
                    config = self.add_message_to_config(config, time_send_ms=s_time, receiver=receiver,
                                                        packet_size_bytes=data_size, expect_reply=expect_reply,
                                                        reply_after_ms_range=reply_after_range)
        write_config_to_file(one.omnet_name, config)
        self.traffic_configurations[one.omnet_name] = config

        self.fill_config_for_non_sending_agents()

    def generate_broadcast_time_triggered_communication(self,
                                                        one: Agent,
                                                        many: list[Agent],
                                                        expect_reply=False,
                                                        reply_after_range=(0, 0)
                                                        ):
        config = {
            "sender": one.omnet_name,
            "messageList": []
        }
        data_size = self.data_size_generator.get_data_size()
        current_time = self.frequency_ms
        while current_time < self.simulation_duration_ms:
            for receiver in many:
                config = self.add_message_to_config(config, time_send_ms=current_time, receiver=receiver,
                                                    packet_size_bytes=data_size, expect_reply=expect_reply,
                                                    reply_after_ms_range=reply_after_range)
            current_time += self.frequency_ms
        write_config_to_file(one.omnet_name, config)
        self.traffic_configurations[one.omnet_name] = config

        self.fill_config_for_non_sending_agents()


class SimpleAgentCommunicationPattern(AgentCommunicationPattern, ABC):
    """
    Another, more specialized abstract class to describe agent communication pattern.
    This class describes simple communication use cases such as time-triggered broadcast communication.
    """

    def __init__(self, simulation_duration_ms: int, communication_graph: CommunicationGraph,
                 trigger: TriggerType, frequency_ms: int, data_size_generator: DataSizeGenerator,
                 communication_mode: CommunicationMode):
        super().__init__(simulation_duration_ms, communication_graph, trigger, frequency_ms, data_size_generator,
                         communication_mode)


class ComplexAgentCommunicationPattern(AgentCommunicationPattern, ABC):
    """
    Another, more specialized abstract class to describe agent communication pattern.
    This class describes complex communication use cases such as heuristics.
    """

    def __init__(self, simulation_duration_ms: int, communication_graph: CommunicationGraph,
                 trigger: TriggerType, data_size_generator: DataSizeGenerator,
                 organizational_structure: OrganizationalStructure):
        self.organizational_structure = organizational_structure
        super().__init__(simulation_duration_ms, communication_graph, trigger, 0, data_size_generator,
                         CommunicationMode.COMPLEX)

    def generate_traffic_configuration_files(self):
        if self.organizational_structure == OrganizationalStructure.CENTRALIZED:
            self.generate_traffic_configuration_files_centralized()
        elif self.organizational_structure == OrganizationalStructure.HIERARCHICAL:
            self.generate_traffic_configuration_files_hierarchical()
        elif self.organizational_structure == OrganizationalStructure.DECENTRALIZED:
            self.generate_traffic_configuration_files_decentralized()

    @abstractmethod
    def generate_traffic_configuration_files_centralized(self):
        """
        Generates traffic configuration files in centralized organization.
        """
        pass

    @abstractmethod
    def generate_traffic_configuration_files_hierarchical(self):
        """
        Generates traffic configuration files in hierarchical organization.
        """
        pass

    @abstractmethod
    def generate_traffic_configuration_files_decentralized(self):
        """
        Generates traffic configuration files in decentralized organization.
        """
        pass


"""
Concrete pattern implementations for ComplexAgentCommunicationPattern.
"""


class AddNewAgent(ComplexAgentCommunicationPattern):
    def __init__(self, simulation_duration_ms: int, communication_graph: CommunicationGraph,
                 data_size_generator: DataSizeGenerator,
                 organizational_structure: OrganizationalStructure, reply_after_range: tuple[int, int]):
        self.reply_after_range = reply_after_range
        super().__init__(simulation_duration_ms, communication_graph, TriggerType.EVENT_TRIGGERED, data_size_generator,
                         organizational_structure)

    def generate_traffic_configuration_files_centralized(self):
        leaf_agents = self.communication_graph.get_agents_by_class(LeafAgent)
        control_center_agents = (
            self.communication_graph.get_agents_by_type(CentralAgent.CentralAgentType.CONTROL_CENTER_AGENT))
        if len(control_center_agents) == 0:
            raise ValueError('No control agent implemented.')
        if len(control_center_agents) > 1:
            raise ValueError('More than one control agent.')
        control_center_agent = control_center_agents[0]

        cc_config = {
            "sender": control_center_agent.omnet_name,
            "messageList": []
        }

        # get a subset of agents that are added to the network
        random_leaf_agents = random.sample(leaf_agents, int(len(leaf_agents)/5))

        # send request from leaf agent to control center agent
        for random_leaf_agent in random_leaf_agents:
            config = {
                "sender": random_leaf_agent.omnet_name,
                "messageList": []
            }

            send_time = random.randint(0, 100)  # in the first 100 ms
            data_size = self.data_size_generator.get_data_size()

            config = self.add_message_to_config(config, time_send_ms=send_time, receiver=control_center_agent,
                                                packet_size_bytes=data_size, expect_reply=True,
                                                reply_after_ms_range=self.reply_after_range)

            write_config_to_file(random_leaf_agent.omnet_name, config)
            self.traffic_configurations[random_leaf_agent.omnet_name] = config

            # send information from control center agent to all leaf agents
            asserted_inform_time = send_time + self.reply_after_range[1]

            data_size = self.data_size_generator.get_data_size()
            for leaf_agent in leaf_agents:
                cc_config = self.add_message_to_config(cc_config, time_send_ms=asserted_inform_time,
                                                       receiver=leaf_agent,
                                                       packet_size_bytes=data_size, expect_reply=False)

        write_config_to_file(control_center_agent.omnet_name, cc_config)
        self.traffic_configurations[control_center_agent.omnet_name] = cc_config

        self.fill_config_for_non_sending_agents()

    def generate_traffic_configuration_files_hierarchical(self):
        leaf_agents = self.communication_graph.get_agents_by_class(LeafAgent)
        control_center_agent = self.get_control_center_agent()
        aggregator_agent = self.get_aggregator_agent()
        random_leaf_agents = random.sample(leaf_agents, int(len(leaf_agents)/5))

        a_config = {
            "sender": aggregator_agent.omnet_name,
            "messageList": []
        }

        # send request from leaf agent to aggregator agent
        for random_leaf_agent in random_leaf_agents:
            config = {
                "sender": random_leaf_agent.omnet_name,
                "messageList": []
            }

            send_time = random.randint(0, 100)  # in the first 100 ms
            data_size = self.data_size_generator.get_data_size()

            config = self.add_message_to_config(config, time_send_ms=send_time, receiver=aggregator_agent,
                                                packet_size_bytes=data_size)

            write_config_to_file(random_leaf_agent.omnet_name, config)
            self.traffic_configurations[random_leaf_agent.omnet_name] = config

            # send request from aggregator agent to control agent

            send_time += 10
            data_size = self.data_size_generator.get_data_size()

            a_config = self.add_message_to_config(a_config, time_send_ms=send_time, receiver=control_center_agent,
                                                  packet_size_bytes=data_size, expect_reply=True,
                                                  reply_after_ms_range=self.reply_after_range)

            # send information from control center agent to all leaf agents
            asserted_inform_time = send_time + self.reply_after_range[1]

            data_size = self.data_size_generator.get_data_size()

            for leaf_agent in leaf_agents:
                a_config = self.add_message_to_config(a_config, time_send_ms=asserted_inform_time,
                                                      receiver=leaf_agent,
                                                      packet_size_bytes=data_size, expect_reply=False)

        write_config_to_file(aggregator_agent.omnet_name, a_config)
        self.traffic_configurations[aggregator_agent.omnet_name] = a_config

        self.fill_config_for_non_sending_agents()

    def generate_traffic_configuration_files_decentralized(self):
        leaf_agents = self.communication_graph.get_agents_by_class(LeafAgent)
        control_center_agents = (
            self.communication_graph.get_agents_by_type(CentralAgent.CentralAgentType.CONTROL_CENTER_AGENT))
        if len(control_center_agents) == 0:
            raise ValueError('No control agent implemented.')
        if len(control_center_agents) > 1:
            raise ValueError('More than one control agent.')
        control_center_agent = control_center_agents[0]

        random_leaf_agents = random.sample(leaf_agents, int(len(leaf_agents)/5))

        for random_leaf_agent in random_leaf_agents:
            # send request from leaf agent to control center agent
            config = get_initial_config(random_leaf_agent)

            send_time = random.randint(0, 100)  # in the first 100 ms
            data_size = self.data_size_generator.get_data_size()

            config = self.add_message_to_config(config, time_send_ms=send_time, receiver=control_center_agent,
                                                packet_size_bytes=data_size, expect_reply=True,
                                                reply_after_ms_range=self.reply_after_range)

            # send information from control center agent to all leaf agents
            asserted_inform_time = send_time + self.reply_after_range[1]

            data_size = self.data_size_generator.get_data_size()

            for neighbor in self.communication_graph.get_neighbors(random_leaf_agent):
                config = self.add_message_to_config(config, time_send_ms=asserted_inform_time,
                                                    receiver=neighbor,
                                                    packet_size_bytes=data_size, expect_reply=False)

            write_config_to_file(random_leaf_agent.omnet_name, config)
            self.traffic_configurations[random_leaf_agent.omnet_name] = config

        self.fill_config_for_non_sending_agents()


class DemandSupplyBalancing(ComplexAgentCommunicationPattern):

    def __init__(self, simulation_duration_ms: int, communication_graph: CommunicationGraph,
                 data_size_generator: DataSizeGenerator, organizational_structure: OrganizationalStructure,
                 t_central_optimization_range: tuple[int, int], p_agree_to_power_supply=1.0,
                 negotiation_duration_ms=100):
        self.t_central_optimization_range = t_central_optimization_range
        self.p_agree_to_power_supply = p_agree_to_power_supply
        self.negotiation_duration_ms = negotiation_duration_ms
        super().__init__(simulation_duration_ms, communication_graph, TriggerType.EVENT_TRIGGERED,
                         data_size_generator, organizational_structure)

    def generate_traffic_configuration_files_centralized(self):
        generator_agents = self.communication_graph.get_agents_by_type(LeafAgent.LeafAgentType.GENERATION_AGENT)
        if len(generator_agents) == 0:
            raise ValueError('No generator agents implemented.')
        random_generator_agent = random.choice(generator_agents)
        control_center_agent = self.get_control_center_agent()

        time_send = random.randint(0, 100)

        # send request from generator agent to control center agent
        # control center agent responds with agree or decline
        gen_config = self.add_message_to_config(
            config=get_initial_config(random_generator_agent),
            time_send_ms=time_send,
            receiver=control_center_agent,
            packet_size_bytes=self.data_size_generator.get_data_size(),
            expect_reply=True,
            reply_after_ms_range=self.t_central_optimization_range
        )
        write_config_to_file(random_generator_agent.omnet_name, gen_config)
        self.traffic_configurations[random_generator_agent.omnet_name] = gen_config

        cc_config = get_initial_config(control_center_agent)

        # if control center agent responds with agree: inform other leaf agents, generator agent sends confirm
        if random.random() < self.p_agree_to_power_supply:
            # control center agent agrees to power supply
            for leaf_agent in self.communication_graph.get_agents_by_class(LeafAgent):
                if leaf_agent == random_generator_agent:
                    continue
                cc_config = self.add_message_to_config(
                    config=cc_config,
                    time_send_ms=time_send + self.t_central_optimization_range[1],
                    receiver=leaf_agent,
                    packet_size_bytes=self.data_size_generator.get_data_size(),
                    expect_reply=False,
                    reply_after_ms_range=(0, 100)
                )
            write_config_to_file(control_center_agent.omnet_name, cc_config)
            self.traffic_configurations[control_center_agent.omnet_name] = cc_config

        self.fill_config_for_non_sending_agents()

    def generate_traffic_configuration_files_hierarchical(self):
        control_center_agent = self.get_control_center_agent()
        aggregator_agent = self.get_aggregator_agent()
        demand_supply_agents = (self.communication_graph.get_agents_by_type(LeafAgent.LeafAgentType.HOUSEHOLD_AGENT) +
                                self.communication_graph.get_agents_by_type(LeafAgent.LeafAgentType.GENERATION_AGENT) +
                                self.communication_graph.get_agents_by_type(LeafAgent.LeafAgentType.STORAGE_AGENT))
        initial_neg_agent = random.choice(demand_supply_agents)

        time_send = random.randint(0, 100)

        # send request from control center agent to aggregator agent
        cc_config = get_initial_config(control_center_agent)
        cc_config = self.add_message_to_config(
            config=cc_config,
            time_send_ms=time_send,
            receiver=aggregator_agent,
            packet_size_bytes=self.data_size_generator.get_data_size(),
            expect_reply=False
        )
        time_send += random.randint(0, 100)
        # aggregator agent requests one of its leaf agents
        agg_config = get_initial_config(aggregator_agent)
        agg_config = self.add_message_to_config(
            config=agg_config,
            time_send_ms=time_send + random.randint(0, 100),
            receiver=initial_neg_agent,
            packet_size_bytes=self.data_size_generator.get_data_size(),
            expect_reply=False
        )

        agent_configs = {agent: get_initial_config(agent) for agent in demand_supply_agents}

        # while not terminated: leaf agent performs local optimization and sends message to its neighbors
        neg_time = 0
        time_send_init = time_send + random.randint(self.t_central_optimization_range[0],
                                                    self.t_central_optimization_range[1])
        for neighbor in self.communication_graph.get_neighbors(initial_neg_agent):
            # send initial neg message
            agent_configs[initial_neg_agent] = self.add_message_to_config(
                config=agent_configs[initial_neg_agent],
                time_send_ms=time_send_init,
                receiver=neighbor,
                packet_size_bytes=self.data_size_generator.get_data_size(),
                expect_reply=False
            )
        participants = [initial_neg_agent]
        while neg_time < self.negotiation_duration_ms:
            time_send += random.randint(self.t_central_optimization_range[0],
                                        self.t_central_optimization_range[1])
            neg_time = time_send - time_send_init
            for participant in participants:
                for neighbor_of_participant in self.communication_graph.get_neighbors(participant):
                    if neighbor_of_participant not in demand_supply_agents:
                        continue
                    agent_configs[participant] = self.add_message_to_config(
                        config=agent_configs[participant],
                        time_send_ms=time_send,
                        receiver=neighbor_of_participant,
                        packet_size_bytes=self.data_size_generator.get_data_size(),
                        expect_reply=False
                    )
                    if neighbor_of_participant not in participants:
                        participants.append(neighbor_of_participant)

        time_send = neg_time + random.randint(self.t_central_optimization_range[0],
                                              self.t_central_optimization_range[1])

        # initial leaf agent sends solution back to aggregator
        agent_configs[initial_neg_agent] = self.add_message_to_config(
            config=agent_configs[initial_neg_agent],
            time_send_ms=time_send,
            receiver=aggregator_agent,
            packet_size_bytes=self.data_size_generator.get_data_size(),
            expect_reply=False
        )

        time_send += random.randint(self.t_central_optimization_range[0],
                                    self.t_central_optimization_range[1])

        # aggregator forwards solution to control center agent
        agg_config = self.add_message_to_config(
            config=agg_config,
            time_send_ms=time_send,
            receiver=control_center_agent,
            packet_size_bytes=self.data_size_generator.get_data_size(),
            expect_reply=False
        )

        write_config_to_file(control_center_agent.omnet_name, cc_config)
        self.traffic_configurations[control_center_agent.omnet_name] = cc_config

        write_config_to_file(aggregator_agent.omnet_name, agg_config)
        self.traffic_configurations[aggregator_agent.omnet_name] = agg_config

        for agent, agent_config in agent_configs.items():
            write_config_to_file(agent.omnet_name, agent_config)
            self.traffic_configurations[agent.omnet_name] = agent_config

        self.fill_config_for_non_sending_agents()

    def generate_traffic_configuration_files_decentralized(self):
        control_center_agent = self.get_control_center_agent()
        demand_supply_agents = (self.communication_graph.get_agents_by_type(LeafAgent.LeafAgentType.HOUSEHOLD_AGENT) +
                                self.communication_graph.get_agents_by_type(LeafAgent.LeafAgentType.GENERATION_AGENT) +
                                self.communication_graph.get_agents_by_type(LeafAgent.LeafAgentType.STORAGE_AGENT))
        initial_neg_agent = random.choice(demand_supply_agents)

        time_send = random.randint(0, 100)

        # send request from control center agent to initial negotiation agent
        cc_config = get_initial_config(control_center_agent)
        cc_config = self.add_message_to_config(
            config=cc_config,
            time_send_ms=time_send,
            receiver=initial_neg_agent,
            packet_size_bytes=self.data_size_generator.get_data_size(),
            expect_reply=False
        )

        agent_configs = {agent: get_initial_config(agent) for agent in demand_supply_agents}

        # while not terminated: leaf agent performs local optimization and sends message to its neighbors
        neg_time = 0
        time_send_init = time_send + random.randint(self.t_central_optimization_range[0],
                                                    self.t_central_optimization_range[1])
        for neighbor in self.communication_graph.get_neighbors(initial_neg_agent):
            # send initial neg message
            agent_configs[initial_neg_agent] = self.add_message_to_config(
                config=agent_configs[initial_neg_agent],
                time_send_ms=time_send_init,
                receiver=neighbor,
                packet_size_bytes=self.data_size_generator.get_data_size(),
                expect_reply=False
            )
        participants = [initial_neg_agent]
        while neg_time < self.negotiation_duration_ms:
            time_send += random.randint(self.t_central_optimization_range[0],
                                        self.t_central_optimization_range[1])
            neg_time = time_send - time_send_init
            for participant in participants:
                for neighbor_of_participant in self.communication_graph.get_neighbors(participant):
                    if neighbor_of_participant not in demand_supply_agents:
                        continue
                    agent_configs[participant] = self.add_message_to_config(
                        config=agent_configs[participant],
                        time_send_ms=time_send,
                        receiver=neighbor_of_participant,
                        packet_size_bytes=self.data_size_generator.get_data_size(),
                        expect_reply=False
                    )
                    if neighbor_of_participant not in participants:
                        participants.append(neighbor_of_participant)

        time_send = neg_time + random.randint(self.t_central_optimization_range[0],
                                              self.t_central_optimization_range[1])

        # initial leaf agent sends solution back to control center agent
        agent_configs[initial_neg_agent] = self.add_message_to_config(
            config=agent_configs[initial_neg_agent],
            time_send_ms=time_send,
            receiver=control_center_agent,
            packet_size_bytes=self.data_size_generator.get_data_size(),
            expect_reply=False
        )

        write_config_to_file(control_center_agent.omnet_name, cc_config)
        self.traffic_configurations[control_center_agent.omnet_name] = cc_config

        for agent, agent_config in agent_configs.items():
            write_config_to_file(agent.omnet_name, agent_config)
            self.traffic_configurations[agent.omnet_name] = agent_config

        self.fill_config_for_non_sending_agents()


class MarketParticipation(ComplexAgentCommunicationPattern):
    def __init__(self, simulation_duration_ms: int, communication_graph: CommunicationGraph,
                 data_size_generator: DataSizeGenerator, organizational_structure: OrganizationalStructure,
                 market_interval_ms: int, t_local_optimization: tuple[int, int], num_iterations_till_goal=0):
        self.market_interval_ms = market_interval_ms
        self.t_local_optimization = t_local_optimization
        self.num_iterations_till_goal = num_iterations_till_goal
        super().__init__(simulation_duration_ms, communication_graph, TriggerType.TIME_TRIGGERED, data_size_generator,
                         organizational_structure)

    def generate_traffic_configuration_files_centralized(self):
        market_agent = self.get_market_agent()
        participant_agents = (self.communication_graph.get_agents_by_type(LeafAgent.LeafAgentType.HOUSEHOLD_AGENT) +
                              self.communication_graph.get_agents_by_type(LeafAgent.LeafAgentType.GENERATION_AGENT) +
                              self.communication_graph.get_agents_by_type(LeafAgent.LeafAgentType.STORAGE_AGENT))

        # in interval:
        time_send = random.randint(0, 100)
        market_agent_config = get_initial_config(market_agent)

        while time_send < self.simulation_duration_ms:
            # send price from market to load/generator agents, expect reply with offer
            for participant_agent in participant_agents:
                market_agent_config = (
                    self.add_message_to_config(config=market_agent_config,
                                               time_send_ms=time_send,
                                               receiver=participant_agent,
                                               packet_size_bytes=self.data_size_generator.get_data_size(),
                                               expect_reply=True,
                                               reply_after_ms_range=self.t_local_optimization))
            time_send += self.market_interval_ms
        write_config_to_file(market_agent.omnet_name, market_agent_config)
        self.traffic_configurations[market_agent.omnet_name] = market_agent_config

        self.fill_config_for_non_sending_agents()

    def generate_traffic_configuration_files_hierarchical(self):
        market_agent = self.get_market_agent()
        aggregator_agent = self.get_aggregator_agent()
        participant_agents = (self.communication_graph.get_agents_by_type(LeafAgent.LeafAgentType.HOUSEHOLD_AGENT) +
                              self.communication_graph.get_agents_by_type(LeafAgent.LeafAgentType.GENERATION_AGENT) +
                              self.communication_graph.get_agents_by_type(LeafAgent.LeafAgentType.STORAGE_AGENT))

        # in interval:
        time_send = random.randint(0, 100)
        market_agent_config = get_initial_config(market_agent)
        aggregator_agent_config = get_initial_config(aggregator_agent)

        while time_send + 500 < self.simulation_duration_ms:
            # send price signal from market to aggregator
            market_agent_config = (
                self.add_message_to_config(config=market_agent_config,
                                           time_send_ms=time_send,
                                           receiver=aggregator_agent,
                                           packet_size_bytes=self.data_size_generator.get_data_size(),
                                           expect_reply=False))
            time_send += random.randint(10, 100)
            # send random number of times message -> reply between aggregator and participants
            for _ in range(self.num_iterations_till_goal):
                time_send += random.randint(10, 100)
                for part_agent in participant_agents:
                    aggregator_agent_config = (
                        self.add_message_to_config(config=aggregator_agent_config,
                                                   time_send_ms=time_send,
                                                   receiver=part_agent,
                                                   packet_size_bytes=self.data_size_generator.get_data_size(),
                                                   expect_reply=True,
                                                   reply_after_ms_range=self.t_local_optimization))
            # inform other participant agents
            time_send += random.randint(10, 100)
            for part_agent in participant_agents:
                aggregator_agent_config = (
                    self.add_message_to_config(config=aggregator_agent_config,
                                               time_send_ms=time_send,
                                               receiver=part_agent,
                                               packet_size_bytes=self.data_size_generator.get_data_size(),
                                               expect_reply=False))
            # inform market agent
            time_send += random.randint(10, 100)
            aggregator_agent_config = (
                self.add_message_to_config(config=aggregator_agent_config,
                                           time_send_ms=time_send,
                                           receiver=market_agent,
                                           packet_size_bytes=self.data_size_generator.get_data_size(),
                                           expect_reply=False))
            time_send += self.market_interval_ms
        write_config_to_file(market_agent.omnet_name, market_agent_config)
        self.traffic_configurations[market_agent.omnet_name] = market_agent_config

        write_config_to_file(aggregator_agent.omnet_name, aggregator_agent_config)
        self.traffic_configurations[aggregator_agent.omnet_name] = aggregator_agent_config

        self.fill_config_for_non_sending_agents()

    def generate_traffic_configuration_files_decentralized(self):
        participant_agents = (self.communication_graph.get_agents_by_type(LeafAgent.LeafAgentType.HOUSEHOLD_AGENT) +
                              self.communication_graph.get_agents_by_type(LeafAgent.LeafAgentType.GENERATION_AGENT) +
                              self.communication_graph.get_agents_by_type(LeafAgent.LeafAgentType.STORAGE_AGENT))

        random_initiator = random.choice(participant_agents)
        initiator_config = get_initial_config(random_initiator)

        time_send = random.randint(0, 100)

        for _ in range(self.num_iterations_till_goal):
            for neighbor in self.communication_graph.get_neighbors(random_initiator):
                if neighbor in participant_agents:
                    initiator_config = (
                        self.add_message_to_config(config=initiator_config,
                                                   time_send_ms=time_send,
                                                   receiver=neighbor,
                                                   packet_size_bytes=self.data_size_generator.get_data_size(),
                                                   expect_reply=True,
                                                   reply_after_ms_range=self.t_local_optimization))
        write_config_to_file(random_initiator.omnet_name, initiator_config)
        self.traffic_configurations[random_initiator.omnet_name] = initiator_config

        self.fill_config_for_non_sending_agents()


class VoltageRegulation(ComplexAgentCommunicationPattern):
    def __init__(self, simulation_duration_ms: int, communication_graph: CommunicationGraph,
                 data_size_generator: DataSizeGenerator, organizational_structure: OrganizationalStructure,
                 t_local_optimization_ms_range: tuple[int, int]):
        self.t_local_optimization_ms_range = t_local_optimization_ms_range
        super().__init__(simulation_duration_ms, communication_graph, TriggerType.TIME_TRIGGERED, data_size_generator,
                         organizational_structure)

    def generate_traffic_configuration_files_centralized(self):
        control_center_agent = self.get_control_center_agent()
        pmu_pdc_agents = (
                self.communication_graph.get_agents_by_type(LeafAgent.LeafAgentType.GRID_INFRASTRUCTURE_AGENT) +
                self.communication_graph.get_agents_by_type(AggregatorAgent.AggregatorAgentType.PDC_AGENT))
        leaf_agents = self.communication_graph.get_agents_by_class(LeafAgent)

        # send measurements from pmu/pdc agents to control center agent
        time_send = random.randint(0, 100)
        agent_configs = {agent: get_initial_config(agent) for agent in pmu_pdc_agents}
        control_center_agent_config = get_initial_config(control_center_agent)
        for agent in pmu_pdc_agents:
            agent_configs[agent] = self.add_message_to_config(config=agent_configs[agent],
                                                              time_send_ms=time_send,
                                                              receiver=control_center_agent,
                                                              packet_size_bytes=self.data_size_generator.get_data_size())

        # send control command from control center agent to leaf agent
        time_send += random.randint(self.t_local_optimization_ms_range[0],
                                    self.t_local_optimization_ms_range[1])
        for agent in leaf_agents:
            control_center_agent_config = self.add_message_to_config(config=control_center_agent_config,
                                                                     time_send_ms=time_send,
                                                                     receiver=agent,
                                                                     packet_size_bytes=self.data_size_generator.get_data_size())
        write_config_to_file(control_center_agent.omnet_name, control_center_agent_config)
        self.traffic_configurations[control_center_agent.omnet_name] = control_center_agent_config

        for agent, agent_config in agent_configs.items():
            write_config_to_file(agent.omnet_name, agent_config)
            self.traffic_configurations[agent.omnet_name] = agent_config

        self.fill_config_for_non_sending_agents()

    def generate_traffic_configuration_files_hierarchical(self):
        substation_agent = \
            self.communication_graph.get_agents_by_type(AggregatorAgent.AggregatorAgentType.SUBSTATION_AGENT)[0]
        pmu_pdc_agents = (
                self.communication_graph.get_agents_by_type(LeafAgent.LeafAgentType.GRID_INFRASTRUCTURE_AGENT) +
                self.communication_graph.get_agents_by_type(AggregatorAgent.AggregatorAgentType.PDC_AGENT))

        # send measurements from pmu/pdc agents to control center agent
        time_send = random.randint(0, 100)
        agent_configs = {agent: get_initial_config(agent) for agent in pmu_pdc_agents}
        for agent in pmu_pdc_agents:
            agent_configs[agent] = self.add_message_to_config(config=agent_configs[agent],
                                                              time_send_ms=time_send,
                                                              receiver=substation_agent,
                                                              packet_size_bytes=self.data_size_generator.get_data_size(),
                                                              expect_reply=True,
                                                              reply_after_ms_range=self.t_local_optimization_ms_range)

        for agent, agent_config in agent_configs.items():
            write_config_to_file(agent.omnet_name, agent_config)
            self.traffic_configurations[agent.omnet_name] = agent_config

        self.fill_config_for_non_sending_agents()

    def generate_traffic_configuration_files_decentralized(self):
        bus_agents = self.communication_graph.get_agents_by_class(LeafAgent) #TODO: should be bus agents again

        # send measurements from pmu/pdc agents to control center agent
        time_send = random.randint(0, 100)
        agent_configs = {agent: get_initial_config(agent) for agent in bus_agents}
        for agent in bus_agents:
            for neighbor in self.communication_graph.get_neighbors(agent):
                if neighbor in bus_agents:
                    agent_configs[agent] = self.add_message_to_config(config=agent_configs[agent],
                                                                      time_send_ms=time_send,
                                                                      receiver=neighbor,
                                                                      packet_size_bytes=self.data_size_generator.get_data_size(),
                                                                      expect_reply=True,
                                                                      reply_after_ms_range=self.t_local_optimization_ms_range)

        for agent, agent_config in agent_configs.items():
            write_config_to_file(agent.omnet_name, agent_config)
            self.traffic_configurations[agent.omnet_name] = agent_config

        self.fill_config_for_non_sending_agents()


class EVManagementSystem(ComplexAgentCommunicationPattern):
    def __init__(self, simulation_duration_ms: int, communication_graph: CommunicationGraph,
                 data_size_generator: DataSizeGenerator, organizational_structure: OrganizationalStructure,
                 t_local_optimization_ms_range: tuple[int, int], num_iterations_till_goal=0):
        self.t_local_optimization_ms_range = t_local_optimization_ms_range
        self.num_iterations_till_goal = num_iterations_till_goal
        super().__init__(simulation_duration_ms, communication_graph, TriggerType.EVENT_TRIGGERED, data_size_generator,
                         organizational_structure)

    def generate_traffic_configuration_files_centralized(self):
        ev_agents = self.communication_graph.get_agents_by_type(LeafAgent.LeafAgentType.HOUSEHOLD_AGENT)
        dso_agent = self.get_grid_operator_agent()

        # ev agents send charge requirement to dso agent, dso agent replies
        time_send = random.randint(0, 100)
        agent_configs = {agent: get_initial_config(agent) for agent in ev_agents}
        for agent in ev_agents:
            agent_configs[agent] = self.add_message_to_config(config=agent_configs[agent],
                                                              time_send_ms=time_send,
                                                              receiver=dso_agent,
                                                              packet_size_bytes=self.data_size_generator.get_data_size(),
                                                              expect_reply=True,
                                                              reply_after_ms_range=self.t_local_optimization_ms_range)

        for agent, agent_config in agent_configs.items():
            write_config_to_file(agent.omnet_name, agent_config)
            self.traffic_configurations[agent.omnet_name] = agent_config

        self.fill_config_for_non_sending_agents()

    def generate_traffic_configuration_files_hierarchical(self):
        market_agent = self.get_market_agent()
        aggregator_agent = self.get_aggregator_agent()
        grid_operator_agent = self.get_grid_operator_agent()
        ev_agents = self.communication_graph.get_agents_by_type(LeafAgent.LeafAgentType.HOUSEHOLD_AGENT)

        agent_to_configs = {}

        time_send_price = random.randint(0, 100)
        # market agent sends price to aggregator
        agent_to_configs[market_agent] = get_initial_config(market_agent)
        agent_to_configs[market_agent] = (
            self.add_message_to_config(config=agent_to_configs[market_agent],
                                       time_send_ms=time_send_price,
                                       receiver=aggregator_agent,
                                       packet_size_bytes=self.data_size_generator.get_data_size(),
                                       expect_reply=False))

        time_send_constraints = random.randint(0, 100)
        # grid operator sends constraints to aggregator
        agent_to_configs[grid_operator_agent] = get_initial_config(grid_operator_agent)
        agent_to_configs[grid_operator_agent] = (
            self.add_message_to_config(config=agent_to_configs[grid_operator_agent],
                                       time_send_ms=time_send_constraints,
                                       receiver=aggregator_agent,
                                       packet_size_bytes=self.data_size_generator.get_data_size(),
                                       expect_reply=False))

        time_send_min = max(time_send_price, time_send_constraints)
        # ev agents send bid to aggregator agent, aggregator replies with control signal
        for agent in ev_agents:
            agent_to_configs[agent] = (
                self.add_message_to_config(config=get_initial_config(agent),
                                           time_send_ms=time_send_min + random.randint(0, 100),
                                           receiver=aggregator_agent,
                                           packet_size_bytes=self.data_size_generator.get_data_size(),
                                           expect_reply=True,
                                           reply_after_ms_range=self.t_local_optimization_ms_range))
        for agent, agent_config in agent_to_configs.items():
            write_config_to_file(agent.omnet_name, agent_config)
            self.traffic_configurations[agent.omnet_name] = agent_config

        self.fill_config_for_non_sending_agents()

    def generate_traffic_configuration_files_decentralized(self):
        # while not terminated:
        # send schedule from ev agent to neighbors and expect reply

        ev_agents = self.communication_graph.get_agents_by_type(LeafAgent.LeafAgentType.HOUSEHOLD_AGENT)

        time_send_min = random.randint(0, 100)
        agent_configs = {agent: get_initial_config(agent) for agent in ev_agents}

        for _ in range(self.num_iterations_till_goal):
            for ev_agent in ev_agents:
                for neighbor in self.communication_graph.get_neighbors(ev_agent):
                    if neighbor in ev_agents:
                        agent_configs[ev_agent] = (
                            self.add_message_to_config(config=agent_configs[ev_agent],
                                                       time_send_ms=time_send_min + random.randint(0, 100),
                                                       receiver=neighbor,
                                                       packet_size_bytes=self.data_size_generator.get_data_size(),
                                                       expect_reply=True,
                                                       reply_after_ms_range=self.t_local_optimization_ms_range))
            time_send_min += 100 + self.t_local_optimization_ms_range[1]

        for agent, agent_config in agent_configs.items():
            write_config_to_file(agent.omnet_name, agent_config)
            self.traffic_configurations[agent.omnet_name] = agent_config

        self.fill_config_for_non_sending_agents()


class FaultDetectionAndLocation(ComplexAgentCommunicationPattern):
    def __init__(self, simulation_duration_ms: int, communication_graph: CommunicationGraph,
                 data_size_generator: DataSizeGenerator, organizational_structure: OrganizationalStructure,
                 t_local_optimization_ms_range: tuple[int, int]):
        self.t_local_optimization_ms_range = t_local_optimization_ms_range
        super().__init__(simulation_duration_ms, communication_graph, TriggerType.EVENT_TRIGGERED, data_size_generator,
                         organizational_structure)

    def generate_traffic_configuration_files_centralized(self):
        pmu_agents = self.communication_graph.get_agents_by_type(LeafAgent.LeafAgentType.GRID_INFRASTRUCTURE_AGENT)
        control_center_agent = self.get_control_center_agent()

        for agent in pmu_agents:
            agent_config = self.add_message_to_config(config=get_initial_config(agent),
                                                      time_send_ms=random.randint(0, 100),
                                                      receiver=control_center_agent,
                                                      packet_size_bytes=self.data_size_generator.get_data_size(),
                                                      expect_reply=False)
            write_config_to_file(agent.omnet_name, agent_config)
            self.traffic_configurations[agent.omnet_name] = agent_config

    def generate_traffic_configuration_files_hierarchical(self):
        pmu_agents = self.communication_graph.get_agents_by_type(LeafAgent.LeafAgentType.GRID_INFRASTRUCTURE_AGENT)
        pdc_agent = self.communication_graph.get_agents_by_type(AggregatorAgent.AggregatorAgentType.PDC_AGENT)[0]

        for agent in pmu_agents:
            agent_config = self.add_message_to_config(config=get_initial_config(agent),
                                                      time_send_ms=random.randint(0, 100),
                                                      receiver=pdc_agent,
                                                      packet_size_bytes=self.data_size_generator.get_data_size(),
                                                      expect_reply=False)
            write_config_to_file(agent.omnet_name, agent_config)
            self.traffic_configurations[agent.omnet_name] = agent_config

    def generate_traffic_configuration_files_decentralized(self):
        leaf_agents = self.communication_graph.get_agents_by_class(LeafAgent)

        agent_with_fault = random.choice(leaf_agents)

        agent_config = get_initial_config(agent_with_fault)
        time_send = random.randint(0, 100)

        for neighbor in self.communication_graph.get_neighbors(agent_with_fault):
            agent_config = self.add_message_to_config(config=agent_config,
                                                      time_send_ms=time_send,
                                                      receiver=neighbor,
                                                      packet_size_bytes=self.data_size_generator.get_data_size(),
                                                      expect_reply=True,
                                                      reply_after_ms_range=self.t_local_optimization_ms_range)
        write_config_to_file(agent_with_fault.omnet_name, agent_config)
        self.traffic_configurations[agent_with_fault.omnet_name] = agent_config


"""
Concrete pattern implementations for SimpleAgentCommunication.
"""


class CustomerAutomation(SimpleAgentCommunicationPattern):
    def __init__(self,
                 simulation_duration_ms: int,
                 communication_graph: CommunicationGraph,
                 trigger_interval_ms: int,
                 num_devices: int):
        data_size_generator = InIntervalDataSizeGenerator(lower_bound_byte=10,
                                                          upper_bound_byte=100)
        self.num_devices = num_devices
        super().__init__(simulation_duration_ms, communication_graph, TriggerType.TIME_TRIGGERED, trigger_interval_ms,
                         data_size_generator, CommunicationMode.BROADCAST)

    def generate_traffic_configuration_files(self):
        """
        Generate traffic for the following message flow:
        in interval x:
            Smart devices -> Home Energy Management System
            Home Energy Management System -> Smart devices
        """
        device_agents = self.communication_graph.get_agents_by_type(LeafAgent.LeafAgentType.DEVICE_AGENT)
        hems_agents = self.communication_graph.get_agents_by_type(LeafAgent.LeafAgentType.HOUSEHOLD_AGENT)
        if len(hems_agents) == 0:
            raise ValueError('No HEMS agent implemented.')
        if len(hems_agents) > 1:
            raise ValueError('More than one HEMS agent.')
        self.generate_to_neighbor_communication(agents=hems_agents + random.sample(device_agents, self.num_devices))


class ScheduledAutomatedMeterReading(SimpleAgentCommunicationPattern):
    def __init__(self, simulation_duration_ms: int, communication_graph: CommunicationGraph):
        data_size_generator = InIntervalDataSizeGenerator(lower_bound_byte=1600,
                                                          upper_bound_byte=2400)
        super().__init__(simulation_duration_ms, communication_graph, TriggerType.TIME_TRIGGERED, 21600000,
                         data_size_generator, CommunicationMode.MANY_TO_ONE)

    def generate_traffic_configuration_files(self):
        control_center_agent = self.get_control_center_agent()
        meter_agents = self.communication_graph.get_agents_by_type(LeafAgent.LeafAgentType.HOUSEHOLD_AGENT)
        self.generate_many_to_one_communication(one=control_center_agent,
                                                many=meter_agents,
                                                send_only_once=True)


class OnDemandAutomatedMeterReading(SimpleAgentCommunicationPattern):
    def __init__(self, simulation_duration_ms: int, communication_graph: CommunicationGraph):
        data_size_generator = FixedDataSizeGenerator(data_size_byte=100)
        super().__init__(simulation_duration_ms, communication_graph, TriggerType.EVENT_TRIGGERED, 10000,
                         data_size_generator, CommunicationMode.MANY_TO_ONE)

    def generate_traffic_configuration_files(self):
        control_center_agent = self.get_control_center_agent()
        meter_agents = self.communication_graph.get_agents_by_type(LeafAgent.LeafAgentType.HOUSEHOLD_AGENT)
        # only some meters send data
        meter_agents = random.sample(meter_agents, int(len(meter_agents) / 3))
        self.generate_many_to_one_communication(one=control_center_agent,
                                                many=meter_agents,
                                                send_only_once=False)


class PricingApplication(SimpleAgentCommunicationPattern):
    def __init__(self, simulation_duration_ms: int,
                 communication_graph: CommunicationGraph,
                 market_interval=5 * 60 * 1000):
        data_size_generator = FixedDataSizeGenerator(data_size_byte=100)
        super().__init__(simulation_duration_ms, communication_graph, TriggerType.TIME_TRIGGERED, market_interval,
                         data_size_generator, CommunicationMode.MANY_TO_ONE)

    def generate_traffic_configuration_files(self):
        market_agent = self.get_market_agent()
        meter_agents = self.communication_graph.get_agents_by_type(LeafAgent.LeafAgentType.HOUSEHOLD_AGENT)
        self.generate_broadcast_time_triggered_communication(one=market_agent,
                                                             many=meter_agents)


class DemandResponse(SimpleAgentCommunicationPattern):
    def __init__(self, simulation_duration_ms: int,
                 communication_graph: CommunicationGraph,
                 reply_after_range: tuple[int, int],
                 communication_mode: CommunicationMode):
        self.reply_after_range = reply_after_range
        data_size_generator = FixedDataSizeGenerator(data_size_byte=100)
        super().__init__(simulation_duration_ms, communication_graph, TriggerType.EVENT_TRIGGERED, 0,
                         data_size_generator, communication_mode)

    def generate_traffic_configuration_files(self):
        control_center_agent = self.get_control_center_agent()
        meter_agents = self.communication_graph.get_agents_by_type(LeafAgent.LeafAgentType.HOUSEHOLD_AGENT)

        send_time = random.randint(0, 100)  # in the first 100 ms

        self.generate_event_triggered_communication(one=control_center_agent,
                                                    many=meter_agents,
                                                    send_time=send_time,
                                                    expect_reply=True,
                                                    reply_after_range=self.reply_after_range)


class DataAcquisition(SimpleAgentCommunicationPattern):
    def __init__(self, simulation_duration_ms: int, communication_graph: CommunicationGraph,
                 reply_after_range: tuple[int, int], ):
        self.reply_after_range = reply_after_range
        data_size_generator = InIntervalDataSizeGenerator(lower_bound_byte=50, upper_bound_byte=1000)
        super().__init__(simulation_duration_ms, communication_graph, TriggerType.TIME_TRIGGERED, 5000,
                         data_size_generator, CommunicationMode.BROADCAST)

    def generate_traffic_configuration_files(self):
        leaf_agents = self.communication_graph.get_agents_by_class(LeafAgent)
        control_center_agent = self.get_control_center_agent()

        self.generate_broadcast_time_triggered_communication(one=control_center_agent,
                                                             many=leaf_agents,
                                                             expect_reply=True,
                                                             reply_after_range=self.reply_after_range)


class VoltageReduction(SimpleAgentCommunicationPattern):
    def __init__(self, simulation_duration_ms: int,
                 communication_graph: CommunicationGraph):
        data_size_generator = InIntervalDataSizeGenerator(lower_bound_byte=50, upper_bound_byte=1000)
        super().__init__(simulation_duration_ms, communication_graph, TriggerType.EVENT_TRIGGERED, 0,
                         data_size_generator, CommunicationMode.BROADCAST)

    def generate_traffic_configuration_files(self):
        control_center_agent = self.get_control_center_agent()
        leaf_agents = self.communication_graph.get_agents_by_class(LeafAgent)

        send_time = random.randint(0, 100)  # in the first 100 ms

        self.generate_event_triggered_communication(one=control_center_agent,
                                                    many=leaf_agents,
                                                    send_time=send_time)


class FaultLocationIsolation(SimpleAgentCommunicationPattern):
    def __init__(self, simulation_duration_ms: int,
                 communication_graph: CommunicationGraph,
                 reply_after_range: tuple[int, int]):
        self.reply_after_range = reply_after_range
        data_size_generator = FixedDataSizeGenerator(data_size_byte=50)
        super().__init__(simulation_duration_ms, communication_graph, TriggerType.EVENT_TRIGGERED, 0,
                         data_size_generator, CommunicationMode.BROADCAST)

    def generate_traffic_configuration_files(self):
        control_center_agent = self.get_control_center_agent()
        leaf_agents = self.communication_graph.get_agents_by_class(LeafAgent)

        send_time = random.randint(0, 100)  # in the first 100 ms

        self.generate_event_triggered_communication(one=control_center_agent,
                                                    many=leaf_agents,
                                                    send_time=send_time,
                                                    expect_reply=True,
                                                    reply_after_range=self.reply_after_range)


class StorageApplication(SimpleAgentCommunicationPattern):
    def __init__(self, simulation_duration_ms: int,
                 communication_graph: CommunicationGraph,
                 reply_after_range: tuple[int, int]):
        self.reply_after_range = reply_after_range
        data_size_generator = FixedDataSizeGenerator(data_size_byte=50)
        super().__init__(simulation_duration_ms, communication_graph, TriggerType.TIME_TRIGGERED, 12000,
                         data_size_generator, CommunicationMode.BROADCAST)

    def generate_traffic_configuration_files(self):
        control_center_agent = self.get_control_center_agent()
        meter_agents = self.communication_graph.get_agents_by_type(LeafAgent.LeafAgentType.HOUSEHOLD_AGENT)
        storage_agents = self.communication_graph.get_agents_by_type(LeafAgent.LeafAgentType.STORAGE_AGENT)

        self.generate_broadcast_time_triggered_communication(one=control_center_agent,
                                                             many=meter_agents + storage_agents,
                                                             expect_reply=True,
                                                             reply_after_range=self.reply_after_range)


class OutageRestorationManagement(SimpleAgentCommunicationPattern):
    def __init__(self, simulation_duration_ms: int,
                 communication_graph: CommunicationGraph,
                 reply_after_range: tuple[int, int]):
        self.reply_after_range = reply_after_range
        data_size_generator = FixedDataSizeGenerator(data_size_byte=25)
        super().__init__(simulation_duration_ms, communication_graph, TriggerType.EVENT_TRIGGERED, 0,
                         data_size_generator, CommunicationMode.UNICAST)

    def generate_traffic_configuration_files(self):
        control_center_agent = self.get_control_center_agent()
        meter_agents = self.communication_graph.get_agents_by_type(LeafAgent.LeafAgentType.HOUSEHOLD_AGENT)

        send_time = random.randint(0, 100)  # in the first 100 ms

        self.generate_event_triggered_communication(one=control_center_agent,
                                                    many=meter_agents,
                                                    send_time=send_time,
                                                    expect_reply=True,
                                                    reply_after_range=self.reply_after_range)


class CustomerInformation(SimpleAgentCommunicationPattern):
    def __init__(self, simulation_duration_ms: int,
                 communication_graph: CommunicationGraph):
        data_size_generator = FixedDataSizeGenerator(data_size_byte=200)
        super().__init__(simulation_duration_ms, communication_graph, TriggerType.TIME_TRIGGERED, 1000,
                         data_size_generator, CommunicationMode.BROADCAST)

    def generate_traffic_configuration_files(self):
        control_center_agent = self.get_control_center_agent()
        meter_agents = self.communication_graph.get_agents_by_type(LeafAgent.LeafAgentType.HOUSEHOLD_AGENT)

        self.generate_broadcast_time_triggered_communication(one=control_center_agent,
                                                             many=meter_agents)


class WACsVoltageStabilityControl(SimpleAgentCommunicationPattern):
    def __init__(self, simulation_duration_ms: int, communication_graph: CommunicationGraph):
        data_size_generator = FixedDataSizeGenerator(data_size_byte=18)
        super().__init__(simulation_duration_ms, communication_graph, TriggerType.EVENT_TRIGGERED, 0,
                         data_size_generator, CommunicationMode.BROADCAST)

    def generate_traffic_configuration_files(self):
        control_center_agent = self.get_control_center_agent()

        pmu_agents = self.communication_graph.get_agents_by_type(LeafAgent.LeafAgentType.GRID_INFRASTRUCTURE_AGENT)
        pdc_agents = self.communication_graph.get_agents_by_type(AggregatorAgent.AggregatorAgentType.PDC_AGENT)

        self.generate_event_triggered_communication(one=control_center_agent,
                                                    many=pmu_agents + pdc_agents,
                                                    expect_reply=True,
                                                    reply_after_range=(0, 100),
                                                    multiple_events=True,
                                                    event_frequency_range=(500, 5000)
                                                    )


class WACsPowerOscillationMonitoring(SimpleAgentCommunicationPattern):
    def __init__(self, simulation_duration_ms: int, communication_graph: CommunicationGraph):
        data_size_generator = FixedDataSizeGenerator(data_size_byte=18)
        super().__init__(simulation_duration_ms, communication_graph, TriggerType.TIME_TRIGGERED, 100,
                         data_size_generator, CommunicationMode.BROADCAST)

    def generate_traffic_configuration_files(self):
        control_center_agent = self.get_control_center_agent()

        pmu_agents = self.communication_graph.get_agents_by_type(LeafAgent.LeafAgentType.GRID_INFRASTRUCTURE_AGENT)
        pdc_agents = self.communication_graph.get_agents_by_type(AggregatorAgent.AggregatorAgentType.PDC_AGENT)

        self.generate_broadcast_time_triggered_communication(one=control_center_agent,
                                                             many=pmu_agents + pdc_agents,
                                                             expect_reply=True,
                                                             reply_after_range=(0, 100))


class WideAreaProtection(SimpleAgentCommunicationPattern):
    def __init__(self, simulation_duration_ms: int, communication_graph: CommunicationGraph):
        data_size_generator = FixedDataSizeGenerator(data_size_byte=18)
        super().__init__(simulation_duration_ms, communication_graph, TriggerType.TIME_TRIGGERED, 100,
                         data_size_generator, CommunicationMode.BROADCAST)

    def generate_traffic_configuration_files(self):
        control_center_agent = self.get_control_center_agent()

        pmu_agents = self.communication_graph.get_agents_by_type(LeafAgent.LeafAgentType.GRID_INFRASTRUCTURE_AGENT)
        pdc_agents = self.communication_graph.get_agents_by_type(AggregatorAgent.AggregatorAgentType.PDC_AGENT)

        self.generate_broadcast_time_triggered_communication(one=control_center_agent,
                                                             many=pmu_agents + pdc_agents,
                                                             expect_reply=True,
                                                             reply_after_range=(0, 100))


class WAMsStateEstimation(SimpleAgentCommunicationPattern):
    def __init__(self, simulation_duration_ms: int, communication_graph: CommunicationGraph):
        data_size_generator = FixedDataSizeGenerator(data_size_byte=52)
        super().__init__(simulation_duration_ms, communication_graph, TriggerType.TIME_TRIGGERED, 100,
                         data_size_generator, CommunicationMode.BROADCAST)

    def generate_traffic_configuration_files(self):
        control_center_agent = self.get_control_center_agent()

        pmu_agents = self.communication_graph.get_agents_by_type(LeafAgent.LeafAgentType.GRID_INFRASTRUCTURE_AGENT)
        pdc_agents = self.communication_graph.get_agents_by_type(AggregatorAgent.AggregatorAgentType.PDC_AGENT)

        if len(pmu_agents + pdc_agents) == 0:
            raise ValueError('No PMU oder PDC agents in network!')

        self.generate_broadcast_time_triggered_communication(one=control_center_agent,
                                                             many=pmu_agents + pdc_agents)
