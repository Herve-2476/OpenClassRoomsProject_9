from django.core.validators import MinValueValidator, MaxValueValidator
from litreview.settings import BASE_DIR
from django.db import models
from authentication.models import User
from PIL import Image
import os


class Ticket(models.Model):
    title = models.CharField(max_length=128, verbose_name="Titre")
    description = models.TextField(max_length=2048, blank=True)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(null=True)

    IMAGE_MAX_SIZE = (200, 200)

    def resize_image(self):

        image = Image.open(self.image.path)
        image.thumbnail(self.IMAGE_MAX_SIZE)
        image.save(self.image.path)

    def delete_image(self, old_image):
        os.remove(str(BASE_DIR) + str(old_image.url))

    def save(self, *args, **kwargs):
        old_image = kwargs.pop("old_image", False)
        super().save(*args, **kwargs)

        # we delete old image and resize new image if changes
        if old_image != self.image:
            if self.image:
                self.resize_image()
            if old_image:
                self.delete_image(old_image)

    def delete(self, *args, **kwargs):
        old_image = kwargs.pop("old_image")
        super().delete(*args, **kwargs)
        if old_image:
            self.delete_image(old_image)


class Review(models.Model):
    headline = models.CharField(verbose_name="Titre", max_length=128)
    ticket = models.ForeignKey(to=Ticket, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
        verbose_name="Note",
        # validates that rating must be between 0 and 5
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )

    body = models.CharField(verbose_name="Commentaire", max_length=8192, blank=True)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    time_created = models.DateTimeField(auto_now_add=True)
    time_updated = models.DateTimeField(null=True)


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
