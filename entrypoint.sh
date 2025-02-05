#!/bin/sh
# Debug: Print the PORT variable
echo "PORT environment variable is: '$PORT'"

# Use the PORT environment variable if set; default to 5000 otherwise.
PORT_VAL=${PORT:-5000}
echo "Starting on port $PORT_VAL"

# Start Gunicorn on the resolved port.
exec gunicorn -w 4 -b 0.0.0.0:"$PORT_VAL" main:app
