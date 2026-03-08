import pickle
import pandas as pd

# Load the trained Machine Learning Model and its corresponding One-Hot Encoder
model = pickle.load(open("model/flight_price_model.pkl", "rb"))
encoder = pickle.load(open("model/encoder.pkl", "rb"))

def predict_flight_price(
    airline,
    source,
    destination,
    stops,
    journey_day,
    journey_month,
    dep_hour,
    dep_min,
    arrival_hour,
    arrival_min,
    duration_hour,
    duration_min
):
    """
    Takes in raw flight details, transforms them into the correct dimensions using
    the pre-trained encoder, and runs them through the ML model to output a price prediction.
    """
    
    # Structure the inputs into a Pandas DataFrame exactly matching the training format
    input_df = pd.DataFrame({
        "Airline": [airline],
        "Source": [source],
        "Destination": [destination],
        "Total_Stops": [stops],
        "Journey_day": [journey_day],
        "Journey_month": [journey_month],
        "Dep_hour": [dep_hour],
        "Dep_min": [dep_min],
        "Arrival_hour": [arrival_hour],
        "Arrival_min": [arrival_min],
        "Duration_hour": [duration_hour],
        "Duration_min": [duration_min]
    })

    # Encode categorical variables (like Airline, Source, etc) into numerical columns
    encoded = encoder.transform(input_df)

    # Ask the trained Random Forest (or similar) model to predict the price
    prediction = model.predict(encoded)

    # Return the first (and only) prediction value from the array
    return prediction[0]
