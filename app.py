from flask import Flask, request, render_template
from src.predict import predict_flight_price

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():

    airline = request.form["airline"]
    source = request.form["source"]
    destination = request.form["destination"]
    stops = int(request.form["stops"])

    journey_day = int(request.form["journey_day"])
    journey_month = int(request.form["journey_month"])

    dep_hour = int(request.form["dep_hour"])
    dep_min = int(request.form["dep_min"])

    arrival_hour = int(request.form["arrival_hour"])
    arrival_min = int(request.form["arrival_min"])

    duration_hour = int(request.form["duration_hour"])
    duration_min = int(request.form["duration_min"])

    price = predict_flight_price(
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
    )

    return render_template("index.html", prediction=round(price,2))


if __name__ == "__main__":
    app.run(debug=True)