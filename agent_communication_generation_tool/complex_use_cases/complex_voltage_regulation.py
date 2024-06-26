import random
import sys
from pathlib import Path

# Add the parent directory of "agent_communication_generation_tool" to sys.path
sys.path.append(Path(__file__).parent.parent.parent.absolute().__str__())

from network_generation.simbench_network_extractor import SystemState
from agent_communication_generation_tool.complex_use_cases.simulation_run_variables import \
    complexities, overlay_types, data_size_generators
from agent_communication_generation_tool.description_classes.simbench_codes import simbench_codes_low_voltage
from agent_communication_generation_tool.description_classes.communication_scenario_description import \
    CommunicationScenarioDescription
from agent_communication_generation_tool.description_classes.agent_communication_pattern import \
    VoltageRegulation, OrganizationalStructure
from agent_communication_generation_tool.description_classes.communication_graph import StarCommunicationGraph
from agent_communication_generation_tool.description_classes.communication_network_description import \
    Simbench5GNetworkDescription, SimbenchLTENetworkDescription

SIMULATION_DURATION_MS = 30 * 1000  # 30 seconds

probabilities_agree_to_supply = [0, 0.5, 1]
negotiation_times = [100, 1000, 5000]

for max_number_of_agents_ in [random.randint(2, 100) for _ in range(5)]:
    for system_state in [SystemState.NORMAL, SystemState.LIMITED, SystemState.FAILED]:
        for data_size_generator_n, data_size_generator in data_size_generators.items():
            for optimization_complexity, reply_after_times in complexities.items():
                simbench_codes = random.sample(simbench_codes_low_voltage, 2)
                for simbench_code in simbench_codes:
                    for network_description_class in [Simbench5GNetworkDescription, SimbenchLTENetworkDescription]:
                        if network_description_class == SimbenchLTENetworkDescription:
                            specifications = [SimbenchLTENetworkDescription.Specification.LTE,
                                              SimbenchLTENetworkDescription.Specification.LTE450]
                        else:
                            specifications = [None]
                        for specification in specifications:
                            communication_network_description = network_description_class(simbench_code=simbench_code,
                                                                                          system_state=system_state,
                                                                                          specification=specification)
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
                                                       central_agent=communication_network_description.substation_agent,
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
