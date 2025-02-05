#!/bin/sh
# If PORT is empty or literally "$PORT", set a default port (5000).
if [ -z "$PORT" ] || [ "$PORT" = "\$PORT" ]; then
  PORT_VAL=5000
else
  PORT_VAL=$PORT
fi

echo "Starting on port $PORT_VAL"
exec gunicorn -w 4 -b 0.0.0.0:"$PORT_VAL" main:app
