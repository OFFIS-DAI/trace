import os
import pandas as pd
import glob
import plotly.graph_objects as go
import plotly.colors
from plotly.subplots import make_subplots

RESULT_DIR_NAME = '../agent_communication_generation_tool/results/sim_data'

dataframes = {}

# Define a function to classify agents by type
def classify_agent(agent_name):
    if 'control_center' in agent_name:
        return 'Control Center Agent'
    elif 'household' in agent_name:
        return 'Household Agent'
    elif 'market' in agent_name:
        return 'Market Agent'
    elif 'pdc' in agent_name:
        return 'PDC Agent'
    elif 'generation' in agent_name:
        return 'Generation Agent'
    elif 'infrastructure' in agent_name:
        return 'Grid Infrastructure Agent'
    elif 'storage' in agent_name:
        return 'Storage Agent'
    else:
        print(agent_name)
        return 'Unknown'

# Add scenario ID to message IDs
def add_scenario(x):
    return str(i) + '_' + str(int(x))

# Process all CSV files
i = 0
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
        elif 'Wifi' in network:
            df['Technology'] = 'Wifi'
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
        df['packet_count'] = df.groupby('msgId')['msgId'].transform('count')
        df['msgId'] = df['msgId'].apply(add_scenario)

        # Sort by timeSend_ms
        df.sort_values(by='timeSend_ms', inplace=True)
        df['time_diff_ms'] = df['timeSend_ms'] - df['timeSend_ms'].copy().shift()

        # Packets still in the network
        packets_in_network = []
        packets_on_link = []
        for index, row in df.iterrows():
            mask = (df['timeSend_ms'] < row['timeSend_ms']) & (df['receivingTime_ms'] > row['timeSend_ms'])
            packets_in_network.append(mask.sum())
            mask_1 = ((df['timeSend_ms'] < row['timeSend_ms']) & (df['receivingTime_ms'] > row['timeSend_ms'])
                      & (df['sender'] == row['sender']) & (df['receiver'] == row['receiver']))
            packets_on_link.append(mask_1.sum())

        df['packets_in_network'] = packets_in_network
        df['packets_on_link'] = packets_on_link
        df['packets_sent_at_same_time'] = df.groupby('timeSend_ms')['timeSend_ms'].transform('count')

        # Apply classification to sender and receiver columns
        df['sender_type'] = df['sender'].apply(classify_agent)
        df['receiver_type'] = df['receiver'].apply(classify_agent)

        if network not in dataframes.keys():
            dataframes[network] = list()
        dataframes[network].append(df)
        i += 1

# Combine all DataFrames into one for analysis
df = pd.concat([pd.concat(dfs) for dfs in dataframes.values()])

# Generate a color palette for the applications
applications = df['Application'].unique()
color_palette = plotly.colors.qualitative.Set2[:len(applications)]  # Use Set2 color palette
app_color_mapping = {app: color_palette[i] for i, app in enumerate(applications)}  # Map each app to a color

#######################################################
# Sender/Receiver Distributions
#######################################################

# Aggregate data for sender and receiver distributions
sender_counts = df.groupby(['Application', 'sender_type']).size().reset_index(name='sender_count')
receiver_counts = df.groupby(['Application', 'receiver_type']).size().reset_index(name='receiver_count')

# Create subplots
fig = make_subplots(
    rows=1, cols=2,
    subplot_titles=(
        "Receiver Distribution",
        "Sender Distribution"
    )
)

# Add sender and receiver distributions with consistent colors
for app in applications:
    sender_data = sender_counts[sender_counts['Application'] == app]
    receiver_data = receiver_counts[receiver_counts['Application'] == app]

    # Add sender data
    fig.add_trace(
        go.Bar(
            x=sender_data['sender_type'],
            y=sender_data['sender_count'],
            name=f"{app}",
            marker_color=app_color_mapping[app]  # Use consistent color
        ),
        row=1, col=1
    )

    # Add receiver data
    fig.add_trace(
        go.Bar(
            x=receiver_data['receiver_type'],
            y=receiver_data['receiver_count'],
            name=f"{app}",
            showlegend=False,
            marker_color=app_color_mapping[app]  # Use consistent color
        ),
        row=1, col=2
    )

# Update layout and axis labels
fig.update_layout(
    barmode='stack',
    height=400,
    showlegend=True,
    legend_title="Applications"
)

fig.update_xaxes(title_text="Sender Types", row=1, col=1)
fig.update_yaxes(title_text="Message Count", row=1, col=1)

fig.update_xaxes(title_text="Receiver Types", row=1, col=2)
fig.update_yaxes(title_text="Message Count", row=1, col=2)

# Show the updated figure
fig.show()

#######################################################
# Simultaneous Messages
#######################################################

# Create subplots, one for each application in a row
fig = make_subplots(
    rows=1, cols=len(applications),
)

# Add boxplots for each application
for i, app in enumerate(applications):
    app_data = df[df['Application'] == app]
    aggregated_data = app_data.groupby('timeSend_ms').size().reset_index(name='simultaneous_count')
    fig.add_trace(
        go.Box(
            y=aggregated_data['simultaneous_count'],
            name=app,
            boxmean=True,
            marker_color=app_color_mapping[app]  # Use consistent color
        ),
        row=1, col=i + 1
    )

# Update layout
fig.update_layout(
    height=400,  # Adjust height for a single row
    width=300 * len(applications),  # Adjust width based on number of applications
    showlegend=True,
    legend_title="Applications"
)

fig.update_yaxes(title_text="Simultaneous Messages", row=1, col=1)

# Show the updated figure
fig.show()

#######################################################
# Messages Over Time
#######################################################

# Define the time bin size (e.g., 1 second = 1000 ms)
bin_size = 1000  # 1000 ms = 1 second

# Add a new column for time bins in seconds
df['time_bin_sec'] = (df['timeSend_ms'].astype('int64') // bin_size)

# Create subplots: one for each application
fig = make_subplots(
    rows=len(applications), cols=1,
    shared_xaxes=True,
    subplot_titles=[f"{app}" for app in applications]
)

# Add bar plots for aggregated message counts in each time bin for each application
for i, app in enumerate(applications):
    app_data = df[df['Application'] == app]
    aggregated_data = app_data.groupby('time_bin_sec').size().reset_index(name='message_count')

    fig.add_trace(
        go.Bar(
            x=aggregated_data['time_bin_sec'],
            y=aggregated_data['message_count'],
            name=f"{app}",
            marker_color=app_color_mapping[app],  # Use consistent color
            showlegend=(i == 0)  # Show legend only once
        ),
        row=i + 1, col=1
    )

# Update layout and axis labels
fig.update_layout(
    height=200 * len(applications),  # Adjust height based on number of applications
    width=500,
    showlegend=True,
    legend_title="Applications"
)

fig.update_xaxes(title_text="Time (s)", col=1, row=len(applications))
for i in range(1, len(applications) + 1):
    fig.update_yaxes(title_text="Message Count", row=i, col=1)

# Show the updated figure
fig.show()
