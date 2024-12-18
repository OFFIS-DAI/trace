import os
import pandas as pd
import glob

RESULT_DIR_NAME = '../agent_communication_generation_tool/results/data'
WRITE_PLOTS_DIR_NAME = 'results'

dataframes = {}

i = 0
files = glob.glob(f'{WRITE_PLOTS_DIR_NAME}/*')
for f in files:
    os.remove(f)


def add_scenario(x):
    return str(i) + '_' + str(int(x))


for filename in os.listdir(RESULT_DIR_NAME):
    if filename.endswith(".csv"):
        df = pd.read_csv(RESULT_DIR_NAME + '/' + filename, index_col=0)
        network = df[df['Parameter'] == 'Network']['Value'].values[0]
        if 'LTE450' in network:
            df['Technology'] = 'LTE450'
        elif 'LTE' in network:
            df['Technology'] = 'LTE'
        elif '5G' in network:
            df['Technology'] = '5G'
        elif 'Ethernet' in network:
            df['Technology'] = 'Ethernet'
        df['Network'] = network
        df['Application'] = df[df['Parameter'] == 'Agent communication pattern']['Value'].values[0]
        agents = df['sender'].dropna().to_list()
        agents.extend(df['receiver'].dropna().to_list())
        agents = list(dict.fromkeys(agents))
        num_agents = len(agents)
        df['number_of_agents'] = num_agents
        if len(df[df['Parameter'] == 'System State']['Value'].values) > 0:
            df['system_state'] = df[df['Parameter'] == 'System State']['Value'].values[0]

        df.dropna(subset=['msgId'], inplace=True)
        df.drop(columns=['Parameter', 'Value'], inplace=True)
        # Counting the number of entries with the same msgId
        df['packet_count'] = df.groupby('msgId')['msgId'].transform('count')
        df['msgId'] = df['msgId'].apply(add_scenario)

        # Sort by timeSend_ms and calculate the time difference between consecutive messages
        df.sort_values(by='timeSend_ms', inplace=True)  # Sort data by timeSend_ms

        df['time_diff_ms'] = df['timeSend_ms'] - df['timeSend_ms'].copy().shift()
        # Calculate packets still in the network
        packets_in_network = []
        packets_on_link = []
        for index, row in df.iterrows():
            # Count packets that were sent before and are still not received when the current packet is sent
            mask = (df['timeSend_ms'] < row['timeSend_ms']) & (df['receivingTime_ms'] > row['timeSend_ms'])
            packets_in_network.append(mask.sum())
            mask_1 = ((df['timeSend_ms'] < row['timeSend_ms']) & (df['receivingTime_ms'] > row['timeSend_ms'])
                      & (df['sender'] == row['sender']) & (df['receiver'] == row['receiver']))
            packets_on_link.append(mask_1.sum())

        df['packets_in_network'] = packets_in_network
        df['packets_on_link'] = packets_on_link
        df['packets_sent_at_same_time'] = df.groupby('timeSend_ms')['timeSend_ms'].transform('count')

        if network not in dataframes.keys():
            dataframes[network] = list()
        dataframes[network].append(df)
        i += 1

print('Number of networks: ', len(dataframes.keys()))
