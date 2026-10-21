from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("dre", "0083_comissao_recursos_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="motivoreprovacao",
            options={
                "unique_together": {("motivo", "recurso")},
                "verbose_name": "Motivo de rejeição",
                "verbose_name_plural": "Motivos de rejeição",
            },
        ),
    ]
