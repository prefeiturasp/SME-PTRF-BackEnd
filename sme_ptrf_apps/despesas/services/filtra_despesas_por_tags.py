from ..models import Despesa

def filtra_despesas_por_tags(item, filtro_informacoes_list, rateio = False):
    if rateio:
        item = item.despesa
    
    if Despesa.TAG_ANTECIPADO['id'] in filtro_informacoes_list and item.teve_pagamento_antecipado():
        return False
    if Despesa.TAG_ESTORNADO['id'] in filtro_informacoes_list and item.possui_estornos():
        return False
    if Despesa.TAG_IMPOSTO['id'] in filtro_informacoes_list and item.possui_retencao_de_impostos():
        return False
    if Despesa.TAG_IMPOSTO_PAGO['id'] in filtro_informacoes_list and item.e_imposto_pago():
        return False
    if Despesa.TAG_IMPOSTO_A_SER_PAGO['id'] in filtro_informacoes_list and item.e_imposto_nao_pago():
        return False
    if (Despesa.TAG_PARCIAL['id'] in filtro_informacoes_list and item.tem_pagamento_com_recursos_proprios()) or (Despesa.TAG_PARCIAL['id'] in filtro_informacoes_list and item.tem_pagamentos_em_multiplas_contas()):
        return False
    if Despesa.TAG_NAO_RECONHECIDA['id'] in filtro_informacoes_list and item.e_despesa_nao_reconhecida():
        return False
    if Despesa.TAG_SEM_COMPROVACAO_FISCAL['id'] in filtro_informacoes_list and item.e_despesa_sem_comprovacao_fiscal():
        return False
    if Despesa.TAG_CONCILIADA['id'] in filtro_informacoes_list and item.conferido:
        return False
    if Despesa.TAG_NAO_CONCILIADA['id'] in filtro_informacoes_list and not item.conferido:
        return False
    return True