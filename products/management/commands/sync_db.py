import csv
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError, transaction
from django.utils import timezone

from products.models import Product

DEFAULT_CSV = Path(settings.BASE_DIR) / "data" / "scrapy_data.csv"
REQUIRED_COLUMNS = {"title", "price", "availability", "product_url", "image_url", "category"}
SYNC_FIELDS = ["title", "price", "availability", "image_url", "category"]
TRUE_VALUES = {"true", "yes", "y", "1", "available"}

def parse_price(raw):
    """'£51.77' or '-1,299.00' -> Decimal('51.77') / Decimal('-1299.00')."""
    cleaned = re.sub(r"[^\d.\-]", "", raw or "")
    try:
        return Decimal(cleaned).quantize(Decimal("0.01"))
    except InvalidOperation:
        raise ValueError(f"invalid price {raw!r}") from None

def parse_availability(raw):
    value = (raw or "").strip().lower()
    return value in TRUE_VALUES or value.startswith("in stock")

def clean_row(row):
    """Normalise one CSV row into model-ready values, or raise ValueError."""
    data = {column: (row.get(column) or "").strip() for column in REQUIRED_COLUMNS}
    for required in ("title", "product_url"):
        if not data[required]:
            raise ValueError(f"missing {required}")
    data["price"] = parse_price(data["price"])
    data["availability"] = parse_availability(data["availability"])
    data["category"] = data["category"] or "Uncategorized"
    return data

class Command(BaseCommand):
    help = "Synchronise products from data/scrapy_data.csv into the database (idempotent)."


    def handle(self,*args,**options):

        path=DEFAULT_CSV
        if not path.is_file():
            raise CommandError(f"CSV file not found{path}")


        rows=self.read_rows(path)
        try:
            with transaction.atomic():
                stats=self.sync(rows)
        except DatabaseError as exc:
            raise CommandError(f"Database error : nothing was save:{exc}") from exc
        
        self.stdout.write(self.style.SUCCESS(
            f"Sync complete: {stats['created']} created, {stats['updated']} updated, "
            f"{stats['unchanged']} unchanged, {stats['skipped']} skipped."
        ))
    
    def read_rows(self,path):

        with path.open(newline="", encoding="utf-8-sig") as data:
            reader=csv.DictReader(data)
            missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
            if missing:
                raise CommandError(f"CSV is missing columns: {sorted(missing)}")
            return list(enumerate(reader, start=2))  # line 1 is the header

    def sync(self,rows):
        stats = {"created": 0, "updated": 0, "unchanged": 0, "skipped": 0}
        existing = {product.product_url: product for product in Product.objects.all()}
        to_create, to_update, seen = [], [], set()


        for line_no ,row in rows:

            try:
                data=clean_row(row)
                candidate_data=Product(**data)
                candidate_data.full_clean(validate_unique=False)
            except (ValueError, ValidationError) as exc:
                reason = "; ".join(exc.messages) if isinstance(exc, ValidationError) else str(exc)
                self.stdout.write(self.style.WARNING(f"Line {line_no} skipped: {reason}"))
                stats["skipped"] += 1
                continue

            url = data["product_url"]
            if url in seen:
                # self.stdout.write(self.style.WARNING(f"Line {line_no} skipped: duplicate URL in CSV"))
                stats["skipped"] += 1
                continue
            seen.add(url)

            current = existing.get(url)
            if current is None:
                to_create.append(candidate_data)
                stats["created"] += 1
            elif self.apply_changes(current, data):
                to_update.append(current)
                stats["updated"] += 1
            else:
                stats["unchanged"] += 1

        Product.objects.bulk_create(to_create)
        Product.objects.bulk_update(to_update, SYNC_FIELDS + ["updated_at"])
        return stats

    @staticmethod
    def apply_changes(product,data):

        changes=False

        for field in SYNC_FIELDS:
            if getattr(product,field)!=data[field]:
                setattr(product,field,data[field])
                changes=True
        if changes:
            product.updated_at=timezone.now()
        return changes
    




    

