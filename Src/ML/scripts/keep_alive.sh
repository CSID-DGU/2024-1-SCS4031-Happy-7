#!/bin/bash

# Description:
# This script runs an infinite loop that logs a message indicating WSL2 is active.
# The message is discarded by redirecting the output to `/dev/null`.
# The loop runs continuously with a 5-minute interval between iterations.

while true; do
    echo "WSL2 is active" > /dev/null
    sleep 300  # Repeat every 5 minutes
done