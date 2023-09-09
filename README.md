# RMY Bot

## Development Environment Setup

1. Install Python version listed in Dockerfile

1. Install dependencies through pip
    
    ```bash
    pip install -r requirements.txt
    ```

1. Update the values appropriately in .env

1. Run Bot Script

    ```bash
    python app/rmy.py
    ```

## Docker Containers Setup

### Using Docker Build and Run

1. Build container

    ```bash
    docker build --tag rmy-bot .
    ```

1. Run container

    ```bash
    docker run -d --env-file .env rmy-bot
    ```

1. If you wish to maintain constant up-time on your hosted device run the following instead

    ```bash
    docker run -d --env-file .env --restart always rmy-bot
    ```

### Using Docker Compose

1. Docker Compose

    ```bash
    docker-compose up
    ```

1. If you wish to maintain constant up-time on your hosted device uncomment the following in compose.yaml

    ```bash
    restart: always
    ```