# Generated by Django 5.0.4 on 2024-04-29 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bank", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="dob",
            field=models.DateField(blank=True, null=True),
        ),
    ]