import datetime
import tkinter as tk
from tkVideoPlayer import TkinterVideo
import os
import time


class VideoPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tkinter Media Player")

        # self.first_video = "Feedback clips/test_new_video.mp4"
        self.path = "Feedback clips"
        self.video_directory = self.path
        print(self.video_directory)
        folder_path = self.path
        files = [f for f in os.listdir(folder_path) if
                 not f.startswith('.') and os.path.isfile(os.path.join(folder_path, f))]
        files.sort()
        self.first_video = files[0] if files else None
        print(self.first_video)
        print("1")

        self.vid_player = TkinterVideo(scaled=True, master=root)
        self.vid_player.pack(expand=True, fill="both")

        self.play_pause_btn = tk.Button(root, text="Play", command=self.play_pause)
        self.play_pause_btn.pack()

        self.skip_minus_5sec = tk.Button(root, text="Skip -5 sec", command=lambda: self.skip(-5))
        self.skip_minus_5sec.pack(side="left")

        self.start_time = tk.Label(root, text=str(datetime.timedelta(seconds=0)))
        self.start_time.pack(side="left")

        self.progress_value = tk.IntVar(root)

        self.progress_slider = tk.Scale(root, variable=self.progress_value, from_=0, to=0, orient="horizontal",
                                        command=self.seek)
        self.progress_slider.pack(side="left", fill="x", expand=True)

        self.end_time = tk.Label(root, text=str(datetime.timedelta(seconds=0)))
        self.end_time.pack(side="left")

        self.vid_player.bind("<<Duration>>", self.update_duration)
        self.vid_player.bind("<<SecondChanged>>", self.update_scale)
        self.vid_player.bind("<<Ended>>", self.video_ended)

        self.skip_plus_5sec = tk.Button(root, text="Skip +5 sec", command=lambda: self.skip(5))
        self.skip_plus_5sec.pack(side="left")

        self.next_clip_btn = tk.Button(root, text="Next Clip", command=self.find_next_video)
        self.next_clip_btn.pack(side="left")

        self.load_video()

        # self.video_directory = os.path.dirname(self.first_video)
        # self.video_directory = self.path
        # print(self.video_directory)
        self.video_files = sorted([file for file in os.listdir(self.video_directory) if file.endswith('.mp4')])
        print(self.video_files)

    def load_video(self):
        video_path = os.path.join(self.video_directory, self.first_video)
        self.vid_player.load(video_path)
        self.progress_slider.config(to=0, from_=0)
        self.play_pause_btn["text"] = "Play"
        self.progress_value.set(0)

    def update_duration(self, event):
        duration = self.vid_player.video_info()["duration"]
        self.end_time["text"] = str(datetime.timedelta(seconds=duration))
        self.progress_slider["to"] = duration

    def update_scale(self, event):
        self.progress_value.set(self.vid_player.current_duration())

    def seek(self, value):
        self.vid_player.seek(int(value))

    def skip(self, value):
        self.vid_player.seek(int(self.progress_slider.get()) + value)
        self.progress_value.set(self.progress_slider.get() + value)

    def play_pause(self):
        if self.vid_player.is_paused():
            self.vid_player.play()
            self.play_pause_btn["text"] = "Pause"
        else:
            self.vid_player.pause()
            self.play_pause_btn["text"] = "Play"

    def find_next_video(self):
        try:
            # If the video is paused, play it briefly before stopping
            if self.vid_player.is_paused():
                self.vid_player.play()
                self.root.after(100, self.vid_player.stop)  # Stop the video after a short delay
            else:
                self.vid_player.stop()

            # Allow a short time for the player to update its state
            self.root.after(200)

            # Move to the next video
            current_index = self.video_files.index(os.path.basename(self.first_video))
            next_index = (current_index + 1) % len(self.video_files)
            next_video_path = os.path.join(self.video_directory, self.video_files[next_index])

            # Load the next video
            print("Loading next video:", next_video_path)
            self.vid_player.load(next_video_path)
            self.first_video = next_video_path  # Update the current video path

            # Reset and update UI elements
            self.play_pause_btn["text"] = "Play"
            self.progress_slider.set(0)
            self.progress_value.set(0)
            self.update_duration(None)

        except Exception as e:
            print("Error occurred:", e)

    def video_ended(self, event):
        self.progress_slider.set(self.progress_slider["to"])
        self.play_pause_btn["text"] = "Play"
        self.progress_slider.set(0)


if __name__ == "__main__":
    root = tk.Tk()
    VideoPlayerApp(root)
    root.mainloop()
