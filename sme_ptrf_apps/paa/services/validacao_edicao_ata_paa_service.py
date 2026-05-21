from sme_ptrf_apps.paa.enums import PaaStatusEnum
from sme_ptrf_apps.paa.models import AtaPaa


def validar_edicao_ata_paa(ata_paa: AtaPaa) -> dict:
    """
    Valida se a ata pode ser editada (participantes, dados da reunião, etc.).

    Regras:
    - PAA em retificação: só permite editar a ata de RETIFICACAO; a de apresentação fica congelada.
    - PAA GERADO: não permite editar ata com PDF já gerado (CONCLUIDO ou EM_PROCESSAMENTO);
      evita PAA GERADO + ata NAO_GERADO (FORA_FLUXO na listagem).
    - Demais casos (elaboração, retificação em andamento): permite;
      o serializer continua invalidando o PDF para obrigar regeração quando aplicável.
    """
    paa = ata_paa.paa

    if paa.status == PaaStatusEnum.EM_RETIFICACAO.name:
        if ata_paa.tipo_ata != AtaPaa.ATA_RETIFICACAO:
            return {
                'is_valid': False,
                'mensagem': (
                    'Durante a retificação, apenas a ata de retificação pode ser editada. '
                    'A ata de apresentação original permanece congelada.'
                ),
            }
        return {'is_valid': True}

    if paa.status == PaaStatusEnum.GERADO.name and ata_paa.documento_gerado:
        if ata_paa.tipo_ata == AtaPaa.ATA_APRESENTACAO:
            mensagem = (
                'O Plano Anual já foi concluído e a ata de apresentação já foi gerada. '
                'Para alterar participantes ou dados da ata, utilize o fluxo de retificação do PAA.'
            )
        else:
            mensagem = (
                'A ata de retificação já foi gerada. '
                'Não é possível alterar participantes ou dados da ata neste estado.'
            )
        return {'is_valid': False, 'mensagem': mensagem}

    if ata_paa.status_geracao_pdf == AtaPaa.STATUS_EM_PROCESSAMENTO:
        return {
            'is_valid': False,
            'mensagem': 'A ata está sendo gerada. Aguarde a conclusão do processamento.',
        }

    return {'is_valid': True}
