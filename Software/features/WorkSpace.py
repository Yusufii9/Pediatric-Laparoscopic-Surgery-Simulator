import cv2
import numpy as np

def calculate_distance(point1, point2):
    return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def update_bar(frame, distance):
    # Calculate the position for the bar based on the distance
    bar_position = int((distance - 50) / 500 * frame.shape[0])

    # Draw the spectrum bar on the left side of the frame
    cv2.rectangle(frame, (0, 0), (20, frame.shape[0]), (255, 255, 255), -1)  # White background
    cv2.rectangle(frame, (0, frame.shape[0] - bar_position), (20, frame.shape[0]), get_color(distance), -1)

def get_color(distance):
    if distance <= 100:
        return (0, 255, 0)  # Green
    elif distance <= 550:
        return (255, 165, 0)  # Orange
    else:
        return (0, 0, 255)  # Red

def main():
    # Initialize camera or video capture
    cap = cv2.VideoCapture(0)  # 0 represents the default camera (you can change it based on your setup)

    while True:
        # Read a frame from the camera
        ret, frame = cap.read()

        # Convert the frame to HSV for better color filtering
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Define the lower and upper bounds for yellow color in HSV
        lower_yellow = np.array([20, 100, 100])
        upper_yellow = np.array([40, 255, 255])

        # Create a binary mask for yellow color
        yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

        # Find contours in the binary image
        contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter out small contours
        contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 500]

        # Extract positions of the two pen tips (assuming there are at least two contours)
        if len(contours) >= 2:
            pen1_tip = tuple(contours[0][:, 0][np.argmin(contours[0][:, 0][:, 0])])
            pen2_tip = tuple(contours[1][:, 0][np.argmax(contours[1][:, 0][:, 0])])

            # Calculate the distance between the two pen tips
            distance = calculate_distance(pen1_tip, pen2_tip)

            # Display the distance
            print(f"Distance between pen tips: {distance:.2f} mm")

            # Update and display the spectrum bar
            update_bar(frame, distance)

            # Check if the distance is within the specified range
            if 50 <= distance <= 100:
                status = "Not good"
            elif distance <= 550:
                status = "Good"
            else:
                status = "Unknown"

            # Display the status on the frame
            cv2.putText(frame, f"Status: {status}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Display the frame
        cv2.imshow("Pen Tracking", frame)

        # Break the loop if 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the camera
    cap.release()

    # Close all OpenCV windows
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
