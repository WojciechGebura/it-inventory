from django.shortcuts import render, get_object_or_404
from .models import Company, Computer

def computers_report(request):
    company_id = request.GET.get("company")
    company = None
    computers = []

    if company_id:
        company = get_object_or_404(Company, pk=company_id)
        computers = Computer.objects.filter(company=company).select_related("assigned_to").prefetch_related("service_actions")
    companies = Company.objects.all()

    return render(request, "inventory/computers_report.html", {
        "company": company,
        "companies": companies,
        "computers": computers,
    })
