import os
import time
from datetime import datetime, timedelta

HEARTBEAT_TIMEOUT = 10  # seconds
WORKER_IDS = [1]  # support for worker1-PW1 and worker2-RW1
LOG_DIR = "logs"

def get_last_heartbeat(worker_id):
    path = f"{LOG_DIR}/worker{worker_id}_heartbeat.txt"
    if os.path.exists(path):
        with open(path, "r") as f:
            return datetime.fromisoformat(f.read().strip())
    return None

def promote_redundant(worker_id):
    print(f"[Coordinator] PROMOTING Redundant Worker{worker_id} to PRIMARY")
    # Create a promotion flag (simplified IPC)
    with open(f"{LOG_DIR}/promote_worker{worker_id}.flag", "w") as f:
        f.write("PROMOTE")

def monitor_heartbeats():
    print("[Coordinator] Monitoring heartbeats...")
    while True:
        for worker_id in WORKER_IDS:
            hb = get_last_heartbeat(worker_id)
            if hb is None:
                print(f"[Coordinator] No heartbeat from Worker{worker_id}")
                continue

            if datetime.now() - hb > timedelta(seconds=HEARTBEAT_TIMEOUT):
                print(f"[Coordinator] Worker{worker_id} FAILED")
                promote_redundant(worker_id)
        time.sleep(5)

if __name__ == "__main__":
    monitor_heartbeats()
