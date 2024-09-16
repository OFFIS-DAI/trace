import random
import sys
from pathlib import Path

# Add the parent directory of "agent_communication_generation_tool" to sys.path
sys.path.append(Path(__file__).parent.parent.parent.absolute().__str__())

from agent_communication_generation_tool.simulation_run_variables import num_agents, system_states, \
    network_description_classes
from agent_communication_generation_tool.simulation_run_variables import \
    complexities, overlay_types, data_size_generators
from agent_communication_generation_tool.description_classes.simbench_codes import simbench_codes_analysis
from agent_communication_generation_tool.description_classes.communication_scenario_description import \
    CommunicationScenarioDescription
from agent_communication_generation_tool.description_classes.agent_communication_pattern import \
    MarketParticipation, OrganizationalStructure
from agent_communication_generation_tool.description_classes.communication_graph import StarCommunicationGraph
from agent_communication_generation_tool.description_classes.communication_network_description import \
    Simbench5GNetworkDescription, SimbenchLTENetworkDescription

SIMULATION_DURATION_MS = 60 * 60 * 1000  # 1 hour

market_intervals = [5 * 60 * 1000, 15 * 60 * 1000, 30 * 60 * 1000]  # 5 minutes, 10 minutes, 30 minutes
num_iterations_till_goal = [1, 5]

for max_number_of_agents_ in num_agents:
    for system_state in system_states:
        for market_interval in market_intervals:
            for data_size_generator_n, data_size_generator in data_size_generators.items():
                for optimization_complexity, reply_after_times in complexities.items():
                    simbench_codes = simbench_codes_analysis
                    for simbench_code in simbench_codes:
                        for network_description_class in network_description_classes:
                            if network_description_class == SimbenchLTENetworkDescription:
                                specifications = [SimbenchLTENetworkDescription.Specification.LTE,
                                                  SimbenchLTENetworkDescription.Specification.LTE450]
                            else:
                                specifications = [True]
                            for specification in specifications:
                                communication_network_description = network_description_class(
                                    simbench_code=simbench_code,
                                    system_state=system_state,
                                    specification=specification)
                                """
                                Centralized
                                """
                                communication_graph = (
                                    StarCommunicationGraph(agents=communication_network_description.agents,
                                                           central_agent=communication_network_description.control_center_agent,
                                                           max_number_of_agents_per_type=max_number_of_agents_))
                                communication_pattern = MarketParticipation(
                                    simulation_duration_ms=SIMULATION_DURATION_MS,
                                    communication_graph=communication_graph,
                                    data_size_generator=data_size_generator,
                                    organizational_structure=OrganizationalStructure.CENTRALIZED,
                                    market_interval_ms=market_interval,
                                    t_local_optimization=reply_after_times)
                                communication_scenario_description = (
                                    CommunicationScenarioDescription(
                                        description_text=f'market_participation_CENTRALIZED_'
                                                         f'{data_size_generator_n}_'
                                                         f'market_interval_{int(market_interval / 60000)}_min_'
                                                         f'complexity_{optimization_complexity}'
                                                         f'simbench_network_'
                                                         f'{communication_network_description.simbench_code},'
                                                         f'_{communication_network_description.technology}'
                                                         f'_system_state_{system_state.name}',
                                        communication_graph=communication_graph,
                                        communication_network_description=communication_network_description,
                                        agent_communication_pattern=communication_pattern))

                                communication_scenario_description.run_simulation()

                                """
                                Hierarchical
                                """
                                for i_till_goal in num_iterations_till_goal:
                                    for overlay_n, overlay in overlay_types(communication_network_description,
                                                                            max_number_of_agents_).items():
                                        communication_pattern = MarketParticipation(
                                            simulation_duration_ms=SIMULATION_DURATION_MS,
                                            communication_graph=overlay,
                                            data_size_generator=data_size_generator,
                                            organizational_structure=OrganizationalStructure.HIERARCHICAL,
                                            market_interval_ms=market_interval,
                                            t_local_optimization=reply_after_times,
                                            num_iterations_till_goal=i_till_goal)
                                        communication_scenario_description = (
                                            CommunicationScenarioDescription(
                                                description_text=f'market_participation_HIERARCHICAL_'
                                                                 f'{data_size_generator_n}_{overlay_n}_'
                                                                 f'market_interval_{int(market_interval / 60000)}_min_'
                                                                 f'complexity_{optimization_complexity}_'
                                                                 f'{i_till_goal}_iterations'
                                                                 f'simbench_network_'
                                                                 f'{communication_network_description.simbench_code},'
                                                                 f'_{communication_network_description.technology}'
                                                                 f'_system_state_{system_state.name}',
                                                communication_graph=overlay,
                                                communication_network_description=communication_network_description,
                                                agent_communication_pattern=communication_pattern))

                                        communication_scenario_description.run_simulation()

                                """
                                Decentralized
                                """
                                for i_till_goal in num_iterations_till_goal:
                                    for overlay_n, overlay in overlay_types(communication_network_description,
                                                                            max_number_of_agents_).items():
                                        communication_pattern = MarketParticipation(
                                            simulation_duration_ms=SIMULATION_DURATION_MS,
                                            communication_graph=overlay,
                                            data_size_generator=data_size_generator,
                                            organizational_structure=OrganizationalStructure.DECENTRALIZED,
                                            market_interval_ms=0,
                                            t_local_optimization=reply_after_times,
                                            num_iterations_till_goal=i_till_goal)
                                        communication_scenario_description = (
                                            CommunicationScenarioDescription(
                                                description_text=f'market_participation_DECENTRALIZED_'
                                                                 f'{data_size_generator_n}_{overlay_n}_'
                                                                 f'complexity_{optimization_complexity}_'
                                                                 f'{i_till_goal}_iterations'
                                                                 f'simbench_network_'
                                                                 f'{communication_network_description.simbench_code},'
                                                                 f'_{communication_network_description.technology}'
                                                                 f'_system_state_{system_state.name}',
                                                communication_graph=overlay,
                                                communication_network_description=communication_network_description,
                                                agent_communication_pattern=communication_pattern))

                                        communication_scenario_description.run_simulation()
