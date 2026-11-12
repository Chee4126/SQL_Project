from django.db import transaction
from django.db.models import Q
from rest_framework.exceptions import NotFound, ValidationError

from apps.rooms.models import Room, RoomAssignment
from apps.students.models import Student


# Lọc các lượt ở giao với khoảng [start_date, end_date]; end_date None là chưa kết thúc.
def overlapping(queryset, start_date, end_date):
    queryset = queryset.filter(Q(end_date__isnull=True) | Q(end_date__gte=start_date))
    if end_date is not None:
        queryset = queryset.filter(start_date__lte=end_date)
    return queryset


# Phân phòng: kiểm tra trùng thời gian của sinh viên và sức chứa của phòng.
@transaction.atomic
def assign_room(student, room, start_date, end_date=None):
    if end_date is not None and end_date < start_date:
        raise ValidationError(
            {"end_date": "Ngày rời phòng không được trước ngày vào phòng."}
        )
    # Khóa sinh viên và phòng để các thao tác đồng thời chạy tuần tự.
    Student.objects.select_for_update().get(pk=student.pk)
    room = Room.objects.select_for_update().select_related("room_type").get(pk=room.pk)

    student_overlap = overlapping(
        RoomAssignment.objects.filter(student=student), start_date, end_date
    )
    if student_overlap.exists():
        raise ValidationError(
            {"student_id": "Sinh viên đã có lượt ở trùng thời gian."}
        )

    capacity = room.room_type.max_occupants
    occupants = overlapping(
        RoomAssignment.objects.filter(room=room), start_date, end_date
    ).count()
    if occupants >= capacity:
        raise ValidationError(
            {"room_id": f"Phòng đã đủ {capacity} người trong khoảng thời gian này."}
        )

    return RoomAssignment.objects.create(
        student=student, room=room, start_date=start_date, end_date=end_date
    )


# Ghi nhận ngày rời phòng cho một lượt ở còn hiệu lực.
@transaction.atomic
def end_assignment(assignment_id, end_date):
    try:
        assignment = RoomAssignment.objects.select_for_update().get(pk=assignment_id)
    except RoomAssignment.DoesNotExist:
        raise NotFound("Không tìm thấy lượt phân phòng.")
    if assignment.end_date is not None:
        raise ValidationError({"end_date": "Lượt ở này đã kết thúc."})
    if end_date < assignment.start_date:
        raise ValidationError(
            {"end_date": "Ngày rời phòng không được trước ngày vào phòng."}
        )
    assignment.end_date = end_date
    assignment.save(update_fields=["end_date"])
    return assignment