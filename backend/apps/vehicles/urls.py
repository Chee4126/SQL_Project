from django.urls import path

from apps.vehicles.views import (
    MonthlyVehicleRegistrationListCreateView,
    VehicleEventCreateView,
    VehicleListView,
    VehicleRegistrationLimitReportView,
)

urlpatterns = [
    path(
        "reports/vehicle-registration-limits",
        VehicleRegistrationLimitReportView.as_view(),
        name="vehicle-registration-limit-report",
    ),
    path("vehicles", VehicleListView.as_view(), name="vehicle-list"),
    path(
        "monthly-vehicle-registrations",
        MonthlyVehicleRegistrationListCreateView.as_view(),
        name="vehicle-registration-list-create",
    ),
    path(
        "monthly-vehicle-registrations/<int:registration_id>/events",
        VehicleEventCreateView.as_view(),
        name="vehicle-event-create",
    ),
]
