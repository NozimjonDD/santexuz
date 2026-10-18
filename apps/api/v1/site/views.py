"""HTTP orchestration only: every mutation delegates to an order service."""

from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.api.common.views import positive_query_id
from apps.api.v1.site import inputs, serializers
from apps.orders import models, selectors, services


@extend_schema_view(
    create=extend_schema(request=inputs.OrderCreateInput, responses={201: serializers.OrderSerializer}),
    plumber_response=extend_schema(request=inputs.ResponseInput, responses=serializers.OrderSerializer),
    inspection=extend_schema(request=inputs.InspectionInput, responses=serializers.OrderSerializer),
    estimate=extend_schema(request=inputs.EstimateInput, responses=serializers.OrderSerializer),
    store_response=extend_schema(request=inputs.ResponseInput, responses=serializers.OrderSerializer),
    material_prices=extend_schema(request=inputs.PriceMaterialsInput, responses=serializers.OrderSerializer),
    approve_quote=extend_schema(request=inputs.QuoteApprovalInput, responses=serializers.OrderSerializer),
    reject_quote=extend_schema(request=inputs.QuoteRejectionInput, responses=serializers.OrderSerializer),
    payments=extend_schema(request=inputs.PaymentInput, responses=serializers.OrderSerializer),
    begin_preparation=extend_schema(request=inputs.EmptyInput, responses=serializers.OrderSerializer),
    deliveries=extend_schema(request=inputs.DeliveryCreateInput, responses=serializers.OrderSerializer),
    delivery_status=extend_schema(request=inputs.DeliveryUpdateInput, responses=serializers.OrderSerializer),
    confirm_delivery=extend_schema(request=inputs.EmptyInput, responses=serializers.OrderSerializer),
    issues=extend_schema(request=inputs.IssueInput, responses=serializers.OrderSerializer),
    work_schedule=extend_schema(request=inputs.WorkScheduleInput, responses=serializers.OrderSerializer),
    start_work=extend_schema(request=inputs.EmptyInput, responses=serializers.OrderSerializer),
    complete_work=extend_schema(request=inputs.EmptyInput, responses=serializers.OrderSerializer),
    accept_work=extend_schema(request=inputs.EmptyInput, responses=serializers.OrderSerializer),
    cancel=extend_schema(request=inputs.CancelInput, responses=serializers.OrderSerializer),
    rating=extend_schema(request=inputs.RatingInput, responses=serializers.OrderSerializer),
    attachments=extend_schema(request=serializers.AttachmentInput, responses={201: serializers.AttachmentSerializer}),
    attachment_download=extend_schema(responses={(200, "application/octet-stream"): bytes}),
    contract_pdf=extend_schema(responses={(200, "application/pdf"): bytes}),
)
class OrderViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.OrderSerializer
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return models.Order.objects.none()
        queryset = selectors.orders_for(self.request.user)
        region_id = positive_query_id(self.request, "region")
        group_id = positive_query_id(self.request, "group")
        if region_id:
            queryset = queryset.filter(region_id=region_id)
        if group_id:
            queryset = queryset.filter(service_group_id=group_id)
        state = self.request.query_params.get("status")
        if state:
            from rest_framework.exceptions import ValidationError
            if state not in models.Order.Status.values:
                raise ValidationError({"status": "Unknown order status."})
            queryset = queryset.filter(status=state)
        if self.action == "retrieve" or (self.action == "list" and self.request.user.is_staff):
            return selectors.order_details(queryset)
        return queryset

    def get_serializer_class(self):
        return serializers.OrderListSerializer if self.action == "list" else serializers.OrderSerializer

    def create(self, request):
        data = inputs.OrderCreateInput(data=request.data)
        data.is_valid(raise_exception=True)
        order = services.create_order(actor=request.user, **data.validated_data)
        return Response(self.get_response_serializer(order.pk).data, status=status.HTTP_201_CREATED)

    def get_response_serializer(self, order_id):
        queryset = selectors.order_details(selectors.orders_for(self.request.user))
        return self.get_serializer(get_object_or_404(queryset, pk=order_id))

    def execute(self, service_name, input_class=inputs.EmptyInput, **extra):
        # Scope lookup first makes foreign order identifiers indistinguishable
        # from missing identifiers, including for action-only endpoints.
        order = self.get_object()
        data = input_class(data=self.request.data)
        data.is_valid(raise_exception=True)
        getattr(services, service_name)(actor=self.request.user, order_id=order.pk, **data.validated_data, **extra)
        order = selectors.order_details(selectors.orders_for(self.request.user)).filter(pk=order.pk).first()
        if order is None:
            return Response({"detail": "Action recorded."})
        return Response(self.get_serializer(order).data)

    @action(detail=True, methods=["post"], url_path="plumber-response")
    def plumber_response(self, request, pk=None):
        return self.execute("respond_plumber", inputs.ResponseInput)

    @action(detail=True, methods=["post"], url_path="inspection")
    def inspection(self, request, pk=None):
        return self.execute("schedule_inspection", inputs.InspectionInput)

    @action(detail=True, methods=["post"], url_path="estimate")
    def estimate(self, request, pk=None):
        return self.execute("submit_estimate", inputs.EstimateInput)

    @action(detail=True, methods=["post"], url_path="store-response")
    def store_response(self, request, pk=None):
        return self.execute("respond_store", inputs.ResponseInput)

    @action(detail=True, methods=["post"], url_path="material-prices")
    def material_prices(self, request, pk=None):
        return self.execute("price_materials", inputs.PriceMaterialsInput)

    @action(detail=True, methods=["post"], url_path="approve-quote")
    def approve_quote(self, request, pk=None):
        return self.execute("approve_quote", inputs.QuoteApprovalInput)

    @action(detail=True, methods=["post"], url_path="reject-quote")
    def reject_quote(self, request, pk=None):
        return self.execute("reject_quote", inputs.QuoteRejectionInput)

    @action(detail=True, methods=["post"], url_path="payments")
    def payments(self, request, pk=None):
        return self.execute("record_payment", inputs.PaymentInput)

    @action(detail=True, methods=["post"], url_path="begin-preparation")
    def begin_preparation(self, request, pk=None):
        return self.execute("begin_preparation")

    @action(detail=True, methods=["post"], url_path="deliveries")
    def deliveries(self, request, pk=None):
        return self.execute("create_delivery", inputs.DeliveryCreateInput)

    @action(detail=True, methods=["post"], url_path=r"deliveries/(?P<delivery_id>[0-9]+)/status")
    def delivery_status(self, request, pk=None, delivery_id=None):
        return self.execute("update_delivery", inputs.DeliveryUpdateInput, delivery_id=int(delivery_id))

    @action(detail=True, methods=["post"], url_path=r"deliveries/(?P<delivery_id>[0-9]+)/confirm")
    def confirm_delivery(self, request, pk=None, delivery_id=None):
        return self.execute("confirm_delivery", delivery_id=int(delivery_id))

    @action(detail=True, methods=["post"], url_path="issues")
    def issues(self, request, pk=None):
        return self.execute("report_issue", inputs.IssueInput)

    @action(detail=True, methods=["post"], url_path="work-schedule")
    def work_schedule(self, request, pk=None):
        return self.execute("schedule_work", inputs.WorkScheduleInput)

    @action(detail=True, methods=["post"], url_path="start-work")
    def start_work(self, request, pk=None):
        return self.execute("start_work")

    @action(detail=True, methods=["post"], url_path="complete-work")
    def complete_work(self, request, pk=None):
        return self.execute("complete_work")

    @action(detail=True, methods=["post"], url_path="accept-work")
    def accept_work(self, request, pk=None):
        return self.execute("accept_work")

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        return self.execute("cancel_order", inputs.CancelInput)

    @action(detail=True, methods=["post"], url_path="rating")
    def rating(self, request, pk=None):
        return self.execute("rate_order", inputs.RatingInput)

    @action(detail=True, methods=["post"], url_path="attachments")
    def attachments(self, request, pk=None):
        order = self.get_object()
        data = serializers.AttachmentInput(data=request.data)
        data.is_valid(raise_exception=True)
        attachment = services.add_attachment(actor=request.user, order_id=order.pk, **data.validated_data)
        return Response(serializers.AttachmentSerializer(attachment).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path=r"attachments/(?P<attachment_id>[0-9]+)/download")
    def attachment_download(self, request, pk=None, attachment_id=None):
        order = self.get_object()
        attachment = get_object_or_404(models.Attachment, order=order, pk=attachment_id)
        try:
            file = attachment.file.open("rb")
        except (FileNotFoundError, OSError):
            raise Http404("Attachment unavailable.")
        response = FileResponse(file, as_attachment=True, filename=attachment.file.name.rsplit("/", 1)[-1])
        response["Cache-Control"] = "private, no-store"
        response["X-Content-Type-Options"] = "nosniff"
        return response

    @action(detail=True, methods=["get"], url_path=r"contracts/(?P<contract_id>[0-9]+)/pdf")
    def contract_pdf(self, request, pk=None, contract_id=None):
        from apps.orders.documents import render_contract

        order = self.get_object()
        contract = get_object_or_404(models.Contract.objects.select_related("quote"), order=order, pk=contract_id)
        response = HttpResponse(render_contract(contract), content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="contract-{order.pk}-v{contract.quote.version}.pdf"'
        response["Cache-Control"] = "private, no-store"
        response["X-Content-Type-Options"] = "nosniff"
        return response
