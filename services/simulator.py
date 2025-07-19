"""
This module simulates random primary node failure, and how coordinator-led recovery 
and redundant promotion works in the system.
"""

import simpy
import random
import time

def fail_worker(env, worker_id, mean_delay):
    delay = random.expovariate(1.0 / mean_delay)
    yield env.timeout(delay)

    print(f"[{env.now:.1f}s] [Simulator] Triggering failure for Worker {worker_id} after {delay:.1f}s")

    # Create a failure flag
    with open(f"logs/fail_worker{worker_id}.flag", "w") as f:
        f.write("FAIL")

if __name__ == "__main__":
    env = simpy.Environment()
    MEAN_FAILURE_TIME = 40  

    # Allow other services to start first
    time.sleep(10)

    # Only simulating one primary node failure (worker1)
    env.process(fail_worker(env, worker_id=1, mean_delay=MEAN_FAILURE_TIME))

    print("[Simulator] Starting stochastic failure simulation...")
    env.run(until=90)
    print("[Simulator] Simulation complete.")
