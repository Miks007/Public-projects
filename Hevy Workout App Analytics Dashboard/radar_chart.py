import pandas as pd 
def calculate_radar_data(df):
    # Original dictionary of muscle groups
    muscle_groups = {
        "Core": ["Abdominals", "Lower Back"],
        "Legs": ["Quadriceps", "Hamstrings", "Glutes", "Calves", "Abductors", "Adductors"],
        "Arms": ["Biceps", "Triceps", "Forearms"],
        "Back": ["Lats", "Upper Back", "Traps"],
        "Shoulders": ["Shoulders"],
        "Chest": ["Chest"],
        "Other": ["Cardio", "Full Body", "Other"]
    }
    # Reverse mapping dictionary: value -> key
    reverse_mapping = {muscle: category for category, muscles in muscle_groups.items() for muscle in muscles}

    df['radar_category'] = df['primary_muscle_group'].map(reverse_mapping)
    radar_df = df.groupby(['radar_category']).agg(
            count=('radar_category', 'count') # Count of radar_category which shows how often muscle group were targeted
        ).reset_index()
    
    required_categories = ['Arms', 'Legs', 'Back', 'Chest', 'Core', 'Shoulders']
    radar_df = radar_df[radar_df['radar_category'].isin(required_categories)]
    return radar_df