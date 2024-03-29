# Generated by Django 4.2.7 on 2024-02-14 04:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0373_ata_presidente_da_reuniao_ata_secretario_da_reuniao"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ata",
            name="presidente_da_reuniao",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="presidente_participante_ata",
                to="core.participante",
            ),
        ),
        migrations.AlterField(
            model_name="ata",
            name="secretario_da_reuniao",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="secretario_participante_ata",
                to="core.participante",
            ),
        ),
    ]
