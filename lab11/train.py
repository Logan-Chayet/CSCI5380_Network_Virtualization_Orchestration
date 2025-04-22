import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

# Load the CSV
data = pd.read_csv("cisco_snmp_health_test.csv")

# Drop any rows with missing values
data.dropna(inplace=True)

# Features and labels
X = data[["cpu", "in_errors", "out_errors"]]
y = data["label"]

# Encode labels (healthy=0, warning=1, failure=2)
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# Define a simple neural network
model = Sequential([
    Dense(16, activation='relu', input_shape=(3,)),
    Dense(8, activation='relu'),
    Dense(3, activation='softmax')  # 3 output classes
])

model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# Train the model
model.fit(X_train, y_train, epochs=30, batch_size=8, validation_split=0.1)

# Evaluate on test set
loss, accuracy = model.evaluate(X_test, y_test)
print(f"\n[✓] Test Accuracy: {accuracy:.2f}")

# Save model and label encoder
model.save("snmp_health_model.keras")
import joblib
joblib.dump(label_encoder, "label_encoder.pkl")

