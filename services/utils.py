"""
Utility funcitons for the services.
"""

import docker
import json
from datetime import datetime

def discover_workers(filter_role=None):
    """
    Discover all running worker containers.
    Optionally filter by role: "primary", "redundant", or None (all).
    Returns: list of tuples (worker_id, role)
    """
    client = docker.from_env()
    workers = []

    try:
        containers = client.containers.list(filters={"status": "running"})
        for c in containers:
            labels = c.labels
            worker_id = labels.get("worker.id")
            role = labels.get("worker.role")

            if worker_id and role:
                if filter_role is None or role == filter_role:
                    workers.append((worker_id, role))
    except Exception as e:
        print(f"[Utils] Docker discovery error: {e}")

    return workers

def get_worker_ids(role="primary"):
    """
    Return worker IDs (ints) for containers with the given role.
    """
    return [int(wid) for wid, r in discover_workers(filter_role=role) if wid.isdigit()]

def safe_read_iso_timestamp(filepath):
    try:
        with open(filepath, "r") as f:
            line = f.read().strip()
            if line:
                return datetime.fromisoformat(line)
    except Exception as e:
        print(f"[Utils] Error reading ISO timestamp from {filepath}: {e}")
    return None

def log(msg, log_path=None):
    print(msg)
    if log_path:
        try:
            with open(log_path, "a") as f:
                f.write(msg + "\n")
        except Exception as e:
            print(f"[Utils] Failed to write to log file: {e}")

def validate_checkpoint(path):
    try:
        with open(path, "r") as f:
            data = json.load(f)
        return "weight" in data
    except Exception:
        return False
