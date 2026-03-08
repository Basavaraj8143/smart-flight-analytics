# SkyIQ — Smart Flight Analytics

## 1. Project Overview
SkyIQ is a full-stack, machine learning-powered web application designed to predict flight prices and analyze historical aviation data. The system allows users to predict the exact ticket price of a future flight based on multiple parameters, simulate "What-If" scenarios (like taking a connecting flight to save money), and explore comprehensive analytics dashboards generated directly from a real-world dataset.

The application leverages a Python (Flask) backend to serve a pre-trained Random Forest model and aggregates data in real-time using Pandas, which is then visualized on a custom-built, responsive HTML/JS/CSS frontend.

---

## 2. Architecture & Tech Stack

### Backend
* **Python 3.12+**
* **Flask**: Lightweight web framework serving API endpoints and rendering HTML templates.
* **Pandas**: Used for loading the historical CSV dataset into memory and performing real-time data aggregations for the analytics dashboard.
* **Scikit-Learn (Pickle)**: Used to load the pre-trained Machine Learning model (`flight_price_model.pkl`) and its associated One-Hot Encoder (`encoder.pkl`).

### Frontend
* **HTML5 (Jinja2 Templates)**: Modularized component architecture (`base.html`, `predict.html`, `analytics.html`, etc.) for maintainability.
* **Vanilla CSS3**: Custom design system featuring CSS variables, glassmorphism, responsive grid layouts, and CSS animations.
* **Vanilla JavaScript (ES6)**: Handles asynchronous API fetching (`fetch`), DOM manipulation, and page routing without a heavy frontend framework.
* **Chart.js**: Utilized for rendering dynamic, interactive `<canvas>` charts (Bar charts, Doughnut charts) in the analytics dashboard.

---

## 3. Core Features

### 3.1. Machine Learning Price Prediction
The `Predict` tab allows users to input specific flight details (Airline, Source, Destination, Stops, Journey Date, and Departure Time).
* **Process**: The frontend sends a JSON payload to the `/predict` Flask endpoint.
* **Transformation**: The backend maps the raw user input into a Pandas DataFrame that identically matches the format expected by the model. The `encoder.pkl` one-hot encodes categorical variables (like Airline strings into integer arrays).
* **Prediction**: The formatted data is passed to the Random Forest model (`model.predict()`), returning a highly accurate estimated price.

### 3.2. Price Simulator (What-If Analysis)
The `Simulator` tab helps users find cheaper alternatives for their route.
* **Comparison Engine**: The backend runs the exact same prediction routing against the top 5 competing airlines simultaneously, instantly generating a competitive price matrix.
* **Sensitivity Analysis (Deltas)**: The backend silently executes three *additional* automated ML predictions, perturbing specific variables:
  * **+1 Stop**: Predicts the price if the user added a layover.
  * **+60 Minutes**: Predicts the price if the flight was an hour longer.
  * **+14 Days**: Predicts the price if the user booked two weeks earlier.

### 3.3. Live Flight Analytics Dashboard
The `Analytics` tab provides exploratory data analysis (EDA) derived directly from the training dataset.
* **Live Aggregation**: Instead of static images, Pandas calculates real-time metrics (e.g., `df.groupby("Airline")["Price"].mean()`) which are sent to the frontend.
* **Interactive Chart.js Visualizations**: 
  * Average Price by Airline (Bar Chart)
  * Price by Number of Stops (Bar Chart)
  * Airline Market Share (Doughnut Chart)
  * Price by Departure Time Slot (Bar Chart)
  * Top 10 Feature Importances (Horizontal Bar Chart extracted directly from the ML model's `feature_importances_` attribute).
* **Code Modals**: Each chart includes a `</> Code` button that opens a modal revealing the exact Python/Pandas logic used to generate that specific dataset.

---

## 4. Directory Structure

\`\`\`text
smart-flight-analytics/
├── app.py                      # Main Flask application and API routes
├── dataset/
│   └── flight_price.csv        # The raw historical dataset for Pandas analytics
├── model/
│   ├── encoder.pkl             # Pre-trained Scikit-Learn One-Hot Encoder
│   └── flight_price_model.pkl  # Pre-trained Random Forest prediction model
├── notebooks/
│   └── flight_price_model.ipynb # Jupyter notebook used to initially train the model
├── src/
│   └── predict.py              # Wrapper for loading pickles and executing predictions
├── static/
│   ├── css/
│   │   └── style.css           # Global stylesheet containing all custom CSS
│   └── js/
│       └── main.js             # Global JS handling API calls and Chart.js rendering
└── templates/
    ├── base.html               # Main layout wrapper (<html>, <head>, <nav>)
    ├── index.html              # Entry point extending base.html
    └── components/
        ├── analytics.html      # Analytics dashboard markup and modals
        ├── home.html           # Hero section markup
        ├── predict.html        # Prediction form and results markup
        └── simulator.html      # Simulator sliders and comparison markup
\`\`\`

---

## 5. Setup & Local Development

1. **Environment Setup**: Ensure Python 3.12+ is installed.
2. **Install Dependencies**:
   \`\`\`bash
   pip install flask pandas scikit-learn
   \`\`\`
3. **Run Application**:
   \`\`\`bash
   python app.py
   \`\`\`
4. **Access**: Navigate to `http://127.0.0.1:5000` in your web browser.
