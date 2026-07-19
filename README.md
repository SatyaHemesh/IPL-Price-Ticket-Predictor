# 🏏 IPL Ticket Price Predictor

> A production-ready Machine Learning web application that predicts IPL cricket match ticket prices using historical data and a Gradient Boosting Regression model.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-black?logo=flask)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3-orange?logo=scikit-learn)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?logo=bootstrap)

---

## 📋 Project Overview

The **IPL Ticket Price Predictor** is a full-stack ML web application that estimates IPL match ticket prices based on real-world factors such as:

- Stadium and city
- Home & Away teams
- Seat category and stand type
- Match type (League / Qualifier / Final)
- Demand level, weather, and booking timing
- Holiday & weekend flags

**Model accuracy:** R² = **96.7%** | RMSE = **₹468**

---

## ✨ Features

| Feature | Details |
|--------|---------|
| 🤖 ML Model | Gradient Boosting Regressor (best of 4 models compared) |
| 🎨 IPL-Themed UI | Dark Blue · Orange · White — responsive Bootstrap 5 |
| 📊 Model Comparison | Linear, Decision Tree, Random Forest, Gradient Boosting |
| 📜 Prediction History | Session-backed last 10 predictions |
| ⬇️ Download | Export prediction as `.txt` report |
| 🌗 Dark/Light Mode | Toggle between themes |
| ✅ Input Validation | Team conflict detection, required fields |
| 🏟️ SRH Demo | One-click load SRH vs MI at Rajiv Gandhi Stadium |
| 💫 Animations | Price count-up, floating ticket card, particles |

---

## 📁 Project Structure

```
IPL-Ticket-Price-Predictor/
│
├── application.py          ← Flask web server
├── train_model.py          ← Model training script
├── model.pkl               ← Saved best model (Gradient Boosting)
├── requirements.txt        ← Python dependencies
├── README.md               ← This file
│
├── dataset/
│   └── ipl_ticket_dataset.csv   ← 1,200 synthetic IPL records
│
├── model_artifacts/
│   ├── encoders.pkl             ← Label encoders for categorical features
│   ├── feature_columns.pkl      ← Feature column order
│   └── model_joblib.pkl         ← Redundant joblib backup
│
├── static/
│   ├── style.css                ← IPL-themed stylesheet
│   └── script.js                ← Frontend logic (AJAX, animations)
│
├── templates/
│   └── index.html               ← Main prediction UI (Jinja2)
│
└── screenshots/                 ← Add demo screenshots here
```

---

## 📦 Dataset

**File:** `dataset/ipl_ticket_dataset.csv`  
**Records:** 1,200 rows | **Columns:** 23

Key columns:

| Column | Description |
|--------|-------------|
| Stadium | One of 10 major IPL venues |
| Home_Team / Away_Team | 10 IPL teams (CSK, MI, RCB, SRH, KKR, ...) |
| Seat_Category | Economy · Standard · Premium · VIP · Corporate |
| Demand_Level | Low · Medium · High · Very High |
| Match_Type | League · Qualifier · Eliminator · Final |
| Predicted_Price | Target variable (₹450 – ₹13,000+) |

---

## 🤖 Machine Learning

### Models Compared

| Model | MAE (₹) | RMSE (₹) | R² Score |
|-------|---------|---------|---------|
| Linear Regression | 2,274 | 2,603 | -0.016 |
| Decision Tree | 539 | 897 | 0.879 |
| Random Forest | 444 | 702 | 0.926 |
| **Gradient Boosting** ✓ | **316** | **468** | **0.967** |

### Feature Engineering

- Label encoding of all categorical columns
- Derived features: `Match_Day`, `City`, `Opponent_Popularity`
- Price multipliers: rivalry pairs, playoffs, demand, weather, booking window

---

## 🚀 Installation

### 1. Clone / Extract the project

```bash
cd IPL-Ticket-Price-Predictor
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate       # Linux/macOS
venv\Scripts\activate          # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ How to Run

### Step 1 — Train the model

```bash
python train_model.py
```

This will:
- Load `dataset/ipl_ticket_dataset.csv`
- Train and compare 4 ML models
- Save the best model as `model.pkl`

### Step 2 — Start the Flask app

```bash
python application.py
```

### Step 3 — Open in browser

```
http://127.0.0.1:5000
```

---

## 🎯 Special Prediction Case

Selecting the following inputs:

| Field | Value |
|-------|-------|
| Date | 26 June 2026 |
| Time | 7:30 PM |
| Stadium | Rajiv Gandhi International Stadium |
| Home Team | SRH |
| Away Team | MI |
| Seat | VIP |

Expected output: **₹1,700 – ₹2,500** (depending on demand and stand)

You can use the **SRH Demo** button to auto-fill these values.

---

## 📸 Screenshots

> Add screenshots to the `screenshots/` folder and link them here.

---

## 🔮 Future Improvements

- [ ] Real IPL ticket data scraping (BookMyShow, Paytm)
- [ ] Player form and pitch condition features
- [ ] Neural network (MLP) model comparison
- [ ] REST API with Swagger documentation
- [ ] Deployment on Render / Railway / AWS EC2
- [ ] Mobile app (React Native)
- [ ] Email prediction reports

---

## 👨‍💻 Author

**Routhu Satya Hemesh**  

---

## 📄 License

MIT License — Free for educational and non-commercial use.
