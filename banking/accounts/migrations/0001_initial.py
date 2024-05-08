# Generated by Django 5.0.4 on 2024-05-08 08:18

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="BudgetControl",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("category_name", models.CharField(max_length=100)),
                ("account_number", models.CharField(max_length=10)),
                (
                    "alloted_budget",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                (
                    "balance_budget",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name="FundTransfer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("sender_account_number", models.CharField(max_length=10)),
                ("receiver_account_number", models.CharField(max_length=10)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=15)),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="InterestRate",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("rate", models.DecimalField(decimal_places=2, max_digits=5)),
            ],
        ),
        migrations.CreateModel(
            name="FixedDeposit",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("amount", models.DecimalField(decimal_places=2, max_digits=15)),
                ("duration_months", models.IntegerField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("end_date", models.DateField(blank=True, null=True)),
                (
                    "total_amount",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=15, null=True
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RecurrentDeposit",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("amount", models.DecimalField(decimal_places=2, max_digits=15)),
                (
                    "frequency",
                    models.CharField(
                        choices=[
                            ("MONTHLY", "Monthly"),
                            ("QUARTERLY", "Quarterly"),
                            ("HALF_YEARLY", "Half-Yearly"),
                            ("YEARLY", "Yearly"),
                        ],
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("end_date", models.DateField(blank=True, null=True)),
                (
                    "total_amount",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=15, null=True
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Savings",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "balance",
                    models.DecimalField(decimal_places=2, default=0, max_digits=15),
                ),
                (
                    "account_number",
                    models.CharField(default=0, max_length=10, unique=True),
                ),
                (
                    "account_type",
                    models.CharField(
                        choices=[("SAVINGS", "Savings"), ("CURRENT", "Current")],
                        max_length=10,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CurrentTransaction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "transaction_type",
                    models.CharField(
                        choices=[("DEPOSIT", "Deposit"), ("WITHDRAWAL", "Withdrawal")],
                        max_length=20,
                    ),
                ),
                ("amount", models.DecimalField(decimal_places=2, max_digits=15)),
                ("date", models.DateTimeField(default=django.utils.timezone.now)),
                ("description", models.TextField(blank=True)),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="current_transactions",
                        to="accounts.savings",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SavingsGoal",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("account_number", models.CharField(max_length=10)),
                ("description", models.CharField(max_length=255)),
                ("goal_amount", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "current_progress",
                    models.DecimalField(decimal_places=2, default=0, max_digits=15),
                ),
                ("achieved", models.BooleanField(default=False)),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SavingsTransaction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "transaction_type",
                    models.CharField(
                        choices=[("DEPOSIT", "Deposit"), ("WITHDRAWAL", "Withdrawal")],
                        max_length=20,
                    ),
                ),
                ("amount", models.DecimalField(decimal_places=2, max_digits=15)),
                ("date", models.DateTimeField(default=django.utils.timezone.now)),
                ("description", models.TextField(blank=True)),
                (
                    "account",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="saving_transactions",
                        to="accounts.savings",
                    ),
                ),
            ],
        ),
    ]
