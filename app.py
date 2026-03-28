@app.route('/predict', methods=['POST'])
def predict():
    name = request.form['name']
    amount = float(request.form['amount'])

    data = np.random.normal(0, 1, (1, 30))
    data[0][-1] = amount

    prob = model.predict_proba(data)[0][1] * 100

    if amount > 15000:
        prob += 10

    confidence = round(prob, 2)

    if confidence > 75:
        result = "High Risk Fraud"
    elif confidence > 40:
        result = "Suspicious"
    else:
        result = "Safe"

    # Save
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("INSERT INTO transactions VALUES (?, ?, ?)", (amount, result, confidence))
    conn.commit()
    conn.close()

    return render_template(
        "payment_result.html",
        name=name,
        amount=amount,
        result=result,
        confidence=confidence
    )