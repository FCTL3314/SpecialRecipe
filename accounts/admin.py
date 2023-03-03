from django.contrib import admin

from accounts.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fields = ('image', 'username', 'first_name', 'last_name', 'email', 'slug', 'date_joined', 'last_login',
              'is_verified', 'is_staff', 'is_active')
    readonly_fields = ('date_joined', 'last_login', 'is_verified',)
    prepopulated_fields = {'slug': ('username',)}
    ordering = ('username',)
    search_fields = ('username', 'first_name', 'last_name')
