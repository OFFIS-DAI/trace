import random
import sys
from pathlib import Path

# Add the parent directory of "agent_communication_generation_tool" to sys.path
sys.path.append(Path(__file__).parent.parent.parent.absolute().__str__())

from agent_communication_generation_tool.util import send_mail_notification
from agent_communication_generation_tool.simulation_run_variables import num_agents, \
    network_description_classes
from agent_communication_generation_tool.simulation_run_variables import \
    complexities, overlay_types, data_size_generators_increasing
from agent_communication_generation_tool.description_classes.simbench_codes import codes_nan_filtered
from agent_communication_generation_tool.description_classes.communication_scenario_description import \
    CommunicationScenarioDescription
from agent_communication_generation_tool.description_classes.agent_communication_pattern import \
    DemandSupplyBalancing, OrganizationalStructure
from agent_communication_generation_tool.description_classes.communication_graph import StarCommunicationGraph
from agent_communication_generation_tool.description_classes.communication_network_description import \
    SimbenchLTENetworkDescription

SIMULATION_DURATION_MS = 30 * 1000  # 30 seconds

probabilities_agree_to_supply = [random.random()]
negotiation_times = [random.randint(100, 500)]

try:
    for max_number_of_agents_ in num_agents:
        for data_size_generator_n, data_size_generator in data_size_generators_increasing.items():
            for optimization_complexity, reply_after_times in complexities.items():
                for p_agree_to_power_supply in probabilities_agree_to_supply:
                    simbench_codes = codes_nan_filtered
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
                                communication_pattern = DemandSupplyBalancing(
                                    simulation_duration_ms=SIMULATION_DURATION_MS,
                                    communication_graph=communication_graph,
                                    data_size_generator=data_size_generator,
                                    organizational_structure=OrganizationalStructure.CENTRALIZED,
                                    p_agree_to_power_supply=p_agree_to_power_supply,
                                    t_central_optimization_range=reply_after_times)
                                communication_scenario_description = (
                                    CommunicationScenarioDescription(
                                        description_text=f'demand_supply_balancing_CENTRALIZED_'
                                                         f'{data_size_generator_n}_'
                                                         f'p_agree_{int(p_agree_to_power_supply * 100)}_'
                                                         f'complexity_{optimization_complexity}'
                                                         f'simbench_network_'
                                                         f'{communication_network_description.simbench_code},'
                                                         f'_{communication_network_description.technology}',
                                        communication_graph=communication_graph,
                                        communication_network_description=communication_network_description,
                                        agent_communication_pattern=communication_pattern))

                                communication_scenario_description.run_simulation()

                                for neg_time in negotiation_times:
                                    for overlay_n, overlay \
                                            in overlay_types(communication_network_description,
                                                             max_number_of_agents_).items():
                                        """
                                        Hierarchical
                                        """
                                        communication_pattern = (
                                            DemandSupplyBalancing(simulation_duration_ms=SIMULATION_DURATION_MS,
                                                                  communication_graph=overlay,
                                                                  data_size_generator=data_size_generator,
                                                                  organizational_structure=OrganizationalStructure.HIERARCHICAL,
                                                                  t_central_optimization_range=reply_after_times,
                                                                  negotiation_duration_ms=neg_time))

                                        communication_scenario_description = (
                                            CommunicationScenarioDescription(
                                                description_text=f'demand_supply_balancing_HIERARCHICAL_'
                                                                 f'{data_size_generator_n}_'
                                                                 f'{overlay_n}_neg_time_{neg_time}_'
                                                                 f'complexity_{optimization_complexity}'
                                                                 f'simbench_network_'
                                                                 f'{communication_network_description.simbench_code},'
                                                                 f'_{communication_network_description.technology}',
                                                communication_graph=overlay,
                                                communication_network_description=communication_network_description,
                                                agent_communication_pattern=communication_pattern))

                                        communication_scenario_description.run_simulation()
                                    for overlay_n, overlay in overlay_types(communication_network_description,
                                                                            max_number_of_agents_).items():
                                        """
                                        Decentralized
                                        """
                                        communication_pattern = (
                                            DemandSupplyBalancing(simulation_duration_ms=SIMULATION_DURATION_MS,
                                                                  communication_graph=overlay,
                                                                  data_size_generator=data_size_generator,
                                                                  organizational_structure=OrganizationalStructure.DECENTRALIZED,
                                                                  t_central_optimization_range=reply_after_times,
                                                                  negotiation_duration_ms=neg_time))

                                        communication_scenario_description = (
                                            CommunicationScenarioDescription(
                                                description_text=f'demand_supply_balancing_DECENTRALIZED_'
                                                                 f'{data_size_generator_n}_'
                                                                 f'{overlay_n}_neg_time_{neg_time}_'
                                                                 f'complexity_{optimization_complexity}'
                                                                 f'simbench_network_'
                                                                 f'{communication_network_description.simbench_code},'
                                                                 f'_{communication_network_description.technology}',
                                                communication_graph=overlay,
                                                communication_network_description=communication_network_description,
                                                agent_communication_pattern=communication_pattern))

                                        communication_scenario_description.run_simulation()
    send_mail_notification(scenario_description='complex demand supply balancing')
except Exception as e :
    send_mail_notification(scenario_description=f'complex demand supply balancing, error: {e}', failed=True)
