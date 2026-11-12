from django.urls import path

from apps.invoices.views import (
    InvoiceDetailView,
    InvoiceGenerateView,
    InvoiceListView,
    InvoiceStatusUpdateView,
    MonthlyStudentCostReportView,
)

urlpatterns = [
    path(
        "reports/monthly-student-costs",
        MonthlyStudentCostReportView.as_view(),
        name="monthly-student-cost-report",
    ),
    path("invoices", InvoiceListView.as_view(), name="invoice-list"),
    path("invoices/generate", InvoiceGenerateView.as_view(), name="invoice-generate"),
    path("invoices/<int:pk>", InvoiceDetailView.as_view(), name="invoice-detail"),
    path(
        "invoices/<int:pk>/status",
        InvoiceStatusUpdateView.as_view(),
        name="invoice-status-update",
    ),
]
