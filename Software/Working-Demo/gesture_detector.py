import os
import cv2
import numpy as np
import tensorflow as tf
import csv
from object_detection.utils import label_map_util
from object_detection.utils import config_util
from object_detection.builders import model_builder


class GestureDetector:
    def __init__(self, model_name, video_path, labelmap_path, pipeline_config_path, checkpoint_path, csv_path):
        self.model_name = model_name
        self.video_path = video_path
        self.labelmap_path = labelmap_path
        self.pipeline_config_path = pipeline_config_path
        self.checkpoint_path = checkpoint_path
        self.csv_path = csv_path
        self.load_model()
        self.category_index = label_map_util.create_category_index_from_labelmap(self.labelmap_path, use_display_name=True)

    def load_model(self):
        configs = config_util.get_configs_from_pipeline_file(self.pipeline_config_path)
        self.detection_model = model_builder.build(model_config=configs['model'], is_training=False)
        ckpt = tf.compat.v2.train.Checkpoint(model=self.detection_model)
        ckpt.restore(os.path.join(self.checkpoint_path, 'ckpt-27')).expect_partial()

    def detect_fn(self, image):
        image, shapes = self.detection_model.preprocess(image)
        prediction_dict = self.detection_model.predict(image, shapes)
        detections = self.detection_model.postprocess(prediction_dict, shapes)
        return detections

    def process_video(self):
        # Open the video file for initial frame count
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            print("Error opening video file")
            return

        fps = cap.get(cv2.CAP_PROP_FPS)

        # Manually count frames
        frame_count = 0
        while True:
            ret, _ = cap.read()
            if not ret:
                break
            frame_count += 1

        cap.release()  # Release the video capture object after counting frames

        if frame_count == 0:
            print("No frames found in the video")
            return

        print(f"Video opened with FPS: {fps}, Total Frames: {frame_count}")

        # Re-open the video file for processing
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            print("Error reopening video file")
            return

        current_gestures = {'RG': None, 'LG': None}
        start_time = {'RG': None, 'LG': None}

        with open(self.csv_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Time Start', 'Time Stop', 'Right Gesture', 'Left Gesture'])

            for frame_number in range(frame_count):
                ret, frame = cap.read()
                if not ret:
                    print(f"End of video reached prematurely at frame {frame_number}.")
                    break

                print(f"Processing frame {frame_number + 1}/{frame_count}")
                input_tensor = tf.convert_to_tensor([np.asarray(frame)], dtype=tf.float32)
                detections = self.detect_fn(input_tensor)
                self.process_detections(detections, writer, frame_number, fps, current_gestures, start_time)

            self.record_last_gestures(writer, frame_count, fps, current_gestures, start_time)

        cap.release()
        cv2.destroyAllWindows()

    def process_detections(self, detections, writer, frame_number, fps, current_gestures, start_time):
        num_detections = int(detections.pop('num_detections'))
        detections = {key: value[0, :num_detections].numpy() for key, value in detections.items()}
        detections['num_detections'] = num_detections
        detections['detection_classes'] = detections['detection_classes'].astype(np.int64)

        highest_score = {'RG': (0, None), 'LG': (0, None)}

        for i in range(num_detections):
            score = detections['detection_scores'][i]
            class_id = detections['detection_classes'][i]
            if class_id in self.category_index and score >= 0.3:
                gesture = self.category_index[class_id]['name']
                if gesture.startswith('RG') and score > highest_score['RG'][0]:
                    highest_score['RG'] = (score, gesture)
                elif gesture.startswith('LG') and score > highest_score['LG'][0]:
                    highest_score['LG'] = (score, gesture)

        for side in ['RG', 'LG']:
            gesture = highest_score[side][1] if highest_score[side][1] else side + '0'
            if gesture != current_gestures[side]:
                if current_gestures[side]:
                    end_time = frame_number / fps
                    writer.writerow([start_time[side], end_time, current_gestures['RG'], current_gestures['LG']])
                    start_time[side] = end_time
                current_gestures[side] = gesture

    def record_last_gestures(self, writer, frame_number, fps, current_gestures, start_time):
        end_time = frame_number / fps
        for side in ['RG', 'LG']:
            if current_gestures[side]:
                writer.writerow([start_time[side], end_time, current_gestures['RG'], current_gestures['LG']])


if __name__ == "__main__":
    # Example usage
    gesture_detector = GestureDetector(
        model_name='my_ssd_mobnet',
        video_path='/Users/esraa/Gesture Reconigtion/Atallah.avi',
        labelmap_path='/Users/esraa/Gesture Reconigtion/annotations/label_map.pbtxt',
        pipeline_config_path='/Users/esraa/Gesture Reconigtion/my_ssd_mobnet/export/pipeline.config',
        checkpoint_path='/Users/esraa/Gesture Reconigtion/my_ssd_mobnet',
        csv_path='/Users/esraa/Gesture Reconigtion/output.csv'
    )
    gesture_detector.process_video()
