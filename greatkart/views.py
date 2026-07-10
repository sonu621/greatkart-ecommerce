# from django.shortcuts import render
# from store.models import Product, ReviewRating

# def home(request):
#     products = Product.objects.all().filter(is_available=True).order_by('created_date')

#     # Get the reviews
#     for product in products:
#         reviews = ReviewRating.objects.filter(product_id=product.id, is_active=True)
    
#     context = {
#         'products': products,
#         'reviews': reviews,
#     }

#     return render(request, 'home.html', context)

from django.shortcuts import render
from store.models import Product, ReviewRating

def home(request):
    products = Product.objects.all().filter(is_available=True).order_by('created_date')
    
    # Get reviews for all products
    reviews = []
    for product in products:
        product_reviews = ReviewRating.objects.filter(product_id=product.id, is_active=True)
        reviews.extend(product_reviews)  # Add reviews to the list
    
    # Alternative: If you want reviews as a dictionary per product
    # reviews_dict = {}
    # for product in products:
    #     reviews_dict[product.id] = ReviewRating.objects.filter(product_id=product.id, is_active=True)
    
    context = {
        'products': products,
        'reviews': reviews,  # Now reviews is always defined
        # 'reviews_dict': reviews_dict,  # If using the alternative
    }
    
    return render(request, 'home.html', context)