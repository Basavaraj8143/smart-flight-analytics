import pickle
import pandas as pd

model = pickle.load(open("model/flight_price_model.pkl","rb"))
encoder = pickle.load(open("model/encoder.pkl","rb"))

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

    input_df = pd.DataFrame({
        "Airline":[airline],
        "Source":[source],
        "Destination":[destination],
        "Total_Stops":[stops],
        "Journey_day":[journey_day],
        "Journey_month":[journey_month],
        "Dep_hour":[dep_hour],
        "Dep_min":[dep_min],
        "Arrival_hour":[arrival_hour],
        "Arrival_min":[arrival_min],
        "Duration_hour":[duration_hour],
        "Duration_min":[duration_min]
    })

    encoded = encoder.transform(input_df)

    prediction = model.predict(encoded)

    return prediction[0]