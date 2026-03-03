import pytest
from rest_framework import status
from model_bakery import baker

pytestmark = pytest.mark.django_db


def test_action_repasses_pendentes_por_periodo(jwt_authenticated_client_a, associacao, periodo, repasse):
    response = jwt_authenticated_client_a.get(
        f'/api/associacoes/{associacao.uuid}/repasses-pendentes-por-periodo/?periodo_uuid={periodo.uuid}',
        content_type='application/json')

    assert response.status_code == status.HTTP_200_OK


def test_action_repasses_pendentes_por_periodo_sem_passar_periodo(jwt_authenticated_client_a, associacao, periodo, repasse):
    response = jwt_authenticated_client_a.get(
        f'/api/associacoes/{associacao.uuid}/repasses-pendentes-por-periodo/',
        content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_action_repasses_pendentes_por_periodo_filtra_por_recurso(jwt_authenticated_client_a, associacao, periodo_factory, 
                                                                    conta_associacao, acao_associacao, recurso_factory):
    """
    Testa se os repasses são filtrados corretamente baseado no recurso do período.
    Valida que apenas repasses do recurso específico são retornados.
    """
    from datetime import date
    
    # Criar dois recursos diferentes
    recurso_1 = recurso_factory(nome='Recurso PTRF')
    recurso_2 = recurso_factory(nome='Recurso Próprio')
    
    # Criar dois períodos com recursos diferentes
    periodo_recurso_1 = periodo_factory(
        referencia='2024.1',
        data_inicio_realizacao_despesas=date(2024, 1, 1),
        data_fim_realizacao_despesas=date(2024, 6, 30),
        recurso=recurso_1
    )
    periodo_recurso_2 = periodo_factory(
        referencia='2024.2',
        data_inicio_realizacao_despesas=date(2024, 7, 1),
        data_fim_realizacao_despesas=date(2024, 12, 31),
        recurso=recurso_2
    )
    
    # Criar ação com recurso 2
    acao_recurso_2 = baker.make('Acao', nome='Ação Recurso 2', recurso=recurso_2)
    acao_associacao_recurso_2 = baker.make(
        'AcaoAssociacao',
        associacao=associacao,
        acao=acao_recurso_2
    )
    
    # Criar tipo de conta com recurso 2
    tipo_conta_recurso_2 = baker.make(
        'TipoConta',
        nome='Conta Recurso 2',
        recurso=recurso_2
    )
    conta_associacao_recurso_2 = baker.make(
        'ContaAssociacao',
        associacao=associacao,
        tipo_conta=tipo_conta_recurso_2
    )
    
    # Repasse para recurso 1 (via período)
    repasse_recurso_1 = baker.make(
        'Repasse',
        associacao=associacao,
        periodo=periodo_recurso_1,
        valor_custeio=1000.00,
        valor_capital=1000.00,
        valor_livre=0,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        status='PENDENTE'
    )
    
    # Repasse para recurso 2 (via ação e conta)
    repasse_recurso_2 = baker.make(
        'Repasse',
        associacao=associacao,
        periodo=periodo_recurso_2,
        valor_custeio=2000.00,
        valor_capital=2000.00,
        valor_livre=0,
        conta_associacao=conta_associacao_recurso_2,
        acao_associacao=acao_associacao_recurso_2,
        status='PENDENTE'
    )
    
    # Fazer requisição com período_recurso_1
    response = jwt_authenticated_client_a.get(
        f'/api/associacoes/{associacao.uuid}/repasses-pendentes-por-periodo/?periodo_uuid={periodo_recurso_1.uuid}',
        content_type='application/json')

    assert response.status_code == status.HTTP_200_OK
    
    # Deve retornar apenas o repasse do recurso_1
    assert len(response.data) == 1
    assert response.data[0]['repasse_acao'] == repasse_recurso_1.acao_associacao.acao.nome
    assert float(response.data[0]['repasse_total']) == round(
        repasse_recurso_1.valor_capital + repasse_recurso_1.valor_custeio + repasse_recurso_1.valor_livre, 2
    )


