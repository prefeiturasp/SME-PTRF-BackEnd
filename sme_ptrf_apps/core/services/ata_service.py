import logging
from sme_ptrf_apps.core.services.ata_dados_service import gerar_dados_ata
from sme_ptrf_apps.core.services.ata_pdf_service import gerar_arquivo_ata_pdf

LOGGER = logging.getLogger(__name__)


def gerar_arquivo_ata(periodo=None, prestacao_de_contas=None, ata=None, usuario=None):
    LOGGER.info(f"Gerando Arquivo da Ata, prestacao de contas {prestacao_de_contas.uuid} e ata {ata.uuid}")

    ata.arquivo_pdf_iniciar()

    try:
        dados_ata = gerar_dados_ata(periodo=periodo, prestacao_de_contas=prestacao_de_contas, ata=ata, usuario=usuario)
        gerar_arquivo_ata_pdf(dados_ata=dados_ata, ata=ata)
        LOGGER.info(f'Gerando arquivo ata em PDF')
        ata.arquivo_pdf_concluir()
        return ata
    except:
        LOGGER.info(f'FALHA AO GERAR O ARQUIVO DA ATA')
        return None

