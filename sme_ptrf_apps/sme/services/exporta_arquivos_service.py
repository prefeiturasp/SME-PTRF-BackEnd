from sme_ptrf_apps.sme.services.saldo_bancario_service import gerar_dados_exportar_xlsx
from sme_ptrf_apps.sme.services.exporta_xlsx_service import gerar_planilha


def gerar_arquivo_xlsx_saldo_bancario(periodo_uuid, conta_uuid, dre_uuid, unidade, tipo_ue, username):
    dados = gerar_dados_exportar_xlsx(periodo_uuid, conta_uuid, dre_uuid, unidade, tipo_ue, username)
    xlsx = gerar_planilha(dados)
    return xlsx
