from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0472_merge_20261111_1234"),
    ]

    operations = [
        migrations.AddField(
            model_name="prestacaoconta",
            name="status_presidente",
            field=models.CharField(
                blank=True,
                max_length=15,
                null=True,
                verbose_name="Status do presidente na conclusão",
            ),
        ),
        migrations.AddField(
            model_name="prestacaoconta",
            name="cargo_substituto_presidente_ausente",
            field=models.CharField(
                blank=True,
                max_length=65,
                null=True,
                verbose_name="Cargo substituto do presidente na conclusão",
            ),
        ),
    ]
