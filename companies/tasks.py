# companies/tasks.py

import csv
import requests
from io import StringIO
from celery import shared_task
from django.db import IntegrityError, transaction
from .models import Company

CSV_DOWNLOAD_URL = (
    "https://drive.google.com/uc?export=download"
    "&id=1okzqXR3dJMDf0Jx2GuqL6DLA3DC6MOBj"
)

@shared_task
def import_companies_task():
    response = requests.get(CSV_DOWNLOAD_URL)
    if response.status_code != 200:
        return f"Failed to download CSV. Status code: {response.status_code}"

    reader = csv.DictReader(StringIO(response.content.decode('utf-8')))
    created = updated = skipped = 0

    for row in reader:
        symbol = (row.get('symbol') or '').strip()
        name   = (row.get('company_name') or '').strip()
        code   = (row.get('scripcode') or '').strip()

        if not symbol or not code:
            skipped += 1
            continue

        try:
            with transaction.atomic():
                obj, was_created = Company.objects.update_or_create(
                    symbol=symbol,
                    defaults={'company_name': name, 'scripcode': code}
                )
            if was_created:
                created += 1
            else:
                updated += 1

        except IntegrityError:
            skipped += 1
            continue

    return f"Import complete: {created} created, {updated} updated, {skipped} skipped."
