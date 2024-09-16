import sys
from pathlib import Path

from agent_communication_generation_tool.description_classes.communication_network_description import \
    Simbench5GNetworkDescription, SimbenchLTENetworkDescription, SimbenchEthernetNetworkDescription
from network_generation.simbench_network_extractor import SystemState

# Add the parent directory of "agent_communication_generation_tool" to sys.path
sys.path.append(Path(__file__).parent.parent.parent.absolute().__str__())

from agent_communication_generation_tool.description_classes.communication_graph import RingOverlayGraph, \
    SmallWorldOverlayGraph, CompleteOverlayGraph
from agent_communication_generation_tool.description_classes.data_size_generator import InIntervalDataSizeGenerator, \
    IncreasingInIntervalDataSizeGenerator

network_description_classes = [#Simbench5GNetworkDescription, SimbenchLTENetworkDescription,
                               SimbenchEthernetNetworkDescription]

data_size_generators = {
    '8-50B': InIntervalDataSizeGenerator(8, 50),
    '50-200B': InIntervalDataSizeGenerator(50, 200),
    '200-1000B': InIntervalDataSizeGenerator(200, 1000)
}

data_size_generators_increasing = {
    '8-50B': IncreasingInIntervalDataSizeGenerator(8, 50),
    '50-200B': IncreasingInIntervalDataSizeGenerator(50, 200),
    '200-1000B': IncreasingInIntervalDataSizeGenerator(200, 1000)
}

system_states = [SystemState.NORMAL]

num_agents = [5, 10, 15, 20, 25, 30, 50, 100]

complexities = {'immediate': (0, 100), 'low': (100, 1000),
                'medium': (1000, 30000), 'high': (30000, 5 * 60 * 1000)}


def overlay_types(communication_network_description, max_number_of_agents):
    return {'ring': RingOverlayGraph(agents=communication_network_description.agents,
                                     central_agent=communication_network_description.control_center_agent,
                                     max_number_of_agents_per_type=max_number_of_agents),
            'small world': SmallWorldOverlayGraph(
                agents=communication_network_description.agents,
                central_agent=communication_network_description.control_center_agent,
                p=0.5,
                max_number_of_agents_per_type=max_number_of_agents),
            'complete': CompleteOverlayGraph(agents=communication_network_description.agents,
                                             central_agent=communication_network_description.control_center_agent,
                                             max_number_of_agents_per_type=max_number_of_agents)}
