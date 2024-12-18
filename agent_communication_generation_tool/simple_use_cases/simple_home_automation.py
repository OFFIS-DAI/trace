import sys
from pathlib import Path

from agent_communication_generation_tool.util import send_mail_notification

# Add the parent directory of "agent_communication_generation_tool" to sys.path
sys.path.append(Path(__file__).parent.parent.parent.absolute().__str__())

from agent_communication_generation_tool.description_classes.communication_scenario_description import \
    CommunicationScenarioDescription
from agent_communication_generation_tool.description_classes.agent_communication_pattern import CustomerAutomation
from agent_communication_generation_tool.description_classes.communication_graph import StarCommunicationGraph
from agent_communication_generation_tool.description_classes.communication_network_description import \
    EthernetDescription, WifiDescription

SIMULATION_DURATION_MS = 300000  # 5 min

speed_mbps = [10, 100, 1000, 10000]
num_devices = [1, 5, 10]

han_networks = ([WifiDescription(WifiDescription.Specification.Wifi_802_11),
                 WifiDescription(WifiDescription.Specification.Wifi_802_11_ac)] +
                [EthernetDescription(speed_mbps=speed_mbps_) for speed_mbps_ in speed_mbps])

for han in han_networks:
    for num_devices_ in num_devices:
        communication_graph = StarCommunicationGraph(agents=han.agents,
                                                     central_agent=han.get_central_agent())
        customer_automation_comm_pattern = CustomerAutomation(simulation_duration_ms=SIMULATION_DURATION_MS,
                                                              communication_graph=communication_graph,
                                                              trigger_interval_ms=60000,
                                                              num_devices=num_devices_)
        communication_scenario_description = (
            CommunicationScenarioDescription(description_text=f'home_automation_{han.config_name}_'
                                                            f'{num_devices_}_devices',
                                             communication_graph=communication_graph,
                                             communication_network_description=han,
                                             agent_communication_pattern=customer_automation_comm_pattern))

        communication_scenario_description.run_simulation()
send_mail_notification(scenario_description='simple home automation')
