#!/bin/bash

# This script automates starting your Docker Compose project,
# opening the Streamlit app, and then shutting it down after a timeout.

# --- Configuration ---
STREAMLIT_PORT="8501"
APP_URL="http://localhost:${STREAMLIT_PORT}"
TIMEOUT_SECONDS=$((45 * 60)) # 45 minutes in seconds
WAIT_INTERVAL_SECONDS=5      # How often to check if Streamlit is ready
MAX_WAIT_ATTEMPTS=24         # Max attempts (24 * 5s = 120s = 2 minutes)

# --- Error Handling ---
set -e # Exit immediately if a command exits with a non-zero status.

# --- Check for Docker ---
if ! command -v docker &> /dev/null
then
    echo "Error: Docker Desktop is not installed or not in your PATH."
    echo "Please install Docker Desktop from https://docs.docker.com/desktop/install/mac-install/"
    exit 1
fi

echo "--- Starting Docker Compose Project ---"
# Ensure Docker Compose is up-to-date and running in detached mode
# --build ensures images are rebuilt if Dockerfile or build context changed
docker-compose up --build -d

echo "Docker Compose services are starting..."

# --- Wait for Streamlit App to be Ready ---
echo "Waiting for Streamlit app to become available at ${APP_URL}..."
ATTEMPT_COUNT=0
while [ ${ATTEMPT_COUNT} -lt ${MAX_WAIT_ATTEMPTS} ]; do
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" ${APP_URL} || echo "000")
    if [ "${HTTP_STATUS}" == "200" ]; then
        echo "Streamlit app is ready!"
        break
    else
        echo "Still waiting for Streamlit app (status: ${HTTP_STATUS}). Retrying in ${WAIT_INTERVAL_SECONDS} seconds..."
        sleep ${WAIT_INTERVAL_SECONDS}
        ATTEMPT_COUNT=$((ATTEMPT_COUNT + 1))
    fi
done

if [ ${HTTP_STATUS} != "200" ]; then
    echo "Error: Streamlit app did not become ready within the expected time."
    echo "Please check Docker Compose logs for errors: docker-compose logs"
    docker-compose down # Attempt to clean up even on failure
    exit 1
fi

# --- Open Browser ---
echo "Opening Streamlit app in your default browser..."
open "${APP_URL}"

# --- Automatic Shutdown Timer ---
echo ""
echo "-------------------------------------------------------------------------"
echo "Your Streamlit app is running. This script will automatically shut down"
echo "Docker Compose in $((TIMEOUT_SECONDS / 60)) minutes."
echo "To stop earlier, simply press Ctrl+C in this terminal window."
echo "-------------------------------------------------------------------------"
echo ""

sleep ${TIMEOUT_SECONDS}

echo "--- Initiating automatic shutdown ---"
echo "Shutting down Docker Compose services..."
docker-compose down

echo "Docker Compose has been shut down successfully."