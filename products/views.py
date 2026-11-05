from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

from django.views.decorators.http import require_POST
from .forms import ProductForm
from .models import Product
from django.core.paginator import Paginator

PRODUCTS_PER_PAGE = 12


def product_list(request):
    products = Product.objects.all()
    
    paginator = Paginator(products, PRODUCTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))
    page_range = paginator.page_range

    return render(request, "products/product_list.html", {"page_obj": page_obj, "page_range": page_range},)

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


 






