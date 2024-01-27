#  coding=utf-8
import sys, os, time, subprocess

ffmpegpath = os.path.join(os.getcwd(), r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\ffmpeg.exe")


def check():
    if os.path.exists(ffmpegpath):
        text = "Batch AVI to MP4 Conversion Tool\n"
        text += "Program initialized successfully!\n"
        text += "=============================================\n"
        print(text)
        return True
    else:
        print("ffmpeg.exe not found, please ensure all files have been extracted!")
        return False


def convert_to_mp4(avi_file_path, export_path):
    try:
        subprocess.run([ffmpegpath, '-y', '-i', avi_file_path, '-vcodec', 'h264', '-acodec', 'aac', '-strict', '-2', f"{export_path}.mp4"])
        print(f"Converted {avi_file_path} to {export_path}.mp4 successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to convert file {avi_file_path}. Error: {e}")


def start():
    path = input("Please enter the path to the folder containing AVI videos: ")
    export_path = input("Please enter the export path: ")
    for (dirpath, dirname, dirfile) in os.walk(path):
        for fileName in dirfile:            # Iterate through all files in the directory
            try:
                fileType = fileName.split(".")[-1]
                if fileType in ["avi"]:     # Check file type
                    avi_file_path = os.path.join(dirpath, fileName)
                    convert_to_mp4(avi_file_path, os.path.join(export_path, fileName.split(".")[0]))           # Execute conversion function
            except IOError as e:
                print(f"Failed to convert file {fileName}")
                print(f"Error: {str(e)}")


def welcome():
    text = "  /$$$$$$  /$$$$$$$  /$$      /$$       /$$      /$$                 /$$          \n"
    text += " /$$__  $$| $$__  $$| $$$    /$$$      | $$$    /$$$                | $$          \n"
    text += "|__/  \ $$| $$  \ $$| $$$$  /$$$$      | $$$$  /$$$$  /$$$$$$   /$$$$$$$  /$$$$$$$\n"
    text += "   /$$$$$/| $$  | $$| $$ $$/$$ $$      | $$ $$/$$ $$ /$$__  $$ /$$__  $$ /$$_____/\n"
    text += "  |___  $$| $$  | $$| $$  $$$| $$      | $$  $$$| $$| $$  \ $$| $$  | $$|  $$$$$$ \n"
    text += " /$$  \ $$| $$  | $$| $$\  $ | $$      | $$\  $ | $$| $$  | $$| $$  | $$ \____  $$\n"
    text += "|  $$$$$$/| $$$$$$$/| $$ \/  | $$      | $$ \/  | $$|  $$$$$$/|  $$$$$$$ /$$$$$$$/\n"
    text += " \______/ |_______/ |__/     |__/      |__/     |__/ \______/  \_______/|_______/ \n"
    print(text)


welcome()
if check():
    start()
    YorN = input("Video conversion complete. Do you want to convert more videos? (Y/N)")
    if YorN.upper() == "Y":
        start()
else:
    print("Program terminated")
    time.sleep(5)
