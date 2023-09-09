# RMY Bot

## Development Environment Setup

1. Install Python version listed in Dockerfile

2. Install dependencies through pip
    
    ```bash
    pip install -r requirements.txt
    ```
3. Run Bot Script

    ```bash
    python app/rmy.py
    ```

## Docker Containers Setup

### Using Docker Build and Run

1. Build container

    ```bash
    docker build --tag rmy-bot .
    ```

2. Run container

    ```bash
    docker run -d --env-file .env rmy-bot
    ```

3. If you wish to maintain constant up-time on your hosted device run the following instead

    ```bash
    docker run -d --env-file .env --restart always rmy-bot
    ```

### Using Docker Compose

1. Docker Compose

    ```bash
    docker-compose up
    ```

2. If you wish to maintain constant up-time on your hosted device uncomment the following in compose.yaml

    ```bash
    restart: always
    ```