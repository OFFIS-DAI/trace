import random
import sys
from pathlib import Path

from agent_communication_generation_tool.description_classes.data_size_generator import InIntervalDataSizeGenerator

# Add the parent directory of "agent_communication_generation_tool" to sys.path
sys.path.append(Path(__file__).parent.parent.parent.absolute().__str__())

from network_generation.simbench_network_extractor import SystemState
from agent_communication_generation_tool.complex_use_cases.simulation_run_variables import \
    complexities, overlay_types, data_size_generators
from agent_communication_generation_tool.description_classes.simbench_codes import simbench_codes_low_voltage
from agent_communication_generation_tool.description_classes.communication_scenario_description import \
    CommunicationScenarioDescription
from agent_communication_generation_tool.description_classes.agent_communication_pattern import \
    MarketParticipation, OrganizationalStructure
from agent_communication_generation_tool.description_classes.communication_graph import StarCommunicationGraph, \
    SmallWorldOverlayGraph
from agent_communication_generation_tool.description_classes.communication_network_description import \
    Simbench5GNetworkDescription, SimbenchLTENetworkDescription

SIMULATION_DURATION_MS = 5 * 60 * 1000 + 1

market_interval = 5 * 60 * 1000  # 5 minutes, 10 minutes, 30 minutes
num_iterations_till_goal = 2
max_num_agents_per_type = 3

communication_network_description = Simbench5GNetworkDescription(
    simbench_code=simbench_codes_low_voltage[2],
    system_state=SystemState.NORMAL)
"""
Centralized
"""
communication_graph = (
    StarCommunicationGraph(agents=communication_network_description.agents,
                           central_agent=communication_network_description.control_center_agent,
                           max_number_of_agents_per_type=max_num_agents_per_type))
communication_pattern = MarketParticipation(
    simulation_duration_ms=SIMULATION_DURATION_MS,
    communication_graph=communication_graph,
    data_size_generator=InIntervalDataSizeGenerator(50, 200),
    organizational_structure=OrganizationalStructure.CENTRALIZED,
    market_interval_ms=market_interval,
    t_local_optimization=(100, 1000))
communication_scenario_description = (
    CommunicationScenarioDescription(
        description_text=f'market_participation_CENTRALIZED_'
                         f'simbench_network_'
                         f'{communication_network_description.simbench_code},'
                         f'_{communication_network_description.technology}',
        communication_graph=communication_graph,
        communication_network_description=communication_network_description,
        agent_communication_pattern=communication_pattern))

communication_scenario_description.run_simulation()

"""
Hierarchical
"""
overlay = SmallWorldOverlayGraph(
                agents=communication_network_description.agents,
                central_agent=communication_network_description.control_center_agent,
                p=0.5,
                max_number_of_agents_per_type=max_num_agents_per_type)
communication_pattern = MarketParticipation(
    simulation_duration_ms=SIMULATION_DURATION_MS,
    communication_graph=overlay,
    data_size_generator=InIntervalDataSizeGenerator(50, 200),
    organizational_structure=OrganizationalStructure.HIERARCHICAL,
    market_interval_ms=market_interval,
    t_local_optimization=(100, 1000),
    num_iterations_till_goal=num_iterations_till_goal)
communication_scenario_description = (
    CommunicationScenarioDescription(
        description_text=f'market_participation_HIERARCHICAL_'
                         f'simbench_network_'
                         f'{communication_network_description.simbench_code},'
                         f'_{communication_network_description.technology}',
        communication_graph=overlay,
        communication_network_description=communication_network_description,
        agent_communication_pattern=communication_pattern))

communication_scenario_description.run_simulation()

"""
Decentralized
"""
communication_pattern = MarketParticipation(
            simulation_duration_ms=SIMULATION_DURATION_MS,
            communication_graph=overlay,
            data_size_generator=InIntervalDataSizeGenerator(50, 200),
            organizational_structure=OrganizationalStructure.DECENTRALIZED,
            market_interval_ms=0,
            t_local_optimization=(100, 1000),
            num_iterations_till_goal=num_iterations_till_goal)
communication_scenario_description = (
    CommunicationScenarioDescription(
        description_text=f'market_participation_DECENTRALIZED_'
                         f'simbench_network_'
                         f'{communication_network_description.simbench_code},'
                         f'_{communication_network_description.technology}',
        communication_graph=overlay,
        communication_network_description=communication_network_description,
        agent_communication_pattern=communication_pattern))

communication_scenario_description.run_simulation()
