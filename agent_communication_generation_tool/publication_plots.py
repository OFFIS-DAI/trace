import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sns.set()

data_df_1 = pd.read_csv('results/data/d980f0dd-a2f7-4429-975e-16ed2d3f9274.csv')
data_df_1['Scenario'] = data_df_1.loc[data_df_1['Parameter'] == 'Organizational structure']['Value'].values[0]
data_df_2 = pd.read_csv('results/data/7edaca60-5362-4dee-8919-987b1ecac8ff.csv')
data_df_2['Scenario'] = data_df_2.loc[data_df_2['Parameter'] == 'Organizational structure']['Value'].values[0]
data_df_3 = pd.read_csv('results/data/4b948a73-ab64-4b15-a2c8-1faa28d630b5.csv')
data_df_3['Scenario'] = data_df_3.loc[data_df_3['Parameter'] == 'Organizational structure']['Value'].values[0]
df = pd.concat([data_df_1, data_df_2, data_df_3], ignore_index=True)

# Prepare the sender type for the whole dataset before looping
df['sender'] = df['sender'].fillna('Unknown')
df['sender_type'] = df['sender'].apply(lambda x: '_'.join(x.split('_')[:-1]) if isinstance(x, str) else x).apply(lambda x: x.replace('_agent', ''))

# Extract all unique sender types to ensure consistent coloring
unique_sender_types = df['sender_type'].unique()
palette = sns.color_palette("colorblind", len(unique_sender_types))  # Choose a palette that fits the number of sender types
color_map = dict(zip(unique_sender_types, palette))  # Map sender types to colors

# Determine the unique scenarios for subplotting
scenarios = df['Scenario'].unique()

# Setup the matplotlib figure and axes
fig, axes = plt.subplots(nrows=len(scenarios), ncols=2, figsize=(13, 3.5 * len(scenarios)))

# Increase vertical space between rows of subplots
fig.subplots_adjust(hspace=0.6, wspace=0.4)  # Increase this value to increase space

# Loop over each scenario and plot on separate subplots
for i, scenario in enumerate(scenarios):
    index = i   # Calculate index for subplot positioning, captions first
    # Filter the DataFrame for the current scenario
    scenario_data = df[df['Scenario'] == scenario]

    # First subplot: Time Sent vs Delay
    sns.scatterplot(ax=axes[index, 0], data=scenario_data, x='timeSend_ms', y='delay_ms')
    axes[index , 0].set_title(f'Market participation ({scenario.lower()}) - Delay times')
    axes[index , 0].set_xlabel('Time Sent (ms)')
    axes[index, 0].set_ylabel('Delay (ms)')

    # Second subplot: Number of Messages Sent per Sender Over Time
    message_counts = scenario_data.groupby(['sender', 'sender_type', 'timeSend_ms']).size().reset_index(name='count')
    sns.scatterplot(ax=axes[index, 1], data=message_counts, x='timeSend_ms', y='sender_type', size='count',
                    sizes=(20, 200), hue='sender_type', palette=color_map, legend=None)
    axes[index, 1].set_title(f'Market participation ({scenario.lower()}) - Messages sent')
    axes[index, 1].set_xlabel('Time Sent (ms)')
    axes[index, 1].set_ylabel('Sender')

# Save the plot
plt.savefig(f'results/plots/paper.pdf',
            format="pdf", bbox_inches="tight")
plt.clf()
plt.close()
