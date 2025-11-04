import logging
from django.db import transaction

logger = logging.getLogger(__name__)


def desabilitar_acao_ptrf_paa(acao):
    """
        Quando ação for desabilitada( acao.exibir_paa = False):
        - altera Prioridades do PAA, set campo acao PTRF None
        - exclui receitas previstas do PAA para acao PTRF

        OBS: Alterações/Exclusões somente se o PAA estiver em elaboração
    """
    with transaction.atomic():

        if acao.exibir_paa:
            # Se Acao for habilitada, apenas retornar
            return acao

        # Se Acao exibir PAA for desabilitada,
        prioridades_com_acao = acao.prioridades_paa_em_elaboracao_acao_ptrf()
        count_prioridades = prioridades_com_acao.count()
        logger.info(f'{count_prioridades} prioridade(s) a ser(em) alterada(s) para acao PTRF None')

        # Limpa campo acao_associacao de todas as prioridades que utilizam a
        # respectiva acao e, desde que o PAA esteja em elaboração
        update = prioridades_com_acao.update(acao_associacao=None)
        logger.info(f'{update} prioridade(s) alterada(s) para Ação PTRF None')

        receitas_previstas_com_acao = acao.receitas_previstas_paa_em_elaboracao_acao_ptrf()
        count_receitas = receitas_previstas_com_acao.count()
        logger.info(f'{count_receitas} receita(s) a ser(em) excluída(s) do PAA')
        # remover receitas previstas do PAA para acao PTRF
        delete = receitas_previstas_com_acao.delete()
        logger.info(f'{delete} receita(s) excluída(s) do PAA')

    return acao
