from django.contrib import admin
from web_site.models import CallBackRequest


@admin.register(CallBackRequest)
class Call_back_requestAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'name', 'age', 'email', 'phone_num', 'note', 'date_create']
    list_display_links = ['id', 'status', 'name', 'age', 'email', 'phone_num']
    list_search = ['id', 'name', 'age', 'phone_num', 'note']
    list_filter = ['status', 'age']