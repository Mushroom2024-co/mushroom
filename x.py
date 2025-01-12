import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

# Set the title of the app
st.set_page_config(page_title="Mushroom Farm Monitoring System", layout="wide")

# Add custom CSS for background and styling
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(to right, #f0f4f8, #d9e4ef);
        color: #333;
        font-family: 'Arial', sans-serif;
    }
    .reportview-container .main {
        padding: 2rem;
        border-radius: 8px;
        background-color: rgba(255, 255, 255, 0.9);
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }
    h1 {
        color: #3F51B5;
        text-align: center;
    }
    h2, h3 {
        color: #3F51B5;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Set the header of the app
st.title("Mushroom Farm Monitoring System")

# Google Sheets data URL
spreadsheet_url = "https://docs.google.com/spreadsheets/d/1S5rbM_i_k_mmWcaT5HfD53hGuAjesUjd7J5TfD8qKT8/gviz/tq?tqx=out:csv"

# Load the data from Google Sheets (CSV format)
@st.cache_data(ttl=5)  # Cache data for 5 seconds
def load_data():
    data = pd.read_csv(spreadsheet_url)
    # Convert 'Timestamp' to datetime
    data['Timestamp'] = pd.to_datetime(data['Timestamp'])
    return data

# Function to display the filtered data by date range
def show_filtered_data(data):
    st.subheader("Filter Data by Date Range")

    # Initialize session state for dates
    if 'start_date' not in st.session_state:
        st.session_state.start_date = data['Timestamp'].min().date()
    if 'end_date' not in st.session_state:
        st.session_state.end_date = data['Timestamp'].max().date()

    # Use the stored dates in session state
    start_date = st.date_input("Start Date", value=st.session_state.start_date, key="start_date_input")
    end_date = st.date_input("End Date", value=st.session_state.end_date, key="end_date_input")

    # Update session state
    st.session_state.start_date = start_date
    st.session_state.end_date = end_date

    # Filter data based on selected dates
    filtered_data = data[(data['Timestamp'].dt.date >= start_date) & (data['Timestamp'].dt.date <= end_date)]
    st.write(filtered_data)

    # Fan and Humidifier status bar chart
    st.subheader("Fan and Humidifier States Over Time")
    fan_humidifier_data = filtered_data[['Timestamp', 'Fan State', 'Humidifier State']].melt(
        id_vars=['Timestamp'], value_vars=['Fan State', 'Humidifier State'], var_name='State', value_name='Status'
    )
    fig_fan_humidifier = px.bar(
        fan_humidifier_data,
        x="Timestamp",
        y="Status",
        color="State",
        title="Fan and Humidifier States Over Time",
        barmode="group",
        color_discrete_sequence=px.colors.qualitative.Plotly  # Professional color scheme
    )
    fig_fan_humidifier.update_layout(xaxis_title="Timestamp", yaxis_title="State", xaxis=dict(tickformat='%Y-%m-%d %H:%M'))
    st.plotly_chart(fig_fan_humidifier, use_container_width=True)

    # Display LED state distribution
    st.subheader("LED State Distribution")
    if 'LED Brightness' in filtered_data.columns:
        led_count = filtered_data['LED Brightness'].value_counts()
        fig_led = px.pie(
            values=led_count.values,
            names=led_count.index,
            title="LED State Distribution",
            hole=0.4,  # Create a donut chart
            color_discrete_sequence=px.colors.qualitative.Plotly,  # Change colors to Plotly's qualitative palette
            labels={'values': 'Count', 'names': 'LED Brightness'},  # Add labels for clarity
        )
        fig_led.update_traces(textinfo='percent+label')  # Show percentage and label on the pie chart
        fig_led.update_layout(showlegend=True)  # Show legend
        st.plotly_chart(fig_led, use_container_width=True)
    else:
        st.warning("The column 'LED Brightness' is missing from the data.")

# Function to display temperature and humidity over time
def show_temp_humidity(data):
    st.subheader("Temperature and Humidity Over Time")
    fig_temp_humidity = plt.figure(figsize=(12, 6))
    plt.plot(data['Timestamp'], data['Temperature'], label='Temperature (°C)', color='tab:red', linewidth=2)
    plt.plot(data['Timestamp'], data['Humidity'], label='Humidity (%)', color='tab:blue', linewidth=2)
    plt.xlabel('Timestamp')
    plt.ylabel('Value')
    plt.title('Temperature and Humidity Over Time', fontsize=16)
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid()  # Add grid for better readability
    st.pyplot(fig_temp_humidity)

# Function to display soil moisture and light intensity over time
def show_soil_light(data):
    st.subheader("Soil Moisture and Light Intensity Over Time")
    fig_soil_light = plt.figure(figsize=(12, 6))
    plt.plot(data['Timestamp'], data['Soil Moisture'], label='Soil Moisture (raw)', color='tab:green', linewidth=2)
    plt.plot(data['Timestamp'], data['Light Intensity'], label='Light Intensity (lux)', color='tab:orange', linewidth=2)
    plt.xlabel('Timestamp')
    plt.ylabel('Value')
    plt.title('Soil Moisture and Light Intensity Over Time', fontsize=16)
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid()  # Add grid for better readability
    st.pyplot(fig_soil_light)

# Main app content
def main():
    # Load data
    data = load_data()

    # Display the Filter Data by Date Range section first
    show_filtered_data(data)
    
    # Display other sections
    show_temp_humidity(data)
    show_soil_light(data)

# Button to refresh data
if st.button('Refresh Data'):
    main()
else:
    main()  # Initial display without refreshing
