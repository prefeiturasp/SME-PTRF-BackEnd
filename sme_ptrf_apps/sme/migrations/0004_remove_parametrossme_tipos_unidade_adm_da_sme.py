# Generated by Django 4.2.7 on 2024-01-11 15:28

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("sme", "0003_tipounidadeadministrativa"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="parametrossme",
            name="tipos_unidade_adm_da_sme",
        ),
    ]