from datetime import datetime, time, timedelta

from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import generics, serializers
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.visitors.models import Visit, Visitor
from apps.visitors.serializers import VisitSerializer


# Liệt kê lượt thăm và ghi nhận khách đến thăm sinh viên.
class VisitListCreateView(generics.ListCreateAPIView):
    serializer_class = VisitSerializer

    def get_queryset(self):
        queryset = Visit.objects.select_related("visitor", "student")
        student_id = self.request.query_params.get("student_id")
        visitor_id = self.request.query_params.get("visitor_id")
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if visitor_id:
            queryset = queryset.filter(visitor_id=visitor_id)
        return queryset


# Ghi nhận thời gian khách rời đi; bỏ trống thì lấy thời điểm hiện tại.
class VisitDepartureView(APIView):
    def patch(self, request, visit_id):
        raw_left_at = request.data.get("left_at", serializers.empty)
        if raw_left_at in (None, serializers.empty):
            left_at = timezone.now()
        else:
            left_at = serializers.DateTimeField().run_validation(raw_left_at)
        with transaction.atomic():
            try:
                visit = Visit.objects.select_for_update().get(pk=visit_id)
            except Visit.DoesNotExist:
                raise NotFound("Không tìm thấy lượt thăm.")
            if visit.left_at is not None:
                raise ValidationError({"left_at": "Lượt thăm này đã ghi nhận rời đi."})
            if left_at < visit.arrived_at:
                raise ValidationError(
                    {"left_at": "Thời gian rời đi không được trước thời gian đến."}
                )
            visit.left_at = left_at
            visit.save(update_fields=["left_at"])
        return Response(VisitSerializer(visit).data)


# Tính khoảng thời gian [bắt đầu, kết thúc) của tuần hoặc tháng chứa ngày tham chiếu.
def period_range(period, ref_date):
    if period == "week":
        start = ref_date - timedelta(days=ref_date.weekday())
        end = start + timedelta(days=7)
    else:
        start = ref_date.replace(day=1)
        end = (start + timedelta(days=32)).replace(day=1)
    tz = timezone.get_current_timezone()
    return (
        timezone.make_aware(datetime.combine(start, time.min), tz),
        timezone.make_aware(datetime.combine(end, time.min), tz),
        start,
        end - timedelta(days=1),
    )


# Báo cáo: mỗi sinh viên, từng khách đến thăm và số lần đến trong tuần hoặc tháng.
class VisitReportView(APIView):
    def get(self, request):
        period = request.query_params.get("period", "month")
        if period not in {"week", "month"}:
            raise ValidationError({"period": "Giá trị phải là week hoặc month."})
        date_param = request.query_params.get("date")
        if date_param:
            ref_date = parse_date(date_param)
            if ref_date is None:
                raise ValidationError({"date": "Ngày phải có dạng YYYY-MM-DD."})
        else:
            ref_date = timezone.localdate()

        start_dt, end_dt, first_day, last_day = period_range(period, ref_date)
        rows = (
            Visit.objects.filter(arrived_at__gte=start_dt, arrived_at__lt=end_dt)
            .values(
                "student_id",
                "student__name",
                "visitor_id",
                "visitor__name",
                "visitor__identity_number",
            )
            .annotate(visit_count=Count("id"))
            .order_by("student__name", "student_id", "visitor__name")
        )
        return Response(
            {
                "period": period,
                "from": first_day,
                "to": last_day,
                "results": [
                    {
                        "student_id": r["student_id"],
                        "student_name": r["student__name"],
                        "visitor_id": r["visitor_id"],
                        "visitor_name": r["visitor__name"],
                        "visitor_identity_number": r["visitor__identity_number"],
                        "visit_count": r["visit_count"],
                    }
                    for r in rows
                ],
            }
        )