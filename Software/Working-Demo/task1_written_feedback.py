
import csv

# Function to check the existence of each possible signal in the CSV column
def check_signals_in_column(csv_file_path, column_name, custom_messages):
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        # Create a list of all the values in the specified column
        column_data = [row[column_name] for row in reader]

    # Dictionary to hold the existence result and corresponding custom message for each signal
    signals_existence_messages = {}

    # Check for each signal's existence in the column data
    for signal in custom_messages.keys():
        if signal in column_data:
            # Use the custom message for when the signal exists
            signals_existence_messages[signal] = custom_messages[signal]

    return signals_existence_messages

# Defining custom messages here
custom_messages = {
    'Ref_task1_L_pitchVel': "Slow down speed of upward-downward or downward-upward motion with the left tool",
    'Ref_task1_R_pitchVel': "Slow down speed of upward-downward or downward-upward motion with the right tool",
    'Ref_task1_R_pitchAcc': "Avoid rapid movements while moving tool up-down or down-up with the right tool",
    'Ref_task1_L_pitchAcc': "Avoid rapid movements while moving tool up-down or down-up with the left tool",
    'Ref_task1_R_yawVel': "Slow down speed of left-right or right-left motion with the right tool",
    'Ref_task1_L_yawVel': "Slow down speed of left-right or right-left motion with the left tool",
    'Ref_task1_R_yawAcc': "Avoid rapid movements while moving right tool right-left or left-right",
    'Ref_task1_L_yawAcc': "Avoid rapid movements while moving left tool right-left or left-right",
    'Ref_task1_R_yaw': "Remain within range when moving right tool left-right or right-left",
    'Ref_task1_L_yaw': "Remain within range when moving left tool left-right or right-left",
    'Ref_task1_L_rollVel': "Slow down speed while rotating left tool",
    'Ref_task1_R_rollVel': "Slow down speed while rotating right tool",
    'Ref_task1_R_rollAcc': "Avoid rapidly rotating left tool",
    'Ref_task1_L_rollAcc': "Avoid rapidly rotating right tool",
    'Ref_task1_R_roll': "Remain within range while rotating right tool",
    'Ref_task1_L_roll': "Remain within range while rotating left tool",
    'Ref_task1_L_surgeVel': "Slow down speed while pulling left tool in or out of trocar",
    'Ref_task1_R_surgeVel': "Slow down speed while pulling right tool in or out of trocar",
    'Ref_task1_R_surgeAcc': "Avoid rapidly pulling right tool in or out",
    'Ref_task1_L_surgeAcc': "Avoid rapidly pulling left tool in or out",
    'Ref_task1_R_surge': "Remain within range while pulling right tool in or out of trocar",
    'Ref_task1_L_surge': "Remain within range while pulling left tool in or out of trocar"
}

# Usage of the function
csv_file_path = 'task1_weak_signal_performance.csv'  # Replace with your CSV file path
column_name = 'Ref Signal'  # Replace with your column name

# Call the function and print the results
signals_existence_messages = check_signals_in_column(csv_file_path, column_name, custom_messages)

# Print the custom messages for each signal
for signal, message in signals_existence_messages.items():
    print(message)
