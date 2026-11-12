from django.db.models import Q
from rest_framework import generics

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


# Xem chi tiết và cập nhật hồ sơ sinh viên (không cho xóa để giữ lịch sử).
class StudentDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = StudentSerializer
    queryset = Student.objects.all()
    lookup_field = "student_id"
    lookup_url_kwarg = "student_id"