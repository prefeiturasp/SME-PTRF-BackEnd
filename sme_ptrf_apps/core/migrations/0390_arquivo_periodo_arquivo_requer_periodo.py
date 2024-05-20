# Generated by Django 4.2.7 on 2024-05-15 08:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0389_migrar_campo_pdf_gerado_previamente"),
    ]

    operations = [
        migrations.AddField(
            model_name="arquivo",
            name="periodo",
            field=models.ForeignKey(
                blank=True,
                help_text="Período associado ao arquivo (opcional)",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="core.periodo",
                verbose_name="Período",
            ),
        ),
        migrations.AddField(
            model_name="arquivo",
            name="requer_periodo",
            field=models.BooleanField(
                choices=[(True, "Sim"), (False, "Não")],
                default=False,
                help_text="Indica se o tipo de carga requer um período",
                verbose_name="Requer período",
            ),
        ),
    ]
