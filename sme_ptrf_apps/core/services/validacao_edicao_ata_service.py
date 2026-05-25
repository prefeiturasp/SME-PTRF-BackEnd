from sme_ptrf_apps.core.models import Ata, PrestacaoConta

STATUS_PC_PERMITE_EDITAR_ATA_APRESENTACAO = {
    PrestacaoConta.STATUS_NAO_APRESENTADA,
    PrestacaoConta.STATUS_NAO_RECEBIDA,
}


def _pc_permite_editar_ata_apresentacao(ata: Ata) -> bool:
    if not ata.prestacao_conta_id:
        return False
    return ata.prestacao_conta.status in STATUS_PC_PERMITE_EDITAR_ATA_APRESENTACAO


def validar_edicao_ata_pc(ata: Ata) -> dict:
    """
    Valida se a ata de PC pode ser editada (participantes, dados da reunião, etc.).

    Regras:
    - Apresentação enquanto a PC não foi recebida (NAO_APRESENTADA / NAO_RECEBIDA):
      edição permitida mesmo com PDF gerado, para permitir regeração.
    - Apresentação após recebimento da PC com PDF gerado: bloqueada;
      alterações devem ser feitas na ata de retificação.
    - Apresentação enquanto existe ata de retificação na PC: bloqueada.
    - Qualquer ata com PDF em processamento: bloqueada até concluir.
    """
    if ata.status_geracao_pdf == Ata.STATUS_EM_PROCESSAMENTO:
        return {
            'is_valid': False,
            'mensagem': 'A ata está sendo gerada. Aguarde a conclusão do processamento.',
        }

    if ata.tipo_ata == Ata.ATA_APRESENTACAO:
        if (
            ata.prestacao_conta_id and
            ata.prestacao_conta.atas_da_prestacao.filter(
                tipo_ata=Ata.ATA_RETIFICACAO,
                previa=False,
            ).exists()
        ):
            return {
                'is_valid': False,
                'mensagem': (
                    'Durante a retificação, apenas a ata de retificação pode ser editada. '
                    'A ata de apresentação original permanece congelada.'
                ),
            }

        if not _pc_permite_editar_ata_apresentacao(ata):
            if ata.documento_gerado or ata.pdf_gerado_previamente:
                return {
                    'is_valid': False,
                    'mensagem': (
                        'A ata de apresentação já foi gerada. '
                        'Para alterar participantes ou dados da reunião, utilize a ata de retificação '
                        'da prestação de contas.'
                    ),
                }

    return {'is_valid': True}
