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

    image_state: int

    def __init__(self, cameraID, font, windowName, displayWidth, displayHeight, red_low, red_high,
                 green_low, green_high, blue_low, blue_high, tip_low, tip_high):
        self.image_state = 5

        # Using cv2.CAP_DSHOW after cameraID specifies direct show, lets program start/open camera much faster.
        self.cap = cv2.VideoCapture(cameraID, cv2.CAP_DSHOW)

        self.displayWidth = displayWidth
        self.displayHeight = displayHeight

        # HSV detection values
        self.red_low = red_low
        self.red_high = red_high
        self.green_low = green_low
        self.green_high = green_high
        self.blue_low = blue_low
        self.blue_high = blue_high
        self.tip_low = tip_low
        self.tip_high = tip_high

        self.task_state = 0 # Ring/suturing task states
        self.timer = 0 # timer variable for moving between task states in ring task

        self.warning_time = [0, 0, 0, 0, 0, 0, 0, 0, 0] # Timer variable array with an index for each different possible warning
        self.task_start = 0 # Time variable to get start time of a task

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.displayWidth)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.displayHeight)

        # Use this when using direct show setting, otherwise it slows down the startup
        self.cap.set(cv2.CAP_PROP_FPS, 30)
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

        self.startup_counter = 16   # Counter variable for sensor startup countdown at program start

        cv2.namedWindow(self.windowName)


def main():

    '''
       Exits program, shuts everything down as needed
    '''
    def quit_program():
        GUI.cap.release()
        cv2.destroyAllWindows
        stop_sensors()
    '''
    Closes the serial port to stop sensors
    '''
    def stop_sensors():
        GUI.ser.close()


    '''
    Open serial port to start sensor data collection
    '''
    def start_sensors():
        try:
            GUI.ser = serial.Serial('COM4', 38400)  # COM port may change depending on computer/devices being used

        except serial.SerialException:
            print(serial.SerialException)
            exit(1)

    '''
    Check if a warning should still be displayed, display if for a full second afterwards
    '''
    def display_warning(frame):
        cur_time = time.time()

        if cur_time - GUI.warning_time[0] < 1:
            cv2.putText(frame, "Too much force!", (500, 700), GUI.font, 1, (0, 0, 255), 2)
        if cur_time - GUI.warning_time[1] < 1:
            cv2.putText(frame, "Slow left pitch acc.", (25, 650), GUI.font, 1, (0, 0, 255), 2)
        if cur_time - GUI.warning_time[2] < 1:
            cv2.putText(frame, "Slow left yaw acc.", (25, 700), GUI.font, 1, (0, 0, 255), 2)
        if cur_time - GUI.warning_time[3] < 1:
            cv2.putText(frame, "Slow right pitch acc.", (925, 650), GUI.font, 1, (0, 0, 255), 2)
        if cur_time - GUI.warning_time[4] < 1:
            cv2.putText(frame, "Slow right yaw acc.", (925, 700), GUI.font, 1, (0, 0, 255), 2)
        if cur_time - GUI.warning_time[5] < 1:
            cv2.putText(frame, "Slow left surge acc.", (25, 600), GUI.font, 1, (0, 0, 255), 2)
        if cur_time - GUI.warning_time[6] < 1:
            cv2.putText(frame, "Slow left rotation acc.", (25, 550), GUI.font, 1, (0, 0, 255), 2)
        if cur_time - GUI.warning_time[7] < 1:
            cv2.putText(frame, "Slow right surge acc.", (900, 600), GUI.font, 1, (0, 0, 255), 2)
        if cur_time - GUI.warning_time[8] < 1:
            cv2.putText(frame, "Slow right rotation acc.", (900, 550), GUI.font, 1, (0, 0, 255), 2)

    '''
    Check sensor data for any possible bad movements throughout a task
    and save the time the warning was detected
    Calls display_warning function to display that warning
    max_force can change depending on task, i.e. how much weight is already sitting on force plate
    '''
    def check_sensor_warnings(frame, data, max_force):
        data_split = data.split("|")

        if len(data.split("|")) == 33:  # Make sure array of proper length
            if float(data_split[0]) > max_force:  # If > max_force N of force, add warning (dependent on task)
                GUI.warning_time[0] = time.time()
            if abs(float(data_split[1])) > GUI.warn_thresholds[1]:  # Left pitch acc
                GUI.warning_time[1] = time.time()
            if abs(float(data_split[2])) > GUI.warn_thresholds[2]:  # Left yaw acc
                GUI.warning_time[2] = time.time()
            if abs(float(data_split[3])) > GUI.warn_thresholds[3]:  # Right pitch acc
                GUI.warning_time[3] = time.time()
            if abs(float(data_split[4])) > GUI.warn_thresholds[4]:  # Right yaw acc
                GUI.warning_time[4] = time.time()
            if abs(float(data_split[5])) > GUI.warn_thresholds[5]:  # Left surge acc
                GUI.warning_time[5] = time.time()
            if abs(float(data_split[6])) > GUI.warn_thresholds[6]:  # Left rotation acc
                GUI.warning_time[6] = time.time()
            if abs(float(data_split[7])) > GUI.warn_thresholds[7]:  # Right surge acc
                GUI.warning_time[7] = time.time()
            if abs(float(data_split[8])) > GUI.warn_thresholds[8]:  # Right rotation acc
                GUI.warning_time[8] = time.time()
        display_warning(frame)


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
                cv2.imshow(GUI.windowName, frame)
                key = cv2.waitKey(int(1000/30))
                # Press Q on keyboard to exit video at anytime
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    break
            else:
                break

        vid.release()
        GUI.image_state = 3 # Go back to feedback page


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
                vars = line.split("|")  # Split each element of the line into a var split up by , character
                time.append(vars[0])
                force.append(vars[1])
                L_pitch.append(vars[2])
                L_yaw.append(vars[3])
                R_pitch.append(vars[4])
                R_yaw.append(vars[5])
                L_surge.append(vars[6])
                L_roll. append(vars[7])
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
                    for j in range(0, len(GUI.spike_times[i])):
                        ax.text(float(GUI.spike_times[i][j]), float(GUI.spike_values[i][j]), "!!!",)
                        print(float(GUI.spike_times[i][j]))
                i += 1
            plt.draw()

        check.on_clicked(handle_click)
        xpos.on_changed(x_update)
        ypos.on_changed(y_update)
        plt.show()



    '''
    Save the times of each warning to a text file
    '''
    def save_spike_times(file, index):

        times = open("sensor_data.txt", "r")
        time_arr = []
        for line in times:
            line = line.strip('\n')
            vars = line.split("|")
            time_arr.append(vars[0])

        time_arr = [f"{float(num):.2f}" for (num) in time_arr]
        for j in range(0, len(GUI.spike_times[index])):
            time_index = GUI.spike_times[index][j]
            file.write(str(time_arr[time_index]) + '\n')

        times.close()

    '''
    Counts spikes in data and returns list of times they occur at
    '''
    def count_spikes():
        # Clearing any left-over values
        GUI.spike_times = [[] for _ in range(9)]
        GUI.spike_values = [[] for _ in range(9)]
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
                    if float(vars[i+1]) > GUI.warn_thresholds[i] and not high:  # i+1 to skip time variable at index 0
                        high = True
                        GUI.spike_times[i].append(j) # Save the time index of the spike start
                        GUI.spike_values[i].append(vars[i+1]) # Save the data value at spike start
                    elif float(vars[i+1]) < GUI.warn_thresholds[i] and high:
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
    def evaluate_state():
        '''
        Ring task.
        States:
        1 - Red ring/peg
        2 - Green ring/peg
        3 - Blue ring/peg
        other - end of task
        '''
        if GUI.image_state == 1:
            # Get latest video frame
            ret, frame = GUI.cap.read()

            # Only write/show a frame if there was a new capture
            if ret == True:
                frameHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                lower_bound = None
                upper_bound = None

                lower_tip_bound = None
                upper_tip_bound = None

                #set detection bounds based off task state
                if (GUI.task_state == 1):  # red
                    lower_bound = GUI.red_low
                    upper_bound = GUI.red_high
                elif (GUI.task_state == 2):  # green
                    lower_bound = GUI.green_low
                    upper_bound = GUI.green_high
                elif (GUI.task_state == 3):  # blue
                    lower_bound = GUI.blue_low
                    upper_bound = GUI.blue_high
                else:
                    lower_bound = np.array([255, 255, 255])
                    upper_bound = np.array([255, 255, 255])
                    GUI.file.close()
                    GUI.image_state = 0
                    return

                myMask = cv2.inRange(frameHSV, lower_bound, upper_bound)

                contours,_ = cv2.findContours(myMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                cv2.putText(frame, "Ring Task", (25, 35), GUI.font, 1, (0, 0, 255), 2)
                cv2.putText(frame, "Main Menu", (1100, 35), GUI.font, 1, (0, 0, 255), 2)
                contour_count = 0
                for cnt in contours:
                    area = cv2.contourArea(cnt)
                    # Only detect countours of this size range, may need changing if camera view of task differs
                    if area > 150 and area < 7000:
                        contour_count += 1
                        (x, y, w, h) = cv2.boundingRect(cnt)
                        cv2.rectangle(frame, (x - 20, y - 20), (x + 20 + w, y + 20 + h), (255, 0, 0), 2)

                height, width, _ = frame.shape
                min_x, min_y = width, height
                max_x = max_y = 0

                lower_tip_bound = GUI.tip_low
                upper_tip_bound = GUI.tip_high

                tipMask = cv2.inRange(frameHSV, lower_tip_bound, upper_tip_bound)
                contours2, _ = cv2.findContours(tipMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                tip_count = 0
                for cnt2 in contours2:
                    area = cv2.contourArea(cnt2)

                    cX_list = []
                    cY_list = []

                    cX_list.append(0)
                    cY_list.append(0)

                    #contour_count = 0
                    if area > 90 and area < 300:
                        tip_count += 1
                        #(x, y, w, h) = cv2.boundingRect(cnt2)
                        #cv2.rectangle(frame, (x - 5, y - 5), (x + 5 + w, y + 5 + h), (0, 255, 0), 2)

                        M = cv2.moments(cnt2)
                        cX = int(M["m10"] / M["m00"])
                        cY = int(M["m01"] / M["m00"])
                        cX_list.append(cX)
                        cY_list.append(cY)
                        # cv2.drawContours(frame, [cnt], -1, (0, 255, 0), 2)
                        # cv2.circle(frame, (cX, cY), 7, (255, 255, 255), -1)
                        coords = str(cX) + ", " + str(cY)
                        (x, y, w, h) = cv2.boundingRect(cnt2)
                        min_x, max_x = min(x, min_x), max(x + w, max_x)
                        min_y, max_y = min(y, min_y), max(y + h, max_y)

                        cv2.rectangle(frame, (x - 5, y - 5), (x + 5 + w, y + 5 + h), (0, 255, 0), 2)

                        #cv2.putText(frame, str(area), (cX, cY), cv2.FONT_HERSHEY_`SIMPLEX, 1, (0, 255, 0), 2)

                        '''if area > 250 or (tip_count > 1):
                            cv2.putText(frame, "open", (cX + 5, cY + 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)'''

                        for i in range(len(cX_list) - 1):
                            #cv2.putText(frame, str(abs(cX - cX_list[i])), (cX + 20, cY + 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                            if (abs(cX - cX_list[i]) < 1000 and (tip_count > 1)) or (area > 200):
                                cv2.putText(frame, "open", (cX + 5, cY + 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                        for i in range(len(cY_list) - 1):
                            #cv2.putText(frame, str(abs(cY - cY_list[i])), (cX + 10, cY + 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                            if (abs(cY - cY_list[i]) < 1000 and (tip_count > 1)) or (area > 200):
                                cv2.putText(frame, "open", (cX + 5, cY + 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

                # Read sensor data
                stuff = GUI.ser.readline()
                stuff_string = stuff.decode()

                # Write sensor data to file with time since task start in seconds
                GUI.file.write(str(round(time.time() - GUI.task_start,3)) + "|" + stuff_string.rstrip() + '\n')


                check_sensor_warnings(frame, stuff_string.rstrip(), GUI.warn_thresholds[0]) # Sending force threshold here incase we want to change depending on task

                # Check contour count, if < 2 for 3 seconds, move onto next ring/peg colour
                if(contour_count < 2 and (time.time() - GUI.timer > 3)):
                    GUI.timer = time.time()
                    GUI.task_state += 1 # move into next state
                elif(contour_count > 1):
                    GUI.timer = time.time() # reset timer

                #Place a timer on screen for task duration
                cv2.putText(frame, str(round(time.time() - GUI.task_start, 2)), (600, 35), GUI.font, 1, (0, 0, 255), 2)
                GUI.out.write(frame)
                cv2.imshow(GUI.windowName, frame)

        elif GUI.image_state == 2:
            ret, frame = GUI.cap.read()
            cv2.putText(frame, "Suturing Task", (25, 35), GUI.font, 1, (0, 0, 255), 2)
            cv2.putText(frame, "Main Menu", (1100, 35), GUI.font, 1, (0, 0, 255), 2)

            # Read sensor data
            stuff = GUI.ser.readline()
            stuff_string = stuff.decode()

            # Write sensor data to file with time since task start in seconds
            GUI.file.write(str(time.time() - GUI.task_start) + "|" + stuff_string.rstrip() + '\n')

            check_sensor_warnings(frame, stuff_string.rstrip(), GUI.warn_thresholds[0]) # Sending force threshold here incase we want to change depending on task

            # Place a timer on screen for task duration
            cv2.putText(frame, str(round(time.time() - GUI.task_start, 2)), (600, 35), GUI.font, 1, (0, 0, 255), 2)
            GUI.out.write(frame)
            cv2.imshow(GUI.windowName, frame)

        elif GUI.image_state == 3:  # Feedback page
            GUI.feedback_menu = np.zeros([GUI.displayHeight, GUI.displayWidth, 3], np.uint8)
            cv2.putText(GUI.feedback_menu, "Main Menu", (1100, 35), GUI.font, 1, (0, 0, 255), 2)
            cv2.putText(GUI.feedback_menu, "Watch Previous Attempt", (880, 685), GUI.font, 1, (0, 0, 255), 2)
            cv2.putText(GUI.feedback_menu, "View Graphical Data", (25, 685), GUI.font, 1, (0, 0, 255), 2)
            cv2.putText(GUI.feedback_menu, "View Times of Warnings", (25, 35), GUI.font, 1, (0, 0, 255), 2)

            #Placing data spike counters
            cv2.putText(GUI.feedback_menu, "Thresholds crossed", (25, 125), GUI.font, 1, (0, 255, 0), 2)
            cv2.putText(GUI.feedback_menu, "Force: " + str(len(GUI.spike_times[0])),(25,170), GUI.font, 1, (0, 255, 0), 2)
            cv2.putText(GUI.feedback_menu, "Left pitch acc: " + str(len(GUI.spike_times[1])), (25, 215), GUI.font, 1, (0, 255, 0), 2)
            cv2.putText(GUI.feedback_menu, "Left yaw acc: " + str(len(GUI.spike_times[2])), (25, 260), GUI.font, 1, (0, 255, 0), 2)
            cv2.putText(GUI.feedback_menu, "Right pitch acc: " + str(len(GUI.spike_times[3])), (25, 305), GUI.font, 1, (0, 255, 0), 2)
            cv2.putText(GUI.feedback_menu, "Right yaw acc: " + str(len(GUI.spike_times[4])), (25, 350), GUI.font, 1, (0, 255, 0), 2)
            cv2.putText(GUI.feedback_menu, "Left surge acc: " + str(len(GUI.spike_times[5])), (25, 395), GUI.font, 1,(0, 255, 0), 2)
            cv2.putText(GUI.feedback_menu, "Left roll acc: " + str(len(GUI.spike_times[6])), (25, 440), GUI.font, 1,(0, 255, 0), 2)
            cv2.putText(GUI.feedback_menu, "Right surge acc: " + str(len(GUI.spike_times[7])), (25, 485), GUI.font, 1,(0, 255, 0), 2)
            cv2.putText(GUI.feedback_menu, "Right roll acc: " + str(len(GUI.spike_times[8])), (25, 530), GUI.font, 1,(0, 255, 0), 2)



            cv2.imshow(GUI.windowName, GUI.feedback_menu)
        elif GUI.image_state == 0:
            cv2.putText(GUI.main_menu, "Pediatric Laparoscopic Training Simulator", (320, 360), GUI.font, 1, (0, 0, 255), 2)
            cv2.putText(GUI.main_menu, "Ring Task", (25, 35), GUI.font, 1, (0, 0, 255), 2)
            cv2.putText(GUI.main_menu, "Suturing Task", (1030, 35), GUI.font, 1, (0, 0, 255), 2)
            cv2.putText(GUI.main_menu, "View Feedback", (1030, 685), GUI.font, 1, (0, 0, 255), 2)
            cv2.putText(GUI.main_menu, "Quit", (25, 685), GUI.font, 1, (0, 0, 255), 2)
            cv2.imshow(GUI.windowName, GUI.main_menu)
        elif GUI.image_state == 5:
            GUI.startup_screen = np.zeros([GUI.displayHeight, GUI.displayWidth, 3], np.uint8) # Clear text from window
            cv2.putText(GUI.startup_screen, "Starting sensors, please wait " + str(GUI.startup_counter) + " seconds...", (320, 360), GUI.font, 1,
                        (0, 0, 255), 2)
            cv2.imshow(GUI.windowName, GUI.startup_screen)
            key = cv2.waitKey(1000)
            GUI.startup_counter -= 1
            if(GUI.startup_counter < 0):
                GUI.image_state = 0


    '''
    Looks for left mouse click anywhere on screen.
    There are different options depending on the which section of the
    screen is clicked, and which screen is currently active'''
    def mouse_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            # Section state changes based on current GUI state
            # Main menu options
            if GUI.image_state == 0:
                # Sectioning window into 4 corners
                # Top left click
                if y < GUI.displayHeight/2 and x < GUI.displayWidth/2:
                    GUI.out = cv2.VideoWriter('outpy.avi', cv2.VideoWriter_fourcc(*'MJPG'), 30, (GUI.displayWidth, GUI.displayHeight))
                    GUI.task_state = 1
                    GUI.image_state = 1    # Ring Task
                    GUI.ser.flushInput()
                    GUI.timer = time.time()
                    GUI.task_start = time.time()
                    GUI.file = open("sensor_data.txt", "w")
                # Top right click
                elif y < GUI.displayHeight/2 and x > GUI.displayWidth/2:
                    GUI.out = cv2.VideoWriter('outpy.avi', cv2.VideoWriter_fourcc(*'MJPG'), 30, (GUI.displayWidth, GUI.displayHeight))
                    GUI.image_state = 2     # Suturing Task
                    GUI.task_start = time.time()
                    GUI.ser.flushInput()
                    GUI.file = open("sensor_data.txt", "w")
                # Bottom left click
                elif y > GUI.displayHeight/2 and x < GUI.displayWidth/2:
                    GUI.image_state = -1    # Quit
                # Bottom right click
                elif y > GUI.displayHeight/2 and x > GUI.displayWidth/2:
                    count_spikes()
                    GUI.image_state = 3     # Feedback page
            # Ring Task options
            elif GUI.image_state == 1:
                if y < GUI.displayHeight / 2 and x > GUI.displayWidth / 2:  # Top Right click
                    GUI.file.close()
                    GUI.image_state = 0  # Back to main menu
            # Suturing Task options
            elif GUI.image_state == 2:
                if y < GUI.displayHeight / 2 and x > GUI.displayWidth / 2:  # Top Right click
                    GUI.file.close()
                    GUI.image_state = 0  # Back to main menu
            # Feedback page options
            elif GUI.image_state == 3:
                if y > GUI.displayHeight/2 and x > GUI.displayWidth/2:
                    play_video("outpy.avi")
                elif y < GUI.displayHeight / 2 and x < GUI.displayWidth / 2:  #Top left click
                    os.startfile("Warning_list.txt")
                elif y < GUI.displayHeight / 2 and x > GUI.displayWidth / 2:  # Top Right click
                    GUI.image_state = 0  # Back to main menu
                elif y > GUI.displayHeight / 2 and x < GUI.displayWidth / 2:    # Bottom left click
                    plot_data()

    # Calls mouse_event function if mouse is clicked on the open window
    cv2.setMouseCallback(GUI.windowName, mouse_event)
    # Initial sensor startup
    start_sensors()

    '''
    While running, make required calls to evaluate the current program state
    '''
    while True:
        try:
            evaluate_state()
        except Exception as e:
            print(e)
            exit(1)

        # Can press "q" key anytime to quit, no matter GUI state
        key = cv2.waitKey(1)
        if key == ord("q") or GUI.image_state == -1:    # state -1 will tell program to quit
            quit_program()
            break

'''
This is the first code that runs at program startup.
Set any values that may change here before creation of GUI class object
and call to main()
'''
if __name__ == '__main__':
    cameraID = 0    # Set Camera ID to change camera input (0, 1, etc.)
    font = cv2.FONT_HERSHEY_SIMPLEX
    windowName = "Pediatric Laparoscopic Training Simulator"
    displayWidth = 1280
    displayHeight = 720

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

    # Create an instance of "GUI"
    GUI = GUI(cameraID, font, windowName, displayWidth, displayHeight,
              red_low, red_high, green_low, green_high, blue_low, blue_high, tip_low, tip_high)
    # Call to execute main method
    try:
        main()
    except Exception as e:
        print(e)
        exit(1)
