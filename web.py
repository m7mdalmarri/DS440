import streamlit as st
import pickle
import pandas as pd
import pydeck as pdk
import base64

# Load the model
with open("RandomForestRegressor.pkl", "rb") as file:
    model = pickle.load(file)

# Load the data
@st.cache_data
def load_data():
    data = pd.read_csv("New_data1.csv")
    return data

data = load_data()

# Background image
background_image_path = "image (3).jpeg"
with open(background_image_path, "rb") as image_file:
    encoded_bg_image = base64.b64encode(image_file.read()).decode()

# CSS
page_bg_img = f'''
<style>
.stApp {{
    background-image: url("data:image/jpeg;base64,{encoded_bg_image}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    color: #FFD700;
}}
.stApp::before {{
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.6);
    z-index: 0;
}}
.stApp > div:first-child {{
    position: relative;
    z-index: 1;
}}
.css-18e3th9 {{
    background-color: rgba(192, 192, 192, 0.1) !important;
    color: #FFD700 !important;
}}
h1, h2 {{
    color: white !important;
}}
.stNumberInput label, .stSelectbox label {{
    font-size: 1.2rem !important;
    font-weight: bold !important;
    color: #DCDCDC !important;
}}
.stButton>button {{
    color: white !important;
    background-color: #32CD32 !important;
    border: none;
}}
.css-1v3fvcr p {{
    color: #FF4500 !important;
}}
.prediction-card {{
    background: linear-gradient(135deg, #ff6f61, #f7b731);
    padding: 20px;
    margin: 20px 0;
    border-radius: 15px;
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.6);
    text-align: center;
    font-size: 1.8rem;
    color: white;
    animation: reveal 1.5s ease;
}}
.white-text {{
    color: white !important;
}}
@keyframes reveal {{
    0% {{ transform: scale(0); opacity: 0; }}
    100% {{ transform: scale(1); opacity: 1; }}
}}
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)

if 'main_page' not in st.session_state:
    st.session_state['main_page'] = False

if not st.session_state['main_page']:
    st.title("Welcome to Property Price Prediction")
    
    # Start button
    if st.button("Click here to start"):
        st.session_state['main_page'] = True

    

else:
    st.title("🏠 Property Price Prediction")
    st.write("## Property Details")

    # Input fields
    size_in_sqft = st.number_input('Area (in Sqft)', min_value=0, max_value=10000, value=1079, step=100)
    bedrooms = st.number_input('Number of Bedrooms', min_value=1, max_value=5, step=1)
    bathrooms = st.number_input('Number of Bathrooms', min_value=1, max_value=5, step=1)
    unit_type = st.selectbox('Unit Type', ['Apartment', 'Villa', 'Townhouse', 'Studio'])
    location = st.selectbox('Location', data['neighborhood'].unique())

    quality_mapping = {
        'Apartment': 2,
        'Villa': 4,
        'Townhouse': 3,
        'Studio': 1
    }
    quality = quality_mapping.get(unit_type, 1)

    # Prediction button
    if st.button("Predict Price"):
        matching_location = data[data['neighborhood'] == location]
        if len(matching_location) > 0:
            lat = matching_location['latitude'].values[0]
            lon = matching_location['longitude'].values[0]

            # Prepare input data for model
            input_data = pd.DataFrame({
                'id': [0],
                'neighborhood': [location],
                'latitude': [lat],
                'longitude': [lon],
                'size_in_sqft': [size_in_sqft],
                'no_of_bedrooms': [bedrooms],
                'no_of_bathrooms': [bathrooms],
                'quality': [quality]
            })

            # Prediction
            try:
                # Predict price per square foot
                predicted_price_per_sqft = model.predict(input_data)[0]
                
                # Calculate the total price
                total_price = abs(predicted_price_per_sqft * size_in_sqft)

                # Display interactive prediction result
                st.markdown(f"""
                <div class="prediction-card">
                    💰 Predicted Total Price: AED {total_price:,.2f}
                </div>
                """, unsafe_allow_html=True)

                
                # Display property location on map
                st.markdown('<div class="map-section-title">Property Location on Map</div>', unsafe_allow_html=True)
                map_data = pd.DataFrame({'lat': [lat], 'lon': [lon]})
                st.pydeck_chart(pdk.Deck(
                    map_style='mapbox://styles/mapbox/light-v9',
                    initial_view_state=pdk.ViewState(
                        latitude=lat,
                        longitude=lon,
                        zoom=14,
                        pitch=50,
                    ),
                    layers=[
                        pdk.Layer(
                            'ScatterplotLayer',
                            data=map_data,
                            get_position='[lon, lat]',
                            get_color='[50, 205, 50, 160]', 
                            get_radius=200,
                        ),
                    ],
                ))
                # Links section below button
                st.markdown('<p class="white-text">Find more properties on <a href="https://www.propertyfinder.ae" target="_blank" style="color: #1E90FF;">Property Finder</a> and <a href="https://www.bayut.com" target="_blank" style="color: #1E90FF;">Bayut</a></p>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Prediction error: {e}")
        else:
            st.error("Location not found in the dataset.")
