#  Start with command -  streamlit run "C:\Users\MikolajPawlak\Documents\GitHub\Public-projects\Hevy workouts\Hevy_app.py"
import streamlit as st
import pandas as pd
import os
import io
from PIL import Image, ImageDraw
import datetime
import matplotlib.pyplot as plt



from human_body_painting import paint

# Specify the path to the directory you want to set as the working directory
new_directory = r'C:\Users\MikolajPawlak\Documents\GitHub\Public-projects\Hevy workouts'

# Change the current working directory to the specified directory
os.chdir(new_directory)

# read data and prepare it for the app
df = pd.read_csv("hevy_workouts_2024_06_22.csv", index_col=0)
df['start_time'] = pd.to_datetime(df['start_time'])
df['end_time'] = pd.to_datetime(df['end_time'])
df['year'] = df['start_time'].dt.year.astype(str)
df['month'] = df['start_time'].dt.month

 
st.write("""
# Hevy workouts analysis
Hello *world!*
""")

min_date = df['start_time'].min().date()
max_date = df['end_time'].max().date()


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
                muscle_groups_choice = st.multiselect("Muscle group", muscle_groups, default='All', placeholder="Choose an option", disabled=False, label_visibility="visible")


    
    
    # filter dataframe
    df = df[(df['start_time'].dt.date >= selected_date[0])  & (df['end_time'].dt.date <= selected_date[1])]

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

container_chart = st.container(border=True)
container_chart.line_chart(grouped_workouts[['num_exercises', 'start_time' ,'year']], 
            x = 'start_time', y = 'num_exercises', color = 'year', 
            x_label ='Workout_number', y_label ='Number of Exercises')



st.dataframe(df)
# workout time
# load 


image = paint('klatka', 'brzuch')
new_size = (image.width // 4, image.height // 4)
image = image.resize(new_size, Image.LANCZOS)
image_bytes = io.BytesIO()
image.save(image_bytes, format='PNG')
image_bytes.seek(0)

# Display the image in Streamlit
st.image(image_bytes, caption='Workout', use_column_width=False)