# Load Testing Application

This load testing application is designed in Go to simulate user behavior and perform actions against a specified target application. It's structured into several modules, each with a specific role in the application.

## Getting Started

### Building the Application

```bash
go build -o loadgen cmd/loadgen/main.go
```

```bash
./loadgen -users=10 -url=http://targetapplication.com
```

## Components

### 1. Command Line Interface (`cmd/loadgen/main.go`)

- **Purpose**: This is the entry point of the load generator tool. It sets up and starts the behavior simulations based on the specified configurations.
- **Features**:
  - Parses command-line flags for the number of concurrent users (`-users`) and the base URL of the target application (`-url`).
  - Initializes and starts the behavior simulations.
  - Supports concurrent execution to simulate multiple users, with random waiting times.

### 2. Behavior Module (`internal/behavior`)

This module is split into several files:

#### `behaviour.go`

- **Purpose**: Defines the `Behavior` interface that all behavior types (like `UserBehavior`) must implement.
- **Functionality**: Outlines the structure for behavior classes, ensuring they provide a method to retrieve their weighted tasks.

#### `executor.go`

- **Purpose**: Manages the execution of tasks within a given behavior.
- **Functionality**: Randomly selects and executes tasks based on their weights.

#### `userbehavior.go`

- **Purpose**: Implements a specific user behavior scenario.
- **Functionality**: Provides a collection of weighted tasks that simulate a particular type of user interaction with the target application.

### 3. Tasks (`internal/tasks/*.go`)

- **Purpose**: Contains the implementation of all specific tasks that can be performed by the behaviors.
- **Functionality**: Each task file is a concrete implementation of the `Task` interface, representing an action that can be executed (like browsing a product or adding items to a cart).

### 4. Utilities (`pkg/utils/random`)

- **Purpose**: Provides utility functions for random number and string generation.
- **Functionality**: Includes functions like `ChoiceString` and `ChoiceInt` to randomly select an element from a slice, aiding in the random selection of tasks and scenarios.

### 5. Config (`config`)

- **Purpose**: Provides configuration for all the different modules.
- **Functionality**: Generates a `config` object carrying all the needed static configuration for the application.
