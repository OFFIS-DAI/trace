import random
import sys
from pathlib import Path

# Add the parent directory of "agent_communication_generation_tool" to sys.path
sys.path.append(Path(__file__).parent.parent.parent.absolute().__str__())

from network_generation.simbench_network_extractor import SystemState
from agent_communication_generation_tool.description_classes.simbench_codes import simbench_codes_low_voltage
from agent_communication_generation_tool.description_classes.communication_scenario_description import \
    CommunicationScenarioDescription
from agent_communication_generation_tool.description_classes.agent_communication_pattern import (
    WACsVoltageStabilityControl)
from agent_communication_generation_tool.description_classes.communication_graph import StarCommunicationGraph
from agent_communication_generation_tool.description_classes.communication_network_description import \
    SimbenchLTENetworkDescription, Simbench5GNetworkDescription

SIMULATION_DURATION_MS = 5 * 60 * 1000  # 5 minutes

for max_number_of_agents_ in [random.randint(2, 100) for _ in range(5)]:
    for system_state in [SystemState.NORMAL, SystemState.LIMITED, SystemState.FAILED]:
        simbench_codes = random.sample(simbench_codes_low_voltage, 2)
        for simbench_code in simbench_codes:
            for specification in [SimbenchLTENetworkDescription.Specification.LTE,
                                  SimbenchLTENetworkDescription.Specification.LTE450]:
                communication_network_description = SimbenchLTENetworkDescription(simbench_code=simbench_code,
                                                                                  system_state=system_state,
                                                                                  specification=specification)
                communication_graph = (
                    StarCommunicationGraph(agents=communication_network_description.agents,
                                           central_agent=communication_network_description.get_central_agent(),
                                           max_number_of_agents_per_type=max_number_of_agents_))
                wap_communication_pattern = WACsVoltageStabilityControl(simulation_duration_ms=SIMULATION_DURATION_MS,
                                                                        communication_graph=communication_graph)

                communication_scenario_description = (
                    CommunicationScenarioDescription(description_text='wac_voltage_stability'
                                                                      f'_num_agents_{max_number_of_agents_}_'
                                                                      f'simbench_network_'
                                                                      f'{communication_network_description.simbench_code}'
                                                                      f'_{specification.name}_'
                                                                      f'system_state_{system_state.name}',
                                                     communication_graph=communication_graph,
                                                     communication_network_description=communication_network_description,
                                                     agent_communication_pattern=wap_communication_pattern))

                communication_scenario_description.run_simulation()

            communication_network_description = Simbench5GNetworkDescription(simbench_code=simbench_code,
                                                                             system_state=system_state)
            communication_graph = (
                StarCommunicationGraph(agents=communication_network_description.agents,
                                       central_agent=communication_network_description.get_central_agent(),
                                       max_number_of_agents_per_type=max_number_of_agents_))
            wap_communication_pattern = WACsVoltageStabilityControl(simulation_duration_ms=SIMULATION_DURATION_MS,
                                                                    communication_graph=communication_graph)

            communication_scenario_description = (
                CommunicationScenarioDescription(description_text='wac_voltage_stability'
                                                                  f'_num_agents_{max_number_of_agents_}_'
                                                                  f'simbench_network_'
                                                                  f'{communication_network_description.simbench_code}'
                                                                  f'_{communication_network_description.technology}'
                                                                  f'_system_state_{system_state.name}',
                                                 communication_graph=communication_graph,
                                                 communication_network_description=communication_network_description,
                                                 agent_communication_pattern=wap_communication_pattern))

            communication_scenario_description.run_simulation()
