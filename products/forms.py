from django import forms
from .models import Product

class ProductForm(forms.ModelForm):

    class Meta:
        model=Product
        fields = ["title", "price", "availability", "product_url", "image_url", "category"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css_class = "form-check-input" if isinstance(field.widget, forms.CheckboxInput) else "form-control"
            field.widget.attrs.setdefault("class", css_class)

    


