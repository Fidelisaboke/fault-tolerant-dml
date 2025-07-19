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

def get_heartbeat_path(worker_id, role):
    return f"logs/worker{worker_id}_{role}_heartbeat.txt"

def send_heartbeat(worker_id, role):
    with open(get_heartbeat_path(worker_id, role), "w") as f:
        f.write(datetime.now().isoformat())

def load_checkpoint(worker_id):
    path = f"shared_storage/worker{worker_id}_ckpt.json"
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    else:
        return {"weight": 0}
    
def check_for_promotion(worker_id):
    promotion_flag = f"logs/promote_worker{worker_id}.flag"
    if os.path.exists(promotion_flag):
        os.remove(promotion_flag)
        return True
    return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", choices=["primary", "redundant"], required=True)
    parser.add_argument("--id", type=int, required=True)
    args = parser.parse_args()

    role = args.role
    worker_id = args.id
    state = load_checkpoint(worker_id)

    # Labels for primary and redundant worker
    pw_label = f"Worker {worker_id} - PW"
    rw_label = f"Worker {worker_id} - RW"

    print(f"[Worker {worker_id} - {role.upper()}] Starting training loop...")

    while True:
        send_heartbeat(worker_id, role)

        if role == "primary":
            state = dummy_train_step(state)
            print(f"[{pw_label}] Trained: {state}")
            save_checkpoint(worker_id, state)

        elif role == "redundant":
            # Sync checkpoint (redundancy)
            try:
                latest_state = load_checkpoint(worker_id)
                if latest_state["weight"] > state["weight"]:
                    state = latest_state
                    print(f"[{rw_label}] Synced: {state}")
            except Exception as e:
                print(f"{rw_label} Waiting for primary checkpoint...")

            # Listen for promotion signal
            if check_for_promotion(worker_id):
                print((f"[{rw_label}] PROMOTED to PRIMARY"))
                role = "primary"

        time.sleep(3)

