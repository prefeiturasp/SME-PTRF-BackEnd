from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0463_altera_nomenclatura_status_reprovada_para_rejeitada"),
    ]

    operations = [
        migrations.AlterField(
            model_name="prestacaoconta",
            name="outros_motivos_reprovacao",
            field=models.TextField(
                blank=True,
                default="",
                verbose_name="Outros motivos para rejeição pela DRE",
            ),
        ),
        migrations.AlterField(
            model_name="prestacaocontareprovadanaoapresentacao",
            name="data_de_reprovacao",
            field=models.DateTimeField(
                blank=True,
                null=True,
                verbose_name="Data da rejeição",
            ),
        ),
    ]
