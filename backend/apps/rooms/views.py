from django.db.models import Count, F, Q
from django.utils import timezone
from rest_framework import generics
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.dateparse import parse_date
from rest_framework.exceptions import NotFound, ValidationError

from apps.rooms.models import Room, RoomAssignment, RoomType
from apps.rooms.serializers import (
    RoomAssignmentEndSerializer,
    RoomAssignmentSerializer,
    RoomSerializer,
    RoomTypeSerializer,
)
from apps.rooms.services import end_assignment
from apps.students.models import Student


# Danh sách phòng kèm số người đang ở tại ngày tham chiếu (mặc định hôm nay).
def rooms_with_occupancy(ref_date=None):
    ref_date = ref_date or timezone.localdate()
    return Room.objects.select_related("room_type").annotate(
        current_occupants=Count(
            "assignments",
            filter=Q(assignments__start_date__lte=ref_date)
            & (
                Q(assignments__end_date__isnull=True)
                | Q(assignments__end_date__gte=ref_date)
            ),
        )
    )

# Liệt kê và tạo loại phòng.
class RoomTypeListCreateView(generics.ListCreateAPIView):
    serializer_class = RoomTypeSerializer
    queryset = RoomType.objects.all()


# Xem và cập nhật loại phòng.
class RoomTypeDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = RoomTypeSerializer
    queryset = RoomType.objects.all()
    lookup_field = "id"
    lookup_url_kwarg = "room_type_id"


# Liệt kê, lọc phòng còn chỗ và tạo phòng.
class RoomListCreateView(generics.ListCreateAPIView):
    serializer_class = RoomSerializer

    def get_queryset(self):
        queryset = rooms_with_occupancy()
        room_type_id = self.request.query_params.get("room_type_id")
        available = self.request.query_params.get("available")
        if room_type_id:
            queryset = queryset.filter(room_type_id=room_type_id)
        if available and available.lower() in {"1", "true", "yes"}:
            queryset = queryset.filter(
                current_occupants__lt=F("room_type__max_occupants")
            )
        return queryset


# Xem và cập nhật phòng.
class RoomDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = RoomSerializer
    lookup_field = "room_id"
    lookup_url_kwarg = "room_id"

    def get_queryset(self):
        return rooms_with_occupancy()


# Liệt kê lượt phân phòng và phân phòng mới cho sinh viên.
class RoomAssignmentListCreateView(generics.ListCreateAPIView):
    serializer_class = RoomAssignmentSerializer

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
                    "room_type_name": room.room_type.name,
                    "max_occupants": room.room_type.max_occupants,
                    "current_occupants": room.current_occupants,
                    "remaining": room.room_type.max_occupants - room.current_occupants,
                    "within_limit": room.current_occupants <= room.room_type.max_occupants,
                }
                for room in rooms
            ]
        )