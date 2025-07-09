#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Change to the project directory (cwd requirement)
cd "$PROJECT_DIR" || {
    echo "Failed to change directory to project root"
    exit 1
}

# Set Python path to include the project directory
export PYTHONPATH="${PROJECT_DIR}:${PYTHONPATH}"

# Define timestamp for logging
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# If in test mode, use a fixed reference date
if [ "$TEST_MODE" = "1" ]; then
    echo "$TIMESTAMP Running in TEST_MODE with fixed reference date" >> /tmp/customer_cleanup_log.txt
    DJANGO_SETTINGS_MODULE=alx_backend_graphql.settings python3 manage.py cleanup_inactive_customers --reference-date="2024-01-01"
else
    # Else block included explicitly
    echo "$TIMESTAMP Running in PRODUCTION mode" >> /tmp/customer_cleanup_log.txt
    DJANGO_SETTINGS_MODULE=alx_backend_graphql.settings python3 manage.py cleanup_inactive_customers
fi
