from django.db import migrations


NOME_RECURSO_PREMIO = "Prêmio Excelência Educacional"


def corrige_motivos_estorno_receitas_premio(apps, schema_editor):
    Recurso = apps.get_model("core", "Recurso")
    Receita = apps.get_model("receitas", "Receita")
    MotivoEstorno = apps.get_model("receitas", "MotivoEstorno")
    ReceitaMotivoEstorno = Receita.motivos_estorno.through

    recurso_legado = Recurso.objects.filter(legado=True).first()
    recurso_premio = Recurso.objects.filter(nome=NOME_RECURSO_PREMIO).first()

    if not recurso_legado or not recurso_premio:
        return

    motivos_premio_por_motivo = {
        motivo.motivo: motivo
        for motivo in MotivoEstorno.objects.filter(recurso=recurso_premio)
    }

    receitas_premio = Receita.objects.filter(
        tipo_receita__e_estorno=True,
        conta_associacao__tipo_conta__recurso=recurso_premio,
        motivos_estorno__recurso=recurso_legado,
    ).distinct()

    vinculos_legado = ReceitaMotivoEstorno.objects.filter(
        receita__in=receitas_premio,
        motivoestorno__recurso=recurso_legado,
    ).select_related("motivoestorno")

    for vinculo in vinculos_legado.iterator():
        motivo_premio = motivos_premio_por_motivo.get(vinculo.motivoestorno.motivo)
        if not motivo_premio:
            continue

        ReceitaMotivoEstorno.objects.get_or_create(
            receita_id=vinculo.receita_id,
            motivoestorno_id=motivo_premio.id,
        )
        vinculo.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("receitas", "0055_motivoestorno_recurso"),
    ]

    operations = [
        migrations.RunPython(
            corrige_motivos_estorno_receitas_premio,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
