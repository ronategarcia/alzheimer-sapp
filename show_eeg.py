import csv
import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

# Parameters
channel_names = ['TP9', 'AF7', 'AF8', 'TP10']  # Muse 2 EEG channel names
csv_filename = 'muse2_eeg_data.csv'  # CSV file that contains recorded EEG data
sampling_rate = 256  # Muse 2 sampling rate

# Read the CSV file
df = pd.read_csv(csv_filename)

# Extract the time and EEG data for each channel
timestamps = df['Timestamp']
eeg_data = df[channel_names].to_numpy()  # Convert the channel data to a NumPy array

# Calculate the time axis for plotting (assuming the timestamps are in seconds)
time_axis = np.arange(0, len(eeg_data)) / sampling_rate

# Initialize figure and subplots for each EEG channel
fig, axs = plt.subplots(2, 2, figsize=(12, 8))  # 2x2 grid of subplots

# Plot EEG data for each channel
for i, ax in enumerate(axs.flat):
    ax.plot(time_axis, eeg_data[:, i])
    ax.set_ylim([-500, 500])  # Adjust limits based on expected EEG range
    ax.set_title(f'EEG Data - {channel_names[i]}')
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('EEG Signal (uV)')

# Display the plot
plt.tight_layout()
plt.show()
