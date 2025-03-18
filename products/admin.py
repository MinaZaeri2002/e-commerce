from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import Product, ProductImage, Category


class CategoryAdmin(admin.ModelAdmin):
    model = Category
    list_display = ['name', ]
    fields = ['name', ]
    search_fields = ['name', ]

    def has_module_permission(self, request):
        return request.user.is_staff

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    fields = ['image']

    def has_add_permission(self, request, obj=None):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff


class ProductAdmin(admin.ModelAdmin):
    model = Product
    inlines = [ProductImageInline]
    list_display = ['title', 'description', 'price', 'quantity', 'category']
    fields = ['title', 'description', 'price', 'quantity', 'category']
    search_fields = ['title', 'category']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "category":
            kwargs["queryset"] = Category.objects.all().order_by('name')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_module_permission(self, request):
        return request.user.is_staff

    def has_add_permission(self, request):
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        return request.user.is_staff

    def has_change_permission(self, request, obj=None):
        return request.user.is_staff

    def has_delete_permission(self, request, obj=None):
        return request.user.is_staff


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)




