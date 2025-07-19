import os
import json
import time

SHARED_DIR = "shared_storage"
LOG_PATH = "logs/checkpoint_manager.log"
TRACKED_WORKERS = [1]

def log(msg):
    print(msg)
    with open(LOG_PATH, "a") as f:
        f.write(msg + "\n")

def validate_checkpoint(path):
    try:
        with open(path, "r") as f:
            data = json.load(f)
        if "weight" in data:
            return True
    except:
        pass
    return False

def monitor_checkpoints():
    log("[CheckpointManager] Starting checkpoint monitor...")
    last_state = {}

    while True:
        for worker_id in TRACKED_WORKERS:
            ckpt_file = f"{SHARED_DIR}/worker{worker_id}_ckpt.json"
            if os.path.exists(ckpt_file):
                if validate_checkpoint(ckpt_file):
                    with open(ckpt_file, "r") as f:
                        state = json.load(f)
                    if last_state.get(worker_id) != state["weight"]:
                        log(f"[CheckpointManager] Worker{worker_id} updated checkpoint: {state}")
                        last_state[worker_id] = state["weight"]
                else:
                    log(f"[CheckpointManager] Invalid checkpoint from Worker{worker_id}")
        time.sleep(5)

if __name__ == "__main__":
    monitor_checkpoints()
