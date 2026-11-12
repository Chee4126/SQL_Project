from django.urls import path

from apps.visitors.views import (
    VisitDepartureView,
    VisitListCreateView,
    VisitorDetailView,
    VisitorListCreateView,
    VisitReportView,
)

urlpatterns = [
    path("visitors", VisitorListCreateView.as_view(), name="visitor-list-create"),
    path(
        "visitors/<int:visitor_id>",
        VisitorDetailView.as_view(),
        name="visitor-detail",
    ),
    path("visits", VisitListCreateView.as_view(), name="visit-list-create"),
    path(
        "visits/<int:visit_id>/departure",
        VisitDepartureView.as_view(),
        name="visit-departure",
    ),
    path("reports/visits", VisitReportView.as_view(), name="visit-report"),
]