import re

import bleach
from rest_framework import serializers

from .models import Comment, User

ALLOWED_TAGS = ["a", "code", "i", "strong"]

ALLOWED_ATTRIBUTES = {
    "a": ["href", "title"],
}


def sanitize_text(text: str) -> str:

    return bleach.clean(
        text,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True,
        strip_comments=True,
    )


def validate_tags_are_closed(text: str) -> bool:
    tag_pattern = re.compile(r"<(/?)(\w+)[^>]*?>")
    stack = []

    self_closing = {"br", "img", "input", "hr"}

    for match in tag_pattern.finditer(text):
        is_closing = match.group(1) == "/"
        tag_name = match.group(2).lower()

        if tag_name in self_closing:
            continue

        if not is_closing:
            stack.append(tag_name)
        else:
            if not stack or stack[-1] != tag_name:
                return False
            stack.pop()
    return len(stack) == 0


def validate_file_extension(file, allowed_extensions: list):
    ext = file.name.rsplit(".", 1)[-1].lower()
    if ext not in allowed_extensions:
        raise serializers.ValidationError(
            f'Allowed formats: {", ".join(allowed_extensions).upper()}.'
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "home_page", "created_at"]
        read_only_fields = ["id", "created_at"]
        validators = []

    def validate_username(self, value):

        if not re.match(r"^[a-zA-Z0-9]+$", value):
            raise serializers.ValidationError(
                "Username can only contain Latin letters and numbers."
            )
        return value


class RecursiveRepliesSerializer(serializers.Serializer):

    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class CommentSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)
    user_data = UserSerializer(write_only=True)
    replies = RecursiveRepliesSerializer(many=True, read_only=True)
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Comment.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Comment
        fields = [
            "id",
            "user",
            "user_data",
            "parent",
            "text",
            "image",
            "txt_file",
            "created_at",
            "replies",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_text(self, value):
        if not validate_tags_are_closed(value):
            raise serializers.ValidationError(
                "Error: Not all HTML tags are closed. Check the markup."
            )
        return sanitize_text(value)

    def validate_image(self, value):
        if value:
            validate_file_extension(value, ["jpg", "jpeg", "gif", "png"])
        return value

    def validate_txt_file(self, value):
        if value:
            validate_file_extension(value, ["txt"])
            if value.size > 100 * 1024:
                raise serializers.ValidationError("text file cannot exceed 100 КБ .")
        return value

    def create(self, validated_data):
        user_data = validated_data.pop("user_data")
        request = self.context.get("request")
        if request:
            user_data["ip_address"] = self._get_client_ip(request)
            user_data["user_agent"] = request.META.get("HTTP_USER_AGENT", "")
        user, _ = User.objects.get_or_create(
            username=user_data["username"],
            email=user_data["email"],
            defaults=user_data,
        )

        comment = Comment.objects.create(user=user, **validated_data)
        return comment

    @staticmethod
    def _get_client_ip(request) -> str:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "0.0.0.0")


class CommentListSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replies_count = serializers.IntegerField(
        source="replies.count",
        read_only=True,
    )

    class Meta:
        model = Comment
        fields = [
            "id",
            "user",
            "text",
            "image",
            "txt_file",
            "created_at",
            "replies_count",
        ]
