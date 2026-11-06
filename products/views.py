from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

from django.views.decorators.http import require_POST
from .forms import ProductForm
from .models import Product
from django.core.paginator import Paginator
from .filters import apply_filters, build_filter_sections

PRODUCTS_PER_PAGE = 12


def product_list(request):
    queryset = apply_filters(Product.objects.order_by("title", "id"), request.GET)
    
    paginator = Paginator(queryset, PRODUCTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))
    page_range = paginator.get_elided_page_range(page_obj.number, on_each_side=2, on_ends=1)

    params = request.GET.copy()
    params.pop("page",None)

    return render(request, "products/product_list.html", {
        "page_obj": page_obj, 
        "page_range": page_range,
        "filter_sections": build_filter_sections(request.GET),
        "querystring": params.urlencode(),
        "is_filtered": any(request.GET.get(key) for key in ("category", "availability")),
        })

def product_update(request,pk):
    product=get_object_or_404(Product,pk=pk)
    

    if request.method=="POST":
        form=ProductForm(request.POST,instance=product)

        if form.is_valid():
            form.save()
            messages.success(request,f'"{product.title}" was updated')
            return  redirect("products:list")
        messages.error(request,"please correct the error below")
    else:
        form =ProductForm(instance=product)
    return render(request, "products/product_form.html", {"form": form, "product": product})

@require_POST
def product_delete(request,pk):
    product=get_object_or_404(Product,pk=pk)
    title=Product.title
    product.delete()
    messages.success(request,f'"{title}" was deleted')

    return redirect("products:list")


 






