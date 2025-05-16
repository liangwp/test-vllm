# VLLM Tester

This is a sample project to test and document the setup of VLLM, Python Dash,
and LangChain.

Unless otherwise stated, all shell commands in the project's documentation are meant to be run
from the project root directory.

## Prerequisites

Developed and tested with the following config:

1. Linux 6.14.5-arch1-1
1. Docker 28.1.1
1. Docker Compose 2.36.0

## Quick Start

1. Start vllm and dash ui:
    ```
    docker compose up --build -d
    ```
1. Follow logs for vllm:
    ```
    docker compose logs -f vllm-tester
    ```
1. Follow logs for dash:
    ```
    docker compose logs -f dash-ui
    ```
1. Shut down everything:
    ```
    docker compose down
    ```

## Development Cycle

1. Start everything:
    ```
    docker compose up --build -d
    ```
1. Follow logs for vllm and dash
    ```
    docker compose logs -f vllm-tester
    docker compose logs -f dash-ui
    ```
1. Update code.
1. Refresh running containers. No need to re-follow logs unless container
   crashed.
    ```
    docker compose up --build -d
    ```
