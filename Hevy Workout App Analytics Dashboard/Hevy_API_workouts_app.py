import requests
import argparse
import pandas as pd
import math
import logging
from datetime import datetime
import os
import tqdm
import sys

def setup_logging():
    global log_file, log_dir, bot_result
    bot_result = {}
    # Create a 'logs' directory
    log_dir = os.path.join(os.getcwd(), 'logs', datetime.now().strftime('%Y-%m-%d'))
    os.makedirs(log_dir, exist_ok=True)

    # Configure the logging module
    log_file = os.path.join(log_dir, f'Hevy_{datetime.now().strftime("%d%m%Y_%H%M%S")}.log')
    logging.basicConfig(
        level=logging.INFO,
        format='\n%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(),
        ]
    )

def get_workout_count(HEVY_API_KEY):
    try:
        url = f'https://api.hevyapp.com/v1/workouts/count'
        headers = {
            'accept': 'application/json',
            'api-key': HEVY_API_KEY
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            print('Workout count:', data['workout_count'])
            logging.info(f'Workout count: {data["workout_count"]}')
            return int(data['workout_count'])
        elif response.status_code == 401:
            logging.error(f"Failed to retrieve data. Unauthorized access: {response.status_code}")
        else:
            logging.error(f"Failed to retrieve data: {response.status_code}")
    except Exception as e:
        logging.error(f"Error: Error during get_workout_count() \n {str(e)}")


def get_workouts(HEVY_API_KEY, page = int, pageSize = int):
    ''' 
    Fetches workout data from the Hevy API and organizes it into DataFrames.

    Parameters:
    - page (int): The page number to start fetching workouts from (1-indexed).
        Must be an integer greater than  1.
    - pageSize (int): The number of workouts to fetch per page.
        Must be an integer in the range [1, 10] and greater than 'page'.

    Returns:
    - df_workouts (pd.DataFrame): A DataFrame containing distinct workout details.
    - df_exercises (pd.DataFrame): A DataFrame containing details of exercises performed during the workouts.
    - df_sets (pd.DataFrame): A DataFrame containing details of each set performed within the exercises
    '''

    try:
        if not (1 <= page):
            raise ValueError("Page must be atleast than 1.")
        if not (1 <= pageSize <= 10):
            raise ValueError("PageSize must be in the range [1, 10].")

        logging.info(f'Fetching workouts from page: {str(page)} (pageSize:{str(pageSize)})')

        url = f'https://api.hevyapp.com/v1/workouts?page={page}&pageSize={pageSize}&since=1970-01-01T00%3A00%3A00Z'
        headers = {
            'accept': 'application/json',
            'api-key': HEVY_API_KEY
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            workouts = data['workouts']

            # Initialize lists to collect data
            workout_list = []
            exercise_list = []
            set_list = []

            # Loop through workouts
            for workout in workouts:
                workout_id = workout['id']
                workout_title = workout['title']
                workout_description = workout['description']
                start_time = workout['start_time']
                end_time = workout['end_time']

                # Add workout to the list
                workout_list.append({
                    'workout_id': workout_id,
                    'title': workout_title,
                    'description': workout_description,
                    'start_time': start_time,
                    'end_time': end_time
                })

                # Loop through exercises
                for exercise in workout['exercises']:
                    exercise_index = exercise['index']
                    exercise_title = exercise['title']
                    exercise_notes = exercise['notes']
                    exercise_template_id = exercise['exercise_template_id']
                    superset_id = exercise['superset_id']

                    # Add exercise to the list
                    exercise_list.append({
                        'workout_id': workout_id,
                        'exercise_index': exercise_index,
                        'title': exercise_title,
                        'notes': exercise_notes,
                        'exercise_template_id': exercise_template_id,
                        'superset_id': superset_id
                    })

                    # Loop through sets
                    for set_ in exercise['sets']:
                        set_index = set_['index']
                        set_type = set_['set_type']
                        weight_kg = set_['weight_kg']
                        reps = set_['reps']
                        distance_meters = set_['distance_meters']
                        duration_seconds = set_['duration_seconds']
                        rpe = set_['rpe']

                        # Add set to the list
                        set_list.append({
                            'workout_id': workout_id,
                            'exercise_index': exercise_index,
                            'set_index': set_index,
                            'set_type': set_type,
                            'weight_kg': weight_kg,
                            'reps': reps,
                            'distance_meters': distance_meters,
                            'duration_seconds': duration_seconds,
                            'rpe': rpe
                        })

            # Create DataFrames
            df_workouts = pd.DataFrame(workout_list)
            df_exercises = pd.DataFrame(exercise_list)
            df_sets = pd.DataFrame(set_list)
            return df_workouts, df_exercises, df_sets
        else:
            logging.error(f"Failed to retrieve data: {response.status_code}")
    except Exception as e:
        logging.error(f"Error: Error during workouts fetch \n {str(e)}")

def get_templates(HEVY_API_KEY, df):
    try:
        df_decoded_templates = pd.DataFrame()
        data_list = []
        templates_total = len(df.exercise_template_id.unique())
        logging.info(f'Found {templates_total} unique templates to decode. Starting to decode ...')
        cntr = 0
        for template_id in df.exercise_template_id.unique():
            cntr += 1 
            url = f'https://api.hevyapp.com/v1/exercise_templates/{template_id}'
            headers = {
                'accept': 'application/json',
                'api-key': HEVY_API_KEY
            }
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                data_list.append(data)
                df_decoded_templates = pd.DataFrame(data_list)
            if cntr % 10 == 0 or cntr == templates_total:
                logging.info(f"Decoded templates {cntr}/{templates_total}.")
        logging.info(f"All templates decoded.")
        df_full = df.merge(df_decoded_templates, how = 'left', left_on= 'exercise_template_id', right_on='id')
        return df_full
    except Exception as e:
        logging.error(f"Error: Error during reading config.ini file \n {str(e)}")

# Define the main function
def main():
    try:
        # Start logging
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        setup_logging()
        # Get HEVY_API_KEY from arguments
        parser = argparse.ArgumentParser(description='Script that uses HEVY_API_KEY')
        parser.add_argument('--HEVY_API_KEY', required=True, help='API key for HEVY')
        args = parser.parse_args()
        HEVY_API_KEY = args.HEVY_API_KEY
        
        logging.error(f"API KEY: ", HEVY_API_KEY)
        
        
        # Get count of workouts
        workout_count = get_workout_count(HEVY_API_KEY)

        # Define empty variables
        df_workouts = pd.DataFrame()
        df_exercises = pd.DataFrame()
        df_sets = pd.DataFrame()

        # Get all workouts based on workcout_count
        logging.info(f'Workout pages count: {math.ceil(workout_count/10)}.')
        for page in range(math.ceil(workout_count/10)):
            page = page + 1 
            df_workouts_temp, df_exercises_temp, df_sets_temp = get_workouts(HEVY_API_KEY,page,10)

            df_workouts = pd.concat([df_workouts, df_workouts_temp], ignore_index=True)
            df_exercises = pd.concat([df_exercises, df_exercises_temp], ignore_index=True)
            df_sets = pd.concat([df_sets, df_sets_temp], ignore_index=True)
        
        logging.info(f'Fetch done. Total workouts got: {str(len(df_workouts))}')

        # Merge all dataframes
        df_merged = pd.merge(df_workouts, df_exercises, how = 'left', on= 'workout_id')
        df_merged = pd.merge(df_merged, df_sets, how = 'left', on= ['workout_id', 'exercise_index'])
        
        # Adjust column names
        df_merged.rename(columns={'title_x': 'workout_title', 'title_y': 'excercise_title'}, inplace= True)

        # Decode templates 
        df_full = get_templates(HEVY_API_KEY, df_merged)

        # Save data to a csv file
        file_name = 'hevy_workouts_' + datetime.now().strftime('%Y_%m_%d') + '.csv'
        df_full.to_csv(file_name)
        logging.info(f'Workouts data saved to: {file_name})')
    except Exception as e:
        logging.error(f'Error in main: {str(e)}')

if __name__ == '__main__':
    main()