# app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import tensorflow as tf
import joblib
import subprocess
import numpy as np
from predict_health import predict_health
import threading
import time
import os
from pysnmp.hlapi import *
import datetime
import csv
import requests

app = Flask(__name__)
community = "ai"

def snmpwalk(ip, oid):
    try:
        result = subprocess.check_output(
            ["snmpwalk", "-v2c", "-c", community, ip, oid],
            stderr=subprocess.STDOUT
        ).decode("utf-8")
        value = result.strip().split(":")[-1].strip()
        return float(value)
    except Exception as e:
        print(f"[ERROR] SNMP failed for {ip} OID {oid}: {e}")
        return None

oids = {
    "cpu": "1.3.6.1.4.1.9.2.1.58.0",
    "in_errors": "1.3.6.1.2.1.2.2.1.14.1",
    "out_errors": "1.3.6.1.2.1.2.2.1.20.1"
}
def get_snmp_data(ip):
    return {
        "cpu": snmpwalk(ip, oids["cpu"]),
        "in_errors": snmpwalk(ip, oids["in_errors"]),
        "out_errors": snmpwalk(ip, oids["out_errors"])
    }
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/train", methods=["GET", "POST"])
def train():
    if request.method == "POST":
        file = request.files["file"]
        if file:
            data = pd.read_csv(file)
            data.dropna(inplace=True)

            X = data[["cpu", "in_errors", "out_errors"]]
            y = data["label"]

            label_encoder = LabelEncoder()
            y_encoded = label_encoder.fit_transform(y)

            X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

            model = Sequential([
                Dense(16, activation='relu', input_shape=(3,)),
                Dense(8, activation='relu'),
                Dense(3, activation='softmax')
            ])

            model.compile(optimizer='adam',
                          loss='sparse_categorical_crossentropy',
                          metrics=['accuracy'])

            model.fit(X_train, y_train, epochs=30, batch_size=8, validation_split=0.1)

            model.save("snmp_health_model.keras")
            joblib.dump(label_encoder, "label_encoder.pkl")

            loss, accuracy = model.evaluate(X_test, y_test)
            percent = str(accuracy*100)+"%"
            
            msg = "Training complete! with accuracy: "+percent

            return render_template("train.html", message=msg)

    return render_template("train.html")

@app.route("/predict", methods=["GET", "POST"])
def predict():
    if request.method == "POST":
        ip = request.form.get("ip")
        if ip:
            cpu = snmpwalk(ip, oids["cpu"])
            in_errors = snmpwalk(ip, oids["in_errors"])
            out_errors = snmpwalk(ip, oids["out_errors"])

            if None in (cpu, in_errors, out_errors):
                return render_template("predict.html", error="SNMP data fetch failed.")

            health = predict_health(cpu, in_errors, out_errors)
            return render_template("predict.html", health=health, ip=ip, cpu=cpu, in_errors=in_errors, out_errors=out_errors)

    return render_template("predict.html")

console_lines = []

# Utility function to append console output
def log_to_console(message):
    console_lines.append(message)
    if len(console_lines) > 100:
        console_lines.pop(0)

csv_file = "cisco_snmp_health.csv"
header = ["timestamp", "ip", "cpu", "in_errors", "out_errors", "label"]

def determine_health(cpu, in_err, out_err):
    if cpu is None or in_err is None or out_err is None:
        return "unknown"
    if cpu > 80 or in_err > 50 or out_err > 50:
        return "failure"
    elif cpu > 50 or in_err > 10 or out_err > 10:
        return "warning"
    else:
        return "healthy"

def poll_devices(ips, duration):
    start_time = time.time()

    # Try to create the CSV with header if it doesn't exist
    try:
        with open(csv_file, "x") as f:
            writer = csv.writer(f)
            writer.writerow(header)
    except FileExistsError:
        pass  # Already exists

    while (time.time() - start_time) < duration:
        now = datetime.datetime.now().isoformat()
        rows = []

        for ip in ips:
            row = [now, ip]
            metrics = []

            for label, oid in oids.items():
                value = snmpwalk(ip, oid)
                metrics.append(value)
                row.append(value)

            health = determine_health(*metrics)
            row.append(health)

            rows.append(row)

            log_to_console(f"{ip}: CPU={metrics[0]}, InErr={metrics[1]}, OutErr={metrics[2]}, Status={health}")

        # Write to CSV
        with open(csv_file, "a") as f:
            writer = csv.writer(f)
            writer.writerows(rows)

        time.sleep(1)  # 1-second polling interval

# Route to fetch console output for real-time updates
@app.route("/get_console")
def get_console():
    return jsonify({"console": console_lines})

# Your gather data route
@app.route("/gather", methods=["GET", "POST"])
def gather():
    global console_lines
    if request.method == "POST":
        console_lines = []

        ips = []
        if "file" in request.files and request.files["file"].filename != "":
            file = request.files["file"]
            df = pd.read_csv(file)
            ips = df["IP"].tolist()
        elif "ips" in request.form and request.form["ips"].strip() != "":
            ips = [ip.strip() for ip in request.form["ips"].strip().splitlines() if ip.strip()]

        duration = int(request.form.get("duration"))

        if not ips:
            log_to_console("No IPs provided.")
            return render_template("gather.html", console_lines=console_lines)

        # Start gathering in a thread
        threading.Thread(target=poll_devices, args=(ips, duration)).start()

        return redirect(url_for('gather'))

    return render_template("gather.html", console_lines=console_lines)

@app.route("/ask", methods=["GET", "POST"])
def ask():
    answer = ""
    if request.method == "POST":
        user_question = request.form["question"]
        print(user_question)
        try:
            df = pd.read_csv("cisco_snmp_health_test.csv")

            # Keep last 50 entries for faster response
            recent_data = df.tail(50).to_dict(orient="records")

            # Create the prompt
            prompt = f"""You are a network assistant.
Here is recent SNMP health data from routers:
{recent_data}

Answer the following question based on the data:
{user_question}
"""

            # Call local Ollama model
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "tinyllama",  # or "llama3", etc.
                    "prompt": prompt,
                    "stream": False
                }
            )
            print(answer)
            if response.status_code == 200:
                result = response.json()
                answer = result["response"]
            else:
                answer = f"Error from LLM API: {response.text}"

        except Exception as e:
            answer = f"Error processing your question: {e}"
    print(answer)
    return render_template("ask.html", answer=answer)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

