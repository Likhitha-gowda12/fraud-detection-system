from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np
import sqlite3
import threading
import time
import random

app = Flask(__name__)

# Load model
model = joblib.load("model/model.pkl")

# Initialize database
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS transactions
                 (amount REAL, result TEXT, confidence REAL)''')
    conn.commit()
    conn.close()

init_db()

# 🔥 AUTO TRANSACTION GENERATOR (REAL-TIME SIMULATION)
def generate_transactions():
    while True:
        amount = random.randint(100, 50000)

        data = np.random.normal(0, 1, (1, 30))
        data[0][-1] = amount

        prob = model.predict_proba(data)[0][1] * 100

        if amount > 15000:
            prob += 20

        confidence = round(prob, 2)

        if amount > 20000:
            result = "High Risk Fraud"
        elif confidence > 60:
            result = "Suspicious"
        elif amount > 10000:
            result = "Suspicious"
        else:
            result = "Safe"

        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("INSERT INTO transactions VALUES (?, ?, ?)", (amount, result, confidence))
        conn.commit()
        conn.close()

        time.sleep(5)  # every 5 seconds

# Start background thread
thread = threading.Thread(target=generate_transactions)
thread.daemon = True
thread.start()

# Home
@app.route('/')
def home():
    return render_template("index.html")

# Manual prediction
@app.route('/predict', methods=['POST'])
def predict():
    amount = float(request.form['amount'])

    data = np.random.normal(0, 1, (1, 30))
    data[0][-1] = amount

    prob = model.predict_proba(data)[0][1] * 100

    if amount > 15000:
        prob += 20

    confidence = round(prob, 2)

    if amount > 20000:
        result = "High Risk Fraud"
    elif confidence > 60:
        result = "Suspicious"
    elif amount > 10000:
        result = "Suspicious"
    else:
        result = "Safe"

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("INSERT INTO transactions VALUES (?, ?, ?)", (amount, result, confidence))
    conn.commit()
    conn.close()

    return render_template("index.html", prediction=result, confidence=confidence)

# Dashboard
@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    data = c.execute("SELECT * FROM transactions ORDER BY rowid DESC LIMIT 10").fetchall()

    total = c.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
    fraud = len([x for x in data if "High Risk" in x[1]])
    suspicious = len([x for x in data if "Suspicious" in x[1]])
    safe = len([x for x in data if "Safe" in x[1]])

    conn.close()

    return render_template(
        "dashboard.html",
        data=data,
        total=total,
        fraud=fraud,
        suspicious=suspicious,
        safe=safe
    )

# API
@app.route('/api/predict', methods=['POST'])
def api_predict():
    data = request.json['features']
    prediction = model.predict([data])[0]
    prob = model.predict_proba([data])[0][1]

    return jsonify({
        "prediction": int(prediction),
        "confidence": float(prob)
    })

# Run
if __name__ == "__main__":
    app.run()