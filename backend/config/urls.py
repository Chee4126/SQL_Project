from django.urls import include, path
from django.http import JsonResponse


def api_root(request):
    """Show the available API base paths when the backend root is opened."""
    return JsonResponse(
        {
            "message": "Backend Django đang hoạt động.",
            "api_base": "/api/",
            "endpoints": [
                "/api/students",
                "/api/services",
                "/api/service-usages",
                "/api/vehicles",
                "/api/monthly-vehicle-registrations",
                "/api/invoices",
                "/api/reports/monthly-student-costs",
                "/api/rooms",
                "/api/room-assignments",

                "/api/auth/login",
                "/api/auth/register",
                "/api/auth/logout",
                "/api/auth/me",
                "/api/accounts",
                "/api/visits",
                "/api/reports/visits",
                "/api/reports/room-capacity",
                "/api/reports/service-usage",
                "/api/reports/service-revenue",
            ],
        }
    )

urlpatterns = [
    path("", api_root, name="api-root"),
    path("api/", include("apps.students.urls")),
    path("api/", include("apps.rooms.urls")),
    path("api/", include("apps.services.urls")),
    path("api/", include("apps.vehicles.urls")),
    path("api/", include("apps.invoices.urls")),
    path("api/", include("apps.accounts.urls")),
    path("api/", include("apps.visitors.urls")),
]
