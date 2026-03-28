import pandas as pd
import os
os.makedirs("model", exist_ok=True)
from sklearn.ensemble import RandomForestClassifier
import joblib

df = pd.read_csv("creditcard.csv")

X = df.drop("Class", axis=1)
y = df["Class"]

model = RandomForestClassifier(n_estimators=50)
model.fit(X, y)

joblib.dump(model, "model/model.pkl")

print("DONE")