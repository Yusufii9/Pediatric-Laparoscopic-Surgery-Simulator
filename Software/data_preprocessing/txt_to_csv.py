import os
import sys
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import warnings

warnings.filterwarnings('ignore')


def get_next_filename():
    exe_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(
        os.path.abspath(__file__))

    files = [f for f in os.listdir(exe_dir) if f.startswith("CleanedSensorData_") and f.endswith('.csv')]

    numbers = [int(f.split('_')[1].split('.')[0]) for f in files if f.split('_')[1].split('.')[0].isdigit()]

    next_number = max(numbers, default=0) + 1

    return os.path.join(exe_dir, f"CleanedSensorData_{next_number}.csv")


def cleaning_sensor_data():
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename()

    with open(file_path, "r") as file:
        data = file.read()

    lines = data.strip().split("\n")
    cleaned_data = [line.split("|") for line in lines]
    cleaned_data = [item for item in cleaned_data if len(item) == 34]
    #  converted_data = converted_data[1:]

    time, force = [], []
    L_pitchAcc, L_yawAcc, L_surgeAcc, L_rollAcc = [], [], [], []
    R_pitchAcc, R_yawAcc, R_surgeAcc, R_rollAcc = [], [], [], []
    L_pitchVel, L_yawVel, L_surgeVel, L_rollVel = [], [], [], []
    R_pitchVel, R_yawVel, R_surgeVel, R_rollVel = [], [], [], []
    L_pitch, L_yaw, L_surge, L_roll = [], [], [], []
    R_pitch, R_yaw, R_surge, R_roll = [], [], [], []
    R_x, R_y, R_z = [], [], []
    L_x, L_y, L_z = [], [], []
    L_motion, R_motion = [], []

    for i in cleaned_data:
        time.append(i[0])
        force.append(i[1])

        L_pitchAcc.append(i[2])
        L_yawAcc.append(i[3])
        R_pitchAcc.append(i[4])
        R_yawAcc.append(i[5])
        L_surgeAcc.append(i[6])
        L_rollAcc.append(i[7])
        R_surgeAcc.append(i[8])
        R_rollAcc.append(i[9])

        L_pitchVel.append(i[10])
        L_yawVel.append(i[11])
        R_pitchVel.append(i[12])
        R_yawVel.append(i[13])
        L_surgeVel.append(i[14])
        L_rollVel.append(i[15])
        R_surgeVel.append(i[16])
        R_rollVel.append(i[17])

        L_pitch.append(i[18])
        L_yaw.append(i[19])
        R_pitch.append(i[20])
        R_yaw.append(i[21])
        L_surge.append(i[22])
        L_roll.append(i[23])
        R_surge.append(i[24])
        R_roll.append(i[25])

        R_x.append(i[26])
        R_y.append(i[27])
        R_z.append(i[28])

        L_x.append(i[29])
        L_y.append(i[30])
        L_z.append(i[31])

        L_motion.append(i[32])
        R_motion.append(i[33])

    temp_df = pd.DataFrame({
        'Time': time,
        'Force': force,
        'L_pitchAcc': L_pitchAcc,
        'L_yawAcc': L_yawAcc,
        'R_pitchAcc': R_pitchAcc,
        'R_yawAcc': R_yawAcc,
        'L_surgeAcc': L_surgeAcc,
        'L_rollAcc': L_rollAcc,
        'R_surgeAcc': R_surgeAcc,
        'R_rollAcc': R_rollAcc,
        'L_pitchVel': L_pitchVel,
        'L_yawVel': L_yawVel,
        'R_pitchVel': R_pitchVel,
        'R_yawVel': R_yawVel,
        'L_surgeVel': L_surgeVel,
        'L_rollVel': L_rollVel,
        'R_surgeVel': R_surgeVel,
        'R_rollVel': R_rollVel,
        'L_pitch': L_pitch,
        'L_yaw': L_yaw,
        'R_pitch': R_pitch,
        'R_yaw': R_yaw,
        'L_surge': L_surge,
        'L_roll': L_roll,
        'R_surge': R_surge,
        'R_roll': R_roll,
        'R_x': R_x,
        'R_y': R_y,
        'R_z': R_z,
        'L_x': L_x,
        'L_y': L_y,
        'L_z': L_z,
        'L_motion': L_motion,
        'R_motion': R_motion
    })

    if not temp_df.empty:
        file_name = get_next_filename()
        temp_df.to_csv(file_name)
        messagebox.showinfo(title="Success", message="Sensor Data Have Been Processed and Saved")
    else:
        messagebox.showwarning(title="Warning", message="No Valid Sensor Data to Save!")


if __name__ == '__main__':
    cleaning_sensor_data()
