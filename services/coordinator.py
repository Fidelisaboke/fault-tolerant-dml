import os
import time
from datetime import datetime, timedelta
from utils import discover_workers, safe_read_iso_timestamp

HEARTBEAT_TIMEOUT = 30
LOG_DIR = "logs"

# Pairs of primary + redundant nodes
WORKERS = [("1", "primary"), ("1", "redundant")]

def refresh_workers(interval=30):
    """Periodically refresh workers."""
    global WORKERS
    while True:
        WORKERS = discover_workers()
        print(f"[Coordinator] Refreshed WORKERS list: {WORKERS}")
        time.sleep(interval)


def get_last_heartbeat(worker_id, role):
    path = f"{LOG_DIR}/worker{worker_id}_{role}_heartbeat.txt"
    return safe_read_iso_timestamp(path)

def promote_redundant(worker_id):
    print(f"[Coordinator] PROMOTING Redundant Worker{worker_id} to PRIMARY")

    # Create a promotion flag (simplified IPC)
    with open(f"{LOG_DIR}/promote_worker{worker_id}.flag", "w") as f:
        f.write("PROMOTE")

    # Touch a refresh trigger for checkpoint manager
    with open(f"{LOG_DIR}/trigger_checkpoint_refresh.flag", "w") as f:
        f.write("REFRESH")


def monitor_heartbeats():
    print("[Coordinator] Monitoring heartbeats...")
    while True:
        for worker_id, role in WORKERS:
            hb = get_last_heartbeat(worker_id, role)
            if hb is None:
                print(f"[Coordinator] No heartbeat from Worker{worker_id} - {role}")
                continue

            print(f"[Coordinator] Last heartbeat for Worker{worker_id} - {role}: {hb.isoformat()}")
            if datetime.now() - hb > timedelta(seconds=HEARTBEAT_TIMEOUT):
                print(f"[Coordinator] Worker{worker_id} - {role} FAILED")

                # Promote redundant counterpart
                if role == "primary": 
                    promote_redundant(worker_id)

        time.sleep(5)


if __name__ == "__main__":
    # import threading
    # threading.Thread(target=refresh_workers, daemon=True).start()
    monitor_heartbeats()
