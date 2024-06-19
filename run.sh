#!/bin/bash

# Function to clean up on script exit
cleanup() {
    echo "Cleaning up..."
    docker container stop $(docker container ls -aq) >/dev/null 2>&1
    pkill -P $$ >/dev/null 2>&1
    exit
}

trap cleanup EXIT

# Main script execution
main() {
    # Check for python & activate enviroment if present, else install it
    if ! command -v python3 &>/dev/null; then
        echo "Python 3 is not installed. Installing..."
        sudo apt install python3 python3-venv
        python3 -m venv venv
    fi

    # Check for redis
    if ! command -v redis-server &>/dev/null; then
        echo "Redis is not installed. Installing..."
        sudo apt install redis
    fi

    # Activate the virtual environment
    source ./venv/bin/activate

    # Check if dependencies are already installed (requirement_installed.txt)
    if [ ! -f "requirement_installed.txt" ]; then
        echo "Installing dependencies..."
        pip install -r requirements.txt
        touch requirement_installed.txt
    fi

    # Start the application
    gunicorn -b 0.0.0.0:8000 PlagiarismChecker.wsgi &

    # Start the celery workers
    celery -A PlagiarismChecker worker -l info &

    # Start the celery beat
    celery -A PlagiarismChecker beat -l info &

    # Wait for user input to exit
    echo "Setup complete. The application is running."
    read -r -d '' _ </dev/tty
}

main
