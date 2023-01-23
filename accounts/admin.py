from django.contrib import admin

from accounts.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)
    search_fields = ('username', 'first_name', 'last_name')
