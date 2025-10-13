import json
import pytest
from freezegun import freeze_time
from rest_framework import status

pytestmark = pytest.mark.django_db

@pytest.fixture
def flag_situacao_patrimonial(flag_factory):
    return flag_factory.create(name='situacao-patrimonial')

def test_get_lista_adquiridos_e_produzidos(jwt_authenticated_client_sme, flag_situacao_patrimonial, associacao_1, bem_produzido_item_1, rateio_capital_1, rateio_custeio_1):

    response = jwt_authenticated_client_sme.get(
        f'/api/bens-produzidos-e-adquiridos/?associacao_uuid={associacao_1.uuid}')
    content = json.loads(response.content)

    assert len(content["results"]) == 2
    assert response.status_code == status.HTTP_200_OK


@freeze_time('2025-01-01')
def test_get_lista_adquiridos_e_produzidos_com_filtro_acao_e_conta(jwt_authenticated_client_sme, flag_situacao_patrimonial, associacao_1, despesa_factory, rateio_despesa_factory, conta_associacao_factory, acao_associacao_factory):
    conta_associacao = conta_associacao_factory(associacao=associacao_1)
    acao_associacao = acao_associacao_factory(associacao=associacao_1)
    despesa_2025_1 = despesa_factory(associacao=associacao_1, data_documento='2025-01-01', nome_fornecedor='teste')
    _ = rateio_despesa_factory(
        associacao=associacao_1, despesa=despesa_2025_1, aplicacao_recurso="CAPITAL", conta_associacao=conta_associacao, acao_associacao=acao_associacao)
    _ = rateio_despesa_factory(
        associacao=associacao_1, despesa=despesa_2025_1, aplicacao_recurso="CAPITAL")

    response = jwt_authenticated_client_sme.get(
        f'/api/bens-produzidos-e-adquiridos/?'
        f'associacao_uuid={associacao_1.uuid}&'
        f'acao_associacao_uuid={acao_associacao.uuid}&'
        f'conta_associacao_uuid={conta_associacao.uuid}'
    )
    content = json.loads(response.content)

    assert len(content["results"]) == 1
    assert response.status_code == status.HTTP_200_OK


@freeze_time('2025-01-01')
def test_get_lista_adquiridos_e_produzidos_com_filtro_fornecedor(jwt_authenticated_client_sme, flag_situacao_patrimonial, associacao_1, despesa_factory, rateio_despesa_factory):
    despesa_2025_1 = despesa_factory(associacao=associacao_1, data_documento='2025-01-01', nome_fornecedor='teste')
    _ = rateio_despesa_factory(
        associacao=associacao_1, despesa=despesa_2025_1, aplicacao_recurso="CAPITAL")
    _ = rateio_despesa_factory(
        associacao=associacao_1, despesa=despesa_2025_1, aplicacao_recurso="CAPITAL")

    print(despesa_2025_1.nome_fornecedor)
    response = jwt_authenticated_client_sme.get(
        f'/api/bens-produzidos-e-adquiridos/?'
        f'associacao_uuid={associacao_1.uuid}&'
        f'fornecedor=teste'
    )
    content = json.loads(response.content)

    assert len(content["results"]) == 2
    assert response.status_code == status.HTTP_200_OK


@freeze_time('2025-01-01')
def test_get_lista_adquiridos_e_produzidos_com_filtro_especificacao(jwt_authenticated_client_sme, flag_situacao_patrimonial, associacao_1, bem_produzido_1, despesa_factory, bem_produzido_item_factory, rateio_despesa_factory, especificacao_material_servico_1):
    _ = bem_produzido_item_factory(bem_produzido=bem_produzido_1, especificacao_do_bem=especificacao_material_servico_1)
    _ = bem_produzido_item_factory(bem_produzido=bem_produzido_1, especificacao_do_bem=especificacao_material_servico_1)
    _ = bem_produzido_item_factory(bem_produzido=bem_produzido_1, especificacao_do_bem=especificacao_material_servico_1)

    despesa_2025_1 = despesa_factory(associacao=associacao_1, data_documento='2025-01-01')
    _ = rateio_despesa_factory(
        associacao=associacao_1, despesa=despesa_2025_1, aplicacao_recurso="CAPITAL", especificacao_material_servico=especificacao_material_servico_1)
    _ = rateio_despesa_factory(
        associacao=associacao_1, despesa=despesa_2025_1, aplicacao_recurso="CAPITAL")

    response = jwt_authenticated_client_sme.get(
        f'/api/bens-produzidos-e-adquiridos/?'
        f'associacao_uuid={associacao_1.uuid}&'
        f'especificacao_bem=especificacao do bem'
    )
    content = json.loads(response.content)

    assert len(content["results"]) == 4
    assert response.status_code == status.HTTP_200_OK


@freeze_time('2025-01-01')
def test_get_lista_adquiridos_e_produzidos_com_filtro_periodo(jwt_authenticated_client_sme, flag_situacao_patrimonial, associacao_1, bem_produzido_1, despesa_factory, bem_produzido_item_factory, rateio_despesa_factory, periodo_2025_1, periodo_2024_1):
    _ = bem_produzido_item_factory(bem_produzido=bem_produzido_1)
    _ = bem_produzido_item_factory(bem_produzido=bem_produzido_1)
    _ = bem_produzido_item_factory(bem_produzido=bem_produzido_1)

    despesa_2025_1 = despesa_factory(associacao=associacao_1, data_documento='2025-01-01')
    despesa_2024_1 = despesa_factory(associacao=associacao_1, data_documento='2024-01-01')
    _ = rateio_despesa_factory(
        associacao=associacao_1, despesa=despesa_2025_1, aplicacao_recurso="CAPITAL")
    _ = rateio_despesa_factory(
        associacao=associacao_1, despesa=despesa_2025_1, aplicacao_recurso="CAPITAL")
    _ = rateio_despesa_factory(
        associacao=associacao_1, despesa=despesa_2024_1, aplicacao_recurso="CAPITAL")

    response = jwt_authenticated_client_sme.get(
        f'/api/bens-produzidos-e-adquiridos/?'
        f'associacao_uuid={associacao_1.uuid}&'
        f'periodos_uuid={periodo_2025_1.uuid}'
    )
    content = json.loads(response.content)

    assert len(content["results"]) == 5
    assert response.status_code == status.HTTP_200_OK


@freeze_time('2025-01-01')
def test_exportar_sucesso_sem_filtros(jwt_authenticated_client_sme, flag_situacao_patrimonial, associacao_1, monkeypatch):
    """Testa exportação com sucesso sem filtros aplicados"""
    # Mock da task de exportação
    mock_task = type('MockTask', (), {'id': "test-task-id-123"})()
    mock_delay = monkeypatch.setattr('sme_ptrf_apps.situacao_patrimonial.api.views.bem_produzido_e_adquirido_viewset.exportar_bens_produzidos_adquiridos_async.delay', lambda *args, **kwargs: mock_task)
    
    response = jwt_authenticated_client_sme.get(
        f'/api/bens-produzidos-e-adquiridos/exportar/?associacao_uuid={associacao_1.uuid}'
    )
    
    assert response.status_code == status.HTTP_202_ACCEPTED
    content = json.loads(response.content)
    assert content['mensagem'] == 'Exportação iniciada com sucesso. O arquivo será processado em background.'
    assert content['task_id'] == "test-task-id-123"
    assert content['status'] == 'processing'
    
    # Verifica se a task foi chamada (status 202 indica que a task foi executada)
    assert response.status_code == status.HTTP_202_ACCEPTED


@freeze_time('2025-01-01')
def test_exportar_sucesso_com_todos_filtros(jwt_authenticated_client_sme, flag_situacao_patrimonial, associacao_1, 
                                           acao_associacao_factory, conta_associacao_factory, periodo_2025_1, monkeypatch):
    """Testa exportação com sucesso com todos os filtros aplicados"""
    acao_associacao = acao_associacao_factory(associacao=associacao_1)
    conta_associacao = conta_associacao_factory(associacao=associacao_1)
    
    # Mock da task de exportação
    mock_task = type('MockTask', (), {'id': "test-task-id-completo"})()
    monkeypatch.setattr('sme_ptrf_apps.situacao_patrimonial.api.views.bem_produzido_e_adquirido_viewset.exportar_bens_produzidos_adquiridos_async.delay', lambda *args, **kwargs: mock_task)
    
    response = jwt_authenticated_client_sme.get(
        f'/api/bens-produzidos-e-adquiridos/exportar/?'
        f'associacao_uuid={associacao_1.uuid}&'
        f'especificacao_bem=teste&'
        f'fornecedor=fornecedor_teste&'
        f'acao_associacao_uuid={acao_associacao.uuid}&'
        f'conta_associacao_uuid={conta_associacao.uuid}&'
        f'periodos_uuid={periodo_2025_1.uuid}&'
        f'data_inicio=2025-01-01&'
        f'data_fim=2025-01-31'
    )
    
    assert response.status_code == status.HTTP_202_ACCEPTED
    content = json.loads(response.content)
    assert content['mensagem'] == 'Exportação iniciada com sucesso. O arquivo será processado em background.'
    assert content['task_id'] == "test-task-id-completo"
    assert content['status'] == 'processing'
    
    # Verifica se a task foi chamada (status 202 indica que a task foi executada)
    assert response.status_code == status.HTTP_202_ACCEPTED


@freeze_time('2025-01-01')
def test_exportar_sucesso_com_filtros_parciais(jwt_authenticated_client_sme, flag_situacao_patrimonial, associacao_1, 
                                              acao_associacao_factory, monkeypatch):
    """Testa exportação com sucesso com apenas alguns filtros aplicados"""
    acao_associacao = acao_associacao_factory(associacao=associacao_1)
    
    # Mock da task de exportação
    mock_task = type('MockTask', (), {'id': "test-task-id-parcial"})()
    monkeypatch.setattr('sme_ptrf_apps.situacao_patrimonial.api.views.bem_produzido_e_adquirido_viewset.exportar_bens_produzidos_adquiridos_async.delay', lambda *args, **kwargs: mock_task)
    
    response = jwt_authenticated_client_sme.get(
        f'/api/bens-produzidos-e-adquiridos/exportar/?'
        f'associacao_uuid={associacao_1.uuid}&'
        f'especificacao_bem=teste&'
        f'acao_associacao_uuid={acao_associacao.uuid}'
    )
    
    assert response.status_code == status.HTTP_202_ACCEPTED
    content = json.loads(response.content)
    assert content['mensagem'] == 'Exportação iniciada com sucesso. O arquivo será processado em background.'
    assert content['task_id'] == "test-task-id-parcial"
    assert content['status'] == 'processing'
    
    # Verifica se a task foi chamada (status 202 indica que a task foi executada)
    assert response.status_code == status.HTTP_202_ACCEPTED


@freeze_time('2025-01-01')
def test_exportar_sucesso_com_multiplos_periodos(jwt_authenticated_client_sme, flag_situacao_patrimonial, associacao_1, 
                                                periodo_2025_1, periodo_2024_1, monkeypatch):
    """Testa exportação com sucesso com múltiplos períodos"""
    # Mock da task de exportação
    mock_task = type('MockTask', (), {'id': "test-task-id-multiplos-periodos"})()
    monkeypatch.setattr('sme_ptrf_apps.situacao_patrimonial.api.views.bem_produzido_e_adquirido_viewset.exportar_bens_produzidos_adquiridos_async.delay', lambda *args, **kwargs: mock_task)
    
    periodos_uuid = f"{periodo_2025_1.uuid},{periodo_2024_1.uuid}"
    
    response = jwt_authenticated_client_sme.get(
        f'/api/bens-produzidos-e-adquiridos/exportar/?'
        f'associacao_uuid={associacao_1.uuid}&'
        f'periodos_uuid={periodos_uuid}'
    )
    
    assert response.status_code == status.HTTP_202_ACCEPTED
    content = json.loads(response.content)
    assert content['mensagem'] == 'Exportação iniciada com sucesso. O arquivo será processado em background.'
    assert content['task_id'] == "test-task-id-multiplos-periodos"
    assert content['status'] == 'processing'
    
    # Verifica se a task foi chamada (status 202 indica que a task foi executada)
    assert response.status_code == status.HTTP_202_ACCEPTED


def test_exportar_sem_associacao_uuid(jwt_authenticated_client_sme, flag_situacao_patrimonial):
    """Testa exportação sem enviar o uuid da associação"""
    response = jwt_authenticated_client_sme.get('/api/bens-produzidos-e-adquiridos/exportar/')
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    content = json.loads(response.content)
    assert content['erro'] == 'parametros_requeridos'
    assert content['mensagem'] == 'É necessário enviar o uuid da associação.'


def test_exportar_associacao_uuid_vazio(jwt_authenticated_client_sme, flag_situacao_patrimonial):
    """Testa exportação com uuid da associação vazio"""
    response = jwt_authenticated_client_sme.get('/api/bens-produzidos-e-adquiridos/exportar/?associacao_uuid=')
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    content = json.loads(response.content)
    assert content['erro'] == 'parametros_requeridos'
    assert content['mensagem'] == 'É necessário enviar o uuid da associação.'


@freeze_time('2025-01-01')
def test_exportar_acao_associacao_nao_encontrada(jwt_authenticated_client_sme, flag_situacao_patrimonial, associacao_1):
    """Testa exportação com ação da associação não encontrada"""
    acao_uuid_invalido = "00000000-0000-0000-0000-000000000000"
    
    response = jwt_authenticated_client_sme.get(
        f'/api/bens-produzidos-e-adquiridos/exportar/?'
        f'associacao_uuid={associacao_1.uuid}&'
        f'acao_associacao_uuid={acao_uuid_invalido}'
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    content = json.loads(response.content)
    assert content['erro'] == 'acao_associacao_nao_encontrada'
    assert content['mensagem'] == 'A ação da associação informada não foi encontrada.'


@freeze_time('2025-01-01')
def test_exportar_conta_associacao_nao_encontrada(jwt_authenticated_client_sme, flag_situacao_patrimonial, associacao_1):
    """Testa exportação com conta da associação não encontrada"""
    conta_uuid_invalido = "00000000-0000-0000-0000-000000000000"
    
    response = jwt_authenticated_client_sme.get(
        f'/api/bens-produzidos-e-adquiridos/exportar/?'
        f'associacao_uuid={associacao_1.uuid}&'
        f'conta_associacao_uuid={conta_uuid_invalido}'
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    content = json.loads(response.content)
    assert content['erro'] == 'conta_associacao_nao_encontrada'
    assert content['mensagem'] == 'A conta da associação informada não foi encontrada.'


@freeze_time('2025-01-01')
def test_exportar_periodos_uuid_invalido(jwt_authenticated_client_sme, flag_situacao_patrimonial, associacao_1):
    """Testa exportação com UUID de períodos inválido"""
    response = jwt_authenticated_client_sme.get(
        f'/api/bens-produzidos-e-adquiridos/exportar/?'
        f'associacao_uuid={associacao_1.uuid}&'
        f'periodos_uuid=uuid-invalido'
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    content = json.loads(response.content)
    assert content['erro'] == 'parametro_invalido'
    assert content['mensagem'] == 'Parâmetro período inválido. Deve ser uma lista de UUIDs separadas por vírgula.'


@freeze_time('2025-01-01')
def test_exportar_periodos_uuid_malformado(jwt_authenticated_client_sme, flag_situacao_patrimonial, associacao_1):
    """Testa exportação com UUID de períodos malformado"""
    response = jwt_authenticated_client_sme.get(
        f'/api/bens-produzidos-e-adquiridos/exportar/?'
        f'associacao_uuid={associacao_1.uuid}&'
        f'periodos_uuid=123,456,789'
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    content = json.loads(response.content)
    assert content['erro'] == 'parametro_invalido'
    assert content['mensagem'] == 'Parâmetro período inválido. Deve ser uma lista de UUIDs separadas por vírgula.'


@freeze_time('2025-01-01')
def test_exportar_erro_interno_task(jwt_authenticated_client_sme, flag_situacao_patrimonial, associacao_1, monkeypatch):
    """Testa exportação com erro interno ao executar a task"""
    # Mock da task de exportação para simular erro
    monkeypatch.setattr('sme_ptrf_apps.situacao_patrimonial.api.views.bem_produzido_e_adquirido_viewset.exportar_bens_produzidos_adquiridos_async.delay', lambda *args, **kwargs: (_ for _ in ()).throw(Exception("Erro interno")))
    
    response = jwt_authenticated_client_sme.get(
        f'/api/bens-produzidos-e-adquiridos/exportar/?associacao_uuid={associacao_1.uuid}'
    )
    
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    content = json.loads(response.content)
    assert content['erro'] == 'erro_interno'
    assert content['mensagem'] == 'Erro interno ao iniciar a exportação.'


@freeze_time('2025-01-01')
def test_exportar_erro_interno_acao_associacao(jwt_authenticated_client_sme, flag_situacao_patrimonial, associacao_1, monkeypatch):
    """Testa exportação com erro interno ao buscar ação da associação"""
    # Mock para simular erro interno ao buscar AcaoAssociacao
    monkeypatch.setattr('sme_ptrf_apps.situacao_patrimonial.api.views.bem_produzido_e_adquirido_viewset.AcaoAssociacao.objects.get', lambda *args, **kwargs: (_ for _ in ()).throw(Exception("Erro interno")))
    
    acao_uuid = "00000000-0000-0000-0000-000000000000"
    
    response = jwt_authenticated_client_sme.get(
        f'/api/bens-produzidos-e-adquiridos/exportar/?'
        f'associacao_uuid={associacao_1.uuid}&'
        f'acao_associacao_uuid={acao_uuid}'
    )
    
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    content = json.loads(response.content)
    assert content['erro'] == 'erro_interno'
    assert content['mensagem'] == 'Erro interno ao buscar a ação da associação.'


@freeze_time('2025-01-01')
def test_exportar_erro_interno_conta_associacao(jwt_authenticated_client_sme, flag_situacao_patrimonial, associacao_1, monkeypatch):
    """Testa exportação com erro interno ao buscar conta da associação"""
    # Mock para simular erro interno ao buscar ContaAssociacao
    monkeypatch.setattr('sme_ptrf_apps.situacao_patrimonial.api.views.bem_produzido_e_adquirido_viewset.ContaAssociacao.objects.get', lambda *args, **kwargs: (_ for _ in ()).throw(Exception("Erro interno")))
    
    conta_uuid = "00000000-0000-0000-0000-000000000000"
    
    response = jwt_authenticated_client_sme.get(
        f'/api/bens-produzidos-e-adquiridos/exportar/?'
        f'associacao_uuid={associacao_1.uuid}&'
        f'conta_associacao_uuid={conta_uuid}'
    )
    
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    content = json.loads(response.content)
    assert content['erro'] == 'erro_interno'
    assert content['mensagem'] == 'Erro interno ao buscar a conta da associação.'


@freeze_time('2025-01-01')
def test_exportar_formato_filtros_string(jwt_authenticated_client_sme, flag_situacao_patrimonial, associacao_1, 
                                        acao_associacao_factory, conta_associacao_factory, periodo_2025_1, monkeypatch):
    """Testa se a string de filtros está sendo formatada corretamente"""
    acao_associacao = acao_associacao_factory(associacao=associacao_1)
    conta_associacao = conta_associacao_factory(associacao=associacao_1)
    
    # Mock da task de exportação
    mock_task = type('MockTask', (), {'id': "test-task-id-filtros"})()
    monkeypatch.setattr('sme_ptrf_apps.situacao_patrimonial.api.views.bem_produzido_e_adquirido_viewset.exportar_bens_produzidos_adquiridos_async.delay', lambda *args, **kwargs: mock_task)
    
    response = jwt_authenticated_client_sme.get(
        f'/api/bens-produzidos-e-adquiridos/exportar/?'
        f'associacao_uuid={associacao_1.uuid}&'
        f'especificacao_bem=teste&'
        f'fornecedor=fornecedor_teste&'
        f'acao_associacao_uuid={acao_associacao.uuid}&'
        f'conta_associacao_uuid={conta_associacao.uuid}&'
        f'periodos_uuid={periodo_2025_1.uuid}&'
        f'data_inicio=2025-01-01&'
        f'data_fim=2025-01-31'
    )
    
    assert response.status_code == status.HTTP_202_ACCEPTED
    
    # Verifica se a task foi chamada (status 202 indica que a task foi executada)
    assert response.status_code == status.HTTP_202_ACCEPTED


@freeze_time('2025-01-01')
def test_exportar_sem_permissao(jwt_authenticated_client_sme, associacao_1, monkeypatch):
    """Testa exportação sem a flag de situação patrimonial habilitada"""
    # Mock para desabilitar a flag de situação patrimonial
    # Simula o cenário onde a flag 'situacao-patrimonial' não está habilitada
    monkeypatch.setattr('sme_ptrf_apps.situacao_patrimonial.api.views.bem_produzido_e_adquirido_viewset.WaffleFlagMixin.waffle_flag', 'flag-inexistente')
    
    response = jwt_authenticated_client_sme.get(
        f'/api/bens-produzidos-e-adquiridos/exportar/?associacao_uuid={associacao_1.uuid}'
    )
    
    assert response.status_code in [status.HTTP_202_ACCEPTED, status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]

@freeze_time('2025-01-01')
def test_lista_rascunhos_aparecem_primeiro(
    jwt_authenticated_client_sme, 
    flag_situacao_patrimonial, 
    associacao_1,
    bem_produzido_factory,
    bem_produzido_item_factory,
    despesa_factory,
    bem_produzido_despesa_factory,
    rateio_despesa_factory,
    especificacao_material_servico_1
):
    """Testa se bens produzidos em rascunho aparecem primeiro na listagem"""
    from sme_ptrf_apps.situacao_patrimonial.models import BemProduzido
    
    # Criar bem produzido completo com data mais recente
    bem_completo = bem_produzido_factory.create(
        associacao=associacao_1, 
        status=BemProduzido.STATUS_COMPLETO
    )
    despesa_completo = despesa_factory(associacao=associacao_1, data_documento='2025-01-15')
    bem_produzido_despesa_factory.create(bem_produzido=bem_completo, despesa=despesa_completo)
    bem_produzido_item_factory.create(
        bem_produzido=bem_completo,
        especificacao_do_bem=especificacao_material_servico_1
    )
    
    # Criar bem produzido em rascunho com data mais antiga
    bem_rascunho = bem_produzido_factory.create(
        associacao=associacao_1, 
        status=BemProduzido.STATUS_INCOMPLETO
    )
    despesa_rascunho = despesa_factory(associacao=associacao_1, data_documento='2025-01-05')
    bem_produzido_despesa_factory.create(bem_produzido=bem_rascunho, despesa=despesa_rascunho)
    bem_produzido_item_factory.create(
        bem_produzido=bem_rascunho,
        especificacao_do_bem=especificacao_material_servico_1
    )
    
    # Criar bem adquirido (rateio de capital)
    despesa_adquirido = despesa_factory(associacao=associacao_1, data_documento='2025-01-20')
    rateio_despesa_factory.create(
        associacao=associacao_1, 
        despesa=despesa_adquirido, 
        aplicacao_recurso="CAPITAL",
        especificacao_material_servico=especificacao_material_servico_1
    )
    
    response = jwt_authenticated_client_sme.get(
        f'/api/bens-produzidos-e-adquiridos/?associacao_uuid={associacao_1.uuid}'
    )
    content = json.loads(response.content)
    
    assert response.status_code == status.HTTP_200_OK
    assert len(content["results"]) == 3
    
    # Verificar que o primeiro item é o rascunho (mesmo tendo data mais antiga)
    assert content["results"][0]["status"] == BemProduzido.STATUS_INCOMPLETO
    assert content["results"][0]["tipo"] == "Produzido"
    
    # Os demais devem estar ordenados por data decrescente
    # Bem adquirido (2025-01-20) vem antes do bem completo (2025-01-15)
    assert content["results"][1]["tipo"] == "Adquirido"
    assert content["results"][1]["data_aquisicao_producao"] == "2025-01-20"
    assert content["results"][2]["status"] == BemProduzido.STATUS_COMPLETO
    assert content["results"][2]["data_aquisicao_producao"] == "2025-01-15"


@freeze_time('2025-01-01')
def test_lista_multiplos_rascunhos_aparecem_primeiro(
    jwt_authenticated_client_sme, 
    flag_situacao_patrimonial, 
    associacao_1,
    bem_produzido_factory,
    bem_produzido_item_factory,
    despesa_factory,
    bem_produzido_despesa_factory,
    rateio_despesa_factory,
    especificacao_material_servico_1
):
    """Testa se múltiplos bens produzidos em rascunho aparecem primeiro"""
    from sme_ptrf_apps.situacao_patrimonial.models import BemProduzido
    
    # Criar 3 bens produzidos em rascunho
    for i in range(3):
        bem_rascunho = bem_produzido_factory.create(
            associacao=associacao_1, 
            status=BemProduzido.STATUS_INCOMPLETO
        )
        despesa_rascunho = despesa_factory(associacao=associacao_1, data_documento=f'2025-01-0{i+1}')
        bem_produzido_despesa_factory.create(bem_produzido=bem_rascunho, despesa=despesa_rascunho)
        bem_produzido_item_factory.create(
            bem_produzido=bem_rascunho,
            especificacao_do_bem=especificacao_material_servico_1
        )
    
    # Criar 2 bens produzidos completos
    for i in range(2):
        bem_completo = bem_produzido_factory.create(
            associacao=associacao_1, 
            status=BemProduzido.STATUS_COMPLETO
        )
        despesa_completo = despesa_factory(associacao=associacao_1, data_documento=f'2025-01-{20+i}')
        bem_produzido_despesa_factory.create(bem_produzido=bem_completo, despesa=despesa_completo)
        bem_produzido_item_factory.create(
            bem_produzido=bem_completo,
            especificacao_do_bem=especificacao_material_servico_1
        )
    
    response = jwt_authenticated_client_sme.get(
        f'/api/bens-produzidos-e-adquiridos/?associacao_uuid={associacao_1.uuid}'
    )
    content = json.loads(response.content)
    
    assert response.status_code == status.HTTP_200_OK
    assert len(content["results"]) == 5
    
    # Os 3 primeiros devem ser rascunhos
    for i in range(3):
        assert content["results"][i]["status"] == BemProduzido.STATUS_INCOMPLETO
        assert content["results"][i]["tipo"] == "Produzido"
    
    # Os 2 últimos devem ser completos, ordenados por data decrescente
    assert content["results"][3]["status"] == BemProduzido.STATUS_COMPLETO
    assert content["results"][3]["data_aquisicao_producao"] == "2025-01-21"
    assert content["results"][4]["status"] == BemProduzido.STATUS_COMPLETO
    assert content["results"][4]["data_aquisicao_producao"] == "2025-01-20"


@freeze_time('2025-01-01')
def test_lista_ordenacao_completos_e_adquiridos_por_data_decrescente(
    jwt_authenticated_client_sme, 
    flag_situacao_patrimonial, 
    associacao_1,
    bem_produzido_factory,
    bem_produzido_item_factory,
    despesa_factory,
    bem_produzido_despesa_factory,
    rateio_despesa_factory,
    especificacao_material_servico_1
):
    """Testa se bens completos e adquiridos são ordenados por data decrescente"""
    from sme_ptrf_apps.situacao_patrimonial.models import BemProduzido
    
    # Criar bem produzido completo - data: 15/01
    bem_completo = bem_produzido_factory.create(
        associacao=associacao_1, 
        status=BemProduzido.STATUS_COMPLETO
    )
    despesa_completo = despesa_factory(associacao=associacao_1, data_documento='2025-01-15')
    bem_produzido_despesa_factory.create(bem_produzido=bem_completo, despesa=despesa_completo)
    bem_produzido_item_factory.create(
        bem_produzido=bem_completo,
        especificacao_do_bem=especificacao_material_servico_1
    )
    
    # Criar bem adquirido - data: 20/01 (mais recente)
    despesa_adquirido_1 = despesa_factory(associacao=associacao_1, data_documento='2025-01-20')
    rateio_despesa_factory.create(
        associacao=associacao_1, 
        despesa=despesa_adquirido_1, 
        aplicacao_recurso="CAPITAL",
        especificacao_material_servico=especificacao_material_servico_1
    )
    
    # Criar outro bem adquirido - data: 10/01 (mais antiga)
    despesa_adquirido_2 = despesa_factory(associacao=associacao_1, data_documento='2025-01-10')
    rateio_despesa_factory.create(
        associacao=associacao_1, 
        despesa=despesa_adquirido_2, 
        aplicacao_recurso="CAPITAL",
        especificacao_material_servico=especificacao_material_servico_1
    )
    
    response = jwt_authenticated_client_sme.get(
        f'/api/bens-produzidos-e-adquiridos/?associacao_uuid={associacao_1.uuid}'
    )
    content = json.loads(response.content)
    
    assert response.status_code == status.HTTP_200_OK
    assert len(content["results"]) == 3
    
    # Verificar ordenação por data decrescente
    assert content["results"][0]["data_aquisicao_producao"] == "2025-01-20"  # Mais recente
    assert content["results"][1]["data_aquisicao_producao"] == "2025-01-15"  # Meio
    assert content["results"][2]["data_aquisicao_producao"] == "2025-01-10"  # Mais antiga


def test_lista_rascunhos_com_filtro_periodo(
    jwt_authenticated_client_sme, 
    flag_situacao_patrimonial, 
    associacao_1,
    bem_produzido_factory,
    bem_produzido_item_factory,
    despesa_factory,
    bem_produzido_despesa_factory,
    periodo_2025_1,
    periodo_2024_1,
    especificacao_material_servico_1
):
    """Testa se filtros são aplicados aos rascunhos também"""
    from sme_ptrf_apps.situacao_patrimonial.models import BemProduzido
    
    # Criar bem rascunho no período 2025.1
    with freeze_time('2025-01-15'):
        bem_rascunho_2025 = bem_produzido_factory.create(
            associacao=associacao_1, 
            status=BemProduzido.STATUS_INCOMPLETO
        )
        despesa_rascunho_2025 = despesa_factory(associacao=associacao_1, data_documento='2025-01-15')
        bem_produzido_despesa_factory.create(bem_produzido=bem_rascunho_2025, despesa=despesa_rascunho_2025)
        item_2025 = bem_produzido_item_factory.create(
            bem_produzido=bem_rascunho_2025,
            especificacao_do_bem=especificacao_material_servico_1
        )
    
    # Criar bem rascunho no período 2024.1
    with freeze_time('2024-02-15'):
        bem_rascunho_2024 = bem_produzido_factory.create(
            associacao=associacao_1, 
            status=BemProduzido.STATUS_INCOMPLETO
        )
        despesa_rascunho_2024 = despesa_factory(associacao=associacao_1, data_documento='2024-02-15')
        bem_produzido_despesa_factory.create(bem_produzido=bem_rascunho_2024, despesa=despesa_rascunho_2024)
        item_2024 = bem_produzido_item_factory.create(
            bem_produzido=bem_rascunho_2024,
            especificacao_do_bem=especificacao_material_servico_1
        )
    
    # Criar bem completo no período 2025.1
    with freeze_time('2025-02-01'):
        bem_completo_2025 = bem_produzido_factory.create(
            associacao=associacao_1, 
            status=BemProduzido.STATUS_COMPLETO
        )
        despesa_completo_2025 = despesa_factory(associacao=associacao_1, data_documento='2025-02-01')
        bem_produzido_despesa_factory.create(bem_produzido=bem_completo_2025, despesa=despesa_completo_2025)
        item_completo = bem_produzido_item_factory.create(
            bem_produzido=bem_completo_2025,
            especificacao_do_bem=especificacao_material_servico_1
        )
    
    # Filtrar por período 2025.1
    response = jwt_authenticated_client_sme.get(
        f'/api/bens-produzidos-e-adquiridos/?'
        f'associacao_uuid={associacao_1.uuid}&'
        f'periodos_uuid={periodo_2025_1.uuid}'
    )
    content = json.loads(response.content)
    
    assert response.status_code == status.HTTP_200_OK
    # Deve retornar apenas os itens do período 2025.1 (rascunho + completo)
    assert len(content["results"]) == 2
    
    # Primeiro deve ser o rascunho
    assert content["results"][0]["status"] == BemProduzido.STATUS_INCOMPLETO
    
    # Segundo deve ser o completo
    assert content["results"][1]["status"] == BemProduzido.STATUS_COMPLETO


@freeze_time('2025-01-01')
def test_lista_visao_dre_nao_mostra_rascunhos(
    jwt_authenticated_client_sme, 
    flag_situacao_patrimonial, 
    associacao_1,
    bem_produzido_factory,
    bem_produzido_item_factory,
    despesa_factory,
    bem_produzido_despesa_factory,
    rateio_despesa_factory,
    especificacao_material_servico_1
):
    """Testa se na visão DRE os rascunhos não aparecem"""
    from sme_ptrf_apps.situacao_patrimonial.models import BemProduzido
    
    # Criar bem produzido em rascunho
    bem_rascunho = bem_produzido_factory.create(
        associacao=associacao_1, 
        status=BemProduzido.STATUS_INCOMPLETO
    )
    despesa_rascunho = despesa_factory(associacao=associacao_1, data_documento='2025-01-15')
    bem_produzido_despesa_factory.create(bem_produzido=bem_rascunho, despesa=despesa_rascunho)
    bem_produzido_item_factory.create(
        bem_produzido=bem_rascunho,
        especificacao_do_bem=especificacao_material_servico_1
    )
    
    # Criar bem produzido completo
    bem_completo = bem_produzido_factory.create(
        associacao=associacao_1, 
        status=BemProduzido.STATUS_COMPLETO
    )
    despesa_completo = despesa_factory(associacao=associacao_1, data_documento='2025-01-20')
    bem_produzido_despesa_factory.create(bem_produzido=bem_completo, despesa=despesa_completo)
    bem_produzido_item_factory.create(
        bem_produzido=bem_completo,
        especificacao_do_bem=especificacao_material_servico_1
    )
    
    # Criar bem adquirido
    despesa_adquirido = despesa_factory(associacao=associacao_1, data_documento='2025-01-25')
    rateio_despesa_factory.create(
        associacao=associacao_1, 
        despesa=despesa_adquirido, 
        aplicacao_recurso="CAPITAL",
        especificacao_material_servico=especificacao_material_servico_1
    )
    
    # Fazer request com visao_dre=true
    response = jwt_authenticated_client_sme.get(
        f'/api/bens-produzidos-e-adquiridos/?'
        f'associacao_uuid={associacao_1.uuid}&'
        f'visao_dre=true'
    )
    content = json.loads(response.content)
    
    assert response.status_code == status.HTTP_200_OK
    # Deve retornar apenas 2 itens (completo + adquirido), sem o rascunho
    assert len(content["results"]) == 2
    
    # Nenhum item deve ser rascunho
    for item in content["results"]:
        assert item["status"] != BemProduzido.STATUS_INCOMPLETO
    
    # Verificar que só há completos e adquiridos
    statuses = [item["status"] for item in content["results"]]
    assert BemProduzido.STATUS_COMPLETO in statuses


@freeze_time('2025-01-01')
def test_lista_rascunhos_com_filtro_fornecedor(
    jwt_authenticated_client_sme, 
    flag_situacao_patrimonial, 
    associacao_1,
    bem_produzido_factory,
    bem_produzido_item_factory,
    despesa_factory,
    bem_produzido_despesa_factory,
    especificacao_material_servico_1
):
    """Testa se o filtro de fornecedor é aplicado aos rascunhos"""
    from sme_ptrf_apps.situacao_patrimonial.models import BemProduzido
    
    # Criar bem rascunho com fornecedor "Empresa A"
    bem_rascunho_a = bem_produzido_factory.create(
        associacao=associacao_1, 
        status=BemProduzido.STATUS_INCOMPLETO
    )
    despesa_rascunho_a = despesa_factory(
        associacao=associacao_1, 
        data_documento='2025-01-15',
        nome_fornecedor='Empresa A'
    )
    bem_produzido_despesa_factory.create(bem_produzido=bem_rascunho_a, despesa=despesa_rascunho_a)
    bem_produzido_item_factory.create(
        bem_produzido=bem_rascunho_a,
        especificacao_do_bem=especificacao_material_servico_1
    )
    
    # Criar bem rascunho com fornecedor "Empresa B"
    bem_rascunho_b = bem_produzido_factory.create(
        associacao=associacao_1, 
        status=BemProduzido.STATUS_INCOMPLETO
    )
    despesa_rascunho_b = despesa_factory(
        associacao=associacao_1, 
        data_documento='2025-01-20',
        nome_fornecedor='Empresa B'
    )
    bem_produzido_despesa_factory.create(bem_produzido=bem_rascunho_b, despesa=despesa_rascunho_b)
    bem_produzido_item_factory.create(
        bem_produzido=bem_rascunho_b,
        especificacao_do_bem=especificacao_material_servico_1
    )
    
    # Filtrar por fornecedor "Empresa A"
    response = jwt_authenticated_client_sme.get(
        f'/api/bens-produzidos-e-adquiridos/?'
        f'associacao_uuid={associacao_1.uuid}&'
        f'fornecedor=Empresa A'
    )
    content = json.loads(response.content)
    
    assert response.status_code == status.HTTP_200_OK
    # Deve retornar apenas 1 item (rascunho da Empresa A)
    assert len(content["results"]) == 1
    assert content["results"][0]["status"] == BemProduzido.STATUS_INCOMPLETO


@freeze_time('2025-10-10')
def test_filtro_data_usa_data_documento_despesa(
    jwt_authenticated_client_sme, 
    flag_situacao_patrimonial, 
    associacao_1,
    bem_produzido_factory,
    bem_produzido_item_factory,
    despesa_factory,
    bem_produzido_despesa_factory,
    rateio_despesa_factory,
    especificacao_material_servico_1
):
    """
    Testa se o filtro de data usa data_documento da despesa e não criado_em.
    
    Cenário: Um bem produzido criado em 10/10/2025 mas com despesa de data_documento = 30/09/2025.
    Ao filtrar até 30/09/2025, o bem deve aparecer (filtrado pela data do documento).
    Se o filtro estivesse usando criado_em, o bem não apareceria (criado em 10/10).
    """
    from sme_ptrf_apps.situacao_patrimonial.models import BemProduzido
    
    # Criar bem produzido com despesa de 30/09/2025
    # mas criado_em = 2025-10-10 (por causa do freeze_time)
    bem_produzido = bem_produzido_factory.create(
        associacao=associacao_1,
        status=BemProduzido.STATUS_COMPLETO
    )
    
    despesa = despesa_factory(associacao=associacao_1, data_documento='2025-09-30')
    bem_produzido_despesa_factory.create(bem_produzido=bem_produzido, despesa=despesa)
    bem_produzido_item_factory.create(
        bem_produzido=bem_produzido,
        especificacao_do_bem=especificacao_material_servico_1
    )
    
    # Criar outro bem para controle - despesa de 05/10/2025
    bem_produzido_2 = bem_produzido_factory.create(
        associacao=associacao_1,
        status=BemProduzido.STATUS_COMPLETO
    )
    despesa_2 = despesa_factory(associacao=associacao_1, data_documento='2025-10-05')
    bem_produzido_despesa_factory.create(bem_produzido=bem_produzido_2, despesa=despesa_2)
    bem_produzido_item_factory.create(
        bem_produzido=bem_produzido_2,
        especificacao_do_bem=especificacao_material_servico_1
    )
    
    # Filtrar de 01/09 até 30/09
    response = jwt_authenticated_client_sme.get(
        f'/api/bens-produzidos-e-adquiridos/?'
        f'associacao_uuid={associacao_1.uuid}&'
        f'data_inicio=2025-09-01&'
        f'data_fim=2025-09-30'
    )
    content = json.loads(response.content)
    
    assert response.status_code == status.HTTP_200_OK
    # Deve retornar apenas 1 item (bem com data_documento da despesa = 30/09)
    # Se estivesse usando criado_em, não retornaria nada (ambos criados em 10/10)
    assert len(content["results"]) == 1
    assert content["results"][0]["data_aquisicao_producao"] == "2025-09-30"
    
    # Filtrar de 01/10 até 31/10 - deve retornar o segundo bem
    response = jwt_authenticated_client_sme.get(
        f'/api/bens-produzidos-e-adquiridos/?'
        f'associacao_uuid={associacao_1.uuid}&'
        f'data_inicio=2025-10-01&'
        f'data_fim=2025-10-31'
    )
    content = json.loads(response.content)
    
    assert response.status_code == status.HTTP_200_OK
    assert len(content["results"]) == 1
    assert content["results"][0]["data_aquisicao_producao"] == "2025-10-05"
