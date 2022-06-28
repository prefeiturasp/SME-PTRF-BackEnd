import logging
from django.forms.models import model_to_dict
from sme_ptrf_apps.core.models.ata import Ata
from sme_ptrf_apps.core.services.ata_dados_service import gerar_dados_ata
from sme_ptrf_apps.core.services.ata_pdf_service import gerar_arquivo_ata_pdf
from sme_ptrf_apps.core.services.associacoes_service import retorna_repasses_pendentes_periodos_ate_agora

LOGGER = logging.getLogger(__name__)


def gerar_arquivo_ata(prestacao_de_contas=None, ata=None, usuario=None):
    LOGGER.info(f"Gerando Arquivo da Ata, prestacao de contas {prestacao_de_contas.uuid} e ata {ata.uuid}")

    ata.arquivo_pdf_iniciar()

    try:
        dados_ata = gerar_dados_ata(prestacao_de_contas=prestacao_de_contas, ata=ata, usuario=usuario)
        gerar_arquivo_ata_pdf(dados_ata=dados_ata, ata=ata)
        LOGGER.info(f'Gerando arquivo ata em PDF')
        ata.arquivo_pdf_concluir()
        return ata
    except Exception as e:
        LOGGER.info(f'FALHA AO GERAR O ARQUIVO DA ATA', e)
        ata.arquivo_pdf_nao_gerado()
        return None


def validar_campos_ata(ata: Ata = None):
    campos_invalidos, campos_nao_required = list(), [
        'arquivo_pdf',
        'comentarios',
        'retificacoes',
        'justificativa_repasses_pendentes'
    ]
    repasse_pendentes = retorna_repasses_pendentes_periodos_ate_agora(
        ata.associacao,
        ata.periodo
    )

    for campo, valor in model_to_dict(ata).items():

        if valor in [None, ''] and campo not in campos_nao_required:
            campos_invalidos.append(campo)

    if repasse_pendentes and ata.justificativa_repasses_pendentes == '':
        campos_invalidos.append('justificativa_repasses_pendentes')

    if campos_invalidos:
        return {'is_valid': False, 'campos': campos_invalidos}
    return {'is_valid': True}
