from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore
from django.db.models import Count
from django.http import JsonResponse
from django.views.generic import TemplateView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Comment
from .serializers import CommentListSerializer, CommentSerializer


class CommentListCreateView(generics.ListCreateAPIView):
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ["user__username", "user__email", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return (
            Comment.objects.filter(parent=None)
            .select_related("user")
            .prefetch_related(
                "replies__user",
                "replies__replies__user",
                "replies__replies__replies__user",
            )
            .annotate(replies_count=Count("replies"))
        )

    def get_serializer_class(self):
        return CommentSerializer


class CommentDetailView(generics.RetrieveAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.select_related("user").prefetch_related(
            "replies__user",
            "replies__replies__user",
        )


class CommentRepliesView(APIView):
    def get(self, request, pk):
        comment = generics.get_object_or_404(
            Comment.objects.prefetch_related("replies__user"),
            pk=pk,
        )
        serializer = CommentSerializer(comment, context={"request": request})
        return Response(serializer.data["replies"])


class IndexView(TemplateView):
    template_name = "index.html"


def captcha_refresh(request):
    new_key = CaptchaStore.generate_key()
    return JsonResponse(
        {
            "key": new_key,
            "image_url": captcha_image_url(new_key),
        }
    )
