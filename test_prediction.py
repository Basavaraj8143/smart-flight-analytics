from src.predict import predict_flight_price

price = predict_flight_price(
    "IndiGo",
    "Delhi",
    "Cochin",
    1,
    15,
    3,
    10,
    30,
    13,
    20,
    2,
    50
)

print("Predicted Flight Price:", price)