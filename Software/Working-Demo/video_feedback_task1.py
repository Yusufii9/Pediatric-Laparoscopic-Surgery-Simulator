import datetime
import tkinter as tk
from tkVideoPlayer import TkinterVideo


class VideoPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tkinter Media Player")

        self.predefined_video_path = "test_new_video.mp4"

        self.vid_player = TkinterVideo(scaled=True, master=root)
        self.vid_player.pack(expand=True, fill="both")

        self.play_pause_btn = tk.Button(root, text="Play", command=self.play_pause)
        self.play_pause_btn.pack()

        self.skip_minus_5sec = tk.Button(root, text="Skip -5 sec", command=lambda: self.skip(-5))
        self.skip_minus_5sec.pack(side="left")

        self.start_time = tk.Label(root, text=str(datetime.timedelta(seconds=0)))
        self.start_time.pack(side="left")

        self.progress_value = tk.IntVar(root)

        self.progress_slider = tk.Scale(root, variable=self.progress_value, from_=0, to=0, orient="horizontal", command=self.seek)
        self.progress_slider.pack(side="left", fill="x", expand=True)

        self.end_time = tk.Label(root, text=str(datetime.timedelta(seconds=0)))
        self.end_time.pack(side="left")

        self.vid_player.bind("<<Duration>>", self.update_duration)
        self.vid_player.bind("<<SecondChanged>>", self.update_scale)
        self.vid_player.bind("<<Ended>>", self.video_ended)

        self.skip_plus_5sec = tk.Button(root, text="Skip +5 sec", command=lambda: self.skip(5))
        self.skip_plus_5sec.pack(side="left")

        # Load the predefined video
        self.load_video()

    def load_video(self):
        self.vid_player.load(self.predefined_video_path)
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

    def video_ended(self, event):
        self.progress_slider.set(self.progress_slider["to"])
        self.play_pause_btn["text"] = "Play"
        self.progress_slider.set(0)


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoPlayerApp(root)
    root.mainloop()
