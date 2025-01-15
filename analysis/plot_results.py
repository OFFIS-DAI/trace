import math
import os
import plotly.io as pio
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from multiprocessing import Pool
import plotly.colors

pio.kaleido.scope.mathjax = None

RESULT_DIR_NAME = '../agent_communication_generation_tool/results/sim_data'
application_selection = ['OnDemandAutomatedMeterReading', 'DataAcquisition', 'WACsVoltageStabilityControl']


# Define a function to classify agents by type
def classify_agent(agent_name):
    if not isinstance(agent_name, str):
        print(agent_name)
        return 'Unknown'  # Default classification for non-string values
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
    elif 'aggregator' in agent_name:
        return 'Aggregator Agent'
    elif 'grid_operator' in agent_name:
        return 'Grid Operator Agent'
    elif 'device' in agent_name:
        return 'Device Agent'
    elif 'substation' in agent_name:
        return 'Substation Agent'
    else:
        print(agent_name)
        return 'Unknown'


# Function to extract technology and network name
def extract_technology_and_network(network_string):
    if not isinstance(network_string, str):
        return 'Unknown', 'Unknown'  # Default values for non-string entries
    try:
        parts = network_string.split('_')  # Split by underscore
        technology = 'Wifi' if parts[1] == '802' else parts[1]  # Second element is the technology
        network_name = parts[2]  # Third element is the network name
        return technology, network_name
    except IndexError:
        return 'Unknown', 'Unknown'  # Default values for invalid formats


# Process each file
def process_file(filepath):
    try:
        scenario_id = os.path.splitext(os.path.basename(filepath))[0]  # Use filename (without extension) as scenario ID

        df = pd.read_csv(filepath, index_col=0)
        if 'receiver' not in df.columns:
            return None
        df['Application'] = df[df['Parameter'] == 'Agent communication pattern']['Value'].values[0]
        df['Network'] = df[df['Parameter'] == 'Network']['Value'].values[0]
        df['Technology'], df['Network Name'] = zip(*df['Network'].apply(extract_technology_and_network))
        df['ScenarioID'] = scenario_id  # Add the scenario ID to the DataFrame
        structure_rows = df[df['Parameter'] == 'Organizational structure']
        organizational_structure = structure_rows['Value'].values[0].lower() if len(structure_rows) > 0 else "simple"
        df['Organizational structure'] = organizational_structure

        df.dropna(axis=0, subset='timeSend_ms', inplace=True)

        df['timeSend_ms'] = df['timeSend_ms']
        df['time_bin_sec'] = (df['timeSend_ms'] / 1000).round()

        df['sender_type'] = df['sender'].apply(classify_agent)
        df['receiver_type'] = df['receiver'].apply(classify_agent)

        if math.nan in df['sender_type'] or math.nan in df['receiver_type']:
            return None

        return df
    except Exception as e:
        print(f"Error processing file {filepath}: {e}")
        return None


# Process files in parallel
filepaths = [os.path.join(RESULT_DIR_NAME, f) for f in os.listdir(RESULT_DIR_NAME) if f.endswith('.csv')]

with Pool() as pool:
    processed_files = pool.map(process_file, filepaths)

# Filter out None and empty DataFrames
valid_dfs = [df for df in processed_files if df is not None and not df.empty]

# Concatenate valid DataFrames
if valid_dfs:
    df = pd.concat(valid_dfs, ignore_index=True)
else:
    raise ValueError("No valid dataframes to concatenate. Ensure files have valid data.")

# Generate a color palette for the applications
applications = df['Application'].unique()
# Use a brighter color palette for better visibility
color_palette = plotly.colors.qualitative.Prism
if len(applications) > len(color_palette):  # Repeat the palette if needed
    color_palette = (color_palette * ((len(applications) // len(color_palette)) + 1))[:len(applications)]

# Map applications to colors
app_color_mapping = {app: color_palette[i] for i, app in enumerate(applications)}

#######################################################
# Message Dispatch Over Time for Selected Applications
#######################################################
# Find the first scenario for each selected application
selected_scenarios = [
    df[df['Application'] == app]['ScenarioID'].iloc[0]
    for app in application_selection if app in df['Application'].unique()
]

# Map scenarios to their corresponding applications
scenario_to_app = {scenario: df[df['ScenarioID'] == scenario]['Application'].iloc[0]
                   for scenario in selected_scenarios}

# Create subplots: one for each scenario/application
num_cols = 1  # Single column for a clean vertical layout
num_rows = len(selected_scenarios)  # One row per scenario/application

fig = make_subplots(
    rows=num_rows, cols=num_cols,
    subplot_titles=[f"{scenario_to_app[scenario]}" for scenario in selected_scenarios],
    shared_xaxes=True
)

# Add scatter plots for each selected scenario
for i, scenario in enumerate(selected_scenarios):
    scenario_data = df[df['ScenarioID'] == scenario].reset_index()  # Reset index for consistent plotting
    grouped_data = scenario_data.groupby(['time_bin_sec', 'packetSize_B_x']).size().reset_index(name='count')

    app = scenario_to_app[scenario]  # Get the application for the current scenario
    row = i + 1

    fig.add_trace(
        go.Scatter(
            x=grouped_data['time_bin_sec'],
            y=grouped_data['packetSize_B_x'],  # Use the packetSize_B_x column for the y-axis
            mode='markers',
            name=f"Scenario {scenario} ({app})",
            marker=dict(
                size=grouped_data['count']*0.2,  # Scale the size by the count
                color=app_color_mapping[app],  # Use the application-specific color
                opacity=0.7
            ),
        ),
        row=row, col=1
    )

    # Set axis labels
    fig.update_yaxes(title_text="Data Size (B)", row=row, col=1)
    fig.update_xaxes(title_text="Time (s)", row=row, col=1)

# Update layout
fig.update_layout(
    height=250 * num_rows,  # Adjust height dynamically based on the number of rows
    width=800,
    showlegend=False,  # No need for a legend since titles indicate applications
    margin=dict(l=50, r=20, t=50, b=50)
)

# Save the figure to a PDF file
output_pdf_path = "results/message_dispatch_selected_applications.pdf"
pio.write_image(fig, output_pdf_path, format="pdf", width=400, height=150 * num_rows)


#######################################################
# Delay analysis
#######################################################

# Analyze delay times by application

# Filter data for applications with non-null delay times
delay_data = df.dropna(subset=['delay_ms'])

# Pivot the data to calculate mean and standard deviation delay times for each technology
mean_delay_table = delay_data.pivot_table(
    index='Application',
    columns='Technology',
    values='delay_ms',
    aggfunc='mean'
)

std_delay_table = delay_data.pivot_table(
    index='Application',
    columns='Technology',
    values='delay_ms',
    aggfunc='std'
)

# Round the values for better readability
mean_delay_table = mean_delay_table.round()
std_delay_table = std_delay_table.round()

# Prepare LaTeX table content
latex_table_data = []
for app in mean_delay_table.index:
    row_data = []
    for tech in mean_delay_table.columns:
        if not pd.isna(mean_delay_table.loc[app, tech]) and not pd.isna(std_delay_table.loc[app, tech]):
            mean_std = f"{mean_delay_table.loc[app, tech]} ± {std_delay_table.loc[app, tech]}"
        else:
            mean_std = "-"
        row_data.append(mean_std)
    latex_table_data.append(f"    {app} & " + " & ".join(row_data) + " \\\\")

# Generate LaTeX table
print("\\begin{table*}[h]")
print("\\centering")
print("\\caption{Mean and standard deviation of delay times (ms) by application and network technology.}")
print("\\label{tab:mean_std_delays}")
print("\\begin{tabular}{l" + "c" * len(mean_delay_table.columns) + "}")
print("    \\toprule")
print(
    "    \\textbf{Application} & " + " & ".join([f"\\textbf{{{tech}}}" for tech in mean_delay_table.columns]) + " \\\\")
print("    \\midrule")
for row in latex_table_data:
    print(row)
print("    \\bottomrule")
print("\\end{tabular}")
print("\\end{table*}")

#######################################################
# Sender/Receiver Distributions
#######################################################
# Aggregate data for sender and receiver distributions across scenarios for each organizational structure
# Filter data for the application "AddNewAgent"
add_new_agent_data = df[df['Application'] == 'AddNewAgent']

# Aggregate data for sender and receiver distributions across scenarios for each organizational structure
sender_counts = add_new_agent_data.groupby(['Organizational structure', 'sender_type']).size().reset_index(name='sender_count')
receiver_counts = add_new_agent_data.groupby(['Organizational structure', 'receiver_type']).size().reset_index(name='receiver_count')


# Get unique organizational structures
organizational_structures = sender_counts['Organizational structure'].unique()

# Determine number of rows needed (1 row per organizational structure)
num_rows = len(organizational_structures)

# Create subplots: one row per organizational structure with two columns (sender and receiver)
fig = make_subplots(
    rows=num_rows, cols=2,
    subplot_titles=[f"{structure}" for structure in organizational_structures for _ in range(2)],
    specs=[[{'type': 'domain'}, {'type': 'domain'}] for _ in range(num_rows)]
)

# Add pie charts for sender and receiver distributions by organizational structure
for i, structure in enumerate(organizational_structures):
    # Sender distribution
    sender_data = sender_counts[sender_counts['Organizational structure'] == structure]
    fig.add_trace(
        go.Pie(
            labels=sender_data['sender_type'],
            values=sender_data['sender_count'],
            textinfo='none',
            name=f"Sender",
            title=f"Sender",
        ),
        row=i + 1, col=1
    )

    # Receiver distribution
    receiver_data = receiver_counts[receiver_counts['Organizational structure'] == structure]
    fig.add_trace(
        go.Pie(
            labels=receiver_data['receiver_type'],
            values=receiver_data['receiver_count'],
            textinfo='none',
            name=f"Receiver",
            title=f"Receiver",
        ),
        row=i + 1, col=2
    )

# Update layout
fig.update_layout(
    margin=dict(l=10, r=10, t=30, b=10),  # Adjust margins: left, right, top, bottom
    height=150 * num_rows,  # Adjust height dynamically based on the number of rows
    width=400,
)

# Save the figure as a PDF
output_pdf_path = "results/sender_receiver_pie_charts_by_structure.pdf"
pio.write_image(fig, output_pdf_path, format="pdf", width=600, height=150 * num_rows)

print(f"Figure saved as PDF: {output_pdf_path}")


#######################################################
# Simultaneous Messages
#######################################################

# Create subplots, one for each application in a row
fig = make_subplots(
    rows=1, cols=len(application_selection),
)

# Add boxplots for each application
for i, app in enumerate(application_selection):
    app_data = df[df['Application'] == app]
    scenario_aggregated = app_data.groupby(['ScenarioID', 'timeSend_ms']).size().reset_index(name='simultaneous_count')
    aggregated_data = scenario_aggregated.groupby('timeSend_ms')['simultaneous_count'].mean().reset_index()
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
    width=300 * len(application_selection),  # Adjust width based on number of applications
    showlegend=False,
    margin=dict(l=60, r=20, t=30, b=50),  # Adjust margins: left, right, top, bottom
    legend_title="Applications"
)

fig.update_yaxes(title_text="Simultaneous Messages", row=1, col=1)

# Save the figure as a PDF
output_pdf_path = "results/simultaneous_messages.pdf"
pio.write_image(fig, output_pdf_path, format="pdf", width=180 * len(application_selection), height=200)

print(f"Figure saved as PDF: {output_pdf_path}")
