from django.urls import path

from .views import (
    CommentDetailView,
    CommentListCreateView,
    CommentRepliesView,
    captcha_refresh,
)

urlpatterns = [
    path("comments/", CommentListCreateView.as_view()),
    path("comments/<int:pk>/", CommentDetailView.as_view()),
    path("comments/<int:pk>/replies/", CommentRepliesView.as_view()),
    path("captcha/", captcha_refresh),
]
