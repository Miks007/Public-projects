import os
import re
from datetime import datetime
import logging


def find_recent_workout_file(directory):
    '''
    Find the most recent Hevy workoutfile based on the file name.
    The file must be named in this pattern: hevy_workouts_(\d{4}_\d{2}_\d{2})\.csv
    For example: "hevy_workouts_2024_06_27.csv" where 2024_06_27 is a date of a file creation.
    Input:
    - directory - a directory path where the function will search for a file.
    Output:
    - most_recent_file - a file name of the most recent file based on date in name.
    '''
    try:
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

        # For all csv files find those that match the pattern and found which one is most recent
        for file in files:
            date = extract_date(file)
            if date:
                if not most_recent_date or date > most_recent_date:
                    most_recent_date = date
                    most_recent_file = file
        
        # If no matching file was found then return that info
        if not most_recent_file:
            most_recent_file = "No matching files found."
        return most_recent_file
    except Exception as e:
        logging.error(f"Error: Error during reading most recent file \n {str(e)}")
