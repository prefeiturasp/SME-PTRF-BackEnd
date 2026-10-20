from django.db import migrations, models
import django.db.models.deletion


NOME_RECURSO_PREMIO = "Prêmio Excelência Educacional"


def vincula_recurso_legado_e_copia_para_premio(apps, schema_editor):
    Recurso = apps.get_model("core", "Recurso")
    TipoAcertoLancamento = apps.get_model("core", "TipoAcertoLancamento")

    recurso_legado = Recurso.objects.get(legado=True)
    TipoAcertoLancamento.objects.filter(recurso__isnull=True).update(
        recurso=recurso_legado
    )

    recurso_premio = Recurso.objects.filter(nome=NOME_RECURSO_PREMIO).first()
    if not recurso_premio:
        return

    tipos_acerto_legado = TipoAcertoLancamento.objects.filter(
        recurso=recurso_legado
    )

    for tipo_acerto in tipos_acerto_legado.iterator():
        TipoAcertoLancamento.objects.update_or_create(
            nome=tipo_acerto.nome,
            categoria=tipo_acerto.categoria,
            recurso=recurso_premio,
            defaults={
                "pode_alterar_saldo_conciliacao": (
                    tipo_acerto.pode_alterar_saldo_conciliacao
                ),
                "ativo": tipo_acerto.ativo,
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0447_corrige_tipo_acerto_documento_solicitacoes_premio"),
    ]

    operations = [
        migrations.AddField(
            model_name="tipoacertolancamento",
            name="recurso",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="core.recurso",
                verbose_name="Recurso",
            ),
        ),
        migrations.RunPython(
            vincula_recurso_legado_e_copia_para_premio,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="tipoacertolancamento",
            name="recurso",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to="core.recurso",
                verbose_name="Recurso",
            ),
        ),
    ]
