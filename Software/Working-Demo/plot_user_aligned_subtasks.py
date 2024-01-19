import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
import warnings
from tkinter import filedialog

from task1_written_feedback import check_signals_in_column

warnings.filterwarnings('ignore')


class DataPlotter:
    def __init__(self):
        self.data = None
        self.signal_pairs = []
        self.fig, self.ax = plt.subplots(figsize=(18, 8))
        plt.subplots_adjust(right=0.5)
        self.current_index = [0]

    def load_data(self, csv_file):
        self.data = pd.read_csv(csv_file)
        for col in self.data.columns:
            if col.startswith('Ref'):
                user_col = col.replace('Ref', 'User')
                if user_col in self.data.columns:
                    self.signal_pairs.append((col, user_col))

    def update_plot(self, index):
        self.ax.clear()
        ref_signal, user_signal = self.signal_pairs[index]
        ref_data = self.data[ref_signal].str.strip('[]').astype(float)
        user_data = self.data[user_signal].str.strip('[]').astype(float)

        self.ax.plot(ref_data, label=f'{ref_signal} (Reference Data)')
        self.ax.plot(user_data, label=f'{user_signal} (User Data)', color='red')

        signal_title = '_'.join(ref_signal.split("_")[1:])
        signal_title = "Aligned_" + signal_title

        self.ax.set_title(signal_title)
        self.ax.set_xlabel('Data Points')
        self.ax.set_ylabel('Magnitude Value')
        self.ax.legend()

    def on_key(self, event):
        if event.key == 'right':
            self.current_index[0] = (self.current_index[0] + 1) % len(self.signal_pairs)
            self.update_plot(self.current_index[0])
            self.fig.canvas.draw()
        elif event.key == 'left':
            self.current_index[0] = (self.current_index[0] - 1) % len(self.signal_pairs)
            self.update_plot(self.current_index[0])
            self.fig.canvas.draw()

    def display_all_feedback(self, feedback_dict):
        all_feedback = "\n".join([message for _, message in feedback_dict.items()])

        # Display the feedback in the right margin of the figure
        self.fig.text(0.6, 0.5, all_feedback, verticalalignment='center', fontsize=10, wrap=True)


    def plot_data(self):
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        self.update_plot(0)
        plt.show()


        # Function to check the existence of each possible signal in the CSV column
    def check_signals_in_column(csv_file_path, column_name, custom_messages):
        with open(csv_file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            # Create a list of all the values in the specified column
            column_data = [row[column_name] for row in reader]

        # Dictionary to hold the existence result and corresponding custom message for each signal
        signals_existence_messages = {}

        # Check for each signal's existence in the column data
        for signal in custom_messages.keys():
            if signal in column_data:
                # Use the custom message for when the signal exists
                signals_existence_messages[signal] = custom_messages[signal]

        return signals_existence_messages

# Defining custom messages here
custom_messages = {
    'Ref_task1_L_pitchVel': "Slow down speed of upward-downward or downward-upward motion with the left tool",
    'Ref_task1_R_pitchVel': "Slow down speed of upward-downward or downward-upward motion with the right tool",
    'Ref_task1_R_pitchAcc': "Avoid rapid movements while moving tool up-down or down-up with the right tool",
    'Ref_task1_L_pitchAcc': "Avoid rapid movements while moving tool up-down or down-up with the left tool",
    'Ref_task1_R_yawVel': "Slow down speed of left-right or right-left motion with the right tool",
    'Ref_task1_L_yawVel': "Slow down speed of left-right or right-left motion with the left tool",
    'Ref_task1_R_yawAcc': "Avoid rapid movements while moving right tool right-left or left-right",
    'Ref_task1_L_yawAcc': "Avoid rapid movements while moving left tool right-left or left-right",
    'Ref_task1_R_yaw': "Remain within range when moving right tool left-right or right-left",
    'Ref_task1_L_yaw': "Remain within range when moving left tool left-right or right-left",
    'Ref_task1_L_rollVel': "Slow down speed while rotating left tool",
    'Ref_task1_R_rollVel': "Slow down speed while rotating right tool",
    'Ref_task1_R_rollAcc': "Avoid rapidly rotating left tool",
    'Ref_task1_L_rollAcc': "Avoid rapidly rotating right tool",
    'Ref_task1_R_roll': "Remain within range while rotating right tool",
    'Ref_task1_L_roll': "Remain within range while rotating left tool",
    'Ref_task1_L_surgeVel': "Slow down speed while pulling left tool in or out of trocar",
    'Ref_task1_R_surgeVel': "Slow down speed while pulling right tool in or out of trocar",
    'Ref_task1_R_surgeAcc': "Avoid rapidly pulling right tool in or out",
    'Ref_task1_L_surgeAcc': "Avoid rapidly pulling left tool in or out",
    'Ref_task1_R_surge': "Remain within range while pulling right tool in or out of trocar",
    'Ref_task1_L_surge': "Remain within range while pulling left tool in or out of trocar"
}


if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    csv_file = filedialog.askopenfilename(title="Select the CSV Data File")
    root.destroy()

    # Usage of the function
    csv_file_path = 'task1_weak_signal_performance.csv'
    column_name = 'Ref Signal'

    # Call the function and print the results
    signals_existence_messages = check_signals_in_column(csv_file_path, column_name, custom_messages)

    plotter = DataPlotter()
    plotter.load_data(csv_file)

    # Pass each message to the plot_data method
    for signal, message in signals_existence_messages.items():
        print(f"Signal: {signal}\nMessage: {message}\n")

    plotter.display_all_feedback(signals_existence_messages)
    plotter.plot_data()

