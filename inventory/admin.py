from django.contrib import admin
from .models import Company, Employee, Computer, ServiceAction, ReportProxy
from django.contrib.admin import SimpleListFilter
from django.urls import path
from django.shortcuts import render

# zmiana nagłówków
admin.site.site_header = "eSupport"
admin.site.site_title = "eSupport"
admin.site.index_title = "Panel administracyjny eSupport"

class ModelValueFilter(SimpleListFilter):
    title = "Model"
    parameter_name = "model"

    def lookups(self, request, model_admin):
        models = (model_admin
                  .get_queryset(request)
                  .values_list("model", flat=True)
                  .order_by()
                  .distinct())
        return [(m, m) for m in models if m]

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(model=value)
        return queryset


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "vat_id")
    search_fields = ("name", "vat_id", "city")
    list_filter = ("city",)
    
class ComputerInline(admin.TabularInline):
    model = Computer
    fk_name = "assigned_to"
    extra = 0
    can_delete = False
    show_change_link = True
    fields = ("name", "brand", "model", "service_tag")
    readonly_fields = ("name", "brand", "model", "service_tag")

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "company", "email", "position", "computers_count")
    search_fields = ("first_name", "last_name", "email", "company__name")
    list_filter = ("company",)
    inlines = [ComputerInline]
    list_select_related = ("company",)

    def computers_count(self, obj):
        return obj.computers.count()
    computers_count.short_description = "Komputery"


class ServiceActionInline(admin.TabularInline):
    model = ServiceAction
    extra = 0
    



@admin.register(Computer)
class ComputerAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "model", "service_tag", "assigned_to", "company_name")
    search_fields = (
        "name", "model", "service_tag",
        "assigned_to__first_name", "assigned_to__last_name",
        "assigned_to__company__name",
    )
    list_filter = (
        "brand",
        "assigned_to",
        "assigned_to__company",   # ← to jest ważne
    )
    list_select_related = ("assigned_to", "assigned_to__company")
    autocomplete_fields = ["assigned_to"]
    ordering = ("name",)
    list_per_page = 25

    # Usuń nasze ręczne filtrowanie z get_queryset (jeśli dodałeś wcześniej)
    # i ZOSTAW poniższą metodę tylko do podania listy firm do szablonu:

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["company_choices"] = Company.objects.only("id", "name").order_by("name")
        extra_context["selected_company"] = request.GET.get("assigned_to__company__id__exact", "")
        return super().changelist_view(request, extra_context=extra_context)

    def company_name(self, obj):
        return obj.company.name if obj.company else "-"
    company_name.short_description = "Firma"





@admin.register(ServiceAction)
class ServiceActionAdmin(admin.ModelAdmin):
    list_display = ("title", "computer", "action_date", "status", "cost")
    search_fields = (
        "title",
        "computer__name",
        "computer__service_tag",
        "computer__model",
        "computer__assigned_to__first_name",
        "computer__assigned_to__last_name",
        "computer__assigned_to__company__name",
    )
    list_filter = (
        "status",
        "action_date",
        "computer",                           # szybkie zawężenie po konkretnym kompie
        "computer__assigned_to__company",     # WAŻNE: żeby admin rozpoznawał parametr z dropdownu
    )
    date_hierarchy = "action_date"
    list_select_related = ("computer", "computer__assigned_to", "computer__assigned_to__company")
    list_per_page = 25
    ordering = ("-action_date", "-id")

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        # lista firm do dropdownu
        extra_context["company_choices"] = Company.objects.only("id", "name").order_by("name")
        # odczyt aktualnie wybranej firmy z GET
        extra_context["selected_company"] = request.GET.get("computer__assigned_to__company__id__exact", "")
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(ReportProxy)
class ComputerReportAdmin(admin.ModelAdmin):
    change_list_template = "admin/inventory/reports_changelist.html"
    # Ukryj przyciski dodaj/usuń/edycja
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return True
    def has_delete_permission(self, request, obj=None): return False

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('raport-komputerow/', self.admin_site.admin_view(self.computers_report), name='inventory_computers_report'),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        # domyślna podstrona zakładki Raporty
        return render(request, "admin/inventory/reports_changelist.html")

    def computers_report(self, request):
        company_id = request.GET.get("company")
        company = None
        computers = []
        if company_id:
            company = Company.objects.filter(pk=company_id).first()
            if company:
                computers = Computer.objects.filter(company=company).select_related("assigned_to").prefetch_related("service_actions")
        companies = Company.objects.all()
        return render(request, "admin/inventory/computers_report.html", {
            "company": company,
            "companies": companies,
            "computers": computers,
        })
