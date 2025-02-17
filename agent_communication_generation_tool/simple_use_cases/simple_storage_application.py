import random
import sys
from pathlib import Path

from agent_communication_generation_tool.util import send_mail_notification

# Add the parent directory of "agent_communication_generation_tool" to sys.path
sys.path.append(Path(__file__).parent.parent.parent.absolute().__str__())

from agent_communication_generation_tool.simulation_run_variables import num_agents, system_states, \
    network_description_classes
from agent_communication_generation_tool.description_classes.simbench_codes import codes_nan_filtered
from agent_communication_generation_tool.description_classes.communication_scenario_description import \
    CommunicationScenarioDescription
from agent_communication_generation_tool.description_classes.agent_communication_pattern import \
    StorageApplication
from agent_communication_generation_tool.description_classes.communication_graph import StarCommunicationGraph
from agent_communication_generation_tool.description_classes.communication_network_description import \
    SimbenchLTENetworkDescription, Simbench5GNetworkDescription

SIMULATION_DURATION_MS = 5 * 60 * 1000  # 5 minutes

try:
    for optimization_complexity, reply_after_times in {'low': (0, 1000), 'medium': (1000, 30000),
                                                       'high': (30000, 5 * 60 * 1000)}.items():
        for max_number_of_agents_ in num_agents:
            for system_state in system_states:
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
                            communication_graph = (
                                StarCommunicationGraph(agents=communication_network_description.agents,
                                                       central_agent=communication_network_description.get_central_agent(),
                                                       max_number_of_agents_per_type=max_number_of_agents_))
                            amr_communication_pattern = StorageApplication(simulation_duration_ms=SIMULATION_DURATION_MS,
                                                                           communication_graph=communication_graph,
                                                                           reply_after_range=reply_after_times)

                            communication_scenario_description = (
                                CommunicationScenarioDescription(
                                    description_text=f'storage_application_complexity_{optimization_complexity}'
                                                     f'_num_agents_{max_number_of_agents_}_'
                                                     f'simbench_network_'
                                                     f'{communication_network_description.simbench_code},'
                                                     f'system_state_{system_state.name}',
                                    communication_graph=communication_graph,
                                    communication_network_description=communication_network_description,
                                    agent_communication_pattern=amr_communication_pattern))

                            communication_scenario_description.run_simulation()
    send_mail_notification(scenario_description='simple storage application')
except Exception as e:
    send_mail_notification(scenario_description=f'simple storage application, error: {e}', failed=True)

