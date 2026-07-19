"""
IPL Ticket Price Predictor — Flask Application
================================================
Professional Flask web app for predicting IPL ticket prices.

Run: python application.py
URL: http://127.0.0.1:5000
"""

import os
import pickle
import json
import datetime
import numpy as np
from flask import Flask, render_template, request, jsonify, session

# ──────────────────────────────────────────────────────────────────────────────
# App Initialization
# ──────────────────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = "ipl_ticket_predictor_secret_2025"

# ──────────────────────────────────────────────────────────────────────────────
# Load Model and Encoders
# ──────────────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "model.pkl"), "rb") as f:
    MODEL = pickle.load(f)

with open(os.path.join(BASE_DIR, "model_artifacts", "encoders.pkl"), "rb") as f:
    ENCODERS = pickle.load(f)

with open(os.path.join(BASE_DIR, "model_artifacts", "feature_columns.pkl"), "rb") as f:
    FEATURE_COLUMNS = pickle.load(f)

# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────
STADIUMS = [
    "Rajiv Gandhi International Stadium",
    "Wankhede Stadium",
    "MA Chidambaram Stadium (Chepauk)",
    "M Chinnaswamy Stadium",
    "Narendra Modi Stadium",
    "Eden Gardens",
    "Arun Jaitley Stadium",
    "Punjab Cricket Association Stadium",
    "Sawai Mansingh Stadium",
    "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium",
]

TEAMS = ["CSK", "MI", "RCB", "SRH", "KKR", "GT", "LSG", "PBKS", "DC", "RR"]

STAND_TYPE_BY_CATEGORY = {
    "Economy":  ["East", "West", "North", "South"],
    "Standard": ["East", "West", "North", "South"],
    "Premium":  ["North", "South", "Premium"],
    "VIP":      ["VIP", "Premium"],
    "Corporate":["Corporate Box", "VIP"],
}

VENUE_CITY = {
    "Rajiv Gandhi International Stadium": "Hyderabad",
    "Wankhede Stadium": "Mumbai",
    "MA Chidambaram Stadium (Chepauk)": "Chennai",
    "M Chinnaswamy Stadium": "Bengaluru",
    "Narendra Modi Stadium": "Ahmedabad",
    "Eden Gardens": "Kolkata",
    "Arun Jaitley Stadium": "Delhi",
    "Punjab Cricket Association Stadium": "Mohali",
    "Sawai Mansingh Stadium": "Jaipur",
    "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium": "Lucknow",
}

VENUE_HOME_TEAM = {
    "Rajiv Gandhi International Stadium": "SRH",
    "Wankhede Stadium": "MI",
    "MA Chidambaram Stadium (Chepauk)": "CSK",
    "M Chinnaswamy Stadium": "RCB",
    "Narendra Modi Stadium": "GT",
    "Eden Gardens": "KKR",
    "Arun Jaitley Stadium": "DC",
    "Punjab Cricket Association Stadium": "PBKS",
    "Sawai Mansingh Stadium": "RR",
    "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium": "LSG",
}

STADIUM_CAPACITY = {
    "Rajiv Gandhi International Stadium": 55000,
    "Wankhede Stadium": 33108,
    "MA Chidambaram Stadium (Chepauk)": 50000,
    "M Chinnaswamy Stadium": 35000,
    "Narendra Modi Stadium": 132000,
    "Eden Gardens": 66000,
    "Arun Jaitley Stadium": 41820,
    "Punjab Cricket Association Stadium": 26950,
    "Sawai Mansingh Stadium": 30000,
    "Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium": 50000,
}

TEAM_POPULARITY = {
    "CSK": "High", "MI": "High", "RCB": "High",
    "KKR": "Medium", "SRH": "Medium", "DC": "Medium",
    "RR": "Medium", "GT": "Medium", "LSG": "Low", "PBKS": "Low"
}

BASE_PRICES = {
    "Economy": 500, "Standard": 900,
    "Premium": 1800, "VIP": 3500, "Corporate": 5000
}


# ──────────────────────────────────────────────────────────────────────────────
# Helper: Safe Encode
# ──────────────────────────────────────────────────────────────────────────────
def safe_encode(encoder, value, col_name):
    """Encode a value; if unseen, use the closest class index."""
    try:
        return int(encoder.transform([value])[0])
    except ValueError:
        # Fallback: return median class index
        return len(encoder.classes_) // 2


# ──────────────────────────────────────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    """Homepage — renders the prediction form."""
    context = {
        "stadiums": STADIUMS,
        "teams": TEAMS,
        "seat_categories": list(BASE_PRICES.keys()),
        "stand_types": list(STAND_TYPE_BY_CATEGORY.values()),
        "weathers": ["Sunny", "Cloudy", "Rainy", "Partly Cloudy"],
        "demand_levels": ["Low", "Medium", "High", "Very High"],
        "match_times": ["3:30 PM", "7:30 PM"],
        "match_types": ["League", "Qualifier", "Eliminator", "Final"],
        "stand_map": json.dumps(STAND_TYPE_BY_CATEGORY),
    }
    return render_template("index.html", **context)


@app.route("/predict", methods=["POST"])
def predict():
    """
    Accepts form submission, builds feature vector,
    runs model inference, and returns JSON result.
    """
    try:
        # ── Parse form ──────────────────────────────────────────────────────
        match_date_str  = request.form.get("match_date", "")
        match_time      = request.form.get("match_time", "7:30 PM")
        stadium         = request.form.get("stadium", "")
        home_team       = request.form.get("home_team", "")
        away_team       = request.form.get("away_team", "")
        seat_category   = request.form.get("seat_category", "Economy")
        stand_type      = request.form.get("stand_type", "East")
        weekend         = request.form.get("weekend", "No")
        holiday         = request.form.get("holiday", "No")
        weather         = request.form.get("weather", "Sunny")
        demand_level    = request.form.get("demand_level", "Medium")
        days_before     = int(request.form.get("days_before_match", 7))
        available_seats = int(request.form.get("available_seats", 5000))
        match_type      = request.form.get("match_type", "League")

        # ── Derived fields ──────────────────────────────────────────────────
        try:
            dt = datetime.datetime.strptime(match_date_str, "%Y-%m-%d")
            match_day = dt.strftime("%A")
        except Exception:
            match_day = "Saturday"

        city                    = VENUE_CITY.get(stadium, "Hyderabad")
        opponent_popularity     = TEAM_POPULARITY.get(away_team, "Medium")
        stadium_capacity        = STADIUM_CAPACITY.get(stadium, 50000)
        prev_attendance         = int(stadium_capacity * 0.75)
        rain_prob               = 60 if weather == "Rainy" else 10
        booking_time            = "7+ days before" if days_before >= 7 else "1-3 days before"

        # ── Validate team combination ────────────────────────────────────────
        if home_team == away_team:
            return jsonify({"error": "Home team and Away team cannot be the same."}), 400

        # ── Build feature dict ───────────────────────────────────────────────
        raw_features = {
            "Match_Day":                match_day,
            "Match_Time":               match_time,
            "Stadium":                  stadium,
            "City":                     city,
            "Home_Team":                home_team,
            "Away_Team":                away_team,
            "Stand_Type":               stand_type,
            "Seat_Category":            seat_category,
            "Match_Type":               match_type,
            "Weekend":                  weekend,
            "Holiday":                  holiday,
            "Opponent_Popularity":      opponent_popularity,
            "Weather":                  weather,
            "Rain_Probability":         rain_prob,
            "Demand_Level":             demand_level,
            "Previous_Match_Attendance": prev_attendance,
            "Stadium_Capacity":         stadium_capacity,
            "Available_Seats":          available_seats,
            "Booking_Time":             booking_time,
            "Days_Before_Match":        days_before,
        }

        # ── Encode categoricals ──────────────────────────────────────────────
        encoded = {}
        cat_cols = [
            "Match_Day", "Match_Time", "Stadium", "City",
            "Home_Team", "Away_Team", "Stand_Type", "Seat_Category",
            "Match_Type", "Weekend", "Holiday", "Opponent_Popularity",
            "Weather", "Demand_Level", "Booking_Time"
        ]
        for col in cat_cols:
            encoded[col] = safe_encode(ENCODERS[col], raw_features[col], col)

        num_cols = [
            "Rain_Probability", "Previous_Match_Attendance",
            "Stadium_Capacity", "Available_Seats", "Days_Before_Match"
        ]
        for col in num_cols:
            encoded[col] = raw_features[col]

        # ── Assemble feature vector in correct order ─────────────────────────
        feature_vector = np.array([[encoded[col] for col in FEATURE_COLUMNS]])

        # ── Predict ──────────────────────────────────────────────────────────
        predicted_price = float(MODEL.predict(feature_vector)[0])
        predicted_price = max(300, round(predicted_price / 50) * 50)

        # ── Compute confidence band ──────────────────────────────────────────
        confidence_low  = int(predicted_price * 0.88)
        confidence_high = int(predicted_price * 1.12)

        # ── Save to session history ──────────────────────────────────────────
        if "history" not in session:
            session["history"] = []

        history_entry = {
            "id":            len(session["history"]) + 1,
            "date":          match_date_str,
            "stadium":       stadium,
            "home":          home_team,
            "away":          away_team,
            "seat":          seat_category,
            "stand":         stand_type,
            "demand":        demand_level,
            "price":         int(predicted_price),
            "timestamp":     datetime.datetime.now().strftime("%d %b %Y, %I:%M %p"),
        }
        session["history"].insert(0, history_entry)
        session["history"] = session["history"][:10]   # Keep last 10
        session.modified = True

        return jsonify({
            "success":          True,
            "predicted_price":  int(predicted_price),
            "confidence_low":   confidence_low,
            "confidence_high":  confidence_high,
            "seat_category":    seat_category,
            "stand_type":       stand_type,
            "stadium":          stadium,
            "match_day":        match_day,
            "match_type":       match_type,
        })

    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500


@app.route("/history")
def history():
    """Returns prediction history as JSON."""
    hist = session.get("history", [])
    return jsonify({"history": hist})


@app.route("/clear_history", methods=["POST"])
def clear_history():
    """Clears prediction history."""
    session.pop("history", None)
    return jsonify({"success": True})


@app.route("/get_stands", methods=["POST"])
def get_stands():
    """Returns valid stand types for the given seat category (AJAX)."""
    seat_category = request.json.get("seat_category", "Economy")
    stands = STAND_TYPE_BY_CATEGORY.get(seat_category, ["East", "West", "North", "South"])
    return jsonify({"stands": stands})


@app.route("/health")
def health():
    """Health-check endpoint."""
    return jsonify({"status": "ok", "model": "Gradient Boosting Regressor"})


# ──────────────────────────────────────────────────────────────────────────────
# Entry Point
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  IPL Ticket Price Predictor")
    print("  Flask Server starting...")
    print("  URL: http://127.0.0.1:5000")
    print("=" * 55)
    app.run(debug=True, host="127.0.0.1", port=5000)
