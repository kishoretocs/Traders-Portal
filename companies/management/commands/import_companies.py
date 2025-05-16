# company/management/commands/import_companies.py

import csv
import requests
from io import StringIO
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError, transaction
from companies.models import Company

# Direct‐download URL for your Google Drive CSV
CSV_DOWNLOAD_URL = (
    "https://drive.google.com/uc?export=download"
    "&id=1okzqXR3dJMDf0Jx2GuqL6DLA3DC6MOBj"
)

class Command(BaseCommand):
    help = 'Fetch the companies CSV from Google Drive and import into Company model'

    def handle(self, *args, **options):
        self.stdout.write("Downloading CSV from Google Drive…")
        resp = requests.get(CSV_DOWNLOAD_URL)
        if resp.status_code != 200:
            raise CommandError(f"Failed to download CSV: HTTP {resp.status_code}")

        reader = csv.DictReader(StringIO(resp.content.decode('utf-8')))
        created = updated = skipped = 0

        for row in reader:
            symbol = (row.get('symbol') or '').strip()
            name   = (row.get('company_name') or '').strip()
            code   = (row.get('scripcode') or '').strip()

            if not symbol or not code:
                self.stdout.write(self.style.WARNING("Skipping row with missing symbol or scripcode"))
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

            except IntegrityError as e:
                # This captures UNIQUE constraint on scripcode or symbol
                self.stdout.write(self.style.WARNING(
                    f"Skipping duplicate entry for symbol={symbol}, scripcode={code}"
                ))
                skipped += 1
                continue

        self.stdout.write(self.style.SUCCESS(
            f"Import complete: {created} created, {updated} updated, {skipped} skipped."
        ))
