from typing import Any
from django.contrib.contenttypes.admin import GenericTabularInline
from django.contrib import admin, messages
from django.db.models.query import QuerySet
from django.http import HttpRequest
from . import models
from django.db.models import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse
from tags.models import TaggedItem


class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'

    def lookups(self, request, model_admin):
        return [
            ('<10', 'Low')
        ]

    def queryset(self, request, queryset: QuerySet):
        if self.value() == '<10':
            return queryset.filter(inventory__lt=10)

class TagInline(GenericTabularInline):
    model = TaggedItem

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [TagInline]
    prepopulated_fields = {
        'slug': ['title']
    }   
    autocomplete_fields = ['collection']
    actions = ['clear_inventory']
    list_display =['title', 'price','inventory_status','collection']
    list_filter = ['collection', 'last_update', InventoryFilter]
    list_per_page = 10
    list_select_related = ['collection']
    search_fields = ['title']

    @admin.display(ordering='inventory')
    def inventory_status(self,product):
        if product.inventory < 10:
            return 'Low'
        return 'OK'
    
    @admin.action(description='Clear inventory')
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory=0)
        self.message_user(
            request,
            f'{updated_count} products were successfully updated.',
            messages.ERROR
        )



@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership','orders']
    list_editable = ['membership']
    ordering = ['first_name', 'last_name']
    list_per_page = 10 
    ordering = ['first_name', 'last_name']
    search_fields = ['first_name__istartswith', 'last_name__istartswith']

    @admin.display(ordering= 'orders_count')
    def orders(self, customer):
        url = (
            reverse('admin:store_order_changelist')
            + '?'
            + urlencode(
                {
                    'customer__id': str(customer.id)
                }
            )
        )
        return format_html('<a href="{}"> {} </a>', url, customer.orders_count)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            orders_count = Count('order')
        )

class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ['product']
    min_num = 1
    max_num = 10
    model = models.OrderItem
    extra = 0


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields =['customer']
    inlines = [OrderItemInline]
    list_display = ['id', 'placed_at', 'customer']
  

@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'products_count']
    search_fields = ['title']

    @admin.display(ordering= 'products_count')
    def products_count(self,collection):
        url = (
            reverse('admin:store_product_changelist')
            + '?'
            + urlencode(
                {
                   'collection__id': str(collection.id)
                }
            )
            )
        return format_html('<a href="{}"> {} </a>', url,collection.products_count)
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            products_count = Count('products')
        )


