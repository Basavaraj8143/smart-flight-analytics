# Smart Flight Analytics and Price Prediction Platform

## Machine Learning Training Pipeline Documentation

---

# 1. Project Objective

The goal of this project is to build a **machine learning model that predicts flight ticket prices** using historical flight data.

The system learns patterns from features such as airline, route, duration, stops, and departure time to estimate the expected ticket price.

This is a **Supervised Machine Learning Regression problem** because:

* We have **input features (X)**
* We have a **target variable (Price)**
* The target value is **continuous numeric data**

Target Variable:

```
Price
```

---

# 2. Dataset Description

The dataset contains **10,683 flight records**.

Each record contains flight details and the corresponding ticket price.

## Features in the Dataset

| Feature         | Description                          |
| --------------- | ------------------------------------ |
| Airline         | Airline company operating the flight |
| Date_of_Journey | Date when the flight departs         |
| Source          | Departure city                       |
| Destination     | Arrival city                         |
| Route           | Flight route between cities          |
| Dep_Time        | Flight departure time                |
| Arrival_Time    | Flight arrival time                  |
| Duration        | Total flight duration                |
| Total_Stops     | Number of stops in the journey       |
| Additional_Info | Extra flight information             |
| Price           | Ticket price (Target Variable)       |

---

# 3. Machine Learning Pipeline

The project follows a structured ML pipeline.

```
Dataset
   ↓
Data Cleaning
   ↓
Feature Engineering
   ↓
Categorical Encoding
   ↓
Train-Test Split
   ↓
Model Training
   ↓
Model Evaluation
   ↓
Best Model Selection
   ↓
Model Saving
```

---

# 4. Data Cleaning

The dataset was first inspected to detect:

* Missing values
* Incorrect formats
* Unnecessary columns

### Handling Missing Values

Rows with missing values were removed:

```
df.dropna()
```

This ensures the model trains on complete data.

---

# 5. Feature Engineering

Feature engineering converts raw data into useful numerical features.

### 5.1 Extract Journey Day and Month

From `Date_of_Journey`:

```
Journey_day
Journey_month
```

These features help the model capture **seasonal price trends**.

---

### 5.2 Extract Departure Time Features

From `Dep_Time`:

```
Dep_hour
Dep_min
```

Departure timing affects flight pricing.

---

### 5.3 Extract Arrival Time Features

From `Arrival_Time`:

```
Arrival_hour
Arrival_min
```

This helps calculate travel timing patterns.

---

### 5.4 Convert Duration

Duration originally appears as:

```
2h 50m
```

It was converted into:

```
Duration_hour
Duration_min
```

This allows the model to process duration numerically.

---

### 5.5 Convert Total Stops

Stops were converted to numeric values.

| Original | Converted |
| -------- | --------- |
| non-stop | 0         |
| 1 stop   | 1         |
| 2 stops  | 2         |
| 3 stops  | 3         |
| 4 stops  | 4         |

This enables the model to understand how stops affect pricing.

---

# 6. Removing Unnecessary Columns

The following columns were removed because they were redundant:

```
Route
Additional_Info
```

These columns did not contribute significantly to price prediction.

---

# 7. Feature and Target Separation

The dataset was separated into:

### Input Features (X)

```
Airline
Source
Destination
Total_Stops
Journey_day
Journey_month
Dep_hour
Dep_min
Arrival_hour
Arrival_min
Duration_hour
Duration_min
```

### Target Variable (y)

```
Price
```

---

# 8. Categorical Feature Encoding

Some features are **categorical** and cannot be used directly by ML models.

Categorical columns:

```
Airline
Source
Destination
```

These were converted using **One Hot Encoding**.

Example:

```
Airline_Indigo
Airline_Vistara
Airline_AirIndia
```

This converts categories into binary numeric features.

---

# 9. Train-Test Split

The dataset was divided into:

```
80% Training Data
20% Testing Data
```

Purpose:

* Train the model on historical data
* Test it on **unseen data** to evaluate performance

Example:

```
Training Samples ≈ 8546
Testing Samples ≈ 2137
```

---

# 10. Model Training

Three regression models were trained.

## 10.1 Linear Regression

A baseline model that assumes a **linear relationship between features and price**.

Advantages:

* Simple
* Fast
* Interpretable

Limitations:

* Cannot capture complex nonlinear patterns.

---

## 10.2 Decision Tree Regressor

A tree-based model that learns **decision rules** from data.

Example rule:

```
If Airline = Vistara AND Stops = 0
→ Higher price
```

Advantages:

* Captures nonlinear relationships
* Easy to interpret

---

## 10.3 Random Forest Regressor

Random Forest is an **ensemble of multiple decision trees**.

Key concepts:

* Bootstrap Sampling
* Feature Randomization
* Aggregation of predictions

Each tree predicts a price, and the final prediction is the **average of all trees**.

Advantages:

* Handles nonlinear relationships
* Reduces overfitting
* Produces more stable predictions

---

# 11. Model Evaluation

Three metrics were used to evaluate model performance.

## Mean Absolute Error (MAE)

Average difference between predicted and actual price.

```
Lower MAE = better model
```

---

## Root Mean Squared Error (RMSE)

Measures prediction error while penalizing large mistakes.

```
Lower RMSE = better model
```

---

## R² Score (Coefficient of Determination)

Measures how well the model explains price variation.

Range:

```
0 → poor model
1 → perfect prediction
```

Example interpretation:

```
R² = 0.80
```

Meaning the model explains **80% of price variability**.

---

# 12. Model Comparison

Typical results observed:

| Model             | R² Score |
| ----------------- | -------- |
| Linear Regression | ~0.62    |
| Decision Tree     | ~0.75    |
| Random Forest     | ~0.80    |

Conclusion:

**Random Forest performed best** because it captured nonlinear relationships between flight features and ticket prices.

---

# 13. Model Saving

The final trained Random Forest model was saved for later use.

```
pickle.dump(model)
```

Saved model file:

```
flight_price_model.pkl
```

This allows the model to be reused without retraining.

---

# 14. Final Outcome

The trained model can now predict flight ticket prices based on:

```
Airline
Source
Destination
Stops
Journey Day
Journey Month
Departure Hour
Duration
```

Example prediction output:

```
Predicted Ticket Price: ₹6,540
```

---

# 15. Future Extensions

Possible improvements include:

* Flight delay prediction
* Price trend forecasting
* Real-time airline data integration
* Interactive web-based prediction platform
* Price change simulation for different travel conditions

---

# 16. Key Machine Learning Concepts Demonstrated

This project demonstrates understanding of:

* Supervised Learning
* Regression Models
* Feature Engineering
* Categorical Encoding
* Model Evaluation Metrics
* Ensemble Learning
* Machine Learning Pipeline Design

---

**End of Documentation**
