from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Product(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    availability = models.BooleanField(default=True)
    product_url = models.URLField(max_length=500, unique=True)
    image_url = models.URLField(max_length=500, blank=True)
    category = models.CharField(max_length=100, blank=True, default="Uncategorized")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title