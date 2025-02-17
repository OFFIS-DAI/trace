import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pandas as pd
import seaborn as sns
import networkx as nx
import matplotlib.pyplot as plt

from agent_communication_generation_tool.description_classes.passwords import MAIL_ADDRESS, PASSWORD


def merge_input_and_output_df(input_df, output_df):
    try:
        return pd.merge(input_df, output_df, on='msgId')
    except KeyError as e:
        return input_df


def send_mail_notification(scenario_description, recipient_mail="malin.radtke@offis.de", failed=False):
    # Send email notification
    try:
        sender_email = MAIL_ADDRESS
        recipient_email = recipient_mail
        email_subject = "Simulation Completed" if not failed else "Simulation Failed "
        email_body = f"The simulation has completed successfully.\n\n Details: {scenario_description}" if not failed \
            else f"The simulation has failed. \n\nDetails: {scenario_description}"

        # Create the email message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = email_subject

        # Add the body to the email
        message.attach(MIMEText(email_body, "plain"))

        # Connect to the SMTP server and send the email
        with smtplib.SMTP("smtp.gmx.com", 587) as server:
            server.starttls()
            server.login(MAIL_ADDRESS, PASSWORD)
            server.sendmail(sender_email, recipient_email, message.as_string())

        print("Notification email sent successfully.")

    except Exception as e:
        print(f"Failed to send email notification: {e}")


def plot_traffic_pattern(scenario_description,
                         result_df, scenario_name):
    """
    Plots delay values for time of sending of messages and saves to file.
    :param scenario_description: simulation configuration.
    :param result_df: DataFrame with results.
    :param scenario_name: name of the scenario.
    :return: save plot in file.
    """
    if 'delay_ms' not in result_df.columns:
        return
    sns.set()

    with_replies = 'calculationStart_ms' in result_df.columns

    if with_replies:
        # Calculate the time difference only for rows where calculationStart_ms is not 0
        result_df['time_diff_ms'] = result_df.apply(
            lambda row: row['timeSend_ms'] - row['calculationStart_ms'] if row['calculationStart_ms'] != 0 else None,
            axis=1
        )
        # Filter to include only rows with a meaningful time difference
        valid_time_diffs_df = result_df.dropna(subset=['time_diff_ms'])

    # Filter rows with maximum receivingTime_ms for each msgId
    max_receiving_time_rows = result_df.loc[result_df.groupby('msgId')['timeSend_ms'].idxmax()]

    # Aggregate data to count messages for each sending time and sender
    message_counts = max_receiving_time_rows.groupby(['timeSend_ms', 'sender']).size().reset_index(name='counts')

    # Merge back to get the counts for each row in the original DataFrame
    max_receiving_time_rows = pd.merge(max_receiving_time_rows, message_counts, on=['timeSend_ms', 'sender'])

    # Create a figure with four subplots
    fig, axes = plt.subplots(2, 3, figsize=(20, 10))
    fig.suptitle(f'{scenario_name}')
    ax1, ax2, ax3, ax4, ax5, ax6 = axes.ravel()

    # Create a scatter plot on the first subplot with different colors for each sender
    sns.scatterplot(x='timeSend_ms', y='delay_ms', data=max_receiving_time_rows, ax=ax1)
    ax1.set_xlabel('Sending Time (ms)')
    ax1.set_ylabel('Delay (ms)')
    ax1.set_title(f'Sending Time vs Delay')

    # Create a histogram (probability density plot) of sending times on the second subplot
    sns.histplot(data=max_receiving_time_rows, x='timeSend_ms', kde=True, ax=ax2, bins=10)
    ax2.set_xlabel('Sending Time (ms)')
    ax2.set_ylabel('Message count')
    ax2.set_title(f'Sending Time Distribution')

    # Modified scatter plot to adjust dot sizes based on message count
    sns.scatterplot(x='timeSend_ms', y='sender', size='counts', hue='sender', data=max_receiving_time_rows, ax=ax3,
                    sizes=(20, 200))
    ax3.set_xlabel('Sending Time (ms)')
    ax3.set_ylabel('Sender')
    ax3.set_title(f'Sending Time vs Sender')
    if ax3.get_legend():
        ax3.get_legend().remove()

    # Retrieve the NetworkX graph from simulation_config
    scenario_description.communication_graph.relabel_graph()
    topology_graph = scenario_description.communication_graph.relabeled_graph

    # Create a subplot for the topology plot
    ax4.set_title(f'Network Topology')
    pos = nx.circular_layout(topology_graph)
    nx.draw(topology_graph, pos, with_labels=True, node_color='skyblue', ax=ax4)

    # Add subplot for packet sizes
    ax5.set_title(f'Packet Sizes')
    sns.histplot(data=result_df, x='packetSize_B_x', ax=ax5, bins=20)
    ax5.set_xlabel('Packet Size (Bytes)')
    ax5.set_ylabel('Count')

    if with_replies:
        # Assuming 'sender' is categorical and you want separate bars for each sender
        sns.barplot(x='sender', y='time_diff_ms', data=valid_time_diffs_df, ax=ax6, errorbar=None)
        ax6.set_xlabel('Sender')
        ax6.set_ylabel('Time Difference (ms)')
        ax6.set_title(f'Calculation Start vs Sending Time')
        ax6.tick_params(axis='x', rotation=45)  # Rotate x labels for better readability

    # Adjust the layout
    plt.tight_layout()

    # Save the plot
    plt.savefig(f'../../agent_communication_generation_tool/results/plots/{scenario_description.id}')
    plt.clf()
    plt.close()
