from django.contrib import admin
from .models import CrmOrder, Recall, FbForm


@admin.register(CrmOrder)
class CrmOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_number', 'customer_name', 'date', 'status', 'source', 'sdek')
    list_filter = ('status', 'sdek', 'date', 'source')
    search_fields = ('name', 'second_name', 'phone', 'email', 'order_number')
    readonly_fields = ('date_timestamp', 'last_call_mark', 'last_change_time_mark')


@admin.register(Recall)
class RecallAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'status')
    list_filter = ('status',)
    search_fields = ('name', 'phone')


@admin.register(FbForm)
class FbFormAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'contact', 'date', 'check_status')
    list_filter = ('check_status', 'date')
    search_fields = ('name', 'contact')
