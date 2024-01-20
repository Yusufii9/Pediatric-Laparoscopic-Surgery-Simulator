import pandas as pd
import warnings
from tkinter import filedialog

warnings.filterwarnings('ignore')


class DataSegmentation:
    def __init__(self):
        self.reference_file = 'CleanedSensorData_8.csv'
        self.user_file_path = filedialog.askopenfilename(title="Choose the CSV Converted Sensor Data File")  # choose 7
        self.labels_file = 'Demo Labelled Video.xlsx'

    def load_data(self):
        self.data_video_10 = pd.read_csv(self.reference_file)
        self.data_video_9 = pd.read_csv(self.user_file_path)
        self.labels_video_10 = pd.read_excel(self.labels_file, sheet_name='YM Trial one')
        self.labels_video_9 = pd.read_excel(self.labels_file, sheet_name='AM Trail one')

    def process_segments(self, data, labels):
        segments = []
        for idx, row in labels.iterrows():
            segment = data[(data['Time'] >= row['Time Start']) & (data['Time'] <= row['Time Stop'])]
            segments.append(segment)
        return segments

    def combine_and_save_segments(self, segments, filename_prefix, task_ranges):
        for task_num, (start, end) in enumerate(task_ranges, start=1):
            combined_segment = pd.concat(segments[start:end], axis=0)
            combined_segment.to_csv(f"{filename_prefix}_Seg{task_num}.csv")

    def run(self):
        self.load_data()
        reference_segments = self.process_segments(self.data_video_10, self.labels_video_10)
        user_segments = self.process_segments(self.data_video_9, self.labels_video_9)

        task_ranges = [(0, 9), (11, 20), (22, 32)]
        self.combine_and_save_segments(reference_segments, "Demo_Reference", task_ranges)
        self.combine_and_save_segments(user_segments, "Demo_user", task_ranges)


if __name__ == "__main__":
    processor = DataSegmentation()
    processor.run()
