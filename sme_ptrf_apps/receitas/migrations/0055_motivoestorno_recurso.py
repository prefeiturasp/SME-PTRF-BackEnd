from django.db import migrations, models
import django.db.models.deletion


NOME_RECURSO_PREMIO = "Prêmio Excelência Educacional"


def vincula_recurso_legado_e_copia_para_premio(apps, schema_editor):
    Recurso = apps.get_model("core", "Recurso")
    MotivoEstorno = apps.get_model("receitas", "MotivoEstorno")

    recurso_legado = Recurso.objects.filter(legado=True).first()
    if not recurso_legado:
        return

    MotivoEstorno.objects.filter(recurso__isnull=True).update(
        recurso=recurso_legado
    )

    recurso_premio = Recurso.objects.filter(nome=NOME_RECURSO_PREMIO).first()
    if not recurso_premio:
        return

    motivos_estorno_legado = MotivoEstorno.objects.filter(
        recurso=recurso_legado
    )

    for motivo_estorno in motivos_estorno_legado.iterator():
        MotivoEstorno.objects.update_or_create(
            motivo=motivo_estorno.motivo,
            recurso=recurso_premio,
            defaults={},
        )


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0449_corrige_tipo_acerto_lancamento_solicitacoes_premio"),
        ("receitas", "0054_migra_receitas_premio_tipo_receita"),
    ]

    operations = [
        migrations.AddField(
            model_name="motivoestorno",
            name="recurso",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="core.recurso",
                verbose_name="Recurso",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="motivoestorno",
            unique_together={("motivo", "recurso")},
        ),
        migrations.RunPython(
            vincula_recurso_legado_e_copia_para_premio,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="motivoestorno",
            name="recurso",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="core.recurso",
                verbose_name="Recurso",
            ),
        ),
    ]
