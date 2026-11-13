from django.db.models import Q
from rest_framework import generics
from rest_framework.exceptions import ValidationError

from apps.students.models import Student
from apps.students.serializers import StudentSerializer


# Liệt kê, tìm kiếm và tạo hồ sơ sinh viên.
class StudentListCreateView(generics.ListCreateAPIView):
    serializer_class = StudentSerializer

    def get_queryset(self):
        queryset = Student.objects.all()
        keyword = self.request.query_params.get("q")
        class_name = self.request.query_params.get("class_name")
        if keyword:
            queryset = queryset.filter(
                Q(student_id__icontains=keyword)
                | Q(name__icontains=keyword)
                | Q(identity_number__icontains=keyword)
            )
        if class_name:
            queryset = queryset.filter(class_name__iexact=class_name)
        return queryset


# Xem, cập nhật hoặc xóa hồ sơ nếu chưa phát sinh dữ liệu lịch sử.
class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StudentSerializer
    queryset = Student.objects.all()
    lookup_field = "student_id"
    lookup_url_kwarg = "student_id"

    def perform_destroy(self, instance):
        references = (
            ("room_assignments", "lịch sử phân phòng"),
            ("visits", "lượt thăm"),
            ("service_usages", "lượt sử dụng dịch vụ"),
            ("monthly_vehicle_registrations", "đăng ký xe tháng"),
            ("invoices", "hóa đơn"),
        )
        used_by = [
            label
            for relation, label in references
            if getattr(instance, relation).exists()
        ]
        if used_by:
            raise ValidationError(
                {"detail": f"Không thể xóa sinh viên đã có {', '.join(used_by)}."}
            )
        instance.delete()