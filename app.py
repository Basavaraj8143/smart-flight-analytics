from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd
from flask import Flask, render_template, request

from src import predict as predictor

app = Flask(__name__)

DATA_PATH = Path("dataset/flight_price.csv")
_df = pd.read_csv(DATA_PATH)


def parse_stop_value(value: Any) -> int:
    if value is None or pd.isna(value):
        return 0
    if isinstance(value, (int, float)):
        return int(value)
    text = str(value).strip().lower()
    if text == "non-stop":
        return 0
    if "stop" in text:
        return int(text.split()[0])
    return int(float(text))


def parse_dep_hour(dep_time: Any) -> int:
    text = str(dep_time).strip()
    try:
        return int(text.split(":")[0])
    except (ValueError, IndexError):
        return 0


_df["Stops_Int"] = _df["Total_Stops"].map(parse_stop_value)
_df["Dep_Hour"] = _df["Dep_Time"].map(parse_dep_hour)

DEFAULT_SOURCE = "Delhi"
DEFAULT_DESTINATION = "Cochin"
SIMULATION_AIRLINES = _df["Airline"].value_counts().head(5).index.tolist()
MAX_STOPS = int(_df["Stops_Int"].max())

def get_options() -> dict[str, list[Any]]:
    airlines = _df["Airline"].value_counts().index.tolist()
    sources = sorted(_df["Source"].dropna().unique().tolist())
    destinations = sorted(_df["Destination"].dropna().unique().tolist())
    stops = sorted(_df["Stops_Int"].dropna().unique().astype(int).tolist())
    return {
        "airlines": airlines,
        "sources": sources,
        "destinations": destinations,
        "stops": stops,
    }


def normalize_feature_name(feature_name: str) -> str:
    if "__" in feature_name:
        feature_name = feature_name.split("__", 1)[1]

    if feature_name.startswith("Airline_"):
        return "Airline"
    if feature_name.startswith("Source_"):
        return "Source"
    if feature_name.startswith("Destination_"):
        return "Destination"
    if feature_name.startswith("Total_Stops"):
        return "Total Stops"
    if feature_name.startswith("Journey_day"):
        return "Journey Day"
    if feature_name.startswith("Journey_month"):
        return "Journey Month"
    if feature_name.startswith("Dep_hour"):
        return "Departure Hour"
    if feature_name.startswith("Dep_min"):
        return "Departure Minute"
    if feature_name.startswith("Arrival_hour"):
        return "Arrival Hour"
    if feature_name.startswith("Arrival_min"):
        return "Arrival Minute"
    if feature_name.startswith("Duration_hour"):
        return "Duration Hour"
    if feature_name.startswith("Duration_min"):
        return "Duration Minute"
    return feature_name


def build_feature_importance() -> list[dict[str, Any]]:
    model = predictor.model
    encoder = predictor.encoder
    importances = getattr(model, "feature_importances_", None)
    if importances is None:
        return []

    feature_names = encoder.get_feature_names_out()
    grouped: dict[str, float] = {}
    for name, importance in zip(feature_names, importances):
        label = normalize_feature_name(str(name))
        grouped[label] = grouped.get(label, 0.0) + float(importance)

    total = sum(grouped.values()) or 1.0
    result = [
        {"name": name, "pct": round((val / total) * 100, 1)}
        for name, val in sorted(grouped.items(), key=lambda x: x[1], reverse=True)
    ]
    return result[:5]


def build_analytics() -> dict[str, Any]:
    global_avg_price = float(_df["Price"].mean())

    airline_avg = (
        _df.groupby("Airline", as_index=False)["Price"]
        .mean()
        .sort_values("Price", ascending=False)
    )
    stops_avg = (
        _df.groupby("Stops_Int", as_index=False)["Price"]
        .mean()
        .sort_values("Stops_Int")
    )

    route_avg = _df.groupby("Route", as_index=False)["Price"].mean()
    expensive_routes = route_avg.sort_values("Price", ascending=False).head(3).copy()
    expensive_routes["tag"] = "exp"
    cheap_routes = route_avg.sort_values("Price", ascending=True).head(2).copy()
    cheap_routes["tag"] = "cheap"
    routes = pd.concat([expensive_routes, cheap_routes], ignore_index=True).drop_duplicates(
        subset=["Route"]
    )
    routes = routes.sort_values("Price", ascending=False)

    slot_defs = [
        ("Morning", "06-12"),
        ("Afternoon", "12-18"),
        ("Evening", "18-21"),
        ("Night", "21-06"),
    ]

    def slot_for_hour(hour: int) -> str:
        if 6 <= hour < 12:
            return "Morning"
        if 12 <= hour < 18:
            return "Afternoon"
        if 18 <= hour < 21:
            return "Evening"
        return "Night"

    slot_stats = (
        _df.assign(Time_Slot=_df["Dep_Hour"].map(slot_for_hour))
        .groupby("Time_Slot", as_index=False)["Price"]
        .mean()
    )
    slot_map = {row["Time_Slot"]: float(row["Price"]) for _, row in slot_stats.iterrows()}
    max_slot = max(slot_map.values()) if slot_map else 1.0

    time_slots = []
    for name, sub in slot_defs:
        value = slot_map.get(name, 0.0)
        pct = round((value / max_slot) * 100, 1) if max_slot else 0.0
        time_slots.append({"label": name, "sub": sub, "pct": pct, "val": round(value, 2)})

    airline_share = (_df["Airline"].value_counts(normalize=True) * 100).round(2)
    top_share = airline_share.head(4)
    market_share = [{"name": name, "share": float(pct)} for name, pct in top_share.items()]
    others = round(max(0.0, 100.0 - float(top_share.sum())), 2)
    if others > 0:
        market_share.append({"name": "Others", "share": others})

    route_counts = _df["Route"].value_counts().head(6)
    dominant_airline = (
        _df.groupby(["Route", "Airline"]).size().reset_index(name="count").sort_values("count")
    )
    dominant_lookup = dominant_airline.groupby("Route").tail(1).set_index("Route")["Airline"]
    route_price_map = _df.groupby("Route")["Price"].mean().to_dict()

    ticker = []
    for route, _count in route_counts.items():
        avg_price = float(route_price_map.get(route, global_avg_price))
        premium_pct = ((avg_price - global_avg_price) / global_avg_price) * 100 if global_avg_price else 0
        direction = "up" if premium_pct >= 0 else "dn"
        ticker.append(
            {
                "label": f"{dominant_lookup.get(route, '')} {route}".strip(),
                "price": round(avg_price, 2),
                "change_pct": round(abs(premium_pct), 1),
                "direction": direction,
            }
        )

    summary = {
        "flights_analyzed": int(len(_df)),
        "airlines": int(_df["Airline"].nunique()),
        "routes": int(_df["Route"].nunique()),
        "avg_price": round(global_avg_price, 2),
    }

    return {
        "summary": summary,
        "ticker": ticker,
        "airline_avg": [
            {"name": row["Airline"], "val": round(float(row["Price"]), 2)}
            for _, row in airline_avg.iterrows()
        ],
        "stops_avg": [
            {
                "name": "Non-stop" if int(row["Stops_Int"]) == 0 else f"{int(row['Stops_Int'])} Stop"
                if int(row["Stops_Int"]) == 1
                else f"{int(row['Stops_Int'])} Stops",
                "val": round(float(row["Price"]), 2),
                "stops": int(row["Stops_Int"]),
            }
            for _, row in stops_avg.iterrows()
        ],
        "routes": [
            {"route": row["Route"], "price": round(float(row["Price"]), 2), "tag": row["tag"]}
            for _, row in routes.iterrows()
        ],
        "time_slots": time_slots,
        "market_share": market_share,
        "feature_importance": build_feature_importance(),
    }


def parse_prediction_payload(data: dict[str, Any]) -> dict[str, int | str]:
    airline = str(data["airline"])
    source = str(data["source"])
    destination = str(data["destination"])
    stops = parse_stop_value(data["stops"])

    journey_day = int(data["journey_day"])
    journey_month = int(data["journey_month"])

    dep_hour = int(data.get("dep_hour", 0))
    dep_min = int(data.get("dep_min", 0))

    if "duration_hour" in data and "duration_min" in data:
        duration_hour = int(data["duration_hour"])
        duration_min = int(data["duration_min"])
    else:
        total = int(data.get("duration", 0))
        duration_hour = total // 60
        duration_min = total % 60

    if "arrival_hour" in data and "arrival_min" in data:
        arrival_hour = int(data["arrival_hour"])
        arrival_min = int(data["arrival_min"])
    else:
        total_min = dep_min + duration_min
        arrival_hour = (dep_hour + duration_hour + total_min // 60) % 24
        arrival_min = total_min % 60

    return {
        "airline": airline,
        "source": source,
        "destination": destination,
        "stops": stops,
        "journey_day": journey_day,
        "journey_month": journey_month,
        "dep_hour": dep_hour,
        "dep_min": dep_min,
        "arrival_hour": arrival_hour,
        "arrival_min": arrival_min,
        "duration_hour": duration_hour,
        "duration_min": duration_min,
    }


def model_predict(payload: dict[str, int | str]) -> float:
    return float(
        predictor.predict_flight_price(
            str(payload["airline"]),
            str(payload["source"]),
            str(payload["destination"]),
            int(payload["stops"]),
            int(payload["journey_day"]),
            int(payload["journey_month"]),
            int(payload["dep_hour"]),
            int(payload["dep_min"]),
            int(payload["arrival_hour"]),
            int(payload["arrival_min"]),
            int(payload["duration_hour"]),
            int(payload["duration_min"]),
        )
    )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json() if request.is_json else request.form
    payload = parse_prediction_payload(data)
    price = model_predict(payload)
    rounded = round(price, 2)

    if request.is_json:
        return {"prediction": rounded}
    return render_template("index.html", prediction=rounded)


@app.route("/api/options", methods=["GET"])
def api_options():
    return get_options()


@app.route("/api/analytics", methods=["GET"])
def api_analytics():
    return build_analytics()


@app.route("/api/simulate", methods=["POST"])
def api_simulate():
    data = request.get_json(force=True, silent=True) or {}
    base_airline = str(data.get("airline", SIMULATION_AIRLINES[0]))
    source = str(data.get("source", DEFAULT_SOURCE))
    destination = str(data.get("destination", DEFAULT_DESTINATION))
    stops = parse_stop_value(data.get("stops", 1))
    dep_hour = int(data.get("dep_hour", 10))
    duration = int(data.get("duration", 180))
    days_to_departure = max(1, int(data.get("days_to_departure", 30)))

    journey_date = datetime.utcnow().date() + timedelta(days=days_to_departure)

    def predict_for(airline: str, stop_count: int, duration_min: int, dep_hour_val: int, day_offset: int) -> float:
        date_for_prediction = datetime.utcnow().date() + timedelta(days=max(1, day_offset))
        payload = {
            "airline": airline,
            "source": source,
            "destination": destination,
            "stops": max(0, min(MAX_STOPS, stop_count)),
            "journey_day": date_for_prediction.day,
            "journey_month": date_for_prediction.month,
            "dep_hour": max(0, min(23, dep_hour_val)),
            "dep_min": 0,
            "duration_hour": max(0, duration_min // 60),
            "duration_min": max(0, duration_min % 60),
            "arrival_hour": (dep_hour_val + (duration_min // 60)) % 24,
            "arrival_min": duration_min % 60,
        }
        return model_predict(payload)

    baseline = predict_for(base_airline, stops, duration, dep_hour, days_to_departure)
    comparison = []
    for airline in SIMULATION_AIRLINES:
        value = predict_for(airline, stops, duration, dep_hour, days_to_departure)
        comparison.append({"airline": airline, "price": round(value, 2)})
    comparison.sort(key=lambda x: x["price"])

    stop_variant = predict_for(base_airline, min(MAX_STOPS, stops + 1), duration, dep_hour, days_to_departure)
    duration_variant = predict_for(base_airline, stops, duration + 60, dep_hour, days_to_departure)
    early_variant = predict_for(base_airline, stops, duration, dep_hour, days_to_departure + 14)

    return {
        "baseline": round(baseline, 2),
        "journey_day": journey_date.day,
        "journey_month": journey_date.month,
        "comparison": comparison,
        "sensitivity": {
            "plus_stop": round(stop_variant - baseline, 2),
            "plus_60_min": round(duration_variant - baseline, 2),
            "plus_14_days_early": round(early_variant - baseline, 2),
        },
    }


if __name__ == "__main__":
    app.run(debug=True)

