from django.urls import path

from apps.services.views import (
    ServiceDetailView,
    ServiceListCreateView,
    ServiceRevenueReportView,
    ServiceUsageCreateView,
    ServiceUsageReportView,
)

urlpatterns = [
    path("services", ServiceListCreateView.as_view(), name="service-list"),
    path("services/<int:pk>", ServiceDetailView.as_view(), name="service-detail"),
    path("service-usages", ServiceUsageCreateView.as_view(), name="service-usage-create"),
    path(
        "reports/service-usage",
        ServiceUsageReportView.as_view(),
        name="service-usage-report",
    ),
    path(
        "reports/service-revenue",
        ServiceRevenueReportView.as_view(),
        name="service-revenue-report",
    ),
]
