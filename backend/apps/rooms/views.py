from django.db import transaction
from django.db.models import Count, F, Q
from django.utils.dateparse import parse_date
from django.utils import timezone
from rest_framework import generics
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.invoices.services import refresh_invoice_for_period
from apps.rooms.models import Room, RoomAssignment
from apps.rooms.serializers import (
    RoomAssignmentEndSerializer,
    RoomAssignmentSerializer,
    RoomSerializer,
)
from apps.rooms.services import end_assignment
from apps.students.models import Student


# Danh sách phòng kèm số người đang ở tại ngày tham chiếu (mặc định hôm nay).
def rooms_with_occupancy(ref_date=None):
    ref_date = ref_date or timezone.localdate()
    return Room.objects.annotate(
        current_occupants=Count(
            "assignments",
            filter=Q(assignments__start_date__lte=ref_date)
            & (
                Q(assignments__end_date__isnull=True)
                | Q(assignments__end_date__gt=ref_date)
            ),
        )
    )


# Liệt kê, lọc phòng còn chỗ và tạo phòng.
class RoomListCreateView(generics.ListCreateAPIView):
    serializer_class = RoomSerializer

    def get_queryset(self):
        date_param = self.request.query_params.get("date")
        if date_param:
            ref_date = parse_date(date_param)
            if ref_date is None:
                raise ValidationError({"date": "Ngày phải có dạng YYYY-MM-DD."})
        else:
            ref_date = timezone.localdate()
        queryset = rooms_with_occupancy(ref_date)
        available = self.request.query_params.get("available")
        if available and available.lower() in {"1", "true", "yes"}:
            queryset = queryset.filter(current_occupants__lt=F("max_occupants"))
        return queryset


# Xem và cập nhật phòng.
class RoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RoomSerializer
    lookup_field = "room_id"
    lookup_url_kwarg = "room_id"

    def get_queryset(self):
        return rooms_with_occupancy()

    def perform_destroy(self, instance):
        if instance.assignments.exists():
            raise ValidationError(
                {"detail": "Không thể xóa phòng đã có lịch sử phân phòng."}
            )
        instance.delete()


# Liệt kê lượt phân phòng và phân phòng mới cho sinh viên.
class RoomAssignmentListCreateView(generics.ListCreateAPIView):
    serializer_class = RoomAssignmentSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        assignment = serializer.save()
        refresh_invoice_for_period(
            student=assignment.student,
            month=assignment.start_date.month,
            year=assignment.start_date.year,
            use_assignment_room=True,
        )

    def get_queryset(self):
        queryset = RoomAssignment.objects.select_related("student", "room")
        student_id = self.request.query_params.get("student_id")
        room_id = self.request.query_params.get("room_id")
        active = self.request.query_params.get("active")
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if room_id:
            queryset = queryset.filter(room_id=room_id)
        if active and active.lower() in {"1", "true", "yes"}:
            queryset = queryset.filter(end_date__isnull=True)
        return queryset


# Ghi nhận ngày rời phòng cho một lượt phân phòng.
class RoomAssignmentEndView(APIView):
    def patch(self, request, assignment_id):
        serializer = RoomAssignmentEndSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        end_date = serializer.validated_data.get("end_date") or timezone.localdate()
        assignment = end_assignment(assignment_id, end_date)
        return Response(RoomAssignmentSerializer(assignment).data)


# Xem lịch sử phân phòng của một sinh viên.
class StudentRoomHistoryView(generics.ListAPIView):
    serializer_class = RoomAssignmentSerializer

    def get_queryset(self):
        student_id = self.kwargs["student_id"]
        if not Student.objects.filter(pk=student_id).exists():
            raise NotFound("Không tìm thấy sinh viên.")
        return RoomAssignment.objects.select_related("student", "room").filter(
            student_id=student_id
        )
# Báo cáo kiểm tra số người ở của từng phòng so với sức chứa tại một ngày.
class RoomCapacityReportView(APIView):
    def get(self, request):
        date_param = request.query_params.get("date")
        if date_param:
            ref_date = parse_date(date_param)
            if ref_date is None:
                raise ValidationError({"date": "Ngày phải có dạng YYYY-MM-DD."})
        else:
            ref_date = timezone.localdate()
        rooms = rooms_with_occupancy(ref_date).order_by("room_id")
        return Response(
            [
                {
                    "room_id": room.room_id,
                    "room_name": room.name,
                    "monthly_price": room.monthly_price,
                    "max_occupants": room.max_occupants,
                    "current_occupants": room.current_occupants,
                    "remaining": room.max_occupants - room.current_occupants,
                    "within_limit": room.current_occupants <= room.max_occupants,
                }
                for room in rooms
            ]
        )