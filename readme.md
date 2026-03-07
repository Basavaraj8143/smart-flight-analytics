# ✈️ Smart Flight Analytics and Prediction Platform

A machine learning-powered web application that predicts flight ticket prices and provides data-driven insights to help users make smarter travel decisions.

---

## 📌 Project Overview

| Detail | Info |
|--------|------|
| **ML Problem Type** | Supervised Learning — Regression |
| **Target Variable** | Flight Ticket Price (₹) |
| **Dataset Size** | 10,683 rows |
| **Backend** | Flask (Python) |
| **Frontend** | HTML, CSS, JavaScript |

---

## 🚀 Features

### 🔮 Core ML Feature
**1. Flight Price Prediction**
- User inputs flight details and the model returns an estimated ticket price.
- **Inputs:** Airline, Source, Destination, Total Stops, Journey Day/Month, Departure Hour, Duration
- **Output:** Predicted price + expected price range

### 🧪 Smart Feature
**2. Price Change Simulator**
- Adjust flight parameters and instantly see how price changes.
- Example: Changing from 1-stop → Non-stop shows a price difference of +₹580

### 📊 Analytics Features
**3. Airline Price Analysis** — Average price comparison across airlines
**4. Stops vs Price Analysis** — How number of stops affects cost
**5. Route Price Analysis** — Most expensive and cheapest routes
**6. Departure Time Impact** — How time of day influences pricing
**7. Feature Importance (Explainable AI)** — Which factors influence price the most

---

## 🏗️ System Architecture

```
Dataset
   ↓
Data Preprocessing
   ↓
Feature Engineering
   ↓
Model Training
   ↓
Model Evaluation
   ↓
Saved ML Model (pickle)
   ↓
Flask Backend API
   ↓
Frontend Web Interface
   ↓
User: Prediction + Analytics
```

---

## 🛠️ Tech Stack

| Category | Tools |
|----------|-------|
| **ML & Data** | Python, Pandas, NumPy, Scikit-learn |
| **Visualization** | Matplotlib, Seaborn |
| **Backend** | Flask |
| **Frontend** | HTML, CSS, JavaScript |
| **Model Storage** | pickle / joblib |

---

## 📋 Project Phases

| Phase | Task |
|-------|------|
| **Phase 1** | Data Understanding — load, explore, identify missing values |
| **Phase 2** | Exploratory Data Analysis — visualize price patterns |
| **Phase 3** | Data Cleaning — handle nulls, fix inconsistencies |
| **Phase 4** | Feature Engineering — extract day, month, hour, duration in minutes |
| **Phase 5** | Feature Encoding — One Hot Encoding for categorical variables |
| **Phase 6** | Train/Test Split — 80% train / 20% test |
| **Phase 7** | Model Training — Linear Regression, Decision Tree, Random Forest |
| **Phase 8** | Model Evaluation — MAE, RMSE, R² Score |
| **Phase 9** | Model Saving — export with pickle |
| **Phase 10** | Web Application — Flask API + frontend form |
| **Phase 11** | Analytics Dashboard — charts and visual insights |

---

## ⚙️ Feature Engineering Details

**From `Date_of_Journey`:** `Journey_day`, `Journey_month`

**From `Dep_Time`:** `Dep_hour`, `Dep_minute`

**From `Arrival_Time`:** `Arrival_hour`, `Arrival_minute`

**From `Duration`:** Converted to total minutes

**From `Total_Stops`:** Converted to numeric (0, 1, 2, 3...)

---

## 📈 ML Models Used

| Model | Notes |
|-------|-------|
| Linear Regression | Baseline model |
| Decision Tree Regressor | Captures non-linear patterns |
| Random Forest Regressor | Best performing — ensemble method |

---

## ✅ Feasibility

| Factor | Details |
|--------|---------|
| **Hardware** | Runs on a normal laptop with 8GB RAM |
| **Training Time** | A few seconds |
| **Software** | All tools are free and open source |
| **Skills Required** | Python, basic ML, basic web development |

---

## 🧠 ML Concepts Demonstrated

- Supervised Learning
- Regression modelling
- Feature Engineering
- Categorical Encoding
- Model Evaluation
- Ensemble Learning (Random Forest)
- Explainable AI (Feature Importance)

---

## 🖥️ Sample Output

**User Input:**
```
Airline       : IndiGo
Source        : Delhi
Destination   : Cochin
Stops         : 1
Departure Hour: 10
Duration      : 180 minutes
```

**System Output:**
```
Predicted Price : ₹6,540
Expected Range  : ₹6,200 – ₹6,900
```

**Insights:**
- Non-stop flights cost ~15% more on this route
- Duration is the most influential feature

---

## 🔮 Future Improvements

- Real-time flight data via API integration
- Flight delay prediction model
- Price trend forecasting (time series)
- Mobile application

---

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/your-username/smart-flight-analytics.git
cd smart-flight-analytics

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

## 🖥️ Frontend ↔ Backend Communication
The user interface is served from `templates/index.html` via Flask. The prediction form collects flight parameters and submits them to the `/predict` endpoint:

* **Normal form POST** – if JavaScript is disabled the browser does a traditional HTTP POST, the server renders the same template with `{{ prediction }}` injected by Jinja.
* **AJAX (fetch)** – the page’s `runPrediction()` function gathers input values, converts the duration to hours/minutes and computes arrival time, then sends a `POST` request with JSON to `/predict`. The Flask route detects `request.is_json`, runs the ML model, and returns a JSON payload `{ "prediction": … }`. The script updates the DOM without reloading the page.

This two‑way setup lets you develop and debug the backend model in Python while keeping the responsive frontend experience you built with vanilla JS.

```python
# example server-side logic (see app.py)
if request.is_json:
    return {"prediction": rounded}
else:
    return render_template("index.html", prediction=rounded)
```

The HTML form now includes `name` attributes that match the model’s expected feature names, and the Flask route will also compute missing fields (arrival times, split duration) when only a total duration is supplied.

With the server running you can open `http://localhost:5000/` in your browser, fill in the fields, and watch the backend-driven prediction appear.

---

## 📁 Project Structure

```
smart-flight-analytics/
│
├── data/
│   └── flight_data.csv
│
├── notebooks/
│   └── EDA_and_Training.ipynb
│
├── model/
│   └── flight_price_model.pkl
│
├── templates/
│   └── index.html
│
├── static/
│   └── style.css
│
├── app.py
├── requirements.txt
└── README.md
```

---

## 👨‍💻 Author

**Bass** — B.E./B.Tech Engineering Project

---

> *"Turning raw flight data into intelligent price predictions."*