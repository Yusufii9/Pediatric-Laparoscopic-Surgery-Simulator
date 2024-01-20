import os
import pandas as pd
import numpy as np
import ast
import warnings
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw
from dtaidistance import dtw
from sklearn.preprocessing import MinMaxScaler
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip, clips_array, TextClip, CompositeVideoClip
from user_task2_evaluation_Testing import Task2PerformanceAnalyzer
from user_task3_evaluation_Testing import Task3PerformanceAnalyzer

warnings.filterwarnings('ignore')


class Task1PerformanceAnalyzer:
    def __init__(self, reference_path, user_path, ref_video_path, user_video_path):
        self.alignment_paths = None
        self.far_away = None
        self.get_inf_df = None
        self.reference_path = reference_path
        self.user_path = user_path
        self.ref_video_path = ref_video_path
        self.user_video_path = user_video_path
        self.signal_columns = None
        self.signal_names = None
        self.reference_data = None
        self.user_data = None
        self.normalized_data = None
        self.dtw_distances = []
        self.load_data()
        self.columns = ['Start Index', 'End Index', 'User Signal', 'Ref Signal', 'DTW Distance (Weak Performance)']
        self.info_df = pd.DataFrame(columns=self.columns)

    def load_data(self):
        self.reference_data = pd.read_csv(self.reference_path)
        self.user_data = pd.read_csv(self.user_path)
        self.reference_data.drop(columns=['Unnamed: 0', 'Unnamed: 0.1'], inplace=True)
        self.user_data.drop(columns=['Unnamed: 0', 'Unnamed: 0.1'], inplace=True)
        self.signal_columns = self.reference_data.columns[:26]  # Adjust if necessary
        self.signal_names = [signal for signal in self.signal_columns]

    @staticmethod
    def dtw_distance(series1, series2):
        """
            Computes Dynamic Time Warping (DTW) distance mathematically between two time series.

            :param series1: First time series
            :param series2: Second time series
            :return: DTW distance
            """
        n, m = len(series1), len(series2)
        dtw_matrix = np.zeros((n + 1, m + 1))

        dtw_matrix[0, :] = np.inf
        dtw_matrix[:, 0] = np.inf
        dtw_matrix[0, 0] = 0

        for i in range(1, n + 1):
            for j in range(1, m + 1):
                cost = abs(series1[i - 1] - series2[j - 1])
                last_min = np.min([dtw_matrix[i - 1, j], dtw_matrix[i, j - 1], dtw_matrix[i - 1, j - 1]])
                dtw_matrix[i, j] = cost + last_min

        return dtw_matrix[n, m]

    @staticmethod
    def string_to_float(string):
        if pd.isnull(string):
            return np.nan
        return float(ast.literal_eval(string)[0])

    def align_data(self):
        dtw_distances = {signal: self.dtw_distance(self.reference_data[signal], self.user_data[signal]) for signal
                         in self.signal_columns}
        aligned_data = {}
        self.alignment_paths = {}  # Store alignment paths for each signal

        for signal in self.signal_names:
            ref_signal = self.reference_data[signal].values.reshape(-1, 1)
            user_signal = self.user_data[signal].values.reshape(-1, 1)

            distance, path = fastdtw(ref_signal, user_signal, dist=euclidean)
            print(f'{signal}: {distance}')
            self.alignment_paths[signal] = path

            aligned_ref = [ref_signal[i] for i, j in path]
            aligned_user = [user_signal[j] for i, j in path]

            aligned_data[f'Ref_task1_{signal}'] = aligned_ref
            aligned_data[f'User_task1_{signal}'] = aligned_user

        df_aligned = pd.DataFrame.from_dict({k: pd.Series(v) for k, v in aligned_data.items()})
        df_aligned.to_csv('aligned_signals_task1.csv', index=True)
        return df_aligned

    def map_aligned_timestamps_to_original(self):
        if self.reference_data is None or self.user_data is None:
            self.load_data()

        aligned_data = pd.read_csv('aligned_signals_task1.csv')
        aligned_data.drop(columns='Unnamed: 0', inplace=True)

        original_timestamps = pd.DataFrame(index=aligned_data.index)

        for signal in self.signal_names:
            path = self.alignment_paths[signal]

            # Map indices to original timestamps
            ref_times = [self.reference_data['Time'][i] for i, j in path]
            user_times = [self.user_data['Time'][j] for i, j in path]

            # Ensure the lengths match with the aligned data
            min_len = min(len(ref_times), len(user_times), len(aligned_data))
            original_timestamps[f'Ref_task1_{signal}_Time'] = pd.Series(ref_times[:min_len])
            original_timestamps[f'User_task1_{signal}_Time'] = pd.Series(user_times[:min_len])

        original_timestamps.to_csv('original_timestamps_task1.csv', index=False)
        return original_timestamps

    def normalize_and_process_windows(self, window_size_seconds=10):
        data = pd.read_csv('aligned_signals_task1.csv')
        data.drop(columns="Unnamed: 0", inplace=True)

        for signal in self.signal_names:
            data[f'Ref_task1_{signal}'] = data[f'Ref_task1_{signal}'].apply(self.string_to_float)
            data[f'User_task1_{signal}'] = data[f'User_task1_{signal}'].apply(self.string_to_float)

        user_exclude_column = 'User_task1_Time'
        ref_exclude_column = 'Ref_task1_Time'
        columns = [col for col in data.columns if col not in [user_exclude_column, ref_exclude_column]]

        # Calculate sampling rate
        ref_time = abs(self.reference_data['Time'].max() - self.reference_data['Time'].min())
        user_time = abs(self.user_data['Time'].max() - self.user_data['Time'].min())
        num_samples_ref = len(self.reference_data['Time'])
        avg_time_between_samples_ref = ref_time / (num_samples_ref - 1)
        sampling_rate_ref = 1 / avg_time_between_samples_ref

        num_samples_user = len(self.user_data['Time'])
        avg_time_between_samples_user = user_time / (num_samples_user - 1)
        sampling_rate_user = 1 / avg_time_between_samples_user

        sampling_rate = max(sampling_rate_ref, sampling_rate_user)
        print(sampling_rate)
        window_size = round(window_size_seconds * sampling_rate)
        print(f"Task 1 Window Size: {window_size}")

        scaler = MinMaxScaler()
        normalized_windows = []

        for start in range(0, len(data.dropna()), window_size):
            end = min(start + window_size, len(data.dropna()))
            window_data = data.iloc[start:end]
            normalized_data = scaler.fit_transform(window_data[columns])
            normalized_window = pd.DataFrame(normalized_data, columns=window_data[columns].columns,
                                             index=window_data.index)
            normalized_windows.append(normalized_window)

            for user_col in [col for col in columns if col.startswith('User_')]:
                ref_col = user_col.replace('User', 'Ref')
                if ref_col in normalized_window.columns:
                    distance = dtw.distance(normalized_window[user_col].values, normalized_window[ref_col].values)
                    if end == len(data.dropna()):
                        self.dtw_distances.append((start, end-1, user_col, ref_col, distance))
                    else:
                        self.dtw_distances.append((start, end, user_col, ref_col, distance))

        self.normalized_data = pd.concat(normalized_windows).round(3)
        self.normalized_data[user_exclude_column] = data[user_exclude_column]
        self.normalized_data[ref_exclude_column] = data[ref_exclude_column]
        self.normalized_data.dropna().to_csv("normalized_data_task1.csv")

        self.get_inf_df = pd.DataFrame(self.dtw_distances, columns=['Start Index', 'End Index', 'User Signal',
                                                                    'Ref Signal', 'DTW Distance'])
        self.get_inf_df = self.get_inf_df.dropna()
        self.get_inf_df.to_csv("infoTest_task1.csv")

        mean_dtw = self.get_inf_df["DTW Distance"].mean()
        max_dtw = self.get_inf_df["DTW Distance"].max()
        min_dtw = self.get_inf_df["DTW Distance"].min()
        std_dtw = self.get_inf_df["DTW Distance"].std()

        print(f"Task 1 Mean DTW Distance: {mean_dtw}")
        print(f"Task 1 Max DTW Distance: {max_dtw}")
        print(f"Task 1 Min DTW Distance: {min_dtw}")
        print(f"Task 1 Standard Deviation: {std_dtw}")

        good_performance = (0.0, mean_dtw)
        moderate = (mean_dtw, mean_dtw + std_dtw)
        self.far_away = (mean_dtw + std_dtw, float('inf'))

        print(good_performance, moderate, self.far_away)

    def process_videos(self):
        original_timestamps = self.map_aligned_timestamps_to_original()

        clip_time_boundaries_list = []

        for i in range(len(self.get_inf_df)):
            if self.get_inf_df["DTW Distance"][i] > self.far_away[0]:
                info_df_data = {'Start Index': self.get_inf_df["Start Index"][i],
                                'End Index': self.get_inf_df["End Index"][i],
                                'User Signal': self.get_inf_df["User Signal"][i],
                                'Ref Signal': self.get_inf_df["Ref Signal"][i],
                                'DTW Distance (Weak Performance)': self.get_inf_df["DTW Distance"][i]}
                self.info_df = pd.concat([self.info_df, pd.DataFrame([info_df_data])], ignore_index=True)

                ref_signal = self.get_inf_df["Ref Signal"][i]
                user_signal = self.get_inf_df["User Signal"][i]
                ref_start_time = original_timestamps[f"{ref_signal}_Time"].iloc[
                    self.get_inf_df.loc[i][0]]  # start index
                ref_end_time = original_timestamps[f"{ref_signal}_Time"].iloc[self.get_inf_df.loc[i][1]]  # end index
                user_start_time = original_timestamps[f"{user_signal}_Time"].iloc[self.get_inf_df.loc[i][0]]
                user_end_time = original_timestamps[f"{user_signal}_Time"].iloc[self.get_inf_df.loc[i][1]]

                clip_time_boundaries_list.append(pd.DataFrame({
                    'Start Index': [self.get_inf_df["Start Index"][i]],
                    'End Index': [self.get_inf_df["End Index"][i]],
                    'Ref Start Time': [ref_start_time],
                    'Ref End Time': [ref_end_time],
                    'User Start Time': [user_start_time],
                    'User End Time': [user_end_time]
                }))

        clip_time_boundaries = pd.concat(clip_time_boundaries_list, ignore_index=True)
        clip_time_boundaries.to_csv("task1_clip_time_boundaries.csv")
        self.info_df.to_csv("task1_weak_signal_performance.csv")

        grouped_clip_time_boundaries = clip_time_boundaries.groupby(['Start Index', 'End Index']).agg({
            'Ref Start Time': 'min',
            'Ref End Time': 'max',
            'User Start Time': 'min',
            'User End Time': 'max'
        }).reset_index()
        grouped_clip_time_boundaries.to_csv("task1_grouped_clip_time_boundaries.csv")

        print(f"Task 1 Ref start timestamps: {grouped_clip_time_boundaries['Ref Start Time'].tolist()}")
        print(f"Task 1 Ref end timestamps: {grouped_clip_time_boundaries['Ref End Time'].tolist()}")
        print(f"Task 1 User start timestamps: {grouped_clip_time_boundaries['User Start Time'].tolist()}")
        print(f"Task 1 User end timestamps: {grouped_clip_time_boundaries['User End Time'].tolist()}")
        print(f"Task 1 Number of proposed combined clips: {len(grouped_clip_time_boundaries)}")

        for index, row in grouped_clip_time_boundaries.iterrows():
            ref_start_seconds = row['Ref Start Time']
            ref_end_seconds = row['Ref End Time']
            user_start_seconds = row['User Start Time']
            user_end_seconds = row['User End Time']

            if (ref_start_seconds != ref_end_seconds) and (user_start_seconds != user_end_seconds):
                user_target_name = f"Task1_Group{index}_User_Clip.mp4"
                ffmpeg_extract_subclip(self.user_video_path, user_start_seconds, user_end_seconds,
                                       targetname=user_target_name)
                user_clip = VideoFileClip(user_target_name)
                # user_text = TextClip("User (You)", fontsize=70, color='white').set_duration(user_clip.duration).
                # set_position(
                #     'bottom')
                user_text = TextClip("User (You)", font="Amiri-bold", fontsize=50, color='white').set_duration(
                    user_clip.duration) \
                    .margin(top=40, left=40, opacity=0).set_position(("left", "top"))
                user_clip_with_text = CompositeVideoClip([user_clip, user_text])

                ref_target_name = f"Task1_Group{index}_Ref_Clip.mp4"
                ffmpeg_extract_subclip(self.ref_video_path, ref_start_seconds, ref_end_seconds,
                                       targetname=ref_target_name)
                ref_clip = VideoFileClip(ref_target_name)
                # ref_text = TextClip("Expert", fontsize=70, color='white').set_duration(ref_clip.duration).
                # set_position(
                #     'bottom')
                ref_text = TextClip("Expert", font="Amiri-bold", fontsize=50, color='white').set_duration(
                    ref_clip.duration).margin(top=40, right=20, opacity=0).set_position(("right", "top"))
                ref_clip_with_text = CompositeVideoClip([ref_clip, ref_text])

                final_clip = clips_array([[user_clip_with_text, ref_clip_with_text]])
                final_clip_name = f"Task 1 Feedback clips/Task1_Final_Clip_{index}.mp4"
                final_clip.write_videofile(final_clip_name)

        directory = 'Task 1 Feedback clips'
        mp4_files = [f for f in os.listdir(directory) if f.endswith('.mp4')]
        print(f"Task 1 Number of actual combined clips: {len(mp4_files)}")


if __name__ == "__main__":
    analysis1 = Task1PerformanceAnalyzer('Demo_Reference_Seg1.csv', 'Demo_user_Seg1.csv', 'Youssef.mp4',
                                        'Atallah.mp4')
    aligned_data_var1 = analysis1.align_data()
    analysis1.normalize_and_process_windows()
    analysis1.process_videos()

    analysis2 = Task2PerformanceAnalyzer('Demo_Reference_Seg2.csv', 'Demo_user_Seg2.csv', 'Youssef.mp4',
                                         'Atallah.mp4')
    aligned_data_var2 = analysis2.align_data()
    analysis2.normalize_and_process_windows()
    analysis2.process_videos()

    analysis3 = Task3PerformanceAnalyzer('Demo_Reference_Seg3.csv', 'Demo_user_Seg3.csv', 'Youssef.mp4',
                                         'Atallah.mp4')
    aligned_data_var3 = analysis3.align_data()
    analysis3.normalize_and_process_windows()
    analysis3.process_videos()
