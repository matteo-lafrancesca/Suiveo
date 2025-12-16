from django.contrib import admin
from .models import (
    Client, Employee, Binome, BinomePause,
    CallTemplate, Call, ClientEmployeeHistory
)

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name")
    search_fields = ("last_name", "first_name")

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name")
    search_fields = ("last_name", "first_name")

@admin.register(Binome)
class BinomeAdmin(admin.ModelAdmin):
    list_display = ("client", "employee", "state", "first_intervention_date")
    list_filter = ("state",)
    search_fields = ("client__last_name", "employee__last_name")

@admin.register(BinomePause)
class BinomePauseAdmin(admin.ModelAdmin):
    list_display = ("binome", "start_date", "end_date", "duration_days")
    list_filter = ("start_date",)

@admin.register(ClientEmployeeHistory)
class ClientEmployeeHistoryAdmin(admin.ModelAdmin):
    list_display = ("client", "employee", "started_at", "ended_at")
    list_filter = ("started_at", "ended_at")
    search_fields = ("client__last_name", "employee__last_name")

admin.site.register(CallTemplate)
admin.site.register(Call)
