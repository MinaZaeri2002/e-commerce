from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import Product, ProductImage, Category


class CategoryAdmin(admin.ModelAdmin):
    model = Category
    list_display = ['name', ]
    fields = ['name', ]
    search_fields = ['name', ]


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    fields = ['image']


class ProductAdmin(admin.ModelAdmin):
    model = Product
    inlines = [ProductImageInline]
    list_display = ['title', 'description', 'price', 'quantity', 'category']
    fields = ['title', 'description', 'price', 'quantity', 'category']
    search_fields = ['title', 'category']


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)

admin.site.unregister(Group)
admin.site.unregister(User)



