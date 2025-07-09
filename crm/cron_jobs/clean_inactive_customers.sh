#!/bin/bash
# Script to delete inactive customers with no orders in the past year

# Change to Django project root (cwd = current working directory)
cd /absolute/path/to/your/alx-backend-graphql_crm || exit 1

# Activate virtual environment if you have one (optional)
# source venv/bin/activate

# Run Django shell command to delete customers
count=$(python3 manage.py shell -c "
from crm.models import Customer
from django.utils import timezone
from datetime import timedelta

one_year_ago = timezone.now() - timedelta(days=365)
deleted, _ = Customer.objects.filter(orders__isnull=True, created__lte=one_year_ago).delete()
print(deleted)
")

# Log result
echo \"\$(date '+%Y-%m-%d %H:%M:%S') Deleted \$count inactive customers\" >> /tmp/customer_cleanup_log.txt