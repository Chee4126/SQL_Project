from django.apps import AppConfig


# Cấu hình Django cho ứng dụng quản lý xe tháng.
class VehiclesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.vehicles"
