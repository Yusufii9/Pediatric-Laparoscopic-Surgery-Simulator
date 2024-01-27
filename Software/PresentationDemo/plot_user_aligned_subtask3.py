import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
import warnings
from tkinter import filedialog


warnings.filterwarnings('ignore')


class DataPlotter3:
    def __init__(self):
        self.data = None
        self.signal_pairs = []
        self.fig, self.ax = plt.subplots(figsize=(18, 8))
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

    def plot_data(self):
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        self.update_plot(0)
        plt.show()


if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    # csv_file = filedialog.askopenfilename(title="Select the CSV Data File")
    csv_file = 'aligned_signals_task3.csv'
    root.destroy()

    plotter = DataPlotter3()
    plotter.load_data(csv_file)
    plotter.plot_data()
