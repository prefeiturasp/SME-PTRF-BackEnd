# Generated by Django 4.2.7 on 2024-01-17 11:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0027_alter_user_pode_acessar_sme"),
    ]

    operations = [
        migrations.AddField(
            model_name="grupo",
            name="suporte",
            field=models.BooleanField(default=False),
        ),
    ]
