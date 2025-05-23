
import csv
import requests
from io import StringIO
from celery import shared_task
from django.db import IntegrityError, transaction
from companies.models import Company
from django.core.management.base import BaseCommand

CSV_DOWNLOAD_URL = (
    "https://drive.google.com/uc?id=1dg0UnNgK0fmc7KyZHXVvGDGu6z7wwTTk&export=download"
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
        code_str = (row.get('co_code') or '').strip()
        try:
            co_code = int(code_str)
        except ValueError:
            skipped += 1
            continue
        if not symbol or not code:
            skipped += 1
            continue

        try:
            with transaction.atomic():
                obj, was_created = Company.objects.update_or_create(
                    co_code=co_code,
                    defaults={'company_name': name, 'scripcode': code, 'symbol':symbol}
                )
            if was_created:
                created += 1
            else:
                updated += 1

        except IntegrityError:
            skipped += 1
            continue

    return f"Import complete: {created} created, {updated} updated, {skipped} skipped."
