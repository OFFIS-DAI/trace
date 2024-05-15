"""
Implementation of the communication scenario to generate agent communication pattern data.
"""
import json
import os
import shutil
import subprocess
import time
import uuid
from datetime import datetime
from os.path import abspath
from pathlib import Path
import pandas as pd

from agent_communication_generation_tool.description_classes.communication_network_description import \
    CommunicationNetworkDescription, SimbenchNetworkDescription
from agent_communication_generation_tool.description_classes.agent_communication_pattern import \
    AgentCommunicationPattern, ComplexAgentCommunicationPattern
from agent_communication_generation_tool.description_classes.communication_graph import CommunicationGraph
from agent_communication_generation_tool.util import merge_input_and_output_df, plot_traffic_pattern

# set inet installation path
INET_PATH = '/home/malin/PycharmProjects/trace/inet4.5/src'
# get root directory and change current path
ROOT = str(Path(abspath(__file__)).parent.parent.parent)


class CommunicationScenarioDescription:
    """
    Description class of a scenario.
    """

    def __init__(self,
                 description_text,
                 communication_network_description: CommunicationNetworkDescription,
                 agent_communication_pattern: AgentCommunicationPattern,
                 communication_graph: CommunicationGraph):
        self.id = uuid.uuid4()
        self.description_text = description_text
        self.communication_network_description = communication_network_description
        self.agent_communication_pattern = agent_communication_pattern
        self.communication_graph = communication_graph

        self.results = dict()

        os.chdir(ROOT)

    def run_simulation(self):
        """
        Generates traffic configuration files and runs OMNeT++ simulation according to definition.
        """
        self.agent_communication_pattern.generate_traffic_configuration_files()
        import pandas as pd
        from datetime import datetime

        # Assuming all the necessary information is available in your current context
        data = [
            {'Parameter': 'Start simulation', 'Value': datetime.now()},
            {'Parameter': 'Simulation configuration ID', 'Value': self.id},
            {'Parameter': 'Network', 'Value': self.communication_network_description.id},
            {'Parameter': 'Communication graph', 'Value': self.communication_graph.get_description()},
            {'Parameter': 'Agent communication pattern', 'Value': self.agent_communication_pattern.__class__.__name__},
            {'Parameter': 'Trigger Type', 'Value': self.agent_communication_pattern.trigger.name},
            {'Parameter': 'Data size generator', 'Value': self.agent_communication_pattern.data_size_generator.get_description()},
            {'Parameter': 'Frequency', 'Value': self.agent_communication_pattern.frequency_ms},
            {'Parameter': 'Simulation duration', 'Value': self.agent_communication_pattern.simulation_duration_ms},
            {'Parameter': 'Communication mode', 'Value': self.agent_communication_pattern.communication_mode.name}
        ]

        # Adding optional fields based on subclass checks
        if issubclass(self.communication_network_description.__class__, SimbenchNetworkDescription):
            data.append({'Parameter': 'System State', 'Value': self.communication_network_description.system_state})

        if issubclass(self.agent_communication_pattern.__class__, ComplexAgentCommunicationPattern):
            data.append({'Parameter': 'Organizational structure', 'Value': self.agent_communication_pattern.organizational_structure.name})

        # Creating the DataFrame
        description_df = pd.DataFrame(data)

        print(f'Run simulation {self.description_text} '
              f'with network {self.communication_network_description.id}.')
        os.system('killall -9 omnet_project_files')
        time.sleep(3)
        os.chdir(ROOT + '/omnet_project_files')
        try:
            # delete results folder with outdated files
            shutil.rmtree('results')
        except FileNotFoundError:
            print('No results folder to delete.')
        # build project
        os.system("make")

        # run simulation
        command = (f"./omnet_project_files -f omnetpp.ini -c {self.communication_network_description.config_name} "
                   f"-n {INET_PATH} -u Cmdenv "
                   f"--sim-time-limit={self.agent_communication_pattern.simulation_duration_ms}ms")
        subprocess.run(command, shell=True)

        time.sleep(5)

        input_df = self.agent_communication_pattern.get_inputs()
        output_df, reply_df = self.get_outputs()
        if isinstance(output_df, pd.DataFrame):

            reply_df.rename({'sendingTime_ms': 'timeSend_ms'}, axis='columns', inplace=True)

            input_df = pd.concat([input_df, reply_df])

            if 'calculationStart_ms' in input_df.columns:
                input_df['calculationStart_ms'] = input_df['calculationStart_ms'].fillna(0)

            input_df.dropna(axis='columns', inplace=True)
            output_df.dropna(axis='columns', inplace=True)

            self.results = merge_input_and_output_df(input_df, output_df)
            self.results = pd.concat([description_df, self.results])

            self.results.to_csv(f'{ROOT}/agent_communication_generation_tool/results/data/{self.id}.csv')
            plot_traffic_pattern(self,
                                 self.results, f'{self.description_text}')
        time.sleep(5)

    def get_outputs(self):
        """
        Get simulation results from OMNeT++ as pandas DataFrame.
        :return: Dataframe.
        """
        dfs = []
        reply_dfs = []
        # change to results folder
        folder_path = "results"
        os.chdir(folder_path)
        for agent in self.communication_graph.agents:
            json_file_path = f'simulation_results_{agent.omnet_name}.json'
            # Read the JSON file
            try:
                with open(json_file_path, 'r') as file:
                    data = json.load(file)

                # Create a DataFrame from the JSON data
                df = pd.DataFrame(data)
                if 'type' in df.columns:
                    reply_dfs.append(df[df['type'] == 'reply'])
                    dfs.append(df[df['type'] != 'reply'])
                else:
                    dfs.append(df)
            except Exception as e:
                print('No such result file for ', agent.omnet_name)
        reply_df = pd.DataFrame() if len(reply_dfs) == 0 else pd.concat(reply_dfs)
        try:
            concated_df = pd.concat(dfs)
        except ValueError:
            concated_df = None
        return concated_df, reply_df
