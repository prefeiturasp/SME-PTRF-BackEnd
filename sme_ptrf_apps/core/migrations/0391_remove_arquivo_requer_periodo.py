# Generated by Django 4.2.7 on 2024-05-15 10:32

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0390_arquivo_periodo_arquivo_requer_periodo"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="arquivo",
            name="requer_periodo",
        ),
    ]