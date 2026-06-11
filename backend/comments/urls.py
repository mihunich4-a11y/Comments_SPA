from django.urls import path

from .views import CommentDetailView, CommentListCreateView, CommentRepliesView

urlpatterns = [
    path("comments/", CommentListCreateView.as_view()),
    path("comments/<int:pk>/", CommentDetailView.as_view()),
    path("comments/<int:pk>/replies/", CommentRepliesView.as_view()),
]
