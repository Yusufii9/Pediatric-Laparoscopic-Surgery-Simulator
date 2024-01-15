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

warnings.filterwarnings('ignore')


class Task1PerformanceAnalyzer:
    def __init__(self, reference_path, user_path, ref_video_path, user_video_path):
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
        # Align the data and calculate DTW distances
        dtw_distances = {signal: self.dtw_distance(self.reference_data[signal], self.user_data[signal]) for signal
                         in self.signal_columns}
        aligned_data = {}

        for signal in self.signal_names:
            ref_signal = self.reference_data[signal].values.reshape(-1, 1)
            user_signal = self.user_data[signal].values.reshape(-1, 1)

            distance, path = fastdtw(ref_signal, user_signal, dist=euclidean)
            print(f'{signal}: {distance}')

            aligned_ref = [ref_signal[i] for i, j in path]
            aligned_user = [user_signal[j] for i, j in path]

            aligned_data[f'Ref_task1_{signal}'] = aligned_ref
            aligned_data[f'User_task1_{signal}'] = aligned_user

        df_aligned = pd.DataFrame.from_dict({k: pd.Series(v) for k, v in aligned_data.items()})
        df_aligned.to_csv('aligned_signals_task1.csv', index=True)
        return df_aligned

    def normalize_and_process_windows(self, window_size_seconds=5):
        # Normalize the data and process it in windows
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
        window_size = round(window_size_seconds * sampling_rate)
        print(f"Window Size: {window_size}")

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

        print(f"Mean DTW Distance: {mean_dtw}")
        print(f"Max DTW Distance: {max_dtw}")
        print(f"Min DTW Distance: {min_dtw}")
        print(f"Standard Deviation: {std_dtw}")

        good_performance = (0.0, mean_dtw)
        moderate = (mean_dtw, mean_dtw + std_dtw)
        self.far_away = (mean_dtw + std_dtw, float('inf'))

        print(good_performance, moderate, self.far_away)

    def process_videos(self):
        read_normalized_data = pd.read_csv("normalized_data_task1.csv")

        ref_start_timestamps = []
        ref_end_timestamps = []
        user_start_timestamps = []
        user_end_timestamps = []

        for i in range(len(self.get_inf_df)):
            if self.get_inf_df["DTW Distance"][i] > self.far_away[0]:

                info_df_data = {'Start Index': self.get_inf_df["Start Index"][i],
                                'End Index': self.get_inf_df["End Index"][i],
                                'User Signal': self.get_inf_df["User Signal"][i],
                                'Ref Signal': self.get_inf_df["Ref Signal"][i],
                                'DTW Distance (Weak Performance)': self.get_inf_df["DTW Distance"][i]}
                self.info_df = pd.concat([self.info_df, pd.DataFrame([info_df_data])], ignore_index=True)

                ref_start_time = read_normalized_data["Ref_task1_Time"].loc[self.get_inf_df.loc[i][0]]  # start index
                ref_end_time = read_normalized_data["Ref_task1_Time"].loc[self.get_inf_df.loc[i][1]]  # end index
                user_start_time = read_normalized_data["User_task1_Time"].loc[self.get_inf_df.loc[i][0]]
                user_end_time = read_normalized_data["User_task1_Time"].loc[self.get_inf_df.loc[i][1]]

                ref_start_timestamps.append(ref_start_time)
                ref_end_timestamps.append(ref_end_time)
                user_start_timestamps.append(user_start_time)
                user_end_timestamps.append(user_end_time)

        self.info_df.to_csv("task1_weak_signal_performance.csv")

        ref_start_timestamps = sorted(list(set(ref_start_timestamps)))
        print(f"Ref start timestamps: {ref_start_timestamps}")
        ref_end_timestamps = sorted(list(set(ref_end_timestamps)))
        print(f"Ref end timestamps: {ref_end_timestamps}")
        user_start_timestamps = sorted(list(set(user_start_timestamps)))
        print(f"User start timestamps: {user_start_timestamps}")
        user_end_timestamps = sorted(list(set(user_end_timestamps)))
        print(f"User end timestamps: {user_end_timestamps}")

        user_clips = []
        ref_clips = []

        min_index_length = min(len(user_start_timestamps), len(user_end_timestamps), len(ref_start_timestamps),
                               len(ref_end_timestamps))
        print(f"Number of combined clips: {min_index_length}")

        for i in range(min_index_length):
            user_start_seconds = user_start_timestamps[i]
            user_end_seconds = user_end_timestamps[i]
            user_target_name = f"Group{i}_Peaks_in_Youssef.mp4"
            ffmpeg_extract_subclip("Youssef.mp4", user_start_seconds, user_end_seconds, targetname=user_target_name)
            user_clip = VideoFileClip(user_target_name)
            user_text = TextClip("You", font="Amiri-bold", fontsize=50, color='white').set_duration(user_clip.duration)\
                .margin(top=40, left=40, opacity=0).set_position(("left", "top"))
            user_clip_with_text = CompositeVideoClip([user_clip, user_text])
            user_clips.append(user_clip_with_text)

            ref_start_seconds = ref_start_timestamps[i]
            ref_end_seconds = ref_end_timestamps[i]
            ref_target_name = f"Group{i}_Peaks_in_Atallah.mp4"
            ffmpeg_extract_subclip("Atallah.mp4", ref_start_seconds, ref_end_seconds, targetname=ref_target_name)
            ref_clip = VideoFileClip(ref_target_name)
            ref_text = TextClip("Expert", font="Amiri-bold", fontsize=50, color='white').set_duration(
                ref_clip.duration).margin(top=40, right=20, opacity=0).set_position(("right", "top"))
            ref_clip_with_text = CompositeVideoClip([ref_clip, ref_text])
            ref_clips.append(ref_clip_with_text)

        # Combine and save each pair of user and ref clips separately, remind yourself
        for i, (user_clip, ref_clip) in enumerate(zip(user_clips, ref_clips)):
            combined_clip = clips_array([[user_clip, ref_clip]])
            combined_clip.write_videofile(f"Feedback clips/Combined_Clip_{i}.mp4")


if __name__ == "__main__":
    analysis = Task1PerformanceAnalyzer('Demo_Reference_Seg1.csv', 'Demo_user_Seg1.csv', 'Atallah.mp4',
                                        'Youssef.mp4')
    aligned_data_var = analysis.align_data()
    analysis.normalize_and_process_windows()
    analysis.process_videos()
