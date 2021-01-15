from ..models import Associacao, Periodo, PrestacaoConta
from datetime import timedelta


def status_prestacao_conta_associacao(periodo_uuid, associacao_uuid):
    '''
    Status Período	Status Documentos PC	Status PC na DRE	Parte Período	        Parte Prestação de Contas	                    Exibe Cadeado	Cor
    Em andamento	Não gerados	            N/A	                Período em andamento.	 		                                                        1
    Em andamento	Gerados	                N/A	                Período em andamento.	Documentos gerados para prestação de contas.	            X	2
    Encerrado	    Não gerados	            Não Recebida	    Período finalizado.	    Documentos Pendentes de geração.		                        3
    Encerrado	    Gerados	                Não Recebida	    Período finalizado.	    Prestação de Contas ainda não recebida pela DRE.	        X	2
    Encerrado	    Gerados	                Recebida	        Período finalizado.	    Prestação de Contas recebida pela DRE.	                    X	4
    Encerrado	    Gerados	                Em Análise	        Período finalizado.	    Prestação de Contas em análise pela DRE.	                X	4
    Encerrado	    Gerados	                Devolvida	        Período finalizado.	    Prestação de Contas devolvida para ajustes.		                3
    Encerrado	    Gerados	                Aprovada	        Período finalizado.	    Prestação de Contas aprovada pela DRE.	                    X	5
    Encerrado	    Gerados	                Reprovada	        Período finalizado.	    Prestação de Contas reprovada pela DRE.	                    X	3
    '''
    periodo = Periodo.by_uuid(periodo_uuid)
    associacao = Associacao.by_uuid(associacao_uuid)
    prestacao = PrestacaoConta.by_periodo(associacao=associacao, periodo=periodo)

    STATUS_PRESTACAO = {
        PrestacaoConta.STATUS_NAO_APRESENTADA: 'Documentos pendentes de geração.',
        PrestacaoConta.STATUS_NAO_RECEBIDA: 'Prestação de contas ainda não recebida pela DRE.',
        PrestacaoConta.STATUS_RECEBIDA: 'Prestação de contas recebida pela DRE.',
        PrestacaoConta.STATUS_EM_ANALISE: 'Prestação de contas em análise pela DRE.',
        PrestacaoConta.STATUS_DEVOLVIDA: 'Prestação de contas devolvida para ajustes.',
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
        else:
            mensagem_prestacao = ''
            cor = LEGENDA_COR[STATUS_PERIODO_EM_ANDAMENTO]

    periodo_bloqueado = True if prestacao and prestacao.status != PrestacaoConta.STATUS_DEVOLVIDA else False

    status = {
        'periodo_encerrado': periodo.encerrado,
        'documentos_gerados': prestacao and prestacao.status not in (
            PrestacaoConta.STATUS_NAO_APRESENTADA, PrestacaoConta.STATUS_DEVOLVIDA),
        'status_prestacao': prestacao.status if prestacao else PrestacaoConta.STATUS_NAO_APRESENTADA,
        'texto_status': mensagem_periodo + ' ' + mensagem_prestacao,
        'periodo_bloqueado': periodo_bloqueado,
        'legenda_cor': cor
    }

    return status


def valida_datas_periodo(
    data_inicio_realizacao_despesas,
    data_fim_realizacao_despesas,
    periodo_anterior
):
    mensagem = "Período de realização de despesas válido."
    valido = True

    if data_inicio_realizacao_despesas > data_fim_realizacao_despesas:
        mensagem = "Data fim de realização de despesas precisa ser posterior à data de início."
        valido = False

    if periodo_anterior and data_inicio_realizacao_despesas - periodo_anterior.data_fim_realizacao_despesas != timedelta(days=1):
        mensagem = ("Data início de realização de despesas precisa ser imediatamente posterior à "
                    "data de fim do período anterior.")
        valido = False

    result = {
        "valido": valido,
        "mensagem": mensagem,
    }

    return result
