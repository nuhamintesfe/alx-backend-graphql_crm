#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Change to the project directory
cd "$PROJECT_DIR" || exit 1

# Set Python path to include the project directory
export PYTHONPATH="${PROJECT_DIR}:${PYTHONPATH}"

# Activate virtualenv if needed
# source venv/bin/activate

# Run inline cleanup logic
deleted=$(DJANGO_SETTINGS_MODULE=alx_backend_graphql.settings python3 manage.py shell -c "
from crm.models import Customer
from django.utils import timezone
from datetime import timedelta

cutoff = timezone.now() - timedelta(days=365)
deleted, _ = Customer.objects.filter(orders__isnull=True, created__lte=cutoff).delete()
print(deleted)
")

# Log to /tmp
echo \"\$(date '+%Y-%m-%d %H:%M:%S') Deleted \$deleted inactive customers\" >> /tmp/customer_cleanup_log.txt
