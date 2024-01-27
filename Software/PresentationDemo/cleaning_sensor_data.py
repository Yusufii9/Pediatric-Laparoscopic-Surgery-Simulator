import os
import sys
import pandas as pd
import tkinter as tk
import warnings
from tkinter import filedialog, messagebox, simpledialog

warnings.filterwarnings('ignore')


class SensorDataCleaner:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def get_next_filename(self):
        exe_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(
            os.path.abspath(__file__))

        files = [f for f in os.listdir(exe_dir) if f.startswith("CleanedSensorData_") and f.endswith('.csv')]
        numbers = [int(f.split('_')[1].split('.')[0]) for f in files if f.split('_')[1].split('.')[0].isdigit()]
        next_number = max(numbers, default=0) + 1
        return os.path.join(exe_dir, f"CleanedSensorData_{next_number}.csv")

    def clean_sensor_data(self):
        self.file_path = filedialog.askopenfilename(title="Choose the Text Sensor Data File")

        if not self.file_path:
            messagebox.showwarning(title="Warning", message="No file selected!")
            return

        with open(self.file_path, "r") as file:
            data = file.read()

        lines = data.strip().split("\n")
        cleaned_data = [line.split("|") for line in lines]
        cleaned_data = [item for item in cleaned_data if len(item) == 34]

        columns = ['Time', 'Force']
        labels = ['L', 'R']
        attributes = ['pitchAcc', 'yawAcc', 'surgeAcc', 'rollAcc', 'pitchVel', 'yawVel', 'surgeVel', 'rollVel',
                      'pitch', 'yaw', 'surge', 'roll', 'x', 'y', 'z', 'motion']
        for label in labels:
            for attribute in attributes:
                columns.append(f'{label}_{attribute}')

        temp_df = pd.DataFrame(cleaned_data, columns=columns)

        if not temp_df.empty:
            file_name = self.get_next_filename()
            temp_df.to_csv(file_name)
            messagebox.showinfo(title="Success", message="Sensor Data Have Been Processed and Saved")
        else:
            messagebox.showwarning(title="Warning", message="No Valid Sensor Data to Save!")


if __name__ == '__main__':
    cleaner = SensorDataCleaner()
    cleaner.clean_sensor_data()
