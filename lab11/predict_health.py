import tensorflow as tf
import joblib
import numpy as np

def predict_health(CPU, in_errors, out_errors):

    # Load model + encoder
    model = tf.keras.models.load_model("snmp_health_model.keras")
    label_encoder = joblib.load("label_encoder.pkl")

    # Example SNMP values: CPU, in_errors, out_errors
    sample = np.array([[CPU, in_errors, out_errors]])


    # Predict
    pred = model.predict(sample)
    label = label_encoder.inverse_transform([pred.argmax()])[0]
    print(f"Predicted health state: {label}")
    return label
