from sme_ptrf_apps.sme.services.saldo_bancario_service import gerar_dados_extrato_dres_exportacao_xlsx
from sme_ptrf_apps.sme.services.exporta_xlsx_service import gerar_planilha


def gerar_arquivo_xlsx_extrato_dres(periodo_uuid, conta_uuid, username):
    dados = gerar_dados_extrato_dres_exportacao_xlsx(periodo_uuid, conta_uuid, username)
    xlsx = gerar_planilha(dados)
    return xlsx
