#  Start with command:
#  streamlit run "C:\Users\MikolajPawlak\Documents\GitHub\Public-projects\Hevy Workout App Analytics Dashboard\Hevy_app.py"
import streamlit as st
import pandas as pd
import os
import io
from PIL import Image, ImageDraw
import datetime
import matplotlib.pyplot as plt
import ast


from find_recent_workout_file import find_recent_workout_file
from human_body_painting import paint
from run_another_python_script import run_sub_script_with_progress


def aggregate_to_list(series):
        # Filter out NaN values and convert to list
        return series.dropna().tolist()

# Specify the path to the directory you want to set as the working directory
app_directory = r'C:\Users\MikolajPawlak\Documents\GitHub\Public-projects\Hevy Workout App Analytics Dashboard'

# Change the current working directory to the specified directory
os.chdir(app_directory)

default_file = find_recent_workout_file(app_directory)
# read data and prepare it for the app


df = pd.read_csv(default_file, index_col=0)
df['start_time'] = pd.to_datetime(df['start_time'])
df['end_time'] = pd.to_datetime(df['end_time'])
df['year'] = df['start_time'].dt.year.astype(str)
df['month'] = df['start_time'].dt.month
df['duration_seconds'] = df['duration_seconds']/60
# Capitalize muscle names
df['primary_muscle_group'] = [muscle_name.capitalize() for muscle_name in df['primary_muscle_group']]
df['secondary_muscle_groups'] = [[item.capitalize() for item in ast.literal_eval(lst)] for lst in df['secondary_muscle_groups']]


df.rename(columns={'duration_seconds': 'duration_minutes'}, inplace= True)
min_date = df['start_time'].min().date()
max_date = df['end_time'].max().date()

st.set_page_config(layout="wide")
st.title(":red-background[Hevy workouts analysis] ")


#######################################
############### CHOISES ###############
#######################################

choice = st.radio('Choose option',
        ['Get your data','Overall analysis', 'Muscle group analysis'],
        horizontal=True)

if choice == 'Get your data':
    
    # Ask user for api_key
    st.write(":orange-background[Provide your *API_KEY* for Hevy workouts and click *Download data* button]")
    HEVY_API_KEY = st.text_input("API_KEY")
    api_ready_button = st.button("Download data")
    if HEVY_API_KEY and api_ready_button:
        st.write(":red[Please don't leave this page]. Data download process started...")
        
        # Run the  script with the argument
        command = f'python Hevy_API_workouts_app.py --HEVY_API_KEY {HEVY_API_KEY}'
        run_sub_script_with_progress(command)
    else:
        st.write("Goodbye")


elif choice == 'Overall analysis':
    #######################################
    ############### FILTERS ###############
    #######################################
    filters_row = st.columns(3)
    for col in filters_row:
        with col.container(border= True):
            if col == filters_row[0]:
                # Add a slider to the Streamlit app for selecting a date
                selected_date = st.slider(
                    "Select date range",
                    min_value = min_date,
                    max_value = max_date,
                    value=(min_date, max_date),  # Default value
                    format="YYYY-MM-DD"
                )
            if col == filters_row[1]:
                # Add a dropbox to choose muslce groups
                muscle_groups_primary = sorted(df.primary_muscle_group.unique())
                primary_muscle_groups_choice = st.multiselect("Primary muscle group", muscle_groups_primary, default=None, placeholder="Choose an option", disabled=False, label_visibility="visible")
                
            if col == filters_row[2]:
                # Add a dropbox to choose muslce groups
                muscle_groups = sorted(df.primary_muscle_group.unique())
                muscle_groups_secondary =  [m for m in muscle_groups if m not in primary_muscle_groups_choice]
                secondary_muscle_groups_choice = st.multiselect("Secondary muscle group", muscle_groups_secondary, default=None, placeholder="Choose an option", disabled=False, label_visibility="visible")
                
    # Filter the dataframe
    # 1. Date
    df = df[(df['start_time'].dt.date >= selected_date[0])  & (df['end_time'].dt.date <= selected_date[1])]
    # 2. Muscle, don't filter if:
    # - if nothing is selected
    if primary_muscle_groups_choice:
        df = df[(df['primary_muscle_group'].isin(primary_muscle_groups_choice))]
    if secondary_muscle_groups_choice:
        df = df[(df['secondary_muscle_groups'].isin(secondary_muscle_groups_choice))]
        
    if (not primary_muscle_groups_choice) and (not secondary_muscle_groups_choice):
        primary_muscle_groups_choice = sorted(df.primary_muscle_group.unique())
        secondary_muscle_groups_choice = pd.unique([item for sublist in df['secondary_muscle_groups'] for item in sublist])

    #######################################
    ############### METRICS ###############
    #######################################


    # Metric 1 - number of workouts
    num_of_workouts = len(df['workout_id'].unique())

    # Metric 2 - average workout time
    df['time'] = df['end_time'] - df['start_time']
    df['weight_total_kg'] = df['reps'] * df['weight_kg']
    grouped_workouts = df.groupby(['workout_id', 'time', 'start_time', 'end_time' ,'year']).agg(
        num_exercises=('excercise_title', 'nunique'),
        weight_total_kg=('weight_total_kg', 'sum') # Sum of weight per workout# Count unique exercises
    ).reset_index()
    grouped_workouts.index +=1
    average_time = grouped_workouts.time.apply(pd.to_timedelta).mean()
    average_time_formatted = str(average_time).split()[-1].split('.')[0]

    # Metric 3 - average number of exercises per workout
    average_exercises = round(grouped_workouts['num_exercises'].mean(),2)

    # Metric 4 - average number of sets per exercise
    grouped_exercises = df.groupby(['workout_id','excercise_title']).agg(
        num_of_sets=('set_index', 'count')  # Average sets per workout
    ).reset_index()
    average_sets = round(grouped_exercises['num_of_sets'].mean(),2)

    metric_row = st.columns(4)

    for col in metric_row:
        with col.container(border= True):
            if col == metric_row[0]:
                st.metric("Workouts", num_of_workouts, delta=None, delta_color="normal", help=None, label_visibility="visible")
            elif col == metric_row[1]:
                st.metric("Average Workout Time", average_time_formatted, delta=None, delta_color="normal", help=None, label_visibility="visible")
            elif col == metric_row[2]:
                st.metric("Average Number Of Exercises Per Workout", average_exercises, delta=None, delta_color="normal", help=None, label_visibility="visible")
            elif col == metric_row[3]:
                st.metric("Average Number Of Sets Per Exercise", average_sets, delta=None, delta_color="normal", help=None, label_visibility="visible")
        
        
        #######################################
        ############### CHARTS ################
        #######################################

    # Show line chart
    # container_chart = st.container(border=True)
    # container_chart.line_chart(grouped_workouts[['num_exercises', 'start_time' ,'year']], 
    #             x = 'start_time', y = 'num_exercises', color = 'year', 
    #             x_label ='Workout_number', y_label ='Number of Exercises')
    
        # Show line chart
    container_chart = st.container(border=True)
    container_chart.scatter_chart(grouped_workouts[['num_exercises', 'start_time' ,'year', 'weight_total_kg']], 
                x = 'start_time', y = 'weight_total_kg', color = 'year', size ='num_exercises',
                x_label ='Workout_number', y_label ='Total Weight in Kg', height = 500)

    # Show dataframe
    st.dataframe(df)
    # workout time
    # load 

    

elif choice == 'Muscle group analysis':

    #######################################
    ############### FILTERS ###############
    #######################################

    filters_row = st.columns(4)
    for col in filters_row:
        with col.container(border= True):
            if col == filters_row[0]:
                # Add a slider to the Streamlit app for selecting a date
                selected_date = st.slider(
                    "Select date range",
                    min_value = min_date,
                    max_value = max_date,
                    value=(min_date, max_date),  # Default value
                    format="YYYY-MM-DD"
                )
            if col == filters_row[1]:
                # Add a dropbox to choose exercise (by title)
                selected_exercises = []
                selected_exercises = st.multiselect("Exercise title", sorted(df['excercise_title'].unique().tolist()), default=None, placeholder="Choose an option", disabled=False, label_visibility="visible")
                
            if col == filters_row[2]:
                # Add a dropbox to choose muslce groups
                muscle_groups_primary = sorted(df.primary_muscle_group.unique())
                primary_muscle_groups_choice = st.multiselect("Primary muscle group", muscle_groups_primary, default=None, placeholder="Choose an option", disabled=False, label_visibility="visible")
                
            if col == filters_row[3]:
                # Add a dropbox to choose muslce groups
                muscle_groups = sorted(df.primary_muscle_group.unique())
                muscle_groups_secondary =  [m for m in muscle_groups if m not in primary_muscle_groups_choice]
                secondary_muscle_groups_choice = st.multiselect("Secondary muscle group", muscle_groups_secondary, default=None, placeholder="Choose an option", disabled=False, label_visibility="visible")
                
    # Filter the dataframe
    # 1. Date
    df = df[(df['start_time'].dt.date >= selected_date[0])  & (df['end_time'].dt.date <= selected_date[1])]
    # 2. Exercise title
    if selected_exercises:
        df = df[df['excercise_title'].isin(selected_exercises)]
    # 3. Muscle, don't filter if:
    # - if no filter is selected
    if primary_muscle_groups_choice:
        df = df[(df['primary_muscle_group'].isin(primary_muscle_groups_choice))]
    if secondary_muscle_groups_choice:
        df = df[(df['secondary_muscle_groups'].isin(secondary_muscle_groups_choice))]
        
    if selected_exercises and (not primary_muscle_groups_choice) and (not secondary_muscle_groups_choice):
        primary_muscle_groups_choice = sorted(df.primary_muscle_group.unique())
        secondary_muscle_groups_choice = pd.unique([item for sublist in df['secondary_muscle_groups'] for item in sublist])

    df['primary_muscle_group'] = [[muscle] for muscle in df['primary_muscle_group']]
    
    #col1, col2 = st.columns([2.55,1])
    col1, col2 = st.columns([2.75,1])
    col1.dataframe(df[['workout_title', 'excercise_title', 'primary_muscle_group', 'secondary_muscle_groups', 'weight_kg', 'reps', 'distance_meters', 'duration_minutes', 'is_custom']])
    

    df_temp = df[['workout_id', 'workout_title', 'excercise_title', 'primary_muscle_group', 'secondary_muscle_groups', 'weight_kg', 'reps', 'distance_meters', 'duration_minutes']]

    # Group by 'excercise_title' and aggregate using the custom function
    grouped = df.groupby('excercise_title').agg({
    'reps': aggregate_to_list,
    'weight_kg': aggregate_to_list,
    'distance_meters': aggregate_to_list,
    'duration_minutes': aggregate_to_list,
     #### <--- ADD HERE MAX VOLUME reps * weight_kg 
    }).reset_index()
    
    # Rename columns in a more concise way
    grouped['max_reps'] = [max(reps) if reps else '' for reps in grouped['reps']]
    grouped['max_weight_kg'] = [max(reps) if reps else '' for reps in grouped['weight_kg']]
    grouped['max_distance_meters'] = [max(reps) if reps else '' for reps in grouped['distance_meters']]
    grouped['max_duration_minutes'] = [max(reps) if reps else '' for reps in grouped['duration_minutes']]

    st.dataframe(
    grouped[['excercise_title', 'max_reps', 'max_weight_kg', 'max_distance_meters','max_duration_minutes']])


    # Show image
    image = paint(primary_muscle_groups_choice, secondary_muscle_groups_choice)
    new_size = (int(image.width // 2.5), int(image.height // 2.5))
    image = image.resize(new_size, Image.LANCZOS)
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='PNG')
    image_bytes.seek(0)

    # Display the image in Streamlit
    col2.image(image_bytes, caption='Workout', use_column_width=False)