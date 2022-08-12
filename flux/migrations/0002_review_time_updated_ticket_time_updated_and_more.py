# Generated by Django 4.0.6 on 2022-08-12 07:15

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('flux', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='time_updated',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='ticket',
            name='time_updated',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='review',
            name='body',
            field=models.CharField(blank=True, max_length=8192, verbose_name=''),
        ),
        migrations.AlterField(
            model_name='review',
            name='headline',
            field=models.CharField(max_length=128, verbose_name='Titre'),
        ),
        migrations.AlterField(
            model_name='review',
            name='rating',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(5)], verbose_name='Note'),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='title',
            field=models.CharField(max_length=128, verbose_name='Titre'),
        ),
        migrations.AlterField(
            model_name='userfollows',
            name='followed_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followed_by', to=settings.AUTH_USER_MODEL, verbose_name='Utilisateurs suivis'),
        ),
    ]
