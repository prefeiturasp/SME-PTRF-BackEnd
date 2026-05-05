from django.db import migrations, models


def popular_tipos_conta_dos_recursos(apps, schema_editor):
    Recurso = apps.get_model("core", "Recurso")
    ParametrosDre = apps.get_model("dre", "ParametrosDre")

    parametros_dre = ParametrosDre.objects.order_by("id").first()
    if not parametros_dre:
        return

    Recurso.objects.all().update(
        tipo_conta_um_id=parametros_dre.tipo_conta_um_id,
        tipo_conta_dois_id=parametros_dre.tipo_conta_dois_id,
    )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("dre", "0079_ataparecertecnicosnapshot"),
        ("core", "0435_add_status_valores_reprogramados_por_recurso"),
    ]

    operations = [
        migrations.AddField(
            model_name="recurso",
            name="tipo_conta_dois",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=models.deletion.CASCADE,
                related_name="recurso_tipo_conta_dois",
                to="core.tipoconta",
            ),
        ),
        migrations.AddField(
            model_name="recurso",
            name="tipo_conta_um",
            field=models.ForeignKey(
                blank=True,
                default=None,
                null=True,
                on_delete=models.deletion.CASCADE,
                related_name="recurso_tipo_conta_um",
                to="core.tipoconta",
            ),
        ),
        migrations.RunPython(popular_tipos_conta_dos_recursos, noop_reverse),
    ]
