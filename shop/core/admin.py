from django.contrib import admin
from .models import Item, Order, OrderItem, Category, Refund, Report


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_granted=True)


make_refund_accepted.short_description = 'Update orders to refund granted'


class ItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'discount_price', 'label', 'category']
    search_fields = ['title']
    list_filter = ['category']


admin.site.register(Item, ItemAdmin)


class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'ref_code', 'ordered_date', 'ordered', 'received', 'refund_requested', 'refund_granted']
    search_fields = ['user__username', 'ref_code']
    actions = [make_refund_accepted]


admin.site.register(Order, OrderAdmin)


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['item', 'quantity', 'user', 'ordered']
    # search_fields = ['name']


admin.site.register(OrderItem, OrderItemAdmin)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


admin.site.register(Category, CategoryAdmin)


class ReportAdmin(admin.ModelAdmin):
    list_display = ['ref_code', 'reason', 'full_name', 'phone_number', 'email']
    search_fields = ['ref_code']


admin.site.register(Report, ReportAdmin)


# class RefundAdmin(admin.ModelAdmin):
#     list_display = ['order__ref_code', 'accepted']
#     search_fields = ['order__ref_code']


# admin.site.register(Refund, RefundAdmin)
