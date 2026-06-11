from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, RegexValidator, URLValidator
from django.db import models
from django.utils import timezone

alphanumeric = RegexValidator(
    r"^[a-zA-Z0-9]+$", "Дозволено лише латинські літери та цифри."
)


class User(models.Model):
    username = models.CharField(max_length=50, validators=[alphanumeric])
    email = models.EmailField(validators=[EmailValidator()])
    home_page = models.URLField(blank=True, null=True, validators=[URLValidator()])
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("username", "email")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.username} <{self.email}>"


def upload_image_path(instance, filename):
    now = timezone.now()
    return f'images/{now.strftime("%Y/%m")}/{filename}'


def upload_file_path(instance, filename):
    now = timezone.now()
    return f'files/{now.strftime("%Y/%m")}/{filename}'


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
    )
    text = models.TextField()
    image = models.ImageField(upload_to=upload_image_path, null=True, blank=True)
    txt_file = models.FileField(upload_to=upload_file_path, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        parent_info = f" (reply to #{self.parent_id})" if self.parent_id else ""
        return f"Comment #{self.id} by {self.user}{parent_info}"

    @property
    def is_root(self):
        return self.parent_id is None

    def get_replies(self):
        return self.replies.select_related("user").order_by("created_at")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            from .tasks import resize_comment_image

            resize_comment_image.delay(self.pk)

    def clean(self):
        if self.txt_file and self.txt_file.size > 100 * 1024:
            raise ValidationError(
                {"txt_file": "Текстовий файл не може перевищувати 100 КБ."}
            )
