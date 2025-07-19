"""
Fault-Tolerant ML Worker Service
- This service handles model training (both primary and redundant).
"""

import argparse
import time
import os
import json
from datetime import datetime

def dummy_train_step(state):
    state["weight"] += 1
    return state

def save_checkpoint(worker_id, state):
    with open(f"shared_storage/worker{worker_id}_ckpt.json", "w") as f:
        json.dump(state, f)

def send_heartbeat(worker_id):
    with open(f"logs/worker{worker_id}_heartbeat.txt", "w") as f:
        f.write(datetime.now().isoformat())

def load_checkpoint(worker_id):
    path = f"shared_storage/worker{worker_id}_ckpt.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    else:
        return {"weight": 0}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", choices=["primary", "redundant"], required=True)
    parser.add_argument("--id", type=int, required=True)
    args = parser.parse_args()

    role = args.role
    worker_id = args.id
    state = load_checkpoint(worker_id)

    print(f"[Worker {worker_id} - {role.upper()}] Starting training loop...")

    while True:
        send_heartbeat(worker_id)

        if role == "primary":
            state = dummy_train_step(state)
            print(f"[Worker {worker_id}] Trained: {state}")
            save_checkpoint(worker_id, state)

        elif role == "redundant":
            # Mirror checkpoint (simulate redundancy)
            try:
                latest_state = load_checkpoint(worker_id)
                if latest_state["weight"] > state["weight"]:
                    state = latest_state
                    print(f"[Worker {worker_id} - RW] Synced: {state}")
            except Exception as e:
                print(f"[Worker {worker_id} - RW] Waiting for checkpoint...")

            # Listen for promotion signal
            promotion_flag = f"logs/promotoe_worker{worker_id}.flag"
            if os.path.exists(promotion_flag):
                print(f"[Worker {worker_id} - RW] PROMOTED to PRIMARY")
                role = "primary"
                os.remove(promotion_flag)

        # Simulate failure trigger
        failure_flag = f"logs/fail_worker{worker_id}.flag"
        if os.path.exists(failure_flag):
            print(f"[Worker {worker_id}] Simulated FAILURE triggered. Shutting down.")
            os.remove(failure_flag)
            break

        time.sleep(3)  # simulate training delay

