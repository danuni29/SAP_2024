import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# Step 1: Read all CSV files from the folder
file_path = r'C:\code\SAP_2024\02_Model\input\weather_data'  # Adjust the path if necessary
all_files = [os.path.join(file_path, f) for f in os.listdir(file_path) if os.path.isfile(os.path.join(file_path, f))]

# Step 2: Combine all files into a single DataFrame
df_list = [pd.read_csv(file) for file in all_files]
weather_data = pd.concat(df_list, ignore_index=True)

# Step 3: Preprocessing
weather_data['date'] = pd.to_datetime(weather_data['date'])
weather_data['year'] = weather_data['date'].dt.year
weather_data['month_day'] = weather_data['date'].dt.strftime('%m-%d')  # Use MM-DD format for X-axis
weather_data = weather_data[(weather_data['date'].dt.month >= 1) & (weather_data['date'].dt.month <= 5)]  # Filter for Jan to May

# Separate data for 2004-2023 (평년) and 2024
past_years_data = weather_data[(weather_data['year'] >= 2004) & (weather_data['year'] <= 2023)]
current_year_data = weather_data[weather_data['year'] == 2024]

# Step 4: Calculate the mean and std deviation for past years (평년)
past_grouped = past_years_data.groupby('month_day').agg({'tavg': ['mean', 'std']}).reset_index()
past_grouped.columns = ['month_day', 'mean_tavg', 'std_tavg']

# Step 5: Group current year data (2024) by date and calculate the mean temperature
current_grouped = current_year_data.groupby('month_day').agg({'tavg': 'mean'}).reset_index()

# Step 6: Plotting with Matplotlib
plt.figure(figsize=(10, 6))

# Plot the mean temperature line for 평년 with a shaded band (standard deviation)
plt.plot(past_grouped['month_day'], past_grouped['mean_tavg'], color='orange', label='평년 (2004-2023)')
plt.fill_between(
    past_grouped['month_day'],
    past_grouped['mean_tavg'] - past_grouped['std_tavg'],
    past_grouped['mean_tavg'] + past_grouped['std_tavg'],
    color='gray', alpha=0.3, label='온도 범위 (±1 표준 편차)'
)

# Plot the line for 2024 (single line after grouping by date)
plt.plot(current_grouped['month_day'], current_grouped['tavg'], color='blue', label='2024년')

# Customizing X-axis to show MM-DD format as in the image
# Generating tick positions for mid-month days
date_ticks = ['01-15', '02-01', '02-15', '03-01', '03-15', '04-01', '04-15', '05-01', '05-15', '06-01']
plt.xticks(date_ticks)

plt.xlabel('Date (MM-DD)')
plt.ylabel('Temperature (°C)')
plt.title('평년 (2004-2023) vs. 2024 일평균 기온 그래프')
plt.legend(loc='upper left')

# Step 7: Show the plot in Streamlit using matplotlib
st.pyplot(plt)
