from django.urls import include, path
from django.http import JsonResponse


def api_root(request):
    """Show the available API base paths when the backend root is opened."""
    return JsonResponse(
        {
            "message": "Backend Django đang hoạt động.",
            "api_base": "/api/",
            "endpoints": [
                "/api/services",
                "/api/service-usages",
                "/api/vehicles",
                "/api/monthly-vehicle-registrations",
                "/api/invoices",
                "/api/reports/monthly-student-costs",
            ],
        }
    )

urlpatterns = [
    path("", api_root, name="api-root"),
    path("api/", include("apps.services.urls")),
    path("api/", include("apps.vehicles.urls")),
    path("api/", include("apps.invoices.urls")),
]
