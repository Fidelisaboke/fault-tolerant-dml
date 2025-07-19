# Fault-Tolerant Distributed Machine Learning System

## Project Overview

This project simulates a fault-tolerant distributed machine learning system using redundant worker nodes and centralized coordination. The system is designed to ensure resilience by promoting standby workers upon failure and preserving model progress through checkpointing.
A simple feedforward neural network has been trained using the MNIST dataset, to demonstrate the implemented 
redundant training architecture.


## Table of Contents

* [Tools and Technologies](#tools-and-technologies)
* [Installation and Setup](#installation-and-setup)
  * [Prerequisites](#prerequisites)
  * [Setup Instructions](#setup-instructions)
* [Basic Usage](#basic-usage)
* [Project Structure](#project-structure)
* [Known Issues](#known-issues)
* [Acknowledgement](#acknowledgement)
* [License](#license)

## Tools and Technologies

* Python 3.10
* Docker & Docker Compose
* TensorFlow (simple model used in simulation)
* Redis (optional for message coordination in future extensions)
* Linux-based shell environment

## Installation and Setup

### Prerequisites

* Python 3.10 or higher
* Docker and Docker Compose
* TensorFlow
* Git

### Setup Instructions

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Fidelisaboke/fault-tolerant-dml.git
   cd fault-tolerant-dml
   ```

2. **Build Docker images**:

   ```bash
   docker-compose build
   ```

3. **Start the system**:

   ```bash
   docker-compose up
   ```

4. **Monitor logs** (optional):

   ```bash
   docker-compose logs -f
   ```

## Basic Usage

Once the system is running:

* Primary workers will begin training a simple feedforward neural network.
* Redundant workers will sync with the primary's checkpoint.
* The coordinator monitors heartbeat signals from all nodes.
* Upon failure of a primary, the redundant is promoted to take over training.
* The checkpoint manager logs progress of valid checkpoints from active primary workers.

You can simulate failures by stopping specific containers manually:

```bash
docker stop worker1_primary
```

* Observe how recovery is handled by checking the logs.

## Project Structure

```
.
├── .gitignore
├── Dockerfile
├── README.md
├── docker-compose.yml
└── services
    ├── checkpoint_manager.py
    ├── coordinator.py
    ├── utils.py
    └── worker.py
```

## Known Issues

* Promotion logic updates internal role but does not modify Docker container labels dynamically.
* Heartbeat logs are file-based; scaling to large clusters may require Redis or Kafka.
* System is currently simulated and does not perform complex ML training beyond a simple feedforward
neural network.

## Acknowledgement

This project was inspired by the need for robustness in distributed machine learning and integrates concepts such as checkpointing, redundancy, failure detection, and task reassignment. Special thanks to open-source contributors and documentation that informed its design.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
