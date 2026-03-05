"""
Serviço que define quando o campo preenchida_em da Ata deve ser atualizado.
Atualiza apenas quando campos de conteúdo (preenchidos pelo usuário) mudam,
usando listas diferentes conforme a flag historico-de-membros.
"""

from datetime import datetime
from waffle import get_waffle_flag_model
from sme_ptrf_apps.core.models import Ata

ATA_CAMPOS_PREENCHIMENTO_COM_FLAG_HISTORICO_MEMBROS = (
    'tipo_ata',
    'tipo_reuniao',
    'convocacao',
    'data_reuniao',
    'local_reuniao',
    'hora_reuniao',
    'comentarios',
    'parecer_conselho',
    'retificacoes',
    'justificativa_repasses_pendentes',
    'presidente_da_reuniao_id',
    'secretario_da_reuniao_id',
    'composicao_id',
)

ATA_CAMPOS_PREENCHIMENTO_SEM_FLAG_HISTORICO_MEMBROS = (
    'tipo_ata',
    'tipo_reuniao',
    'convocacao',
    'data_reuniao',
    'local_reuniao',
    'hora_reuniao',
    'presidente_reuniao',
    'cargo_presidente_reuniao',
    'secretario_reuniao',
    'cargo_secretaria_reuniao',
    'comentarios',
    'parecer_conselho',
    'retificacoes',
    'justificativa_repasses_pendentes',
)


def _campo_preenchimento_mudou(instance, old_ata, campos):
    for field_name in campos:
        new_val = getattr(instance, field_name, None)
        old_val = getattr(old_ata, field_name, None)
        if new_val != old_val:
            return True
    return False


def atualizar_preenchida_em_se_mudou_conteudo(ata_instance):
    """
    Atualiza preenchida_em na instância apenas quando campos de conteúdo mudaram.
    """
    if ata_instance._state.adding:
        return

    flags = get_waffle_flag_model()
    flag_historico_de_membros = flags.objects.filter(
        name='historico-de-membros', everyone=True
    ).exists()

    try:
        old_ata = Ata.objects.filter(pk=ata_instance.pk).first()
    except (ValueError, TypeError):
        return
    if not old_ata:
        return

    if flag_historico_de_membros:
        campos = ATA_CAMPOS_PREENCHIMENTO_COM_FLAG_HISTORICO_MEMBROS
    else:
        campos = ATA_CAMPOS_PREENCHIMENTO_SEM_FLAG_HISTORICO_MEMBROS

    if _campo_preenchimento_mudou(ata_instance, old_ata, campos):
        ata_instance.preenchida_em = datetime.now()
