import os
import threading
import time  # To track time for 1-minute recording
import tkinter as tk
import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pylsl import StreamInlet, resolve_byprop

from result_page import show_result_brain_wave


def start_stream():
    cmd = "muselsl stream"
    os.system(cmd)


# Parameters
window_size = 5  # Seconds of data to display at once
sampling_rate = 256  # Typical sampling rate of Muse 2 is 256 Hz
window_length = window_size * sampling_rate
channel_names = ['TP9', 'AF7', 'AF8', 'TP10']  # Muse 2 EEG channel names
record_duration = 60  # For testing, record data for 1 minute, but the actual duration should be between 5-10 minutes

# Initialize figure and subplots
fig, axs = plt.subplots(2, 2, figsize=(12, 8))  # 2x2 grid of subplots
x_data = np.arange(0, window_size, 1 / sampling_rate)
eeg_data = np.zeros((len(channel_names), window_length))
lines = []
# Create a TXT file to store the EEG data
txt_filename = 'muse2_eeg_data.txt'


def create_plot():
    # Create a plot for each channel
    for i, ax in enumerate(axs.flat):
        line, = ax.plot(x_data, eeg_data[i, :])
        ax.set_ylim([-500, 500])  # Adjust limits based on expected EEG range
        ax.set_title(f'EEG Data - {channel_names[i]}')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('EEG Signal (uV)')
        lines.append(line)
    # Apply tight layout to prevent elements from being cut off
    fig.tight_layout()


def create_txt_file():
    # Create a TXT file to store the EEG data
    with open(txt_filename, mode='w') as file:
        # Write the header with channel names
        file.write('Timestamp\t' + '\t'.join(channel_names) + '\n')


def start_recording(main_window, window, label=None, label_image=None, button=None):
    # Resolve the EEG stream
    print("Looking for an EEG stream...")
    streams = resolve_byprop('type', 'EEG', timeout=10) # looks for the Muse2 headband

    if not streams:
        print("No EEG streams found.")
        if label:
            label.config(text="No EEG streams found. \n Please check the connection and try again.", font=("Arial", 16),
                         fg="red")
            label.update()
            button.pack_forget()
        if label_image:
            label_image.pack()

    else:
        label.config(text="Recording EEG data...")
        label.update()
        print("EEG stream found!")
        # Embed the Matplotlib figure in the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        inlet = StreamInlet(streams[0])

        # Start time for 1-minute recording
        start_time = time.time()

        # Update plot with new data and save to TXT
        def update_plot_and_save():
            global eeg_data

            # Pull data from the stream
            sample, timestamp = inlet.pull_sample()
            new_data = np.array(sample[:4]).reshape(-1, 1)  # Only keep the first 4 channels (EEG)

            # Shift the data and update the plot
            eeg_data = np.roll(eeg_data, -1, axis=1)
            eeg_data[:, -1] = new_data[:, 0]

            # Save the new data to the TXT file
            with open(txt_filename, mode='a') as file:
                file.write(f"{timestamp}\t" + '\t'.join(map(str, sample[:4])) + '\n')

            # Update each line in the subplots
            for i, line in enumerate(lines):
                line.set_ydata(eeg_data[i, :])

            # Adjust layout and redraw the plot
            fig.tight_layout()
            # fig.show()
        #     Redraw the plot
            canvas.draw()

        #     Continue updating if recording duration has not been reached
            if time.time() - start_time < record_duration:
                window.after(10, update_plot_and_save)
            else:
                print(f"Recording complete. Data saved to {txt_filename}")

                show_result_brain_wave(main_window, window, file_path=txt_filename)

        # Schedule the first update on the main thread
        window.after(10, update_plot_and_save)


def run_brain_wave(main_window, window, label_image, label=None, button=None):
    # Start the Muse stream in a separate thread
    t1 = threading.Thread(target=start_stream)
    t1.start()
    time.sleep(10)  # Allow some time for the Muse stream to start
    # hide the label_image
    label_image.pack_forget()
    create_plot()
    create_txt_file()

    # Start recording directly on the main thread
    start_recording(main_window, window, label=label, label_image=label_image, button=button)
