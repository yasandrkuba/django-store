from django.urls import path, include, re_path
from rest_framework import routers
from . import views

# router = routers.DefaultRouter()
# router.register(r'items', views.ItemViewSet)


urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('product/<slug>/', views.ItemDetailView.as_view(), name='product'),
    path('order-summary/', views.OrderSummaryView.as_view(), name='order-summary'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('add-to-cart/<slug>/', views.add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', views.remove_from_cart, name='remove-from-cart'),
    path('remove-single-item-from-cart/<slug>/', views.remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    path('payment/', views.PaymentView.as_view(), name='payment'),
    path('request-refund/', views.RequestRefundView.as_view(), name='request-refund'),
    path('order-list/', views.order_list, name='order-list'),
    path('order-detail/<int:pk>/', views.order_detail, name='order-detail'),
    path('order/<int:pk>/report/', views.ReportView.as_view(), name='report'),
    path('category/<slug:slug>/', views.filter_by_category, name='filter-by-category'),
    path('search-results/', views.SearchView.as_view(), name='search'),
    path('api/v1/drf-auth/', include('rest_framework.urls')),
    path('api/v1/', include('djoser.urls')),
    re_path(r'ˆauth/', include('djoser.urls.authtoken')),
]
