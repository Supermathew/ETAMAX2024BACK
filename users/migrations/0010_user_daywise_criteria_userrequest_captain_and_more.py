# Generated by Django 5.0.2 on 2024-02-29 03:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0009_user_gender_userrequest_gender"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="daywise_criteria",
            field=models.TextField(
                default='{"F": 1, "S": 1, "T": 1}',
                verbose_name="daywise_Criteria JSON (DONT FILL THIS)",
            ),
        ),
        migrations.AddField(
            model_name="userrequest",
            name="captain",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="captain",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="userrequest",
            name="captain_paid",
            field=models.BooleanField(default=False, verbose_name="captain paid"),
        ),
    ]