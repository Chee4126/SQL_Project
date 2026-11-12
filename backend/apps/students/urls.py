from django.urls import path

from apps.students.views import StudentDetailView, StudentListCreateView

urlpatterns = [
    path("students", StudentListCreateView.as_view(), name="student-list-create"),
    path("students/<str:student_id>", StudentDetailView.as_view(), name="student-detail"),
]