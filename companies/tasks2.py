import csv
import requests
from io import StringIO
from celery import shared_task
from django.db import transaction, IntegrityError
from companies.models import Company, finalcial

CSV_DOWNLOAD_URL = (
    "https://drive.google.com/uc?id=1YyCV9tw6pPRRJlezC41QHdqWV36IR6xV&export=download"
)

@shared_task
def import_finalcial_task():
    response = requests.get(CSV_DOWNLOAD_URL)
    if response.status_code != 200:
        return f"Failed to download CSV. Status code: {response.status_code}"

    reader = csv.DictReader(StringIO(response.content.decode('utf-8')))
    created = updated = skipped = 0

    for row in reader:
        try:
            row_id = int(row.get("id", "").strip())
            ttm_ason = int(row.get("ttm_ason", "").strip())
            pe = float(row.get("pe", "").strip())
            roe_ttm = float(row.get("roe_ttm", "").strip())
            company_id = int(row.get("company_id", "").strip())
        except (ValueError, TypeError):
            skipped += 1
            continue

        try:
            company = Company.objects.get(co_code=company_id)
        except (Company.DoesNotExist, Company.MultipleObjectsReturned):
            skipped += 1
            continue

        try:
            with transaction.atomic():
                obj, created_obj = finalcial.objects.update_or_create(
                    id=row_id,
                    defaults={
                        "ttm_ason": ttm_ason,
                        "pe": pe,
                        "roe_ttm": roe_ttm,
                        "company_id": company,
                    }
                )
            if created_obj:
                created += 1
            else:
                updated += 1
        except IntegrityError:
            skipped += 1
            continue

    return f"Import complete: {created} created, {updated} updated, {skipped} skipped."
