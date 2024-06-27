import os
import re
from datetime import datetime

def find_recent_workout_file(directory):
    # Pattern to recognize the date in the file names
    pattern = re.compile(r'hevy_workouts_(\d{4}_\d{2}_\d{2})\.csv')

    # Function to extract date from file name
    def extract_date(filename):
        match = pattern.search(filename)
        if match:
            return datetime.strptime(match.group(1), '%Y_%m_%d')
        return None

    # List all files in the directory
    files = [file for file in os.listdir(directory) if file.endswith('.csv')]

    # Extract dates and find the most recent file
    most_recent_date = None
    most_recent_file = None

    for file in files:
        date = extract_date(file)
        if date:
            if not most_recent_date or date > most_recent_date:
                most_recent_date = date
                most_recent_file = file

    if not most_recent_file:
        most_recent_file = "No matching files found."
    return most_recent_file
