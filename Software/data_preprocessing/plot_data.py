import numpy as np
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt2
from warnings import simplefilter


def plot_all_data():
    fig, ax = plt.subplots(15, 2, gridspec_kw={"width_ratios": [15, 15]})
    # plt.setp(ax[14, 2].get_xticklabels(), fontsize=2, rotation=90)

    # Set the vertical/horizontal spacing between the subplots
    fig.subplots_adjust(hspace=2, wspace=2)

    # plt.subplots_adjust(bottom=0.3)

    file = open("sensor_data.txt", "r")
    lines = file.readlines()

    time = []
    force = []

    # Acceleration data
    L_pitchAcc = []
    L_yawAcc = []
    L_surgeAcc = []
    L_rollAcc = []

    R_pitchAcc = []
    R_yawAcc = []
    R_surgeAcc = []
    R_rollAcc = []

    # Velocity data

    L_pitchVel = []
    L_yawVel = []
    L_surgeVel = []
    L_rollVel = []

    R_pitchVel = []
    R_yawVel = []
    R_surgeVel = []
    R_rollVel = []

    # Rotation Data

    L_pitch = []
    L_yaw = []
    L_surge = []
    L_roll = []

    R_pitch = []
    R_yaw = []
    R_surge = []
    R_roll = []

    # Motion Data
    L_motion = []
    R_motion = []

    for line in lines:
        if len(line.split("|")) == 34:
            line = line.strip("\n")  # Remove new line char from end of line
            vars = line.split(
                "|"
            )  # Split each element of the line into a var split up by | character
            time.append(vars[0])
            force.append(vars[1])

            L_pitchAcc.append(vars[2])
            L_yawAcc.append(vars[3])
            R_pitchAcc.append(vars[4])
            R_yawAcc.append(vars[5])
            L_surgeAcc.append(vars[6])
            L_rollAcc.append(vars[7])
            R_surgeAcc.append(vars[8])
            R_rollAcc.append(vars[9])

            L_pitchVel.append(vars[10])
            L_yawVel.append(vars[11])
            R_pitchVel.append(vars[12])
            R_yawVel.append(vars[13])
            L_surgeVel.append(vars[14])
            L_rollVel.append(vars[15])
            R_surgeVel.append(vars[16])
            R_rollVel.append(vars[17])

            L_pitch.append(vars[18])
            L_yaw.append(vars[19])
            R_pitch.append(vars[20])
            R_yaw.append(vars[21])
            L_surge.append(vars[22])
            L_roll.append(vars[23])
            R_surge.append(vars[24])
            R_roll.append(vars[25])

            L_motion.append(vars[26])
            R_motion.append(vars[27])

    file.close()

    # Converts String values in array to numbers
    time = [f"{float(num):.2f}" for (num) in time]
    force = [f"{float(num):.2f}" for (num) in force]
    L_pitchAcc = [f"{float(num):.2f}" for (num) in L_pitchAcc]
    R_pitchAcc = [f"{float(num):.2f}" for (num) in R_pitchAcc]
    L_yawAcc = [f"{float(num):.2f}" for (num) in L_yawAcc]
    R_yawAcc = [f"{float(num):.2f}" for (num) in R_yawAcc]
    L_surgeAcc = [f"{float(num):.2f}" for (num) in L_surgeAcc]
    R_surgeAcc = [f"{float(num):.2f}" for (num) in R_surgeAcc]
    L_rollAcc = [f"{float(num):.2f}" for (num) in L_rollAcc]
    R_rollAcc = [f"{float(num):.2f}" for (num) in R_rollAcc]

    L_pitchVel = [f"{float(num):.2f}" for (num) in L_pitchVel]
    R_pitchVel = [f"{float(num):.2f}" for (num) in R_pitchVel]
    L_yawVel = [f"{float(num):.2f}" for (num) in L_yawVel]
    R_yawVel = [f"{float(num):.2f}" for (num) in R_yawVel]
    L_surgeVel = [f"{float(num):.2f}" for (num) in L_surgeVel]
    R_surgeVel = [f"{float(num):.2f}" for (num) in R_surgeVel]
    L_rollVel = [f"{float(num):.2f}" for (num) in L_rollVel]
    R_rollVel = [f"{float(num):.2f}" for (num) in R_rollVel]

    L_pitch = [f"{float(num):.2f}" for (num) in L_pitch]
    R_pitch = [f"{float(num):.2f}" for (num) in R_pitch]
    L_yaw = [f"{float(num):.2f}" for (num) in L_yaw]
    R_yaw = [f"{float(num):.2f}" for (num) in R_yaw]
    L_surge = [f"{float(num):.2f}" for (num) in L_surge]
    R_surge = [f"{float(num):.2f}" for (num) in R_surge]
    L_roll = [f"{float(num):.2f}" for (num) in L_roll]
    R_roll = [f"{float(num):.2f}" for (num) in R_roll]

    L_motion = [f"{float(num):.2f}" for (num) in L_motion]
    R_motion = [f"{float(num):.2f}" for (num) in R_motion]

    # Ensures float type 32bit
    # time = np.array(time) --> Don't need?
    force = np.array(force, dtype=np.float32)

    L_pitchAcc = np.array(L_pitchAcc, dtype=np.float32)
    R_pitchAcc = np.array(R_pitchAcc, dtype=np.float32)
    L_yawAcc = np.array(L_yawAcc, dtype=np.float32)
    R_yawAcc = np.array(R_yawAcc, dtype=np.float32)
    L_surgeAcc = np.array(L_surgeAcc, dtype=np.float32)
    R_surgeAcc = np.array(R_surgeAcc, dtype=np.float32)
    L_rollAcc = np.array(L_rollAcc, dtype=np.float32)
    R_rollAcc = np.array(R_rollAcc, dtype=np.float32)

    L_pitchVel = np.array(L_pitchVel, dtype=np.float32)
    R_pitchVel = np.array(R_pitchVel, dtype=np.float32)
    L_yawVel = np.array(L_yawVel, dtype=np.float32)
    R_yawVel = np.array(R_yawVel, dtype=np.float32)
    L_surgeVel = np.array(L_surgeVel, dtype=np.float32)
    R_surgeVel = np.array(R_surgeVel, dtype=np.float32)
    L_rollVel = np.array(L_rollVel, dtype=np.float32)
    R_rollVel = np.array(R_rollVel, dtype=np.float32)

    L_pitch = np.array(L_pitch, dtype=np.float32)
    R_pitch = np.array(R_pitch, dtype=np.float32)
    L_yaw = np.array(L_yaw, dtype=np.float32)
    R_yaw = np.array(R_yaw, dtype=np.float32)
    L_surge = np.array(L_surge, dtype=np.float32)
    R_surge = np.array(R_surge, dtype=np.float32)
    L_roll = np.array(L_roll, dtype=np.float32)
    R_roll = np.array(R_roll, dtype=np.float32)

    L_motion = np.array(L_motion, dtype=np.float32)
    R_motion = np.array(R_motion, dtype=np.float32)

    # Scaling down...
    """for i in range(len(L_surge)):
        L_surge[i] = L_surge[i]/500000

    for i in range(len(R_surge)):
        R_surge[i] = R_surge[i]/500000

    for i in range(len(L_roll)):
        L_roll[i] = L_roll[i]/500000

    for i in range(len(R_roll)):
        R_roll[i] = R_roll[i]/500000"""

    # Pitch
    ax[0, 0].plot(
        np.asarray(time, float),
        np.asarray(L_pitchAcc, float),
        visible=True,
        color="red",
        label="L_pitchAcc",
    )
    ax[0, 0].set_title("L_pitchAcc", fontsize=10)
    ax[0, 1].plot(np.asarray(time, float), R_pitchAcc, "tab:orange")
    ax[0, 1].set_title("R_pitchAcc", fontsize=10)
    ax[1, 0].plot(np.asarray(time, float), L_pitchVel, "tab:green")
    ax[1, 0].set_title("L_pitchVel", fontsize=10)
    ax[1, 1].plot(np.asarray(time, float), R_pitchVel, "tab:red")
    ax[1, 1].set_title("R_pitchVel", fontsize=10)
    ax[2, 0].plot(np.asarray(time, float), L_pitch, "tab:blue")
    ax[2, 0].set_title("L_pitch", fontsize=10)
    ax[2, 1].plot(np.asarray(time, float), R_pitch, "tab:blue")
    ax[2, 1].set_title("R_pitch", fontsize=10)

    # Yaw
    ax[3, 0].plot(np.asarray(time, float), L_yawAcc, "tab:orange")
    ax[3, 0].set_title("L_yawAcc", fontsize=10)
    ax[3, 1].plot(np.asarray(time, float), R_yawAcc, "tab:orange")
    ax[3, 1].set_title("R_yawAcc", fontsize=10)
    ax[4, 0].plot(np.asarray(time, float), L_yawVel, "tab:green")
    ax[4, 0].set_title("L_yawVel", fontsize=10)
    ax[4, 1].plot(np.asarray(time, float), R_yawVel, "tab:red")
    ax[4, 1].set_title("R_yawVel", fontsize=10)
    ax[5, 0].plot(np.asarray(time, float), L_yaw, "tab:blue")
    ax[5, 0].set_title("L_yaw", fontsize=10)
    ax[5, 1].plot(np.asarray(time, float), R_yaw, "tab:blue")
    ax[5, 1].set_title("R_yaw", fontsize=10)

    # Surge
    ax[6, 0].plot(np.asarray(time, float), L_surgeAcc, visible=True, color="red")
    ax[6, 0].set_title("L_surgeAcc", fontsize=10)
    ax[6, 1].plot(np.asarray(time, float), R_surgeAcc, "tab:orange")
    ax[6, 1].set_title("R_surgeAcc", fontsize=10)
    ax[7, 0].plot(np.asarray(time, float), L_surgeVel, "tab:green")
    ax[7, 0].set_title("L_surgeVel", fontsize=10)
    ax[7, 1].plot(np.asarray(time, float), R_surgeVel, "tab:red")
    ax[7, 1].set_title("R_surgeVel", fontsize=10)
    ax[8, 0].plot(np.asarray(time, float), L_surge, "tab:blue")
    ax[8, 0].set_title("L_surge", fontsize=10)
    ax[8, 1].plot(np.asarray(time, float), R_surge, "tab:blue")
    ax[8, 1].set_title("R_surge", fontsize=10)

    # Roll
    ax[9, 0].plot(np.asarray(time, float), -L_rollAcc, visible=True, color="red")
    ax[9, 0].set_title("L_rollAcc", fontsize=10)
    ax[9, 1].plot(np.asarray(time, float), R_rollAcc, "tab:orange")
    ax[9, 1].set_title("R_rollAcc", fontsize=10)
    ax[10, 0].plot(np.asarray(time, float), -L_rollVel, "tab:green")
    ax[10, 0].set_title("L_rollVel", fontsize=10)
    ax[10, 1].plot(np.asarray(time, float), R_rollVel, "tab:red")
    ax[10, 1].set_title("R_rollVel", fontsize=10)
    ax[11, 0].plot(np.asarray(time, float), -L_roll, "tab:blue")
    ax[11, 0].set_title("L_roll", fontsize=10)
    ax[11, 1].plot(np.asarray(time, float), R_roll, "tab:blue")
    ax[11, 1].set_title("R_roll", fontsize=10)

    # Force
    ax[12, 0].plot(np.asarray(time, float), force, "tab:blue")
    ax[12, 0].set_ybound(lower=-3, upper=3)
    ax[12, 0].set_title("Force", fontsize=10)

    # L motion
    ax[13, 0].plot(np.asarray(time, float), L_motion, "tab:blue")
    ax[13, 0].set_ybound(lower=-3, upper=3)
    ax[13, 0].set_title("L Motion", fontsize=10)

    # R motion
    ax[13, 1].plot(np.asarray(time, float), R_motion, "tab:blue")
    ax[13, 1].set_ybound(lower=-3, upper=3)
    ax[13, 1].set_title("R Motion", fontsize=10)

    # ------------------------3D Plot--------------------

    # ignore all future warnings
    simplefilter(action="ignore", category=FutureWarning)
    fig = plt.figure(figsize=plt.figaspect(0.5))
    # =============
    # First subplot
    # =============
    # set up the axes for the first plot
    ax2 = fig.add_subplot(1, 2, 1, projection="3d")
    ax2.set_title("Left Tool", fontsize=20)
    xLabel = ax2.set_xlabel("X-axis", linespacing=3.2)
    yLabel = ax2.set_ylabel("Y-axis", linespacing=3.1)
    zLabel = ax2.set_zlabel("Z-Axis", linespacing=3.4)
    # Data for a three-dimensional line for the left tool

    """countL0=0
    countL1=0

    for elem in L_motion:
        if elem == 0:
            countL0+= 1
        else:
            countL1+=1

    countR0 = 0
    countR1 = 0

    for elem in R_motion:
        if elem == 0:
            countR0+= 1
        else:
            countR1+=1

    if ((len(set(L_motion)) == 0)):
        for elem in L_surge:
            elem = 0

        for elem in L_roll:
            elem = 0

        for elem in L_motion:
            elem = 0"""

    yawLM = np.array(
        [
            [np.cos(L_yaw), 0, np.sin(L_yaw)],
            [0, 1, 0],
            [-np.sin(L_yaw), 0, np.cos(L_yaw)],
        ],
        dtype=object,
    )
    pitchLM = np.array(
        [
            [1, 0, 0],
            [0, np.cos(L_pitch), -np.sin(L_pitch)],
            [0, np.sin(L_pitch), np.cos(L_pitch)],
        ],
        dtype=object,
    )
    rollLM = np.array(
        [
            [np.cos(L_roll), -np.sin(L_roll), 0],
            [np.sin(L_roll), np.cos(L_roll), 0],
            [0, 0, 1],
        ],
        dtype=object,
    )
    surgeLM = np.array([[0], [0], [-L_surge]], dtype=object)
    rotationLM = np.dot(np.dot(np.dot(pitchLM, yawLM), rollLM), surgeLM)
    # L_toolx = np.array([[L_x], [0], [0]], dtype=object)
    # L_tooly = np.array([[0], [L_y], [0]], dtype=object)
    # L_toolz = np.array([[0], [0], [L_z]], dtype=object)
    # L_tool = np.add(np.add(L_toolx, L_tooly), L_toolz)
    L_tooltip = rotationLM
    vector = np.vectorize(float)

    ax2.plot(vector(L_tooltip[0][0]), vector(L_tooltip[1][0]), vector(L_tooltip[2][0]))

    # =============
    # Second subplot
    # =============
    # set up the axes for the first plot
    # set up the axes for the first plot
    ax3 = fig.add_subplot(1, 2, 2, projection="3d")
    ax3.set_title("Right Tool", fontsize=20)
    xLabel = ax3.set_xlabel("X-axis", linespacing=3.2)
    yLabel = ax3.set_ylabel("Y-axis", linespacing=3.1)
    zLabel = ax3.set_zlabel("Z-Axis", linespacing=3.4)

    # Data for a three-dimensional line for the left tool

    yawRM = np.array(
        [
            [np.cos(R_yaw), 0, np.sin(R_yaw)],
            [0, 1, 0],
            [-np.sin(R_yaw), 0, np.cos(R_yaw)],
        ],
        dtype=object,
    )
    pitchRM = np.array(
        [
            [1, 0, 0],
            [0, np.cos(R_pitch), -np.sin(R_pitch)],
            [0, np.sin(R_pitch), np.cos(R_pitch)],
        ],
        dtype=object,
    )
    rollRM = np.array(
        [
            [np.cos(R_roll), -np.sin(R_roll), 0],
            [np.sin(R_roll), np.cos(R_roll), 0],
            [0, 0, 1],
        ],
        dtype=object,
    )
    surgeRM = np.array([[0], [0], [R_surge]], dtype=object)
    rotationRM = np.dot(np.dot(np.dot(pitchRM, yawRM), rollRM), surgeRM)
    # R_toolx = np.array([[R_x], [0], [0]], dtype=object)
    # R_tooly = np.array([[0], [R_y], [0]], dtype=object)
    # R_toolz = np.array([[0], [0], [R_z]], dtype=object)
    # R_tool = np.add(np.add(R_toolx, R_tooly), R_toolz)
    R_tooltip = rotationRM
    vector = np.vectorize(float)

    ax3.plot(vector(R_tooltip[0][0]), vector(R_tooltip[1][0]), vector(R_tooltip[2][0]))

    print("")
    """print(np.average(L_pitch))
    print(np.average(L_yaw))
    print(np.average(L_roll))
    print(np.average(L_surge))
    print(np.average(L_x))
    print(np.average(L_y))
    print(np.average(L_z))"""

    # print("-----")
    """print(np.average(R_pitch)) 
    print(np.average(R_yaw))
    print(np.average(R_roll))
    print(np.average(R_surge))
    print(np.average(R_x))
    print(np.average(R_y))
    print(np.average(R_z))"""

    print("Left Surge")
    print(L_surge)
    print("")
    print("Left Roll")
    print(L_roll)
    print("")

    """print("L Yaw")
    print(L_yaw)
    print("")
    print("L Pitch")
    print(L_pitch)
    print("")"""

    """print("R Yaw")
    print(R_yaw)
    print("")
    print("R Pitch")
    print(R_pitch)
    print("")"""

    print("Right Surge")
    print(R_surge)
    print("")
    print("Right Roll")
    print(R_roll)
    print("")

    print("L Motion")
    print(L_motion)
    print("")
    print("R Motion")
    print(R_motion)
    print("")

    plt.show()
    plt2.show()


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    plot_all_data()
