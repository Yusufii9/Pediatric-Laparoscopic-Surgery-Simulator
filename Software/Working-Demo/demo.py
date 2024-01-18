import tkinter as tk
from tkinter import messagebox, filedialog, Toplevel

import cv2
import imageio
from PIL import Image, ImageTk
import pandas as pd
import os
import numpy as np
import time
import serial
import threading
#import matplotlib.pyplot as plt
#from matplotlib.widgets import Slider, CheckButtons
from cleaning_sensor_data import SensorDataCleaner
from seg_data_to_subtasks import DataSegmentation
from user_task1_evaluation_Testing import Task1PerformanceAnalyzer
from plot_user_aligned_subtasks import DataPlotter
from show_feedback_video import VideoPlayer
from itertools import cycle
from video_feedback_task1_Testing import Task1VideoPlayFeedback
from video_playback import VideoPlayback

if not dir("Feedback clips"):
    os.mkdir("Feedback clips")  # add exception handling
else:
    pass


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Video Application')

        # Get the screen width and height
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()

        # Set the window size to the maximum screen size
        self.geometry(f'{self.screen_width}x{self.screen_height}')
        self.resizable(False, False)
        self.configure(bg='black')
        self.video_name = "LapSim1.mkv"
        self.video = imageio.get_reader(self.video_name)
        self.canvas = tk.Canvas(self, width=self.screen_width, height=self.screen_height)
        self.bind('<ButtonPress-1>', self.mouse_down)
        self.bind('<ButtonRelease-1>', self.mouse_up)
        self.bind('<B1-Motion>', self.mouse_drag)
        # First, create the shadow with an offset (e.g., 2 pixels to the right and down)
        self.shadow_offset_x = 3
        self.shadow_offset_y = 3
        self.shadow_color = 'black'
        self.welcome_text = self.canvas.create_text(self.screen_width/2, self.screen_height/3 + 50, text='Welcome', font=('MS Sans Serif', 100), fill='black', tags=("overlay", "text",))
        #self.welcome_shadow = self.canvas.create_text(self.screen_width/2 + self.shadow_offset_x, self.screen_height/3 + self.shadow_offset_y,text="Welcome",font=('MS Sans Serif', 100), fill=self.shadow_color, tags=("shadow",))
        #self.rect = self.canvas.create_rectangle(self.screen_width/2 + 400, 700, self.screen_height/3 + 100, 100, fill="black")
        self.current_user = None
        self.back_button = None
        self.buttons = []
        self.base_directory = 'C:/Users/hudaa/PycharmProjects/pythonProject1/UserData'
        # Initialize the cycle of images
        self.image_paths = ["Slide2.png", "Slide3.png", "Slide4.png", "Slide5.png", "Slide6.png", "Slide7.png", "Slide8.png", "Slide9.png"]
        self.load_video()
        self.start_menu()
        self.canvas.pack()


    def create_user_folder(self, username):
        # Sanitize the username to prevent any invalid characters for folder names
        # This is important for security and compatibility of folder names
        safe_username = ''.join(c for c in username if c.isalnum() or c in (' ', '_')).rstrip()

        # Create the full path for the user's folder
        user_folder_path = os.path.join(self.base_directory, safe_username)

        # Check if the folder already exists, and if not, create it
        if not os.path.exists(user_folder_path):
            os.makedirs(user_folder_path)
            print(f"Folder created for user {safe_username} at {user_folder_path}")
        else:
            print(f"Folder already exists for user {safe_username} at {user_folder_path}")

        return user_folder_path
    def set_current_user(self, username):
        self.current_user = username
        #user_folder = self.create_user_folder(self.base_directory, self.current_user)

    def mouse_down(self, event):
        self.x, self.y = event.x, event.y

    def mouse_up(self, event):
        self.x, self.y = None, None

    def mouse_drag(self, event):
        if self.x and self.y:
            deltax = event.x - self.x
            deltay = event.y - self.y
            x0 = self.winfo_x() + deltax
            y0 = self.winfo_y() + deltay
            self.geometry(f"+{x0}+{y0}")

    def load_video(self):
        self.after(0, self.stream())

    def update_frame(self, frame_iterator):
        try:
            image = next(frame_iterator)
            resized_image = Image.fromarray(image).resize((self.winfo_screenwidth(), self.winfo_screenheight()),Image.Resampling.LANCZOS)  # Use the screen dimensions
            frame_image = ImageTk.PhotoImage(image=resized_image)
            if hasattr(self, 'canvas_image_id'):
                # Update the existing image object
                self.canvas.itemconfig(self.canvas_image_id, image=frame_image)
            else:
                # Create a new canvas image object and keep its ID
                self.canvas_image_id = self.canvas.create_image(
                    0, 0, anchor='nw', image=frame_image, tags=("video_frame",)
                )
                # Send this image to the back, so buttons/text stay on top
                self.canvas.tag_lower('video_frame')

            # Keep a reference to the image to prevent garbage-collection
            self.canvas.image = frame_image

            # Send this image to the back, so buttons/text stay on top
            self.canvas.tag_lower('video_frame')
            self.canvas.tag_raise('overlay')
            self.canvas.update_idletasks()

            # Schedule the next frame update
            self.after(33, self.update_frame, frame_iterator)  # For ~30fps, adjust as needed
        except StopIteration:
            # Handle the end of the video stream
            self.canvas.delete(self.canvas_image_id)  # Remove the video frame
            self.start_menu()  # Call start_menu or handle the video ending

    def stream(self):
        frame_iterator = iter(self.video.iter_data())
        self.update_frame(frame_iterator)

        #self.canvas.create_text(self.screen_width/3 + 20 + self.shadow_offset_x, (self.screen_height/4 - 20) + self.shadow_offset_y,text="Pediatric Laparoscopic Surgical Simulator",font=('Helvetica', 16), fill=self.shadow_color, tags=("shadow",))
        self.canvas.create_text(
            self.screen_width/3 + 20, self.screen_height/4 - 20,
            text="Pediatric Laparoscopic Surgical Simulator",
            font=('MS Sans Serif', 20), fill='black', tags=("overlay",)
        )

        if (self.current_user != None):
            self.canvas.create_text(
                800, 300,
                text="Welcome "+str(self.current_user),
                font=('MS Sans Serif', 18), fill='white', tags=("overlay",)
            )

    def raise_buttons_and_text(self):
        # Assuming all your buttons and text have a common tag like "overlay"
        self.canvas.tag_raise("overlay")

    def start_menu(self):
        self.remove_buttons()
        if self.back_button is not None:
            self.back_button.destroy()
            self.back_button = None  # Set back_button to None after destroying
        self.canvas.itemconfig(self.welcome_text, text='Welcome', font=('MS Sans Serif', 100))
        #self.canvas.itemconfig(self.welcome_shadow, text='Welcome', font=('MS Sans Serif', 100))
        self.add_button('Close', self.destroy, (self.screen_height/3 + 200))
        self.add_button('Start', self.user_window, (self.screen_height/3 + 150))
        self.canvas.tag_raise('overlay')
        self.canvas.update_idletasks()

    def add_button(self, text, command, y_position):
        button = tk.Button(self, text=text, command=command, anchor='center',
                           width=20, height=2, activebackground='#65e7ff',
                           background='#05d7ff', foreground='black',
                           activeforeground='black', highlightthickness=2,
                           highlightbackground='#05d7ff', highlightcolor='white',
                           border=0, cursor='hand1', font=('MS Sans Serif', 8, 'bold'), relief='raised')
        button_canvas = self.canvas.create_window(self.screen_width/2 - 30, y_position, anchor='nw', window=button,tags=("overlay",))
        # Add the button and its canvas item ID to the list
        self.buttons.append((button, button_canvas))

    def remove_buttons(self):
        # Iterate through the buttons and destroy them
        for button, button_canvas in self.buttons:
            button.destroy()
            self.canvas.delete(button_canvas)

        # Clear the list of buttons
        self.buttons = []

    def add_back_button(self, text, command):
        button = tk.Button(self, text=text, command=command, anchor='center',
                           width=50, height=2, activebackground='#65e7ff',
                           background='#05d7ff', foreground='black',
                           activeforeground='black', highlightthickness=2,
                           highlightbackground='#05d7ff', highlightcolor='white',
                           border=0, cursor='hand1', font=('MS Sans Serif', 8, 'bold'))
        self.canvas.create_window(0, 0, anchor='nw', window=button,tags=("overlay",))
        return button

    def test_train_window(self):
        self.remove_buttons()
        if self.back_button is not None:
            self.back_button.destroy()
            self.back_button = None  # Set back_button to None after destroying
        # Create text on the canvas for the welcome message and simulator name
        self.canvas.itemconfig(self.welcome_text, text='Task Menu')
        #self.canvas.itemconfig(self.welcome_shadow, text='Task Menu', font=('MS Sans Serif', 80))

        if (self.current_user != None):
            self.canvas.create_text(
                self.screen_width/2 + 20, self.screen_height-200,
                text="Welcome "+str(self.current_user),
                font=('MS Sans Serif', 18), fill='white', tags=("overlay",)
            )
            self.canvas.create_text((self.screen_width/2 + 20) + self.shadow_offset_x, self.screen_height - 200 + self.shadow_offset_y,text="Welcome "+str(self.current_user),font=('MS Sans Serif', 18), fill=self.shadow_color, tags=("shadow",))
            self.title('Video Application (User Logged In: '+str(self.current_user)+')')
        else:
            self.canvas.create_text(
                self.screen_width/2 + 30, self.screen_height-200,
                text="Welcome Guest",
                font=('MS Sans Serif', 24), fill='black', tags=("overlay",)
            )
            #self.canvas.create_text((self.screen_width/2 + 20) + self.shadow_offset_x, self.screen_height - 200 + self.shadow_offset_y,text="Welcome Guest",font=('MS Sans Serif', 18), fill=self.shadow_color, tags=("shadow",))
            self.title('Video Application (Guest User)')

        self.add_button('Feedback', self.show_feedback_popup, (self.screen_height/3 + 250))
        self.add_button('Examination', self.task_menu, (self.screen_height/3 + 200))
        self.add_button('Training', self.task_menu, (self.screen_height/3 + 150))



    def task_menu(self):
        self.remove_buttons()
        if self.back_button is not None:
            self.back_button.destroy()
            self.back_button = None  # Set back_button to None after destroying
        self.canvas.itemconfig(self.welcome_text, text='Task Menu', font=('MS Sans Serif', 80))
        #self.canvas.itemconfig(self.welcome_shadow, text='Task Menu', font=('MS Sans Serif', 80))
        self.add_button('Loop', self.destroy, (self.screen_height/3 + 250))
        self.add_button('Suturing', self.destroy, (self.screen_height/3 + 200))
        self.add_button('Peg Transfer', self.GUI_launch, (self.screen_height/3 + 150))
        self.back_button = self.add_back_button('Back', self.test_train_window)

    def user_window(self):
        self.remove_buttons()
        if self.back_button is not None:
            self.back_button.destroy()
            self.back_button = None  # Set back_button to None after destroying
        self.canvas.itemconfig(self.welcome_text, text='Login Menu', font=('MS Sans Serif', 80))
        #self.canvas.itemconfig(self.welcome_shadow, text='Login Menu', font=('MS Sans Serif', 80))
        self.add_button('Guest User', self.test_train_window, (self.screen_height/3 + 200))
        self.add_button('Login/Register', self.login_window, (self.screen_height/3 + 150))

    def on_user_logged_in(self):
        # Code to run when user is logged in
        # You could update the main application window or switch to another screen
        # For example, show a message or open another window
        username = self.current_user
        user_folder = self.create_user_folder(username)
        messagebox.showinfo("Login", "User has logged in.")
        self.test_train_window()
        # You could also call self.start_menu() or any other method to refresh the main window

    def login_window(self):
        login = LoginRegister(self, on_close=self.on_user_logged_in, on_login_success=self.set_current_user)
        login.grab_set()  # Makes the login window modal

    def on_GUI_close(self):
        self.test_train_window()

    def run_data_processing(self):
        self.current_image_index = 0

        # Function to update the image displayed in the top-level window
        def update_image():
            self.current_image_index = (self.current_image_index + 1) % len(self.image_paths)

            try:
                photo = tk.PhotoImage(file=self.image_paths[self.current_image_index])
                image_label.config(image=photo)
                image_label.image = photo
            except Exception as e:
                print(f"Failed to load image: {self.image_paths[self.current_image_index]} - Error: {e}")

            new_window.after(5000, update_image)

        def close_new_window():
                new_window.destroy()
                self.deiconify()

        def background_task():
            try:
                self.analysis = Task1PerformanceAnalyzer('Demo_Reference_Seg1.csv', 'Demo_user_Seg1.csv', 'Atallah.mp4',
                                                         'Youssef.mp4')
                self.aligned_data = self.analysis.align_data()
                self.analysis.normalize_and_process_windows()
                self.analysis.process_videos()
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
            finally:
                # Use after method to safely close the window from the main thread
                new_window.after(0, close_new_window)
        try:
            cleaner = SensorDataCleaner()
            cleaner.clean_sensor_data()
            processor = DataSegmentation()
            processor.run()
            messagebox.showinfo("Success", "Data processing completed successfully.")

            # Create a new window
            new_window = tk.Toplevel(self)
            new_window.title("Processing Video...")
            new_window.grab_set()
            self.withdraw()  # Show the window

            self.current_image_index = 0  # Start with the first image

            # Set up the initial image
            initial_photo = tk.PhotoImage(file=self.image_paths[self.current_image_index])
            image_label = tk.Label(new_window, image=initial_photo)
            image_label.pack()

            # Start the cycle of image updates
            update_image()

            # Start the background task in a separate thread
            background_thread = threading.Thread(target=background_task, daemon=True)
            background_thread.start()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def video_playback(self):
        video_window = tk.Toplevel()
        VideoPlayback(video_window)

    def feedback_menu(self):
        self.remove_buttons()
        if self.back_button is not None:
            self.back_button.destroy()
            self.back_button = None  # Set back_button to None after destroying
        self.canvas.itemconfig(self.welcome_text, text='Feedback Menu', font=('MS Sans Serif', 80))
        #self.canvas.itemconfig(self.welcome_shadow, text='Feedback Menu', font=('MS Sans Serif', 80))
        self.add_button('History', self.destroy, (self.screen_height/3 + 300))
        self.add_button('Video Playback', self.video_playback, (self.screen_height/3 + 250))
        self.add_button('Evaluation', self.evaluation_menu, (self.screen_height/3 + 200))
        self.add_button('Process Data', self.run_data_processing, (self.screen_height/3 + 150))
        self.back_button = self.add_back_button('Back', self.test_train_window)

    # Function to show the pop-up window
    def show_feedback_popup(self):
        messagebox.showinfo("Reminder", "Click 'Process Data' button before evaluating")
        self.feedback_menu()

    def evaluation_menu(self):
        self.remove_buttons()
        if self.back_button is not None:
            self.back_button.destroy()
            self.back_button = None  # Set back_button to None after destroying
        self.canvas.itemconfig(self.welcome_text, text='Evaluation Menu', font=('MS Sans Serif', 80))
        #self.canvas.itemconfig(self.welcome_shadow, text='Evaluation Menu', font=('MS Sans Serif', 80))
        self.add_button('Loop', self.destroy, (self.screen_height/3 + 250))
        self.add_button('Suturing', self.destroy, (self.screen_height/3 + 200))
        self.add_button('Peg Transfer', self.peg_evaluation_sub_menu, (self.screen_height/3 + 150))
        self.back_button = self.back_button = self.add_back_button('Back', self.feedback_menu)

    def peg_evaluation_sub_menu(self):
        self.remove_buttons()
        if self.back_button is not None:
            self.back_button.destroy()
            self.back_button = None  # Set back_button to None after destroying
        self.canvas.itemconfig(self.welcome_text, text='Evaluation Menu', font=('MS Sans Serif', 80))
        #self.canvas.itemconfig(self.welcome_shadow, text='Evaluation Menu', font=('MS Sans Serif', 80))
        self.add_button('Tool Trajectory', self.destroy, (self.screen_height/3 + 250))
        self.add_button('Visual Feedback', self.peg_sub_task_visual, (self.screen_height/3 + 200))
        self.add_button('Video Feedback', self.peg_sub_task_video, (self.screen_height/3 + 150))
        self.back_button = self.add_back_button('Back', self.evaluation_menu)

    def video_feedback(self):
        video_window = tk.Toplevel()
        Task1VideoPlayFeedback(video_window)

    def peg_sub_task_video(self):
        self.remove_buttons()
        if self.back_button is not None:
            self.back_button.destroy()
            self.back_button = None  # Set back_button to None after destroying
        self.canvas.itemconfig(self.welcome_text, text='Video Feedback', font=('MS Sans Serif', 80))
        #self.canvas.itemconfig(self.welcome_shadow, text='Video Feedback', font=('MS Sans Serif', 80))
        self.add_button('Subtask 3', self.destroy, (self.screen_height/3 + 250))
        self.add_button('Subtask 2', self.destroy, (self.screen_height/3 + 200))
        self.add_button('Subtask 1', self.video_feedback, (self.screen_height/3 + 150))
        self.back_button = self.add_back_button('Back', self.peg_evaluation_sub_menu)

    def visual_test(self):
        root = tk.Tk()
        root.withdraw()
        csv_file = filedialog.askopenfilename(title="Select the CSV Data File")
        root.destroy()

        plotter = DataPlotter()
        plotter.load_data(csv_file)
        plotter.plot_data()

    def peg_sub_task_visual(self):
        self.remove_buttons()
        if self.back_button is not None:
            self.back_button.destroy()
            self.back_button = None  # Set back_button to None after destroying
        self.canvas.itemconfig(self.welcome_text, text='Visual Feedback', font=('MS Sans Serif', 80))
        #self.canvas.itemconfig(self.welcome_shadow, text='Visual Menu', font=('MS Sans Serif', 80))
        self.add_button('Subtask 3', self.destroy, (self.screen_height/3 + 250))
        self.add_button('Subtask 2', self.destroy, (self.screen_height/3 + 200))
        self.add_button('Subtask 1', self.visual_test, (self.screen_height/3 + 150))
        self.back_button = self.add_back_button('Back', self.peg_evaluation_sub_menu)

    def GUI_launch(self):
        self.grab_set()
        peg_task = GUI(cameraID, font, windowName, self.winfo_screenwidth(), self.winfo_screenheight(), red_low, red_high, green_low, green_high, blue_low, blue_high, on_GUI_close=self.on_GUI_close)


class LoginRegister(tk.Toplevel):
        def __init__(self, master=None, on_close=None,on_login_success=None,**kw):
            super().__init__(master=master, **kw)
            self.on_close = on_close
            self.on_login_success = on_login_success
            self.title("Login/Register")
            self.geometry("400x300")
            self.lift(master)

            self.username_var = tk.StringVar()
            self.password_var = tk.StringVar()

            # This is a simplified login, you would want something more secure for a real system.
            self.user_data = {
                'Huda': 'password123'
            }

            self.create_widgets()

        def create_widgets(self):
            tk.Label(self, text="Enter details below", font=('Arial', 12)).pack()
            tk.Label(self, text="Username").pack()
            username_entry = tk.Entry(self, textvariable=self.username_var).pack()
            tk.Label(self, text="Password").pack()
            tk.Entry(self, textvariable=self.password_var, show='*').pack()
            tk.Button(self, text="Login", command=self.login_user).pack()
            tk.Button(self, text="Register", command=self.register_user).pack()

        def login_user(self):
            username = self.username_var.get()
            password = self.password_var.get()

            try:
                with open('user_data.txt', 'r') as file:
                    for line in file:
                        # Split on comma, and strip to remove whitespace and newlines
                        parts = [part.strip() for part in line.split(',', 1)]
                        if len(parts) == 2:
                            stored_username, stored_password = parts
                            if username == stored_username and password == stored_password:
                                messagebox.showinfo("Success", "Login Successful")
                                if self.on_login_success:  # Call the callback with the username
                                    self.on_login_success(username)
                                self.destroy()
                                if self.on_close:
                                    self.on_close()
                                return
                    # If no match found, display error
                    messagebox.showerror("Error", "Incorrect Username or Password")
            except FileNotFoundError:
                messagebox.showerror("Error", "User data file not found.")
            except Exception as e:
                messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

        def register_user(self):
            username = self.username_var.get()
            password = self.password_var.get()

            user_exists = False
            try:
                with open('user_data.txt', 'r+') as file:
                    users = file.readlines()
                    for line in users:
                        # Split on comma, and strip to remove whitespace and newlines
                        parts = [part.strip() for part in line.split(',', 1)]
                        if len(parts) == 2:
                            stored_username, _ = parts
                            if username == stored_username:
                                user_exists = True
                                break

                if user_exists:
                    messagebox.showerror("Error", "User already exists")
                else:
                    with open('user_data.txt', 'a') as file:
                        file.write(f"{username}, {password}\n")
                        messagebox.showinfo("Success", "User registered successfully")
                        if self.on_login_success:  # Call the callback with the username
                            self.on_login_success(username)
                        self.destroy()
                        if self.on_close:
                            self.on_close()
            except FileNotFoundError:
                with open('user_data.txt', 'w') as file:
                    file.write(f"{username}, {password}\n")
                    messagebox.showinfo("Success", "User registered successfully")
                    self.destroy()
                    if self.on_close:
                        self.on_close()
            except Exception as e:
                messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

'''
SYSC4907 Capstone Engineering Project "Pediatric Laparoscopic Surgery Simulator"

Main program file for Pediatric Laparoscopic Surgery Simulator Project
Run this file to run the project

Author: Nathan Mezzomo
Date Created: November 2, 2022
Last Edited: February 8, 2023
'''
import os

import cv2
import numpy as np
import time
import serial
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, CheckButtons

'''
GUI class contains variables for use throughout the program as well as 
image capture settings, interface settings, etc.
'''
#TODO: Rename to app (?) for more proper naming convention. Not everything GUI related
class GUI(object):

    def __init__(self, cameraID, font, windowName, displayWidth, displayHeight, red_low, red_high,
                 green_low, green_high, blue_low, blue_high, on_GUI_close=None):


        # Using cv2.CAP_DSHOW after cameraID specifies direct show, lets program start/open camera much faster.
        self.cap = cv2.VideoCapture(cameraID, cv2.CAP_DSHOW)
        self.on_GUI_close = on_GUI_close

        self.image_state = 5
        self.displayWidth = displayWidth
        self.displayHeight = displayHeight


        # HSV detection values
        self.red_low = red_low
        self.red_high = red_high
        self.green_low = green_low
        self.green_high = green_high
        self.blue_low = blue_low
        self.blue_high = blue_high

        self.task_state = 0 # Ring/suturing task states
        self.timer = 0 # timer variable for moving between task states in ring task

        self.warning_time = [0, 0, 0, 0, 0, 0, 0, 0, 0] # Timer variable array with an index for each different possible warning
        self.task_start = 0 # Time variable to get start time of a task

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.displayWidth)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.displayHeight)

        # Use this when using direct show setting, otherwise it slows down the startup
        self.cap.set(cv2.CAP_PROP_FPS, 15)
        print(self.cap.get(cv2.CAP_PROP_FPS))
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

        ret, frame = self.cap.read()

        # Main menu image
        self.main_menu = np.zeros([self.displayHeight, self.displayWidth, 3], np.uint8)

        #TODO: Feedback page(s)
        self.feedback_menu = np.zeros([self.displayHeight, self.displayWidth, 3], np.uint8)

        # Startup screen to show sensors starting
        self.startup_screen = np.zeros([self.displayHeight, self.displayWidth, 3], np.uint8)

        self.font = font
        self.windowName = windowName

        # defining variables for future assignment
        self.out = None     # Video output
        self.ser = None     # Serial var for sensor data input
        self.file = None    # Sensor data file

        # Spike count/time for feedback purposes
        self.spike_times = [[] for _ in range(9)]   # 2D array --> i,j where i = data index, j = times saved for that data index
        self.spike_values = [[] for _ in range(9)]  # 2D array to save the data value at spike start for plotting purposes

        # Sensor warning thresholds
        '''
        From Left to Right:
        Force, L_pitchAcc, L_yawAcc, R_pitchAcc, R_yawAcc, L_PMW_Y_acc,
        L_PMW_X_acc, R_PMW_Y_acc, R_PMW_X_acc
        '''
        self.warn_thresholds = [1, 1, 1, 1, 1, 0.5, 0.1, 0.5, 0.1]

        self.startup_counter = 16  # Counter variable for sensor startup countdown at program start

        cv2.namedWindow(self.windowName)

        try:
            self.main()
        except Exception as e:
            print(e)
            exit(1)


    def main(self):

            '''
               Exits program, shuts everything down as needed
            '''
            def quit_program(self):
                self.cap.release()
                cv2.destroyAllWindows
                stop_sensors(self)
            '''
            Closes the serial port to stop sensors
            '''
            def stop_sensors(self):
                self.ser.close()

            '''
            Open serial port to start sensor data collection
            '''
            def start_sensors(self):
                try:
                    self.ser = serial.Serial('COM3', 31250)   # COM port may change depending on computer/devices being used
                    self.ser.flushInput()

                except serial.SerialException:
                    self.ser.close()
                    print(serial.SerialException)
                    exit(1)

            '''
            Check if a warning should still be displayed, display if for a full second afterwards
            '''
            def display_warning(self, frame):
                cur_time = time.time()

                if cur_time - self.warning_time[0] < 1:
                    cv2.putText(frame, "Too much force!", (int(self.displayWidth/2 - 80), 700), self.font, 1, (255, 215, 5), 2)
                if cur_time - self.warning_time[1] < 1:
                    cv2.putText(frame, "Slow left pitch acc.", (0, self.displayHeight - 450), self.font, 1, (255, 215, 5), 2)
                if cur_time - self.warning_time[2] < 1:
                    cv2.putText(frame, "Slow left yaw acc.", (0, self.displayHeight - 500), self.font, 1, (255, 215, 5), 2)
                if cur_time - self.warning_time[3] < 1:
                    cv2.putText(frame, "Slow right pitch acc.", (self.displayWidth - 400, self.displayHeight - 450), self.font, 1, (255, 215, 5), 2)
                if cur_time - self.warning_time[4] < 1:
                    cv2.putText(frame, "Slow right yaw acc.", (self.displayWidth - 400, self.displayHeight - 500), self.font, 1, (255, 215, 5), 2)
                if cur_time - self.warning_time[5] < 1:
                    cv2.putText(frame, "Slow left surge acc.", (0, self.displayHeight - 400), self.font, 1, (255, 215, 5), 2)
                if cur_time - self.warning_time[6] < 1:
                    cv2.putText(frame, "Slow left rotation acc.", (0, self.displayHeight - 350), self.font, 1, (255, 215, 5), 2)
                if cur_time - self.warning_time[7] < 1:
                    cv2.putText(frame, "Slow right surge acc.", (self.displayWidth - 400, self.displayHeight - 400), self.font, 1, (255, 215, 5), 2)
                if cur_time - self.warning_time[8] < 1:
                    cv2.putText(frame, "Slow right rotation acc.", (self.displayWidth - 400, self.displayHeight - 350), self.font, 1, (255, 215, 5), 2)

            '''
            Check sensor data for any possible bad movements throughout a task
            and save the time the warning was detected
            Calls display_warning function to display that warning
            max_force can change depending on task, i.e. how much weight is already sitting on force plate
            '''
            def check_sensor_warnings(self, frame, data, max_force):
                data_split = data.split("|")

                if len(data.split("|")) == 33:     # Make sure array of proper length
                    if float(data_split[0]) > max_force:   # If > max_force N of force, add warning (dependent on task)
                        self.warning_time[0] = time.time()
                    if abs(float(data_split[1])) > self.warn_thresholds[1]:   # Left pitch acc
                        self.warning_time[1] = time.time()
                    if abs(float(data_split[2])) > self.warn_thresholds[2]:   # Left yaw acc
                        self.warning_time[2] = time.time()
                    if abs(float(data_split[3])) > self.warn_thresholds[3]:   # Right pitch acc
                        self.warning_time[3] = time.time()
                    if abs(float(data_split[4])) > self.warn_thresholds[4]:   # Right yaw acc
                        self.warning_time[4] = time.time()
                    if abs(float(data_split[5])) > self.warn_thresholds[5]:    # Left surge acc
                        self.warning_time[5] = time.time()
                    if abs(float(data_split[6])) > self.warn_thresholds[6]:    # Left rotation acc
                        self.warning_time[6] = time.time()
                    if abs(float(data_split[7])) > self.warn_thresholds[7]:    # Right surge acc
                        self.warning_time[7] = time.time()
                    if abs(float(data_split[8])) > self.warn_thresholds[8]:    # Right rotation acc
                        self.warning_time[8] = time.time()
                display_warning(self, frame)


            '''
            Plays video of most recent task attempt
            '''
            def play_video(videoname):

                vid = cv2.VideoCapture(videoname)
                if(vid.isOpened() == False):
                    print("Error opening video file")

                while(vid.isOpened()):

                    ret,frame = vid.read()
                    if ret == True:
                        cv2.imshow(self.windowName, frame)
                        key = cv2.waitKey(int(1000/30))
                        # Press Q on keyboard to exit video at anytime
                        if cv2.waitKey(25) & 0xFF == ord('q'):
                            break
                    else:
                        break

                vid.release()
                self.image_state = 3 # Go back to feedback page


            '''
            Plots all data read from sensor data txt file
            Includes sliders to scroll through time, and adjust y-axis scale
            '''
            def plot_data():
                fig, ax = plt.subplots(figsize=(25, 15))
                plt.subplots_adjust(bottom=0.3)

                file = open("sensor_data.txt", "r")
                lines = file.readlines()

                time = []
                force = []
                L_pitch = []
                L_yaw = []
                L_surge = []
                L_roll = []

                R_pitch = []
                R_yaw = []
                R_surge = []
                R_roll = []

                for line in lines:
                    if (len(line.split("|")) == 10):
                        line = line.strip('\n')  # Remove new line char from end of line
                        vars = line.split("|")  # Split each element of the line into a var split up by | character
                        time.append(vars[0])
                        force.append(vars[1])
                        L_pitch.append(vars[2])
                        L_yaw.append(vars[3])
                        R_pitch.append(vars[4])
                        R_yaw.append(vars[5])
                        L_surge.append(vars[6])
                        L_roll.append(vars[7])
                        R_surge.append(vars[8])
                        R_roll.append(vars[9])

                file.close()
                # Converts String values in array to numbers
                time = [f"{float(num):.2f}" for (num) in time]
                force = [f"{float(num):.2f}" for (num) in force]
                L_pitch = [f"{float(num):.2f}" for (num) in L_pitch]
                R_pitch = [f"{float(num):.2f}" for (num) in R_pitch]
                L_yaw = [f"{float(num):.2f}" for (num) in L_yaw]
                R_yaw = [f"{float(num):.2f}" for (num) in R_yaw]
                L_surge = [f"{float(num):.2f}" for (num) in L_surge]
                R_surge = [f"{float(num):.2f}" for (num) in R_surge]
                L_roll = [f"{float(num):.2f}" for (num) in L_roll]
                R_roll = [f"{float(num):.2f}" for (num) in R_roll]

                # Ensures float type 32bit
                # time = np.array(time) --> Don't need?
                force = np.array(force, dtype=np.float32)
                L_pitch = np.array(L_pitch, dtype=np.float32)
                R_pitch = np.array(R_pitch, dtype=np.float32)
                L_yaw = np.array(L_yaw, dtype=np.float32)
                R_yaw = np.array(R_yaw, dtype=np.float32)
                L_surge = np.array(L_surge, dtype=np.float32)
                R_surge = np.array(R_surge, dtype=np.float32)
                L_roll = np.array(L_roll, dtype=np.float32)
                R_roll = np.array(R_roll, dtype=np.float32)


                # How many x values shown on screen at once
                visible_range = 15  # Range of x values visible at once
                y_range = 5  # Default y range
                ax.set_xlim(0, visible_range)
                ax.set_ylim(-y_range, y_range)

                # Slider positioning
                axcolor = 'lightgoldenrodyellow'
                axpos = plt.axes([0.2, 0.15, 0.65, 0.03], facecolor=axcolor)
                aypos = plt.axes([0.2, 0.1, 0.65, 0.03], facecolor=axcolor)

                # fig, ax = plt.subplots()
                l1, = ax.plot(time, force, visible=False, color='blue', label='Force (N)')
                l2, = ax.plot(time, L_pitch, visible=False, color='red', label='Left Pitch')
                l3, = ax.plot(time, L_yaw, visible=False, color='green', label='Left Yaw')
                l4, = ax.plot(time, R_pitch, visible=False, color='pink', label='Right Pitch')
                l5, = ax.plot(time, R_yaw, visible=False, color='purple', label='Right Yaw')
                l6, = ax.plot(time, R_surge, visible=False, color='brown', label='Right Surge')
                l7, = ax.plot(time, R_roll, visible=False, color='orange', label='Right Roll')
                l8, = ax.plot(time, L_surge, visible=False, color='black', label='Left Surge')
                l9, = ax.plot(time, L_roll, visible=False, color='silver', label='Left Roll')
                lines = [l1, l2, l3, l4, l5, l6, l7, l8, l9]

                fig.subplots_adjust(left=0.25)
                rax = fig.add_axes([0.025, 0.4, 0.1, 0.2])

                labels = [str(line.get_label()) for line in lines]
                visibility = [line.get_visible() for line in lines]
                check = CheckButtons(rax, labels, visibility)

                # X-axis Slider(ax, label, valmin, valmax)
                xpos = Slider(axpos, 'Time', 0, len(time) - visible_range, valinit=0., valstep=0.1)
                xpos.valtext.set_visible(False)
                # Y-axis Slider
                ypos = Slider(aypos, 'Y-Range', 0.1, 25, valinit=10, valstep=0.1)
                ypos.valtext.set_visible(False)

                def x_update(val):
                    pos = xpos.val
                    ax.set_xlim(pos, pos + visible_range)
                    fig.canvas.draw_idle()

                def y_update(val):
                    pos = ypos.val
                    ax.set_ylim(-pos, pos)
                    fig.canvas.draw_idle()

                def handle_click(label):
                    index = labels.index(label)
                    lines[index].set_visible(
                        not lines[index].get_visible())  # Set visibility to be opposite of what it was set at

                    # Place text at each spike on visible lines
                    for txt in ax.texts:    # Clearing all text first
                        txt.set_visible(False)

                    i = 0
                    for li in lines:
                        if li.get_visible():
                            for j in range(0, len(self.spike_times[i])):
                                ax.text(float(self.spike_times[i][j]), float(self.spike_values[i][j]), "!!!",)
                                print(float(self.spike_times[i][j]))
                        i += 1
                    plt.draw()

                check.on_clicked(handle_click)
                xpos.on_changed(x_update)
                ypos.on_changed(y_update)
                plt.show()



            '''
            Save the times of each warning to a text file
            '''
            def save_spike_times(self, file, index):

                times = open("sensor_data.txt", "r")
                time_arr = []
                for line in times:
                    line = line.strip('\n')
                    vars = line.split("|")
                    time_arr.append(vars[0])

                time_arr = [f"{float(num):.2f}" for (num) in time_arr]
                for j in range(0, len(self.spike_times[index])):
                    time_index = self.spike_times[index][j]
                    file.write(str(time_arr[time_index]) + '\n')

                times.close()

            '''
            Counts spikes in data and returns list of times they occur at
            '''
            def count_spikes(self):
                # Clearing any left-over values
                self.spike_times = [[] for _ in range(9)]
                self.spike_values = [[] for _ in range(9)]
                #count, index = 0, 0
                high = False
                file = open("sensor_data.txt", "r")
                lines = file.readlines()
                for i in range(0, 9):
                    j = 0
                    for line in lines:
                        if(len(line.split("|")) == 10):
                            line = line.strip('\n')
                            vars = line.split("|")
                            if float(vars[i+1]) > self.warn_thresholds[i] and not high:  # i+1 to skip time variable at index 0
                                high = True
                                self.spike_times[i].append(j) # Save the time index of the spike start
                                self.spike_values[i].append(vars[i+1]) # Save the data value at spike start
                            elif float(vars[i+1]) < self.warn_thresholds[i] and high:
                                high = False
                            j += 1
                file.close()

                # Print the times into another text file so a user can see the list of times

                file = open("Warning_list.txt", "w")
                file.write("Warning Type and times (seconds): \n")
                file.write("Force: \n")
                save_spike_times(file, 0)
                file.write("Left Pitch Acceleration: \n")
                save_spike_times(file, 1)
                file.write("Left Yaw Acceleration: \n")
                save_spike_times(file, 2)
                file.write("Right Pitch Acceleration: \n")
                save_spike_times(file, 3)
                file.write("Right Yaw Acceleration: \n")
                save_spike_times(file, 4)
                file.write("Left Surge Acceleration: \n")
                save_spike_times(file, 5)
                file.write("Left Roll Acceleration: \n")
                save_spike_times(file, 6)
                file.write("Right Surge Acceleration: \n")
                save_spike_times(file, 7)
                file.write("Right Roll Acceleration: \n")
                save_spike_times(file, 8)

                file.close()



            '''
            Checks which state the interface is currently is, and processes information depending
            on that state.
            Image States:
            -1 - Quit program
            0 - Main Menu
            1 - Ring Task
            2 - Suturing Task
            3 - Feedback
            4 - not used
            5 - Sensor startup page (Initial startup screen to wait for sensor startup)
            '''
            def evaluate_state(self):
                '''
                Ring task.
                States:
                1 - Red ring/peg
                2 - Green ring/peg
                3 - Blue ring/peg
                other - end of task
                '''


                if self.image_state == 1:
                    # Get latest video frame
                    ret, frame = self.cap.read()
                    if ret:
                        frame = cv2.resize(frame, (self.displayWidth, self.displayHeight))

                    # Only write/show a frame if there was a new capture
                    if ret == True:
                        frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                        lower_bound = None
                        upper_bound = None

                        #set detection bounds based off task state
                        if (self.task_state == 1):  # red
                            lower_bound = self.red_low
                            upper_bound = self.red_high
                        elif (self.task_state == 2):  # green
                            lower_bound = self.green_low
                            upper_bound = self.green_high
                        elif (self.task_state == 3):  # blue
                            lower_bound = self.blue_low
                            upper_bound = self.blue_high
                        else:
                            lower_bound = np.array([255, 255, 255])
                            upper_bound = np.array([255, 255, 255])
                            #self.file.close()
                            #quit_program(self)
                            #return

                        myMask = cv2.inRange(frameHSV, lower_bound, upper_bound)

                        contours,_ = cv2.findContours(myMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                        def back(*args):
                            pass


                        contour_count = 0
                        for cnt in contours:
                            area = cv2.contourArea(cnt)
                            # Only detect countours of this size range, may need changing if camera view of task differs
                            if area > 150 and area < 7000:
                                contour_count += 1
                                (x, y, w, h) = cv2.boundingRect(cnt)
                                cv2.rectangle(frame, (x - 20, y - 20), (x + 20 + w, y + 20 + h), (255, 0, 0), 2)

                        # Read sensor data
                        stuff = self.ser.readline()
                        stuff_string = stuff.decode()

                        # Write sensor data to file with time since task start in seconds
                        self.file.write(str(time.time() - self.task_start) + "|" + stuff_string.rstrip() + '\n')
                        print(str(time.time() - self.task_start) + "|" + stuff_string.rstrip()+ '\n')

                        check_sensor_warnings(self, frame, stuff_string.rstrip(), self.warn_thresholds[0]) # Sending force threshold here incase we want to change depending on task

                        # Check contour count, if < 2 for 3 seconds, move onto next ring/peg colour
                        if(contour_count < 2 and (time.time() - self.timer > 3)):
                            self.timer = time.time()
                            self.task_state += 1 # move into next state
                        elif(contour_count > 1):
                            self.timer = time.time() # reset timer

                        #Place a timer on screen for task duration
                        cv2.putText(frame, str(round(time.time() - self.task_start, 2)), (int(self.displayWidth/2), 50), self.font, 1, (0, 0, 0), 2)
                        self.out.write(frame)
                        cv2.imshow(self.windowName, frame)

                elif self.image_state == 2:

                    #self.out = cv2.VideoWriter('outpy.avi', cv2.VideoWriter_fourcc(*'MJPG'), 30, (self.displayWidth, self.displayHeight))
                    """----------"""
                    ret, frame = self.cap.read()
                    cv2.putText(frame, "Suturing Task", (25, 35), self.font, 1, (0, 255, 0), 2)
                    cv2.putText(frame, "Main Menu", (1100, 35), self.font, 1, (255, 215, 5), 2)

                    # Read sensor data
                    stuff = self.ser.readline()
                    stuff_string = stuff.decode()

                    # Write sensor data to file with time since 5task start in seconds
                    self.file.write(str(time.time() - self.task_start) + "|" + stuff_string.rstrip() + '\n')

                    check_sensor_warnings(self,frame, stuff_string.rstrip(), self.warn_thresholds[0]) # Sending force threshold here incase we want to change depending on task

                    # Place a timer on screen for task duration
                    #cv2.putText(frame, str(round(time.time() - self.task_start, 2)), (600, 35), self.font, 1, (255, 215, 5), 2)
                    self.out.write(frame)
                    cv2.imshow(self.windowName, frame)

                elif self.image_state == 3:  # Feedback page
                    self.feedback_menu = np.zeros([self.displayHeight, self.displayWidth, 3], np.uint8)
                    cv2.putText(self.feedback_menu, "Main Menu", (1100, 35), self.font, 1, (255, 215, 5), 2)
                    cv2.putText(self.feedback_menu, "Watch Previous Attempt", (880, 685), self.font, 1, (255, 215, 5), 2)
                    cv2.putText(self.feedback_menu, "View Graphical Data", (25, 685), self.font, 1, (255, 215, 5), 2)
                    cv2.putText(self.feedback_menu, "View Times of Warnings", (25, 35), self.font, 1, (255, 215, 5), 2)

                    #Placing data spike counters
                    cv2.putText(self.feedback_menu, "Thresholds crossed", (25, 125), self.font, 1, (0, 255, 0), 2)
                    cv2.putText(self.feedback_menu, "Force: " + str(len(self.spike_times[0])),(25,170), self.font, 1, (0, 255, 0), 2)
                    cv2.putText(self.feedback_menu, "Left pitch acc: " + str(len(self.spike_times[1])), (25, 215), self.font, 1, (0, 255, 0), 2)
                    cv2.putText(self.feedback_menu, "Left yaw acc: " + str(len(self.spike_times[2])), (25, 260), self.font, 1, (0, 255, 0), 2)
                    cv2.putText(self.feedback_menu, "Right pitch acc: " + str(len(self.spike_times[3])), (25, 305), self.font, 1, (0, 255, 0), 2)
                    cv2.putText(self.feedback_menu, "Right yaw acc: " + str(len(self.spike_times[4])), (25, 350), self.font, 1, (0, 255, 0), 2)
                    cv2.putText(self.feedback_menu, "Left surge acc: " + str(len(self.spike_times[5])), (25, 395), self.font, 1,(0, 255, 0), 2)
                    cv2.putText(self.feedback_menu, "Left roll acc: " + str(len(self.spike_times[6])), (25, 440), self.font, 1,(0, 255, 0), 2)
                    cv2.putText(self.feedback_menu, "Right surge acc: " + str(len(self.spike_times[7])), (25, 485), self.font, 1,(0, 255, 0), 2)
                    cv2.putText(self.feedback_menu, "Right roll acc: " + str(len(self.spike_times[8])), (25, 530), self.font, 1,(0, 255, 0), 2)



                    cv2.imshow(self.windowName, self.feedback_menu)
                elif self.image_state == 0:
                    cv2.putText(self.main_menu, "Pediatric Laparoscopic Training Simulator", (320, 360), self.font, 1, (255, 215, 5), 2)
                    cv2.putText(self.main_menu, "Ring Task", (25, 35), self.font, 1, (255, 215, 5), 2)
                    cv2.putText(self.main_menu, "Suturing Task", (1030, 35), self.font, 1, (255, 215, 5), 2)
                    cv2.putText(self.main_menu, "View Feedback", (1030, 685), self.font, 1, (255, 215, 5), 2)
                    cv2.putText(self.main_menu, "Quit", (25, 685), self.font, 1, (255, 215, 5), 2)
                    cv2.imshow(self.windowName, self.main_menu)
                elif self.image_state == 5:
                   # Load an image
                    image_path = 'pegtask.png'
                    startup_image = cv2.imread(image_path)

                    # Check if the image needs resizing to fit the display window
                    if startup_image.shape[0] != self.displayHeight or startup_image.shape[1] != self.displayWidth:
                        startup_image = cv2.resize(startup_image, (self.displayWidth, self.displayHeight))

                    # Create/Open the OpenCV window
                    cv2.namedWindow(self.windowName)

                    self.out = cv2.VideoWriter('outpy.avi', cv2.VideoWriter_fourcc(*'MJPG'), 15, (self.displayWidth, self.displayHeight))
                    self.startup_counter -= 1

                    while self.startup_counter >= 0:
                        # Create a copy of the image to work with
                        image_with_text = startup_image.copy()

                        # Add countdown timer text to the image copy
                        countdown_text = str(self.startup_counter)
                        cv2.putText(image_with_text, countdown_text, (self.displayWidth - 200, self.displayHeight - 100), self.font, 1, (0, 0, 0))

                        # Display the updated image
                        cv2.imshow(self.windowName, image_with_text)

                        # Wait for a short time (e.g., 1000 milliseconds) to update the display
                        key = cv2.waitKey(1000)

                        # Check if the window is closed
                        if cv2.getWindowProperty(self.windowName, cv2.WND_PROP_VISIBLE) < 1:
                            break

                        # Decrement the counter
                        self.startup_counter -= 1

                    # Perform other tasks after the countdown
                    self.image_state = 1
                    self.task_state = 1
                    self.ser.flushInput()
                    self.timer = time.time()
                    self.task_start = time.time()
                    self.file = open("sensor_data.txt", "w")



            '''
            Looks for left mouse click anywhere on screen.
            There are different options depending on the which section of the
            screen is clicked, and which screen is currently active'''
            def mouse_event(event, x, y, flags, param):
                if event == cv2.EVENT_LBUTTONDOWN:
                    # Section state changes based on current GUI state
                    # Main menu options
                    if self.image_state == 0:
                        # Sectioning window into 4 corners
                        # Top left click
                        if y < self.displayHeight/2 and x < self.displayWidth/2:
                            self.out = cv2.VideoWriter('outpy.avi', cv2.VideoWriter_fourcc(*'MJPG'), 30, (self.displayWidth, self.displayHeight))
                            self.task_state = 1
                            self.image_state = 1    # Ring Task
                            self.ser.flushInput()
                            self.timer = time.time()
                            self.task_start = time.time()
                            self.file = open("sensor_data.txt", "w")
                        # Top right click
                        elif y < self.displayHeight/2 and x > self.displayWidth/2:
                            self.out = cv2.VideoWriter('outpy.avi', cv2.VideoWriter_fourcc(*'MJPG'), 30, (self.displayWidth, self.displayHeight))
                            self.image_state = 2     # Suturing Task
                            self.task_start = time.time()
                            self.ser.flushInput()
                            self.file = open("sensor_data.txt", "w")
                        # Bottom left click
                        elif y > self.displayHeight/2 and x < self.displayWidth/2:
                            self.image_state = -1    # Quit
                        # Bottom right click
                        elif y > self.displayHeight/2 and x > self.displayWidth/2:
                            count_spikes(self)
                            self.image_state = 3     # Feedback page
                    # Ring Task options
                    elif self.image_state == 1:
                        if y < self.displayHeight / 2 and x > self.displayWidth / 2:  # Top Right click
                            self.file.close()
                            self.image_state = 0  # Back to main menu
                    # Suturing Task options
                    elif self.image_state == 2:
                        if y < self.displayHeight / 2 and x > self.displayWidth / 2:  # Top Right click
                            self.file.close()
                            self.image_state = 0  # Back to main menu
                    # Feedback page options
                    elif self.image_state == 3:
                        if y > self.displayHeight/2 and x > self.displayWidth/2:
                            play_video("outpy.avi")
                        elif y < self.displayHeight / 2 and x < self.displayWidth / 2:  #Top left click
                            os.startfile("Warning_list.txt")
                        elif y < self.displayHeight / 2 and x > self.displayWidth / 2:  # Top Right click
                            self.image_state = 0  # Back to main menu
                        elif y > self.displayHeight / 2 and x < self.displayWidth / 2:    # Bottom left click
                            plot_data()


            # Calls mouse_event function if mouse is clicked on the open window
            cv2.namedWindow(self.windowName, cv2.WINDOW_GUI_NORMAL)
            cv2.setMouseCallback(self.windowName, mouse_event)
            # Initial sensor startup
            start_sensors(self)
            window_closed = False

            '''
            While running, make required calls to evaluate the current program state
            '''

            def show_popup():
                """Display a simple Tkinter popup window without buttons."""
                popup = tk.Tk()
                popup.withdraw()  # Hide the main Tk window
                messagebox.showinfo("Reminder", "Task Exited.\n\nBe sure to check your feedback in the Feedback Menu")
                popup.destroy()

            while True:
                try:
                    evaluate_state(self)
                except Exception as e:
                    print(e)
                    exit(1)

                # Can press "q" key anytime to quit, no matter GUI state
                key = cv2.waitKey(1)
                if key == ord("q") or self.image_state == -1:    # state -1 will tell program to quit
                    if self.on_GUI_close:
                        self.on_GUI_close()
                    show_popup()
                    quit_program(self)
                    break

                # Check if the window was closed
                if cv2.getWindowProperty(self.windowName, cv2.WND_PROP_VISIBLE) < 1:
                    window_closed = True
                    if self.on_GUI_close:
                        self.on_GUI_close()
                    show_popup()
                    quit_program(self)
                    break

            # Close the OpenCV window if it was not closed using "q"
            if not window_closed:
                if self.on_GUI_close:
                    self.on_GUI_close()
                show_popup()
                quit_program(self)



# Run the application
if __name__ == "__main__":
    cameraID = 0  # Set Camera ID to change camera input (0, 1, etc.)
    font = cv2.FONT_HERSHEY_SIMPLEX
    windowName = "Pediatric Laparoscopic Training Simulator"

    '''
    HSV Ranges
    Use HSV.py to find appropriate values if recalibration required
    '''
    red_low = np.array([0, 100, 150])  # [H, S, V]
    red_high = np.array([15, 255, 255])
    green_low = np.array([30, 100, 50])
    green_high = np.array([95, 255, 255])
    blue_low = np.array([75, 135, 0])
    blue_high = np.array([115, 255, 255])
    tip_low = np.array([17, 84, 141])
    tip_high = np.array([27, 165, 169])

    app = Application()
    app.mainloop()
