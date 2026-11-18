from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0473_prestacaoconta_status_presidente_conclusao"),
    ]

    operations = [
        migrations.AddField(
            model_name="prestacaoconta",
            name="cargo_conselheiro_assinatura",
            field=models.CharField(
                blank=True,
                max_length=65,
                null=True,
                verbose_name="Conselheiro que assina na conclusão",
            ),
        ),
        migrations.AddField(
            model_name="associacao",
            name="cargo_conselheiro_assinatura",
            field=models.CharField(
                blank=True,
                max_length=65,
                null=True,
                verbose_name="Conselheiro que assina o demonstrativo",
            ),
        ),
    ]
