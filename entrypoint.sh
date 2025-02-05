#!/bin/sh
# Use the PORT environment variable if set, otherwise default to 5000.
PORT_VAL=${PORT:-5000}
echo "Starting on port $PORT_VAL"
exec gunicorn -w 4 -b 0.0.0.0:"$PORT_VAL" main:app
