from django.urls import path

from apps.visitors.views import (
    VisitDepartureView,
    VisitListCreateView,
    VisitReportView,
)

urlpatterns = [
    path("visits", VisitListCreateView.as_view(), name="visit-list-create"),
    path(
        "visits/<int:visit_id>/departure",
        VisitDepartureView.as_view(),
        name="visit-departure",
    ),
    path("reports/visits", VisitReportView.as_view(), name="visit-report"),
]