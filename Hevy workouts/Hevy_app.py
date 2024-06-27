#  Start with command -  streamlit run "C:\Users\MikolajPawlak\Documents\GitHub\Public-projects\Hevy workouts\Hevy_app.py"
import streamlit as st
import pandas as pd
import os
import io
from PIL import Image, ImageDraw
import datetime
import matplotlib.pyplot as plt


from find_recent_workout_file import find_recent_workout_file
from human_body_painting import paint


def aggregate_to_list(series):
        # Filter out NaN values and convert to list
        return series.dropna().tolist()

# Specify the path to the directory you want to set as the working directory
app_directory = r'C:\Users\MikolajPawlak\Documents\GitHub\Public-projects\Hevy workouts'

# Change the current working directory to the specified directory
os.chdir(app_directory)

default_file = find_recent_workout_file(app_directory)
# read data and prepare it for the app


df = pd.read_csv(default_file, index_col=0)
df['start_time'] = pd.to_datetime(df['start_time'])
df['end_time'] = pd.to_datetime(df['end_time'])
df['year'] = df['start_time'].dt.year.astype(str)
df['month'] = df['start_time'].dt.month
min_date = df['start_time'].min().date()
max_date = df['end_time'].max().date()

st.set_page_config(layout="wide")
st.write(""" # Hevy workouts analysis """)


#######################################
############### CHOISES ###############
#######################################

choice = st.radio('Choose analysis option',
         ['Overall', 'Period comparison', 'Muscle' ],
         horizontal=True)

if choice == 'Overall':
    #######################################
    ############### FILTERS ###############
    #######################################
    filters_row = st.columns(2)
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
                muscle_groups = ['All','Back', 'Chest', 'Core', 'Shoulders', 'Arms', 'Legs']
                muscle_groups_choice = eval(str(st.multiselect("Muscle group", muscle_groups, default='All', placeholder="Choose an option", disabled=False, label_visibility="visible")))
    
    # Filter the dataframe
    # 1. Date
    df = df[(df['start_time'].dt.date >= selected_date[0])  & (df['end_time'].dt.date <= selected_date[1])]
    # 2. Muscle, don't filter if:
    # - if All is selected
    # - if nothing is selected
    if not ('All' in muscle_groups_choice) and len(muscle_groups_choice)>0:
        df = df[(df['primary'].isin(muscle_groups_choice)) | (df['secondary'].isin(muscle_groups_choice))]


    #######################################
    ############### METRICS ###############
    #######################################


    # Metric 1 - number of workouts
    num_of_workouts = len(df['workout_id'].unique())

    # Metric 2 - average workout time
    df['time'] = df['end_time'] - df['start_time']
    grouped_workouts = df.groupby(['workout_id', 'time', 'start_time', 'end_time' ,'year']).agg(
        num_exercises=('excercise_title', 'nunique'),  # Count unique exercises
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
    container_chart = st.container(border=True)
    container_chart.line_chart(grouped_workouts[['num_exercises', 'start_time' ,'year']], 
                x = 'start_time', y = 'num_exercises', color = 'year', 
                x_label ='Workout_number', y_label ='Number of Exercises')


    # Show dataframe
    st.dataframe(df)
    # workout time
    # load 

    

elif choice == 'Muscle':

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
                muscle_groups_primary = ['All','Back', 'Chest', 'Core', 'Shoulders', 'Arms', 'Legs']
                primary_muscle_groups_choice = st.multiselect("Primary muscle group", muscle_groups_primary, default='All', placeholder="Choose an option", disabled=False, label_visibility="visible")

            if col == filters_row[2]:
                # Add a dropbox to choose muslce groups
                muscle_groups = ['All','Back', 'Chest', 'Core', 'Shoulders', 'Arms', 'Legs']
                muscle_groups_secondary = ['All'] + [m for m in muscle_groups if m not in primary_muscle_groups_choice and m != 'All']
                secondary_muscle_groups_choice = st.multiselect("Secondary muscle group", muscle_groups_secondary, default='All', placeholder="Choose an option", disabled=False, label_visibility="visible")

    # Filter the dataframe
    # 1. Date
    df = df[(df['start_time'].dt.date >= selected_date[0])  & (df['end_time'].dt.date <= selected_date[1])]
    # 2. Muscle, don't filter if:
    # - if All is selected
    # - if nothing is selected
    if not ('All' in primary_muscle_groups_choice) and len(primary_muscle_groups_choice)>0:
        df = df[(df['primary'].isin(primary_muscle_groups_choice))]
    if not ('All' in secondary_muscle_groups_choice) and len(secondary_muscle_groups_choice)>0:
        df = df[(df['secondary'].isin(secondary_muscle_groups_choice))]

    st.dataframe(df)

    st.dataframe(
    df[['workout_title', 'excercise_title', 'primary', 'secondary', 'weight_kg', 'reps', 'distance_meters', 'duration_seconds']],
    column_config={
        "workout_title": "workout_title",
        "excercise_title": "excercise_title",
        "primary": "primary",
        "secondary": "secondary",
        "weight_kg": "weight_kg",
        "reps": "reps",
        "distance_meters": "distance_meters",
        "duration_seconds": "duration_seconds",
        "weight_kg_time": st.column_config.LineChartColumn(
            "Views (past 30 days)", y_min=0, y_max=5000
        ),
    },
    hide_index=True,
)
    
    col1, col2 = st.columns([2.55,1])
    col1.dataframe(df[['workout_title', 'excercise_title', 'primary', 'secondary', 'weight_kg', 'reps', 'distance_meters', 'duration_seconds']])
    

    df_temp = df[['workout_id', 'workout_title', 'excercise_title', 'primary', 'secondary', 'weight_kg', 'reps', 'distance_meters', 'duration_seconds']]

    # Group by 'excercise_title' and aggregate using the custom function
    grouped = df.groupby('excercise_title').agg({
    'reps': aggregate_to_list,
    'weight_kg': aggregate_to_list,
    'distance_meters': aggregate_to_list,
    'duration_seconds': aggregate_to_list
    }).reset_index()

    # Rename columns in a more concise way
    grouped.columns = ['excercise_title', 'max_reps', 'max_weight_kg', 'max_distance_meters', 'max_duration_seconds']

    col1.dataframe(
    grouped,
    column_config={
        "excercise_title": "excercise_title",
        "max_reps": st.column_config.LineChartColumn("max_reps"),
        "max_weight_kg": st.column_config.LineChartColumn("max_weight_kg"),
        "max_distance_meters": st.column_config.LineChartColumn("max_distance_meters"),
        "max_duration_seconds": st.column_config.LineChartColumn("max_duration_seconds"),
        
    })


    # Show image
    image = paint(primary_muscle_groups_choice, secondary_muscle_groups_choice)
    new_size = (int(image.width // 2.5), int(image.height // 2.5))
    image = image.resize(new_size, Image.LANCZOS)
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='PNG')
    image_bytes.seek(0)

    # Display the image in Streamlit
    col2.image(image_bytes, caption='Workout', use_column_width=False)