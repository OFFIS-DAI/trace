import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import glob
from functools import reduce

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
        df['Network'] = network
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
corr_dfs = []

for network_tech, dataframes_tech in dataframes.items():
    print(f'Network and technology: {network_tech}, number of dataframes: {len(dataframes_tech)}')
    total_dataframe = pd.concat(dataframes_tech)

    # Set seaborn style
    sns.set(style="whitegrid")

    # Calculate mean delay_ms for each system state
    mean_delay_by_state = total_dataframe.copy().groupby('system_state')['delay_ms'].mean().reset_index()

    # Plot the summarized data
    sns.barplot(data=mean_delay_by_state, x='system_state', y='delay_ms')
    plt.title('Mean Delay (ms) vs System State')
    plt.xlabel('System State')
    plt.ylabel('Mean Delay (ms)')
    plt.savefig(f'{WRITE_PLOTS_DIR_NAME}/system_states_' + network_tech + '.pdf',
                format="pdf", bbox_inches="tight")
    plt.clf()

    # Calculate the maximum delay_ms for each msgId group
    max_delay_df = total_dataframe.groupby('msgId').agg({
        'delay_ms': 'max',
        'timeSend_ms': 'first',  # Assuming timeSend_ms does not vary within a msgId group
        'packetSize_B_x': 'first',  # Assuming packetSize_B_x does not vary within a msgId group
        'number_of_agents': 'first',  # Assuming number_of_agents does not vary within a msgId group
        'Technology': 'first',  # Assuming Technology does not vary within a msgId group
        'packets_in_network': 'first',
        'packets_on_link': 'first',
        'time_diff_ms': 'first',
        'packets_sent_at_same_time': 'first',
        'system_state': 'first',
        'Network': 'first',
        'sender': 'first',
        'receiver': 'first'
    })

    # Plotting
    for parameter in ['timeSend_ms', 'packetSize_B_x', 'number_of_agents', 'packets_in_network', 'time_diff_ms',
                      'packets_sent_at_same_time']:
        sns.scatterplot(data=max_delay_df, x=parameter, y='delay_ms', hue='Technology')
        plt.title(f'Max Delay (ms) vs {parameter}')
        plt.xlabel(f'{parameter}')
        plt.ylabel('Max Delay (ms)')
        plt.legend(title='Technology')
        plt.tight_layout()
        plt.savefig(f'{WRITE_PLOTS_DIR_NAME}/' + parameter + '_' + network_tech + '.pdf',
                    format="pdf", bbox_inches="tight")
        plt.clf()

    # correlation analysis
    for attr in ['receiver', 'sender', 'Network', 'system_state', 'Technology']:
        max_delay_df[attr] = max_delay_df[attr].astype('category').cat.codes
    f, ax = plt.subplots(figsize=(10, 8))
    corr = max_delay_df.corr()

    plt.title(f'Correlation analysis for {network_tech}')
    sns.heatmap(corr, vmin=-1, vmax=1, annot=True)

    plt.savefig(f'{WRITE_PLOTS_DIR_NAME}/correlation_' + network_tech + '.pdf',
                format="pdf", bbox_inches="tight")
    plt.clf()
    corr_dfs.append(corr.fillna(0))

d = reduce(lambda x, y: x.add(y, fill_value=0), corr_dfs) / len(corr_dfs)
print(d)
sns.heatmap(d, vmin=-1, vmax=1, annot=True)
plt.savefig(f'{WRITE_PLOTS_DIR_NAME}/correlation_total.pdf',
            format="pdf", bbox_inches="tight")
plt.clf()
