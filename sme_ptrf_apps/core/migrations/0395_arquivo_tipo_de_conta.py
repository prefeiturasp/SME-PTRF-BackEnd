# Generated by Django 4.2.7 on 2024-05-22 01:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0394_alter_arquivo_periodo"),
    ]

    operations = [
        migrations.AddField(
            model_name="arquivo",
            name="tipo_de_conta",
            field=models.ForeignKey(
                blank=True,
                help_text="Tipo de conta associado ao arquivo (opcional dependendo do tipo de carga)",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="core.tipoconta",
                verbose_name="Tipo de conta",
            ),
        ),
    ]
