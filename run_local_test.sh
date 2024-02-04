#!/bin/bash

# Load environment variables from .env file
if [[ -f .env ]]; then
    export $(cat .env | xargs)
fi

# make sure you have TELEGRAM_TOKEN and CHAT_ID in your .env file

# Function to start Flask app and ngrok
start_services() {
    # Start Flask app in the background
    flask run --debug --port 5002 &
    sleep 2
    ngrok http 5002 & sleep 2

    ngrok_url=$(curl -s localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url')

    # Send the ngrok URL via Telegram API
    send_telegram_message "Ngrok URL: $ngrok_url"
}

# Function to send message using Telegram API
send_telegram_message() {
    local message="$1"

    curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_TOKEN/sendMessage" \
        -d "chat_id=$CHAT_ID" \
        -d "text=$message" \
        > /dev/null
}

# Function to send termination message
send_termination_message() {
    send_telegram_message "Site terminated"
}

# Trap interrupt signal and stop services
trap 'pkill -P $$; send_termination_message; exit 0' SIGINT

# Start services
start_services

# Wait for interruption
wait
