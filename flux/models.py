from django.core.validators import MinValueValidator, MaxValueValidator
from litreview.settings import BASE_DIR
from django.db import models
from authentication.models import User
from PIL import Image
import os


class Ticket(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2048, blank=True)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)

    IMAGE_MAX_SIZE = (800, 800)

    def resize_image(self):

        image = Image.open(self.image)
        image.thumbnail(self.IMAGE_MAX_SIZE)
        image.save(self.image.path)
        print("image réduite sauvegardée")

    def save(self, *args, **kwargs):
        image_resize = kwargs.pop("image_resize", True)
        super().save(*args, **kwargs)
        if image_resize and self.image:
            self.resize_image()

    def delete(self, *args, **kwargs):
        old_image = kwargs.pop("old_image")
        if old_image:
            os.remove(str(BASE_DIR) + str(old_image.url))

        super().delete(*args, **kwargs)


class Review(models.Model):
    headline = models.CharField(max_length=128)
    ticket = models.ForeignKey(to=Ticket, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        # validates that rating must be between 0 and 5
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )

    body = models.CharField(max_length=8192, blank=True)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    time_created = models.DateTimeField(auto_now_add=True)


class UserFollows(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="following")
    followed_user = models.ForeignKey(
        verbose_name="Utilisateurs suivis", to=User, on_delete=models.CASCADE, related_name="followed_by"
    )

    class Meta:
        # ensures we don't get multiple UserFollows instances
        # for unique user-user_followed pairs
        unique_together = (
            "user",
            "followed_user",
        )
