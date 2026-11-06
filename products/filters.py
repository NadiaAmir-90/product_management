from .models import Product

AVAILABILITY_CHOICES = [
    ("in_stock", "In stock"),
    ("out_of_stock", "Out of stock"),
]

def apply_filters(queryset,params):
    """apply filter in the database using ?category=... and ?availability=..."""

    category=params.get("category")
    availability = params.get("availability")

    if category:
        queryset=queryset.filter(category=category)
    if availability=="in_stock":
        queryset=queryset.filter(availability=True)
    elif availability=="out_of_stock":
        queryset=queryset.filter(availability=False)
    return queryset


def _link(params,key,value):

    """Other filters are kept and `page` is dropped, because a new filter
    should start again from page 1 (admin's list_filter does the same)."""

    new=params.copy()
    new.pop("page",None)

    if value is None:
        new.pop(key,None)
    else :
        new[key]=value
    query = new.urlencode()
    return f"?{query}" if query else "?"

def _options(params,key,choices):
    """which options are selected : ALL, or specific catergory or availability"""
    selected=params.get(key)
    options = [{"label": "All", "url": _link(params, key, None), "active": not selected}]

    for value,label in choices:
        options.append({
            "label":label,
            "url": _link(params, key, value),
            "active": selected == value,
        })
    return options



def build_filter_sections(params):
    """ filter 'By availability' / 'By category'"""

    categories = Product.objects.exclude(category="").order_by("category").values_list("category", flat=True).distinct()
    return [
        {"title": "By availability", "options": _options(params, "availability", AVAILABILITY_CHOICES)},
        {"title": "By category", "options": _options(params, "category", [(c, c) for c in categories])},
    ]