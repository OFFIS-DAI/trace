import numpy as np
import pandas as pd
import os
import plotly.express as px
import plotly.io as pio
import plotly.colors
pio.kaleido.scope.mathjax = None

RESULT_DIR_NAME = '../agent_communication_generation_tool/results/sim_data'
filepaths = [os.path.join(RESULT_DIR_NAME, f) for f in os.listdir(RESULT_DIR_NAME) if f.endswith('.csv')]

application_to_fano_factor = {}
results = []

for file in filepaths:
    data = pd.read_csv(file)

    if 'timeSend_ms' not in data:
        continue

    # Extract application
    application_rows = data[data['Parameter'] == 'Agent communication pattern']
    application = application_rows['Value'].values[0] if len(application_rows) > 0 else "Unknown Application"

    # Extract organizational structure
    structure_rows = data[data['Parameter'] == 'Organizational structure']
    organizational_structure = structure_rows['Value'].values[0].lower() if len(structure_rows) > 0 else "simple"

    # Combine application and structure for full identification
    full_application = f"{application} ({organizational_structure})"

    if full_application not in application_to_fano_factor:
        application_to_fano_factor[full_application] = []

    # Drop NaN values in 'timeSend_ms'
    data.dropna(axis=0, subset=['timeSend_ms'], inplace=True)
    if len(data) == 0:
        continue
    data.sort_values(by='timeSend_ms', inplace=True)

    # Calculate the minimum and maximum time for binning
    min_time = data['timeSend_ms'].min()
    max_time = data['timeSend_ms'].max()

    # Handle the case where all messages occur at the same timestamp
    if min_time == max_time:
        mean_num_messages = data.shape[0]
        variance_num_messages = 0
        fano_factor = 0
        application_to_fano_factor[full_application].append(fano_factor)
        continue

    # Total number of messages
    total_num_messages = data.shape[0]

    # Mean number of messages per millisecond
    mean_num_messages = total_num_messages / (max_time - min_time + 1)

    # Define time bins (window size = 1 millisecond)
    data['time_bin'] = (data['timeSend_ms'] // 1).astype(int)

    # Count the number of messages in each millisecond
    message_counts = data.groupby('time_bin').size()

    # Create a complete Series with all time bins, filling missing bins with 0
    time_bins = np.arange(min_time, max_time + 1, 1)

    complete_message_counts = pd.Series(0, index=time_bins)
    complete_message_counts.update(message_counts)

    # Calculate the variance of message counts
    variance_num_messages = complete_message_counts.var()

    # Calculate Fano Factor
    fano_factor = variance_num_messages / mean_num_messages if mean_num_messages > 0 else np.nan

    # Store the Fano Factor
    application_to_fano_factor[full_application].append(fano_factor)

# Aggregate results for visualization
for application, fano_factors in application_to_fano_factor.items():
    base_application = application.split(' (')[0]
    structure = application.split(' (')[-1].strip(')')
    if len(fano_factors) > 0:
        # Offset zero Fano factors for visualization
        fano_factors = [value if value > 0 else 1e-2 for value in fano_factors]
        results.append({
            "Application": application,
            "Fano Factor Mean": np.mean(fano_factors),
            "Fano Factor Std": np.std(fano_factors),
            "Base Application": base_application,
            "Structure": structure
        })

df = pd.DataFrame(results)

# Sort by Base Application and Structure for better grouping
df.sort_values(by=["Base Application", "Structure"], inplace=True)

# Visualization using Plotly
fig = px.bar(
    df,
    x="Base Application",
    y="Fano Factor Mean",
    error_y="Fano Factor Std",
    color="Structure",
    barmode="group",
    labels={"Base Application": "Base Application", "Fano Factor Mean": "Fano Factor"},
    opacity=0.9,  # Make bars bolder
    color_discrete_sequence=plotly.colors.qualitative.Antique
)

# Update layout for better readability
fig.update_layout(
    xaxis_title="",
    yaxis_title="Fano Factor (Log Scale)",
    yaxis_type="log",  # Apply log scale
    yaxis=dict(range=[-2, None]),  # Ensure lower limit for log scale
    xaxis_tickangle=45,  # Rotate labels for base applications
    font=dict(size=12),  # Bold fonts
    title_font_size=18,
    legend=dict(title="Organizational Structure"),
    margin=dict(l=100, r=40, t=80, b=80)  # Adjust margins
)

# Add reference lines for Poisson process (Fano = 1) and CBR process (Fano = ~0)
fig.add_shape(
    type="line",
    x0=-0.5,
    x1=len(df["Base Application"].unique()) - 0.5,
    y0=1,
    y1=1,
    line=dict(color="gray", width=2, dash="dash"),
    xref="x",
    yref="y",
    name="Poisson Process (Fano = 1)"
)
fig.add_annotation(
    x=-0.5,
    y=1e-2,
    text="Poisson",
    showarrow=False,
    font=dict(color="gray", size=10, weight="bold"),
    xanchor="right",  # Align text to the right
    xshift=-20  # Shift text further left
)

fig.add_shape(
    type="line",
    x0=-0.5,
    x1=len(df["Base Application"].unique()) - 0.5,
    y0=1e-2,
    y1=1e-2,
    line=dict(color="darkslategray", width=2, dash="dash"),
    xref="x",
    yref="y",
    name="CBR"
)
fig.add_annotation(
    x=-0.5,
    y=-2,
    text="CBR",
    showarrow=False,
    font=dict(color="darkslategray", size=10, weight="bold"),
    xanchor="right",  # Align text to the right
    xshift=-20  # Shift text further left
)

# Adjust bar width for better spacing
fig.update_traces(width=0.5)  # Increase the bar width for bold appearance

# Save the figure to a PDF file
output_pdf_path = "results/fano_factors.pdf"
pio.write_image(fig, output_pdf_path, format="pdf", width=1000, height=400)
