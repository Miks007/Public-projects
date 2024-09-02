import subprocess
import time
import os
from glob import glob
import streamlit as st

def find_latest_log_file(base_log_dir="logs"):
    # Find the newest log folder based on the date
    log_folders = glob(os.path.join(base_log_dir, "*/"))
    if not log_folders:
        raise FileNotFoundError("No log folders found.")

    # Sort folders by modification time (newest first)
    log_folders.sort(key=os.path.getmtime, reverse=True)
    newest_log_folder = log_folders[0]

    # Find the newest log file in the newest log folder
    log_files = glob(os.path.join(newest_log_folder, "*.log"))
    if not log_files:
        raise FileNotFoundError("No log files found in the latest log folder.")

    # Sort log files by modification time (newest first)
    log_files.sort(key=os.path.getmtime, reverse=True)
    newest_log_file = log_files[0]

    return newest_log_file


def run_sub_script_with_progress(command):
    # command example: python another_script.py --key 1234  # Use 'python3' if required
    # Path to the script B
    script_b_path = os.path.dirname(os.path.abspath(__file__))

    # Start script B
    process = subprocess.Popen(command)
    
    # Find the latest log file dynamically
    try:
        time.sleep(2)
        log_file_path = find_latest_log_file()
        #st.write(f"Reading from log file: {log_file_path}")

        # Open the log file in read mode
        with open(log_file_path, 'r') as log_file:

            for line in log_file:
                st.write(line, end='')  # Print each line without adding extra newlines
                
            try:
                # Continuously read new lines from the log file
                while process.poll() is None:  # While script B is running
                    line = log_file.readline()
                    if line:
                        st.write(line, end='')  # Print each line without adding extra newlines
                    else:
                        time.sleep(0.1)  # Wait a bit before trying to read again
            except KeyboardInterrupt:
                # If the user interrupts, terminate the process
                process.terminate()
                st.write("Process terminated.")

    except FileNotFoundError as e:
        st.write(e)