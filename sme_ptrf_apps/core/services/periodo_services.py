import logging
from datetime import timedelta
from ..models import Associacao, Periodo, PrestacaoConta

def status_prestacao_conta_associacao(periodo_uuid, associacao_uuid):
    """
    Status Período	Status Documentos PC	Status PC na DRE	Parte Período	        Parte Prestação de Contas	                    Exibe Cadeado	Cor
    Em andamento	Não gerados	            N/A	                Período em andamento.	 		                                                        1
    Em andamento	Gerados	                N/A	                Período em andamento.	Documentos gerados para prestação de contas.	            X	2
    Encerrado	    Não gerados	            Não Recebida	    Período finalizado.	    Documentos Pendentes de geração.		                        3
    Encerrado	    Gerados	                Não Recebida	    Período finalizado.	    Prestação de Contas ainda não recebida pela DRE.	        X	2
    Encerrado	    Gerados	                Recebida	        Período finalizado.	    Prestação de Contas recebida pela DRE.	                    X	4
    Encerrado	    Gerados	                Em Análise	        Período finalizado.	    Prestação de Contas em análise pela DRE.	                X	4
    Encerrado	    Gerados	                Devolvida	        Período finalizado.	    Prestação de Contas devolvida para ajustes.		                3
    Encerrado	    Gerados	                Devolvida Retornada Período finalizado.	    Prestação de Contas apresentada após acertos.		            X   2
    Encerrado	    Gerados	                Devolvida Recebida  Período finalizado.	    Prestação de Contas recebida após acertos.		            X   4
    Encerrado	    Gerados	                Aprovada	        Período finalizado.	    Prestação de Contas aprovada pela DRE.	                    X	5
    Encerrado	    Gerados	                Reprovada	        Período finalizado.	    Prestação de Contas reprovada pela DRE.	                    X	3
    """

    def pc_requer_ata_retificacao(prestacao_conta):
        if not prestacao_conta:
            return False

        ultima_analise = prestacao_conta.analises_da_prestacao.filter(status='DEVOLVIDA').last()

        return ultima_analise is not None and (ultima_analise.requer_alteracao_em_lancamentos or ultima_analise.requer_informacao_devolucao_ao_tesouro)

    def pc_tem_solicitacoes_de_acerto_pendentes(prestacao_conta):
        if not prestacao_conta or prestacao_conta.status != PrestacaoConta.STATUS_DEVOLVIDA:
            return False

        ultima_analise = prestacao_conta.analises_da_prestacao.last()

        return ultima_analise is not None and ultima_analise.tem_acertos_pendentes

    def pc_requer_geracao_documentos(prestacao_conta):
        # Necessário devido a conflitos no import direto
        from sme_ptrf_apps.core.services.prestacao_contas_services import pc_requer_geracao_documentos
        return pc_requer_geracao_documentos(prestacao_conta)

    periodo = Periodo.by_uuid(periodo_uuid)
    associacao = Associacao.by_uuid(associacao_uuid)
    prestacao = PrestacaoConta.by_periodo(associacao=associacao, periodo=periodo)

    STATUS_PRESTACAO = {
        PrestacaoConta.STATUS_NAO_APRESENTADA: 'Documentos pendentes de geração.',
        PrestacaoConta.STATUS_NAO_RECEBIDA: 'Prestação de contas ainda não recebida pela DRE.',
        PrestacaoConta.STATUS_RECEBIDA: 'Prestação de contas recebida pela DRE.',
        PrestacaoConta.STATUS_EM_ANALISE: 'Prestação de contas em análise pela DRE.',
        PrestacaoConta.STATUS_DEVOLVIDA: 'Prestação de contas devolvida para ajustes.',
        PrestacaoConta.STATUS_DEVOLVIDA_RETORNADA: 'Prestação de contas apresentada após acertos.',
        PrestacaoConta.STATUS_DEVOLVIDA_RECEBIDA: 'Prestação de contas recebida após acertos.',
        PrestacaoConta.STATUS_APROVADA: 'Prestação de contas aprovada pela DRE.',
        PrestacaoConta.STATUS_APROVADA_RESSALVA: 'Prestação de contas aprovada com ressalvas pela DRE.',
        PrestacaoConta.STATUS_REPROVADA: 'Prestação de contas reprovada pela DRE.',
        PrestacaoConta.STATUS_EM_PROCESSAMENTO: 'Documentos em processamento.'
    }

    STATUS_PERIODO_EM_ANDAMENTO = 'PERIODO_EM_ANDAMENTO'
    LEGENDA_COR = {
        STATUS_PERIODO_EM_ANDAMENTO: 1,
        PrestacaoConta.STATUS_NAO_APRESENTADA: 3,
        PrestacaoConta.STATUS_NAO_RECEBIDA: 2,
        PrestacaoConta.STATUS_RECEBIDA: 4,
        PrestacaoConta.STATUS_EM_ANALISE: 4,
        PrestacaoConta.STATUS_DEVOLVIDA: 3,
        PrestacaoConta.STATUS_DEVOLVIDA_RETORNADA: 2,
        PrestacaoConta.STATUS_DEVOLVIDA_RECEBIDA: 4,
        PrestacaoConta.STATUS_APROVADA: 5,
        PrestacaoConta.STATUS_APROVADA_RESSALVA: 5,
        PrestacaoConta.STATUS_REPROVADA: 3,
        PrestacaoConta.STATUS_EM_PROCESSAMENTO: 6
    }

    mensagem_periodo = 'Período finalizado.' if periodo.encerrado else 'Período em andamento.'

    if periodo.encerrado:
        if prestacao:
            mensagem_prestacao = STATUS_PRESTACAO[prestacao.status]
            cor = LEGENDA_COR[prestacao.status]
        else:
            mensagem_prestacao = STATUS_PRESTACAO[PrestacaoConta.STATUS_NAO_APRESENTADA]
            cor = LEGENDA_COR[PrestacaoConta.STATUS_NAO_APRESENTADA]
    else:
        if prestacao and prestacao.status == PrestacaoConta.STATUS_NAO_RECEBIDA:
            mensagem_prestacao = 'Documentos gerados para prestação de contas.'
            cor = LEGENDA_COR[PrestacaoConta.STATUS_NAO_RECEBIDA]
        elif prestacao:
            mensagem_prestacao = STATUS_PRESTACAO[prestacao.status]
            cor = LEGENDA_COR[prestacao.status]
        else:
            mensagem_prestacao = ''
            cor = LEGENDA_COR[STATUS_PERIODO_EM_ANDAMENTO]

    periodo_bloqueado = True if prestacao else False

    if prestacao and prestacao.status not in (PrestacaoConta.STATUS_NAO_APRESENTADA, PrestacaoConta.STATUS_DEVOLVIDA):
        documentos_gerados = True
    elif prestacao and prestacao.status == PrestacaoConta.STATUS_DEVOLVIDA:
        documentos_gerados = not pc_requer_geracao_documentos(prestacao)
    else:
        documentos_gerados = False

    pc_requer_conclusao = not prestacao or prestacao.status in (PrestacaoConta.STATUS_NAO_APRESENTADA, PrestacaoConta.STATUS_DEVOLVIDA)

    status = {
        'periodo_encerrado': periodo.encerrado,
        'documentos_gerados': documentos_gerados,
        'pc_requer_conclusao': pc_requer_conclusao,
        'status_prestacao': prestacao.status if prestacao else PrestacaoConta.STATUS_NAO_APRESENTADA,
        'texto_status': mensagem_periodo + ' ' + mensagem_prestacao,
        'periodo_bloqueado': periodo_bloqueado,
        'legenda_cor': cor,
        'prestacao_de_contas_uuid': prestacao.uuid if prestacao and prestacao.uuid else None,
        'requer_retificacao': pc_requer_ata_retificacao(prestacao),
        'tem_acertos_pendentes': pc_tem_solicitacoes_de_acerto_pendentes(prestacao),
    }

    return status


def valida_datas_periodo(
    data_inicio_realizacao_despesas,
    data_fim_realizacao_despesas,
    periodo_anterior,
    periodo_uuid=None
):
    mensagem = "Período de realização de despesas válido."
    valido = True

    if data_fim_realizacao_despesas:
        if data_inicio_realizacao_despesas > data_fim_realizacao_despesas:
            mensagem = "Data fim de realização de despesas precisa ser posterior à data de início."
            valido = False

    if periodo_anterior:
        if periodo_anterior.data_fim_realizacao_despesas is None:
            mensagem = "Períodos abertos são podem ser selecionados como anterior à um período."
            valido = False

        elif data_inicio_realizacao_despesas - periodo_anterior.data_fim_realizacao_despesas != timedelta(days=1):
            mensagem = ("Data início de realização de despesas precisa ser imediatamente posterior à "
                        "data de fim do período anterior.")
            valido = False
    else:
        if (not periodo_uuid and Periodo.objects.exists()) or (
         periodo_uuid and Periodo.objects.exclude(uuid=periodo_uuid).exists()):
            mensagem = "Período anterior não definido só é permitido para o primeiro período cadastrado."
            valido = False
    result = {
        "valido": valido,
        "mensagem": mensagem,
    }

    return result


def periodo_aceita_alteracoes_na_associacao(periodo, associacao):
    prestacao = PrestacaoConta.by_periodo(associacao=associacao, periodo=periodo)
    periodo_bloqueado = True if prestacao and prestacao.status != PrestacaoConta.STATUS_DEVOLVIDA else False
    return not periodo_bloqueado
