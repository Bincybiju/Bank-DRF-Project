# Generated by Django 5.0.4 on 2024-04-30 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0005_remove_expense_user_remove_savingsgoal_user_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="budgetcontrol",
            name="account_number",
            field=models.CharField(max_length=10),
        ),
    ]
