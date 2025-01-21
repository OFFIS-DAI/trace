import numpy as np
import pandas as pd
import os
import plotly.express as px
import plotly.io as pio
import plotly.colors

pio.kaleido.scope.mathjax = None

# Directory for result files
RESULT_DIR_NAME = '../agent_communication_generation_tool/results/sim_data'
filepaths = [os.path.join(RESULT_DIR_NAME, f) for f in os.listdir(RESULT_DIR_NAME) if f.endswith('.csv')]

# Initialize data structures
application_to_fano_factor = {}
results = []

# Fano factor calculation and data aggregation
for file in filepaths:
    data = pd.read_csv(file)

    if 'timeSend_ms' not in data:
        continue

    # Extract application and structure
    application_rows = data[data['Parameter'] == 'Agent communication pattern']
    application = application_rows['Value'].values[0] if len(application_rows) > 0 else "Unknown Application"

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
df.sort_values(by=["Base Application", "Structure"], inplace=True)

# Original Fano Factor Plot
fig_fano = px.bar(
    df,
    x="Base Application",
    y="Fano Factor Mean",
    error_y="Fano Factor Std",
    color="Structure",
    barmode="group",
    labels={"Base Application": "Base Application", "Fano Factor Mean": "Fano Factor"},
    opacity=0.9,
    color_discrete_sequence=plotly.colors.qualitative.Antique
)

fig_fano.update_layout(
    xaxis_title="",
    yaxis_title="Fano Factor (Log Scale)",
    yaxis_type="log",
    yaxis=dict(range=[-2, None]),
    xaxis_tickangle=45,
    font=dict(size=12),
    title_font_size=18,
    legend=dict(title="Organizational Structure"),
    margin=dict(l=100, r=40, t=80, b=80)
)

fig_fano.add_shape(
    type="line",
    x0=-0.5,
    x1=len(df["Base Application"].unique()) - 0.5,
    y0=1,
    y1=1,
    line=dict(color="gray", width=2, dash="dash"),
    xref="x",
    yref="y"
)
fig_fano.add_annotation(
    x=-0.5,
    y=1e-2,
    text="Poisson",
    showarrow=False,
    font=dict(color="gray", size=10, weight="bold"),
    xanchor="right",
    xshift=-20
)

fig_fano.add_shape(
    type="line",
    x0=-0.5,
    x1=len(df["Base Application"].unique()) - 0.5,
    y0=1e-2,
    y1=1e-2,
    line=dict(color="darkslategray", width=2, dash="dash"),
    xref="x",
    yref="y"
)
fig_fano.add_annotation(
    x=-0.5,
    y=-2,
    text="CBR",
    showarrow=False,
    font=dict(color="darkslategray", size=10, weight="bold"),
    xanchor="right",
    xshift=-20
)


def categorize_fano(fano):
    if fano < 0.1:
        return "F(w) ≈ 0"  # Use Unicode ≈
    elif fano < 0.9:
        return "F(w) < 1"
    elif 0.9 <= fano <= 1.1:
        return "F(w) ≈ 1"
    elif fano > 1.1:
        return "F(w) > 1"


df["Fano Factor Category"] = df["Fano Factor Mean"].apply(categorize_fano)

merged_df = pd.DataFrame()
for file in filepaths:
    data = pd.read_csv(file)
    if "timeSend_ms" not in data or "delay_ms" not in data:
        continue

    application_rows = data[data["Parameter"] == "Agent communication pattern"]
    application = application_rows["Value"].values[0] if len(application_rows) > 0 else "Unknown Application"

    structure_rows = data[data["Parameter"] == "Organizational structure"]
    organizational_structure = structure_rows["Value"].values[0].lower() if len(structure_rows) > 0 else "simple"

    full_application = f"{application} ({organizational_structure})"
    if full_application in df["Application"].values:
        fano_mean = df.loc[df["Application"] == full_application, "Fano Factor Mean"].values[0]
        fano_category = categorize_fano(fano_mean)

        scenario_data = data[["timeSend_ms", "delay_ms"]].copy()
        scenario_data["Application"] = full_application
        scenario_data["Fano Factor Category"] = fano_category
        merged_df = pd.concat([merged_df, scenario_data], ignore_index=True)

agg_data = merged_df.groupby("Fano Factor Category").agg(
    Delay_Mean=("delay_ms", "mean"),
    Delay_Std=("delay_ms", "std"),
    Count=("delay_ms", "size")
).reset_index()

# Define Fano factor category order
fano_order = ["F(w) ≈ 0", "F(w) < 1", "F(w) ≈ 1", "F(w) > 1"]

# Filter categories based on what is present in the data
unique_categories = df["Fano Factor Category"].unique()
print(unique_categories)
filtered_order = [category for category in fano_order if category in unique_categories]

print(filtered_order)

# Map the order and sort the DataFrame
df["Fano Category Order"] = df["Fano Factor Category"].map(lambda x: filtered_order.index(x))
df.sort_values(by="Fano Category Order", inplace=True)


fig_delay = px.bar(
    agg_data,
    x="Fano Factor Category",
    y="Delay_Mean",
    error_y="Delay_Std",
    color="Fano Factor Category",
    labels={"Delay_Mean": "Mean Delay (ms)", "Fano Factor Category": "Fano Factor Category"},
    barmode="group",
    category_orders={"Fano Factor Category": filtered_order},
    # title="Dependencies Between Fano Factor Categories and Delay Times",
    color_discrete_sequence=plotly.colors.qualitative.Prism
)

fig_delay.update_layout(
    xaxis_title="Fano Factor Category",
    yaxis_title="Mean Delay (ms)",
    font=dict(size=12),
    title_font_size=18,
    margin=dict(l=50, r=50, t=80, b=50),
    showlegend=False
)

# Save Plots
fig_fano.write_image("results/fano_factors.pdf", format="pdf", width=1000, height=400)
fig_delay.write_image("results/fano_vs_delay.pdf", format="pdf", width=400, height=400)
