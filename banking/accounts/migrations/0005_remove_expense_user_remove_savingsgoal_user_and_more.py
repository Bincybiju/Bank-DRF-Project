# Generated by Django 5.0.4 on 2024-04-30 08:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_budget_expense_savingsgoal"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="expense",
            name="user",
        ),
        migrations.RemoveField(
            model_name="savingsgoal",
            name="user",
        ),
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
                (
                    "account_number",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="accounts.savings",
                    ),
                ),
            ],
        ),
        migrations.DeleteModel(
            name="Budget",
        ),
        migrations.DeleteModel(
            name="Expense",
        ),
        migrations.DeleteModel(
            name="SavingsGoal",
        ),
    ]