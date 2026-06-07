from flask import Flask, request, jsonify, render_template
import pickle
import re
import requests
import pandas as pd
import os
import sqlite3

app = Flask(__name__)

# ===============================
# LOAD MODEL
# ===============================
model      = pickle.load(open("sentiment_model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl",      "rb"))

DATASET_FILE = "dataset.csv"
DB_PATH      = "safety_data.db"

# ===============================
# KNOWN LOCATIONS — hardcoded exact coordinates
# Prevents Nominatim from returning wrong results for key campus locations.
# Add any location that keeps getting wrong coords here.
# Keys are lowercase — matched case-insensitively.
# ===============================
KNOWN_LOCATIONS = {
    # Vishwakarma University campus — all common name variants
    "vishwakarma university":           (18.4592, 73.8853),
    "vit pune":                         (18.4592, 73.8853),
    "vishwakarma uni":                  (18.4592, 73.8853),
    "vu pune":                          (18.4592, 73.8853),
    "vishwakarma institute":            (18.4592, 73.8853),
    "vishwakarma university pune":      (18.4592, 73.8853),
    "vit kondhwa":                      (18.4592, 73.8853),

    # Other key Pune locations (existing survey areas)
    "bopdev ghat":                      (18.4422, 73.8371),
    "sinhgad road":                     (18.4802, 73.8098),
    "katraj chowk":                     (18.4512, 73.8612),
    "gangadham":                        (18.5011, 73.8388),
    "swargate":                         (18.5031, 73.8599),
    "shanti nagar":                     (18.4912, 73.8621),
    "shantinagar":                      (18.4912, 73.8621),
    "taljai hill":                      (18.4768, 73.8744),
    "khadki":                           (18.5688, 73.8526),
    "shivajinagar":                     (18.5302, 73.8476),
    "kothrud":                          (18.5074, 73.8077),
    "baner":                            (18.5590, 73.7868),
    "wakad":                            (18.5985, 73.7610),
    "hinjewadi":                        (18.5912, 73.7378),
    "viman nagar":                      (18.5679, 73.9143),
    "koregaon park":                    (18.5363, 73.8938),
    "hadapsar":                         (18.5018, 73.9252),
    "aundh":                            (18.5594, 73.8078),
}

def resolve_coordinates(area, pre_lat=None, pre_lon=None, df=None):
    """
    Resolve lat/lon for a given area name.
    Priority order:
      1. Known locations dictionary (hardcoded exact coords)
      2. Pre-resolved coords passed from frontend
      3. Existing CSV entry
      4. Nominatim geocoding (fallback)
    """
    key = area.lower().strip()

    # 1. Check known locations dict first — most accurate
    if key in KNOWN_LOCATIONS:
        return KNOWN_LOCATIONS[key]

    # Also do partial match for known locations
    for known_key, coords in KNOWN_LOCATIONS.items():
        if known_key in key or key in known_key:
            return coords

    # 2. Use pre-resolved coords from frontend if provided
    if pre_lat is not None and pre_lon is not None:
        return float(pre_lat), float(pre_lon)

    # 3. Use existing CSV entry
    if df is not None and area in df["Location"].values:
        row = df[df["Location"] == area].iloc[0]
        return row["lat"], row["lon"]

    # 4. Fallback to Nominatim
    return get_coordinates(area)

# ===============================
# CREATE DATASET IF NOT EXISTS (original)
# ===============================
if not os.path.exists(DATASET_FILE):
    df = pd.DataFrame(columns=["Location", "Sentiment", "lat", "lon"])
    df.to_csv(DATASET_FILE, index=False)

# ===============================
# INIT SQLITE DB (new — for aggregation)
# ===============================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            location   TEXT    NOT NULL,
            lat        REAL    NOT NULL,
            lon        REAL    NOT NULL,
            user_input TEXT,
            sentiment  TEXT    NOT NULL,
            safety     TEXT    NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ===============================
# TEXT PREPROCESS (original — unchanged)
# ===============================
def preprocess(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z ]", " ", text)
    return text

# ===============================
# HOME PAGE (original — unchanged)
# ===============================
@app.route("/")
def home():
    return render_template("index.html")

# ===============================
# PREDICT SENTIMENT (original — unchanged)
# ===============================
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    text = data["text"]
    clean = preprocess(text)
    vec   = vectorizer.transform([clean])
    prediction = model.predict(vec)[0]

    if prediction == "Negative":
        risk   = 80
        emotion = "Fear"
    elif prediction == "Neutral":
        risk   = 50
        emotion = "Neutral"
    else:
        risk   = 20
        emotion = "Comfort"

    return jsonify({
        "sentiment":  prediction,
        "emotion":    emotion,
        "risk_score": risk
    })

# ===============================
# GET COORDINATES (original — unchanged, used as fallback)
# ===============================
def get_coordinates(area):
    url      = f"https://nominatim.openstreetmap.org/search?q={area}+Pune+India&format=json"
    response = requests.get(url, headers={"User-Agent": "SafetyAI/1.0"}).json()
    if len(response) > 0:
        return float(response[0]["lat"]), float(response[0]["lon"])
    return None, None

# ===============================
# SAVE FEEDBACK (original preserved + extended with known-locations override)
# ===============================
@app.route("/submit-feedback", methods=["POST"])
def submit_feedback():
    data      = request.get_json()
    area      = data["area"]
    sentiment = data["sentiment"]
    user_text = data.get("text", "")

    # ── Original CSV logic (unchanged) ──
    df = pd.read_csv(DATASET_FILE)

    # Resolve coordinates using priority system
    pre_lat = data.get("lat")
    pre_lon = data.get("lon")
    lat, lon = resolve_coordinates(area, pre_lat, pre_lon, df)

    new_row = {"Location": area, "Sentiment": sentiment, "lat": lat, "lon": lon}
    df = pd.concat([df, pd.DataFrame([new_row])])
    df.to_csv(DATASET_FILE, index=False)

    # ── Also write to SQLite for aggregation ──
    if lat and lon:
        safety_map = {"Positive": "Safe", "Neutral": "Moderate", "Negative": "Unsafe"}
        safety     = safety_map.get(sentiment, "Moderate")

        conn = get_db()
        conn.execute(
            'INSERT INTO reports (location, lat, lon, user_input, sentiment, safety) VALUES (?,?,?,?,?,?)',
            (area, float(lat), float(lon), user_text, sentiment, safety)
        )
        conn.commit()
        conn.close()

    return jsonify({"status": "saved", "lat": lat, "lon": lon, "sentiment": sentiment})

# ===============================
# MAP DATA (original — unchanged)
# ===============================
@app.route("/map-data")
def map_data():
    df        = pd.read_csv(DATASET_FILE)
    score_map = {"Positive": 1, "Neutral": 0, "Negative": -1}
    df["score"] = df["Sentiment"].map(score_map)

    area_scores = df.groupby(["Location", "lat", "lon"])["score"].mean().reset_index()
    result = []

    for _, row in area_scores.iterrows():
        score = row["score"]
        color = "green" if score > 0.3 else ("orange" if score < -0.3 else "yellow")
        result.append({
            "area":  row["Location"],
            "lat":   row["lat"],
            "lng":   row["lon"],
            "color": color
        })

    return jsonify(result)

# ===============================
# GET LOCATIONS DATA (aggregated — for real-time map markers)
# ===============================
@app.route("/get_locations_data", methods=["GET"])
def get_locations_data():
    conn = get_db()
    rows = conn.execute('''
        SELECT
            location,
            AVG(lat)  AS lat,
            AVG(lon)  AS lon,
            SUM(CASE WHEN safety = 'Safe'     THEN 1 ELSE 0 END) AS safe,
            SUM(CASE WHEN safety = 'Moderate' THEN 1 ELSE 0 END) AS moderate,
            SUM(CASE WHEN safety = 'Unsafe'   THEN 1 ELSE 0 END) AS unsafe
        FROM reports
        GROUP BY location
    ''').fetchall()
    conn.close()

    return jsonify([
        {
            "location": r["location"],
            "lat":      round(r["lat"],  6),
            "lon":      round(r["lon"],  6),
            "safe":     r["safe"],
            "moderate": r["moderate"],
            "unsafe":   r["unsafe"]
        }
        for r in rows
    ])

# ===============================
# RECENT REPORTS FEED
# ===============================
@app.route("/recent_reports", methods=["GET"])
def recent_reports():
    conn = get_db()
    rows = conn.execute(
        'SELECT location, safety, sentiment, created_at FROM reports ORDER BY created_at DESC LIMIT 20'
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

# ===============================
# RUN APP (original — unchanged)
# ===============================
if __name__ == "__main__":
    app.run(debug=True) 