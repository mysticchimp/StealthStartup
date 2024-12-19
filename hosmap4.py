import streamlit as st
import pandas as pd
import pydeck as pdk

# Load Hospital Data from CSV
file_path = "/Users/pratikgaad/desktop/python/hosmap/hospital-data-with-geocodes-clean.csv"
hospital_data = pd.read_csv(file_path)

# Ensure Latitude and Longitude columns are properly formatted as floats
hospital_data['Latitude'] = pd.to_numeric(hospital_data['Latitude'], errors='coerce')
hospital_data['Longitude'] = pd.to_numeric(hospital_data['Longitude'], errors='coerce')

# Remove rows with missing or invalid Latitude/Longitude values
hospital_data = hospital_data.dropna(subset=['Latitude', 'Longitude'])

# Sidebar Filters for searching hospitals
st.sidebar.header("Search Filters")

# Dropdown for "Services"
services_options = sorted(hospital_data['Services'].dropna().unique())
selected_service = st.sidebar.selectbox("Select a Service:", ["All"] + services_options)

# Dropdown for "Insurers"
insurers_options = sorted(hospital_data['Insurance Coverage'].dropna().unique())
selected_insurer = st.sidebar.selectbox("Select an Insurer:", ["All"] + insurers_options)

# Dropdown for "Hospital Type"
if 'Hospital Type' in hospital_data.columns:
    hospital_type_options = sorted(hospital_data['Hospital Type'].dropna().unique())
    selected_hospital_type = st.sidebar.selectbox("Select Hospital Type:", ["All"] + hospital_type_options)
else:
    selected_hospital_type = "All"

# Dropdown for "State"
state_options = sorted(hospital_data['State'].dropna().unique())
selected_state = st.sidebar.selectbox("Select a State:", ["All"] + state_options)

# Dropdown for "Hospital Ownership"
if 'Hospital Ownership' in hospital_data.columns:
    ownership_options = sorted(hospital_data['Hospital Ownership'].dropna().unique())
    selected_ownership = st.sidebar.selectbox("Select Hospital Ownership:", ["All"] + ownership_options)
else:
    selected_ownership = "All"

# Geo Location Inputs in Sidebar
st.sidebar.subheader("Your Location")
latitude = st.sidebar.number_input("Enter your latitude:", value=40.7128, format="%.6f")
longitude = st.sidebar.number_input("Enter your longitude:", value=-74.0060, format="%.6f")

if st.sidebar.button("Reset Filters"):
    selected_service = "All"
    selected_insurer = "All"
    selected_hospital_type = "All"
    selected_state = "All"
    selected_ownership = "All"
    latitude, longitude = 40.7128, -74.0060  # Reset to default location (New York City)

# Filter hospitals based on user input
filtered_hospitals = hospital_data

if selected_service != "All":
    filtered_hospitals = filtered_hospitals[filtered_hospitals['Services'].str.contains(selected_service, case=False)]

if selected_insurer != "All":
    filtered_hospitals = filtered_hospitals[filtered_hospitals['Insurance Coverage'].str.contains(selected_insurer, case=False)]

if selected_hospital_type != "All" and 'Hospital Type' in hospital_data.columns:
    filtered_hospitals = filtered_hospitals[filtered_hospitals['Hospital Type'] == selected_hospital_type]

if selected_state != "All":
    filtered_hospitals = filtered_hospitals[filtered_hospitals['State'] == selected_state]

if selected_ownership != "All" and 'Hospital Ownership' in hospital_data.columns:
    filtered_hospitals = filtered_hospitals[filtered_hospitals['Hospital Ownership'] == selected_ownership]

# Map Configuration
st.title("Find Hospitals Near Your Location")
view_state = pdk.ViewState(
    latitude=latitude,
    longitude=longitude,
    zoom=10,
    pitch=50,
)

# Layer for User Location (Bright Blue Marker)
user_location_layer = pdk.Layer(
    "ScatterplotLayer",
    data=pd.DataFrame({"Latitude": [latitude], "Longitude": [longitude]}),
    get_position=["Longitude", "Latitude"],
    get_radius=1000,  # Radius in meters
    get_color=[0, 0, 255],  # Bright blue color (RGB)
)

# Layer for Hospital Locations (Red Markers)
hospital_layer = pdk.Layer(
    "ScatterplotLayer",
    data=filtered_hospitals,
    get_position=["Longitude", "Latitude"],
    get_radius=500,  # Radius in meters
    get_color=[255, 0, 0],  # Red color (RGB)
    pickable=True,
)

# Render Map with Pydeck
r = pdk.Deck(
    layers=[user_location_layer, hospital_layer],
    initial_view_state=view_state,
    tooltip={
        "html": "<b>{Hospital Name}</b><br>Services: {Services}<br>Insurers: {Insurance Coverage}",
        "style": {"color": "white"},
    },
)
st.pydeck_chart(r)

# Display Filtered Hospital Data Below Map
st.write("Filtered Hospitals:")
st.dataframe(filtered_hospitals)





