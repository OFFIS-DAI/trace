import random
import sys
from pathlib import Path

# Add the parent directory of "agent_communication_generation_tool" to sys.path
sys.path.append(Path(__file__).parent.parent.parent.absolute().__str__())

from network_generation.simbench_network_extractor import SystemState
from agent_communication_generation_tool.complex_use_cases.simulation_run_variables import data_size_generators, \
    complexities, overlay_types
from agent_communication_generation_tool.description_classes.simbench_codes import simbench_codes_low_voltage
from agent_communication_generation_tool.description_classes.communication_scenario_description import \
    CommunicationScenarioDescription
from agent_communication_generation_tool.description_classes.agent_communication_pattern import \
    AddNewAgent, OrganizationalStructure
from agent_communication_generation_tool.description_classes.communication_graph import StarCommunicationGraph
from agent_communication_generation_tool.description_classes.communication_network_description import \
    Simbench5GNetworkDescription, SimbenchLTENetworkDescription

SIMULATION_DURATION_MS = 30 * 1000  # 30 seconds


for system_state in [SystemState.NORMAL, SystemState.LIMITED, SystemState.FAILED]:
    for data_size_generator_n, data_size_generator in data_size_generators.items():
        for optimization_complexity, reply_after_times in complexities.items():
            simbench_codes = random.sample(simbench_codes_low_voltage, 2)
            for simbench_code in simbench_codes:
                for network_description_class in [Simbench5GNetworkDescription, SimbenchLTENetworkDescription]:
                    for specification in [SimbenchLTENetworkDescription.Specification.LTE,
                                          SimbenchLTENetworkDescription.Specification.LTE450]:
                        communication_network_description = network_description_class(simbench_code=simbench_code,
                                                                                      system_state=system_state,
                                                                                      specification=specification)

                        for overlay_n, overlay in (
                                overlay_types(communication_network_description, 1000).items()):
                            communication_pattern = AddNewAgent(simulation_duration_ms=SIMULATION_DURATION_MS,
                                                                communication_graph=overlay,
                                                                reply_after_range=reply_after_times,
                                                                data_size_generator=data_size_generator,
                                                                organizational_structure=OrganizationalStructure.DECENTRALIZED)

                            communication_scenario_description = (
                                CommunicationScenarioDescription(
                                    description_text=f'add_new_agent_DECENTRALIZED_{overlay_n}_'
                                                     f'{data_size_generator_n}_'
                                                     f'complexity_{optimization_complexity}_'
                                                     f'simbench_network_'
                                                     f'{communication_network_description.simbench_code},'
                                                     f'_{communication_network_description.technology}'
                                                     f'_system_state_{system_state.name}',
                                    communication_graph=overlay,
                                    communication_network_description=communication_network_description,
                                    agent_communication_pattern=communication_pattern))
                            communication_scenario_description.run_simulation()

                        for organizational_structure in [OrganizationalStructure.CENTRALIZED,
                                                         OrganizationalStructure.HIERARCHICAL]:
                            communication_graph = (
                                StarCommunicationGraph(agents=communication_network_description.agents,
                                                       central_agent=communication_network_description.control_center_agent,
                                                       aggregator_agent=communication_network_description.aggregator_agent))
                            communication_pattern = AddNewAgent(simulation_duration_ms=SIMULATION_DURATION_MS,
                                                                communication_graph=communication_graph,
                                                                reply_after_range=reply_after_times,
                                                                data_size_generator=data_size_generator,
                                                                organizational_structure=organizational_structure)

                            communication_scenario_description = (
                                CommunicationScenarioDescription(
                                    description_text=f'add_new_agent_{organizational_structure.name}_'
                                                     f'{data_size_generator_n}_'
                                                     f'complexity_{optimization_complexity}_'
                                                     f'simbench_network_'
                                                     f'{communication_network_description.simbench_code},'
                                                     f'_{communication_network_description.technology}',
                                    communication_graph=communication_graph,
                                    communication_network_description=communication_network_description,
                                    agent_communication_pattern=communication_pattern))

                            communication_scenario_description.run_simulation()
