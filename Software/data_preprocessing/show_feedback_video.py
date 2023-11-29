import cv2


class VideoPlayer:
    def __init__(self, video_path):
        self.video_path = video_path
        self.cap = cv2.VideoCapture(self.video_path)
        self.paused = False

    def play_video(self):
        while True:
            if not self.paused:
                ret, frame = self.cap.read()
                if not ret:
                    break  # End of video
                cv2.imshow('Video', frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):  # Quit
                break
            elif key == ord('p'):  # Pause
                self.paused = not self.paused

        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    video_path = "test_task1.mp4"
    player = VideoPlayer(video_path)
    player.play_video()