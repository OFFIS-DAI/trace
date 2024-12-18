import random
import sys
from pathlib import Path

# Add the parent directory of "agent_communication_generation_tool" to sys.path
sys.path.append(Path(__file__).parent.parent.parent.absolute().__str__())

from agent_communication_generation_tool.simulation_run_variables import num_agents, system_states, \
    network_description_classes
from agent_communication_generation_tool.simulation_run_variables import \
    complexities, overlay_types, data_size_generators
from agent_communication_generation_tool.description_classes.simbench_codes import codes_nan_filtered
from agent_communication_generation_tool.description_classes.communication_scenario_description import \
    CommunicationScenarioDescription
from agent_communication_generation_tool.description_classes.agent_communication_pattern import \
    VoltageRegulation, OrganizationalStructure
from agent_communication_generation_tool.description_classes.communication_graph import StarCommunicationGraph
from agent_communication_generation_tool.description_classes.communication_network_description import \
    SimbenchLTENetworkDescription

SIMULATION_DURATION_MS = 30 * 1000  # 30 seconds

probabilities_agree_to_supply = [random.random()]
negotiation_times = [random.randint(100,500)]

for max_number_of_agents_ in num_agents:
    for system_state in system_states:
        for data_size_generator_n, data_size_generator in data_size_generators.items():
            for optimization_complexity, reply_after_times in complexities.items():
                simbench_codes = codes_nan_filtered
                for simbench_code in simbench_codes:
                    for network_description_class in network_description_classes:
                        if network_description_class == SimbenchLTENetworkDescription:
                            specifications = [SimbenchLTENetworkDescription.Specification.LTE,
                                              SimbenchLTENetworkDescription.Specification.LTE450]
                        else:
                            specifications = [True]
                        for specification in specifications:
                            communication_network_description = network_description_class(simbench_code=simbench_code,
                                                                                          system_state=system_state,
                                                                                          specification=specification,
                                                                                          max_number_of_agents_per_type=max_number_of_agents_)
                            """
                            Centralized
                            """
                            communication_graph = (
                                StarCommunicationGraph(agents=communication_network_description.agents,
                                                       central_agent=communication_network_description.control_center_agent,
                                                       aggregator_agent=communication_network_description.aggregator_agent,
                                                       max_number_of_agents_per_type=max_number_of_agents_))
                            communication_pattern = VoltageRegulation(simulation_duration_ms=SIMULATION_DURATION_MS,
                                                                      communication_graph=communication_graph,
                                                                      data_size_generator=data_size_generator,
                                                                      organizational_structure=OrganizationalStructure.CENTRALIZED,
                                                                      t_local_optimization_ms_range=reply_after_times)
                            communication_scenario_description = (
                                CommunicationScenarioDescription(description_text=f'voltage_regulation_CENTRALIZED_'
                                                                                  f'{data_size_generator_n}_'
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
                            communication_graph = (
                                StarCommunicationGraph(agents=communication_network_description.agents,
                                                       central_agent=random.choice(communication_network_description.substation_agents),
                                                       aggregator_agent=communication_network_description.pdc_agent,
                                                       max_number_of_agents_per_type=max_number_of_agents_))
                            communication_pattern = VoltageRegulation(simulation_duration_ms=SIMULATION_DURATION_MS,
                                                                      communication_graph=communication_graph,
                                                                      data_size_generator=data_size_generator,
                                                                      organizational_structure=OrganizationalStructure.HIERARCHICAL,
                                                                      t_local_optimization_ms_range=reply_after_times)
                            communication_scenario_description = (
                                CommunicationScenarioDescription(description_text=f'voltage_regulation_HIERARCHICAL_'
                                                                                  f'{data_size_generator_n}_'
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
                            Decentralized
                            """
                            for overlay_n, overlay in overlay_types(communication_network_description,
                                                                    max_number_of_agents_).items():
                                communication_pattern = VoltageRegulation(simulation_duration_ms=SIMULATION_DURATION_MS,
                                                                          communication_graph=overlay,
                                                                          data_size_generator=data_size_generator,
                                                                          organizational_structure=OrganizationalStructure.DECENTRALIZED,
                                                                          t_local_optimization_ms_range=reply_after_times)
                                communication_scenario_description = (
                                    CommunicationScenarioDescription(
                                        description_text=f'voltage_regulation_DECENTRALIZED_'
                                                         f'{data_size_generator_n}_{overlay_n}_'
                                                         f'complexity_{optimization_complexity}_'
                                                         f'simbench_network_'
                                                         f'{communication_network_description.simbench_code},'
                                                         f'_{communication_network_description.technology}'
                                                         f'_system_state_{system_state.name}',
                                        communication_graph=overlay,
                                        communication_network_description=communication_network_description,
                                        agent_communication_pattern=communication_pattern))

                                communication_scenario_description.run_simulation()
