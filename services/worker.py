"""
Fault-Tolerant ML Worker Service
- This service handles model training (both primary and redundant).
"""

import argparse
import time
import os
import json
from datetime import datetime

# Tensorflow modules
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.datasets import mnist

MODEL_DIR = "shared_storage"

def build_model():
    model = Sequential([
        Flatten(input_shape=(28, 28)),
        Dense(128, activation='relu'),
        Dense(10, activation='softmax')
    ])
    model.compile(optimizer='adam', loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return model

def save_model_checkpoint(model, worker_id):
    model.save(f"{MODEL_DIR}/worker{worker_id}_model.keras")


def load_model_checkpoint(worker_id):
    path = f"{MODEL_DIR}/worker{worker_id}_model.keras"
    if os.path.exists(path):
        print(f"[Worker {worker_id}] Loaded full model checkpoint.")
        return load_model(path)  # Loads full model including optimizer
    return None


def log_metrics(worker_id, role, loss, accuracy):
    """Log model metrics per worker."""
    log_path = f"logs/metrics_worker{worker_id}_{role}.log"
    timestamp = datetime.now().isoformat()
    with open(log_path, "a") as f:
        f.write(f"{timestamp}, Loss: {loss:.4f}, Accuracy: {accuracy:.4f}\n")


def get_heartbeat_path(worker_id, role):
    return f"logs/worker{worker_id}_{role}_heartbeat.txt"


def send_heartbeat(worker_id, role):
    with open(get_heartbeat_path(worker_id, role), "w") as f:
        f.write(datetime.now().isoformat())

    
def check_for_promotion(worker_id):
    promotion_flag = f"logs/promote_worker{worker_id}.flag"
    if os.path.exists(promotion_flag):
        os.remove(promotion_flag)
        return True
    return False


# Load and preprocess data once
(x_train, y_train), _ = mnist.load_data()
x_train = x_train / 255.0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", choices=["primary", "redundant"], required=True)
    parser.add_argument("--id", type=int, required=True)
    args = parser.parse_args()

    role = args.role
    worker_id = args.id

    # Load model if checkpoint exists, otherwise build fresh
    model = load_model_checkpoint(worker_id)
    if model is None:
        model = build_model()

    # Labels for primary and redundant worker
    pw_label = f"Worker {worker_id} - PW"
    rw_label = f"Worker {worker_id} - RW"

    print(f"[Worker {worker_id} - {role.upper()}] Starting training loop...")

    while True:
        send_heartbeat(worker_id, role)

        if role == "primary":
            # Training on a small batch
            history = model.fit(x_train[:256], y_train[:256], epochs=1, verbose=0)
            loss = history.history["loss"][0]
            accuracy = history.history["accuracy"][0]

            # Save checkpoint and model metrics
            save_model_checkpoint(model, worker_id)
            log_metrics(worker_id, role, loss, accuracy)

            print(f"[{pw_label}] Trained - Loss: {loss:.4f}, Accuracy: {accuracy:.4f}")

        elif role == "redundant":
            try:
                model = load_model_checkpoint(worker_id)
                print(f"[{rw_label}] Synced model from primary.")
            except Exception as e:
                print(f"Error: {str(e)}")
                print(f"{rw_label} Waiting for model checkpoint...")

            if check_for_promotion(worker_id):
                print(f"[{rw_label}] PROMOTED to PRIMARY")
                role = "primary"
