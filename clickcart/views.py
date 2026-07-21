from django.shortcuts import render
from django.db.models import Avg, Count, Q
from store.models import Product, ReviewRating
from django.utils import timezone

def home(request):
    # Annotate products with review data directly in the queryset
    products = Product.objects.filter(
        is_available=True
    ).annotate(
        avg_rating=Avg('reviewrating__rating', filter=Q(reviewrating__is_active=True)),
        review_count=Count('reviewrating', filter=Q(reviewrating__is_active=True))
    ).order_by('-created_date')[:12]
    
    # Calculate overall stats
    total_products = Product.objects.filter(is_available=True).count()
    
    overall_avg = ReviewRating.objects.filter(
        is_active=True
    ).aggregate(avg=Avg('rating'))['avg'] or 0
    
    total_reviews = ReviewRating.objects.filter(is_active=True).count()
    
    # Get today's purchases (if you have order data)
    today = timezone.now().date()
    # today_purchases = OrderProduct.objects.filter(
    #     order__created_at__date=today,
    #     order__is_ordered=True
    # ).count()
    today_purchases = 100  # Replace with actual query when orders are set up
    
    # Recent buyers (if you have user data)
    # recent_buyers = Account.objects.filter(
    #     orders__is_ordered=True
    # ).distinct()[:5]
    recent_buyers = ['Sarah', 'Mike', 'Emma', 'John', 'Lisa']  # Replace with actual query
    
    context = {
        'products': products,  # These already have avg_rating and review_count
        'total_products': total_products,
        'avg_rating': overall_avg,
        'total_reviews': total_reviews,
        'today_purchases': today_purchases,
        'recent_buyers': recent_buyers,
    }
    
    return render(request, 'home.html', context)