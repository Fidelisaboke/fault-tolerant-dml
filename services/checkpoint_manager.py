import os
import json
import time
from utils import get_worker_ids, validate_checkpoint, log

SHARED_DIR = "shared_storage"
LOG_PATH = "logs/checkpoint_manager.log"

# Tracking primary workers for checkpointing
TRACKED_WORKERS = [1]

def refresh_worker_list(interval=30):
    global TRACKED_WORKERS
    while True:
        TRACKED_WORKERS = get_worker_ids(role="primary")
        log(f"[CheckpointManager] Updated tracked workers: {TRACKED_WORKERS}", LOG_PATH)
        time.sleep(interval)

def monitor_checkpoints():
    log("[CheckpointManager] Starting checkpoint monitor...")
    last_state = {}

    while True:
        # Check if a refresh trigger was placed
        if os.path.exists(f"{LOG_PATH}/trigger_checkpoint_refresh.flag"):
            TRACKED_WORKERS[:] = get_worker_ids()
            os.remove(f"{LOG_PATH}/trigger_checkpoint_refresh.flag")
            log(f"[CheckpointManager] Triggered immediate refresh.")

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
    # import threading
    # threading.Thread(target=refresh_worker_list, daemon=True).start()
    monitor_checkpoints()
