import os
import tempfile

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from pathlib import Path
from unittest.mock import patch
from .models import Product

HEADER = "title,price,availability,product_url,image_url,category\n"

ROW_A = "Book A,10.00,In stock,https://example.com/a,,Fiction\n"

ROW_B = "Book B,20.50,Out of stock,https://example.com/b,,Poetry\n"

# check is th csv file imported in the database correctly ?
class SyncDbTests(TestCase):
    def sync(self, text):
        """Write `text` to a temporary CSV and run sync_db against it."""
        handle = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8")
        self.addCleanup(os.unlink, handle.name)
        handle.write(text)
        handle.close()
        with patch("products.management.commands.sync_db.DEFAULT_CSV", Path(handle.name)):
            call_command("sync_db")

    def test_sync_is_idempotent(self):
        self.sync(HEADER + ROW_A + ROW_B)
        self.sync(HEADER + ROW_A + ROW_B)
        self.assertEqual(Product.objects.count(), 2)

    def test_changed_row_is_updated_not_duplicated(self):
        self.sync(HEADER + ROW_A)
        changed = "Book A,15.00,In stock,https://example.com/a,,Fiction\n"
        self.sync(HEADER + changed)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(str(Product.objects.get().price), "15.00")

    def test_invalid_rows_are_skipped(self):
        bad = "No Price,abc,In stock,https://example.com/c,,Fiction\n"
        self.sync(HEADER + ROW_A + bad)
        self.assertEqual(Product.objects.count(), 1)
        

# check product update ,delete ,list and pagination

class ProductViewTests(TestCase):
    def setUp(self):
        self.product=Product.objects.create(
            title="Book A",
            price="10.00",
            product_url="https://example.com/a"
        )
    def test_list_page_ok(self):
        response=self.client.get(reverse("products:list"))

        self.assertEqual(response.status_code,200)
    
    def test_delete_rejects_get(self):
        response=self.client.get(reverse("products:delete",args=[self.product.pk]))

        self.assertEqual(response.status_code,405)
    
    def test_delete_post_removes_product(self):
        response=self.client.post(
            reverse("products:delete",args=[self.product.pk])
        )
        self.assertRedirects(
            response,
            reverse("products:list")
        )

        self.assertFalse(Product.objects.exists())
    
    def test_update_unknown_id_returns_404(self):
        response=self.client.get(
            reverse("products:update",args=[9999])
        )
        self.assertEqual(response.status_code,404)

    def test_list_is_paginated(self):
        for i in range(25):
            Product.objects.create(
                title=f"Item{i}",
                price="1.00",
                product_url=f"https://example.com/item-{i}"
            )
        page_one=self.client.get(
            reverse("products:list")
        )
        self.assertEqual(len(page_one.context["page_obj"]),12)

        page_three=self.client.get(reverse("products:list"),{"page":3})
        self.assertEqual(len(page_three.context["page_obj"]),2)

    def test_bad_page_number_falls_back(self):
        response=self.client.get(
            reverse("products:list"),
            {"page":"abc"}
        )
        self.assertEqual(response.status_code,200)

    def test_sidebar_links_keep_other_filters(self):
        Product.objects.create(
            title="B",price="1.00",product_url="https://example.com/b",category="Poetry"
        )
        response=self.client.get(
            reverse("products:list"),
            {"category":"Poetry"}
        )
        sections={s["title"]:s["options"] for s in response.context["filter_sections"]}
        in_stock=next(o for o in sections["By availability"] if o["label"] == "In stock")

        self .assertIn("category=Poetry",in_stock["url"])
        self.assertIn("availability=in_stock",in_stock["url"])

    def test_unknown_availability_value_is_ignored(self):
        response=self.client.get(
            reverse("products:list"),
            {"availability":"nonsense"}
        )
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.context["page_obj"]),1)
        