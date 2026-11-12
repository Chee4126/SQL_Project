from django.urls import path

from apps.rooms.views import (
    RoomAssignmentEndView,
    RoomAssignmentListCreateView,
    RoomDetailView,
    RoomListCreateView,
    RoomTypeDetailView,
    RoomTypeListCreateView,
    StudentRoomHistoryView,
    RoomCapacityReportView,
)

urlpatterns = [
    path("room-types", RoomTypeListCreateView.as_view(), name="room-type-list-create"),
    path(
        "room-types/<int:room_type_id>",
        RoomTypeDetailView.as_view(),
        name="room-type-detail",
    ),
    path("rooms", RoomListCreateView.as_view(), name="room-list-create"),
    path("rooms/<str:room_id>", RoomDetailView.as_view(), name="room-detail"),
    path(
        "room-assignments",
        RoomAssignmentListCreateView.as_view(),
        name="room-assignment-list-create",
    ),
    path(
        "room-assignments/<int:assignment_id>/end",
        RoomAssignmentEndView.as_view(),
        name="room-assignment-end",
    ),
    path(
        "students/<str:student_id>/room-history",
        StudentRoomHistoryView.as_view(),
        name="student-room-history",
    ),
        path(
        "reports/room-capacity",
        RoomCapacityReportView.as_view(),
        name="room-capacity-report",
    ),
]