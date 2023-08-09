import json
from datetime import timedelta

import pytest
from freezegun import freeze_time
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from sme_ptrf_apps.users.models import Grupo
from model_bakery import baker
from rest_framework import status

from sme_ptrf_apps.receitas.models import Receita, Repasse

pytestmark = pytest.mark.django_db


def test_create_receita_deve_gerar_erro_data_da_receita_maior_que_data_encerramento_associacao(
    jwt_authenticated_client_p,
    tipo_receita,
    detalhe_tipo_receita,
    acao,
    acao_associacao,
    associacao_com_data_de_encerramento,
    tipo_conta,
    conta_associacao,
    payload_receita_data_de_encerramento
):
    response = jwt_authenticated_client_p.post('/api/receitas/', data=json.dumps(payload_receita_data_de_encerramento),
                                               content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = json.loads(response.content)

    data_de_encerramento = associacao_com_data_de_encerramento.data_de_encerramento.strftime("%d/%m/%Y")
    esperado = {
        "erro_data_de_encerramento": 'True',
        "data_de_encerramento": f"{data_de_encerramento}",
        "mensagem": f"A data do crédito não pode ser posterior à {data_de_encerramento}, data de encerramento da associação."
    }

    assert result == esperado


def test_create_receita(
    jwt_authenticated_client_p,
    tipo_receita,
    detalhe_tipo_receita,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    payload_receita
):
    response = jwt_authenticated_client_p.post('/api/receitas/', data=json.dumps(payload_receita),
                                               content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert Receita.objects.filter(uuid=result["uuid"]).exists()

    receita = Receita.objects.get(uuid=result["uuid"])

    assert receita.associacao.uuid == associacao.uuid
    assert receita.detalhe_tipo_receita == detalhe_tipo_receita


def test_criar_receita_com_conta_do_tipo_invalido(
    jwt_authenticated_client_p,
    tipo_receita,
    detalhe_tipo_receita,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    conta_associacao_cartao,
    payload_receita
):
    payload_receita['conta_associacao'] = str(conta_associacao_cartao.uuid)
    response = jwt_authenticated_client_p.post('/api/receitas/', data=json.dumps(payload_receita),
                                               content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == ['O tipo de receita Estorno não permite salvar créditos com contas do tipo Cartão']


def test_create_receita_repasse(
    jwt_authenticated_client_p,
    tipo_receita,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    repasse,
    payload_receita_repasse
):
    with freeze_time('2019-11-29'):
        assert Repasse.objects.get(uuid=repasse.uuid).status == 'PENDENTE'

        response = jwt_authenticated_client_p.post('/api/receitas/', data=json.dumps(payload_receita_repasse),
                                                   content_type='application/json')

        assert response.status_code == status.HTTP_201_CREATED

        result = json.loads(response.content)

        assert Receita.objects.filter(uuid=result["uuid"]).exists()

        receita = Receita.objects.get(uuid=result["uuid"])

        assert receita.associacao.uuid == associacao.uuid

        assert receita.repasse.uuid == repasse.uuid

        assert Repasse.objects.get(uuid=repasse.uuid).status == 'PENDENTE'


def test_create_receita_estorno(
    jwt_authenticated_client_p,
    tipo_receita,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    repasse,
    payload_receita_estorno,
    rateio_no_periodo_100_custeio
):
    response = jwt_authenticated_client_p.post('/api/receitas/', data=json.dumps(payload_receita_estorno),
                                               content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert Receita.objects.filter(uuid=result["uuid"]).exists()

    receita = Receita.objects.get(uuid=result["uuid"])

    assert receita.rateio_estornado == rateio_no_periodo_100_custeio


def test_create_receita_repasse_valor_diferente(
    jwt_authenticated_client_p,
    tipo_receita,
    periodo,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    repasse,
    payload_receita_repasse
):
    with freeze_time('2019-11-29'):
        payload_receita_repasse['valor'] = 2000.67
        response = jwt_authenticated_client_p.post('/api/receitas/', data=json.dumps(payload_receita_repasse),
                                                   content_type='application/json')
        result = json.loads(response.content)

        assert result == ['Valor do payload não é igual ao valor do CAPITAL.']
        assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_tabelas(
    jwt_authenticated_client_p,
    tipo_receita,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    detalhe_tipo_receita
):
    response = jwt_authenticated_client_p.get(
        f'/api/receitas/tabelas/?associacao_uuid={associacao.uuid}', content_type='application/json')
    result = json.loads(response.content)

    """
    'periodos': [{'data_fim_realizacao_despesas': '2019-08-31',
                  'data_inicio_realizacao_despesas': '2019-01-01',
                  'referencia': '2019.1',
                  'referencia_por_extenso': '1° repasse de 2019',
                  'uuid': '8022449b-86b4-4884-a431-6dd352be5c62'}],
    """

    assert response.status_code == status.HTTP_200_OK

    assert len(result['tipos_receita']) == 1
    assert len(result['categorias_receita']) == 3
    assert len(result['acoes_associacao']) == 1
    assert len(result['contas_associacao']) == 1
    assert len(result['periodos']) == 1


def test_get_receitas(
    jwt_authenticated_client_p,
    tipo_receita,
    detalhe_tipo_receita,
    receita,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    despesa_saida_recurso
):
    response = jwt_authenticated_client_p.get(
        f'/api/receitas/?associacao_uuid={associacao.uuid}', content_type='application/json')
    result = json.loads(response.content)

    uuids_esperado = [f'{receita.uuid}']

    result_uuids = []
    for item in result:
        result_uuids.append(item['uuid'])

    assert response.status_code == status.HTTP_200_OK
    assert result_uuids == uuids_esperado


def test_update_receita_deve_gerar_erro_data_da_receita_maior_que_data_encerramento_associacao(
    jwt_authenticated_client_p,
    tipo_receita,
    detalhe_tipo_receita,
    acao,
    acao_associacao,
    associacao_com_data_de_encerramento,
    tipo_conta,
    conta_associacao,
    receita_data_de_encerramento,
    payload_receita_data_de_encerramento
):
    response = jwt_authenticated_client_p.put(f'/api/receitas/{receita_data_de_encerramento.uuid}/?associacao_uuid={associacao_com_data_de_encerramento.uuid}',
                                              data=json.dumps(payload_receita_data_de_encerramento),
                                              content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST

    result = json.loads(response.content)

    data_de_encerramento = associacao_com_data_de_encerramento.data_de_encerramento.strftime("%d/%m/%Y")
    esperado = {
        "erro_data_de_encerramento": 'True',
        "data_de_encerramento": f"{data_de_encerramento}",
        "mensagem": f"A data do crédito não pode ser posterior à {data_de_encerramento}, data de encerramento da associação."
    }

    assert result == esperado


def test_update_receita(
    jwt_authenticated_client_p,
    tipo_receita,
    detalhe_tipo_receita,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    receita,
    payload_receita
):
    response = jwt_authenticated_client_p.put(f'/api/receitas/{receita.uuid}/?associacao_uuid={associacao.uuid}',
                                              data=json.dumps(payload_receita),
                                              content_type='application/json')

    assert response.status_code == status.HTTP_200_OK

    result = json.loads(response.content)

    receita = Receita.objects.get(uuid=result["uuid"])

    assert receita.associacao.uuid == associacao.uuid
    assert receita.detalhe_tipo_receita == detalhe_tipo_receita


def test_update_receita_com_conta_invalida(
    jwt_authenticated_client_p,
    tipo_receita,
    detalhe_tipo_receita,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    receita,
    conta_associacao_cartao,
    payload_receita
):
    payload_receita['conta_associacao'] = str(conta_associacao_cartao.uuid)
    response = jwt_authenticated_client_p.put(f'/api/receitas/{receita.uuid}/?associacao_uuid={associacao.uuid}',
                                              data=json.dumps(payload_receita),
                                              content_type='application/json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == ['O tipo de receita Estorno não permite salvar créditos com contas do tipo Cartão']


def test_deleta_receita_repasse(
    jwt_authenticated_client_p,
    tipo_receita_repasse,
    acao,
    acao_associacao_role_cultural,
    associacao,
    tipo_conta_cartao,
    conta_associacao_cartao,
    receita_yyy_repasse,
    repasse_realizado
):
    assert Repasse.objects.get(uuid=repasse_realizado.uuid).status == 'REALIZADO'

    assert Receita.objects.filter(uuid=receita_yyy_repasse.uuid).exists()

    response = jwt_authenticated_client_p.delete(
        f'/api/receitas/{receita_yyy_repasse.uuid}/?associacao_uuid={associacao.uuid}',
        content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not Receita.objects.filter(uuid=receita_yyy_repasse.uuid).exists()

    assert Repasse.objects.get(uuid=repasse_realizado.uuid).status == 'PENDENTE'


def test_retrive_receitas(
    jwt_authenticated_client_p,
    receita,
    associacao,
):
    response = jwt_authenticated_client_p.get(
        f'/api/receitas/{receita.uuid}/?associacao_uuid={associacao.uuid}', content_type='application/json')
    result = json.loads(response.content)

    uuid_esperado = f'{receita.uuid}'

    assert response.status_code == status.HTTP_200_OK
    assert result['uuid'] == uuid_esperado


def test_create_receita_livre_aplicacao(
    jwt_authenticated_client_p,
    tipo_receita,
    detalhe_tipo_receita,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    payload_receita_livre_aplicacao
):
    response = jwt_authenticated_client_p.post('/api/receitas/', data=json.dumps(payload_receita_livre_aplicacao),
                                               content_type='application/json')

    assert response.status_code == status.HTTP_201_CREATED

    result = json.loads(response.content)

    assert Receita.objects.filter(uuid=result["uuid"]).exists()

    receita = Receita.objects.get(uuid=result["uuid"])

    assert receita.associacao.uuid == associacao.uuid

    assert receita.detalhe_tipo_receita == detalhe_tipo_receita


def test_create_receita_repasse_livre_aplicacao(
    jwt_authenticated_client_p,
    tipo_receita,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    repasse_2020_1_livre_aplicacao_pendente,
    payload_receita_repasse_livre_aplicacao
):
    with freeze_time('2020-03-29'):
        assert Repasse.objects.get(uuid=repasse_2020_1_livre_aplicacao_pendente.uuid).status == 'PENDENTE'

        response = jwt_authenticated_client_p.post('/api/receitas/',
                                                   data=json.dumps(payload_receita_repasse_livre_aplicacao),
                                                   content_type='application/json')

        assert response.status_code == status.HTTP_201_CREATED

        result = json.loads(response.content)

        assert Receita.objects.filter(uuid=result["uuid"]).exists()

        receita = Receita.objects.get(uuid=result["uuid"])

        assert receita.associacao.uuid == associacao.uuid

        assert receita.repasse.uuid == repasse_2020_1_livre_aplicacao_pendente.uuid

        assert Repasse.objects.get(uuid=repasse_2020_1_livre_aplicacao_pendente.uuid).status == 'REALIZADO'


@freeze_time('2020-03-29')
def test_create_receita_repasse_livre_aplicacao_valor_diferente(
    jwt_authenticated_client_p,
    tipo_receita,
    periodo,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    repasse_2020_1_livre_aplicacao_pendente,
    payload_receita_repasse_livre_aplicacao
):
    payload_receita_repasse_livre_aplicacao['valor'] = 2000.67
    response = jwt_authenticated_client_p.post('/api/receitas/',
                                               data=json.dumps(payload_receita_repasse_livre_aplicacao),
                                               content_type='application/json')
    result = json.loads(response.content)

    assert result == ['Valor do payload não é igual ao valor do LIVRE.']
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_deleta_receita_repasse_livre_aplicacao(
    jwt_authenticated_client_p,
    tipo_receita_repasse,
    acao,
    acao_associacao_role_cultural,
    associacao,
    tipo_conta_cartao,
    conta_associacao_cartao,
    receita_repasse_livre_aplicacao,
    repasse_realizado_livre_aplicacao
):
    assert Repasse.objects.get(uuid=repasse_realizado_livre_aplicacao.uuid).status == 'REALIZADO'

    assert Receita.objects.filter(uuid=receita_repasse_livre_aplicacao.uuid).exists()

    response = jwt_authenticated_client_p.delete(
        f'/api/receitas/{receita_repasse_livre_aplicacao.uuid}/?associacao_uuid={associacao.uuid}',
        content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not Receita.objects.filter(uuid=receita_repasse_livre_aplicacao.uuid).exists()

    assert Repasse.objects.get(uuid=repasse_realizado_livre_aplicacao.uuid).status == 'PENDENTE'


@pytest.fixture
def repasse_so_capital(associacao, conta_associacao, acao_associacao, periodo):
    return baker.make(
        'Repasse',
        associacao=associacao,
        periodo=periodo,
        valor_custeio=0,
        valor_capital=1000.28,
        valor_livre=0,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        status='PENDENTE'
    )


def test_create_receita_repasse_capital_com_valores_custeio_e_livre_aplicacao_zerados(
    jwt_authenticated_client_p,
    tipo_receita_repasse,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    repasse_so_capital,
):
    payload = {
        'associacao': str(associacao.uuid),
        'data': '2019-09-26',
        'valor': 1000.28,
        'categoria_receita': 'CAPITAL',
        'conta_associacao': str(conta_associacao.uuid),
        'acao_associacao': str(acao_associacao.uuid),
        'tipo_receita': tipo_receita_repasse.id,
        'repasse': str(repasse_so_capital.uuid)
    }
    with freeze_time('2019-11-29'):
        assert Repasse.objects.get(uuid=repasse_so_capital.uuid).status == 'PENDENTE'

        response = jwt_authenticated_client_p.post('/api/receitas/', data=json.dumps(payload),
                                                   content_type='application/json')

        assert response.status_code == status.HTTP_201_CREATED

        result = json.loads(response.content)

        assert Receita.objects.filter(uuid=result["uuid"]).exists()

        receita = Receita.objects.get(uuid=result["uuid"])

        assert receita.associacao.uuid == associacao.uuid

        assert receita.repasse.uuid == repasse_so_capital.uuid

        assert Repasse.objects.get(uuid=repasse_so_capital.uuid).status == 'REALIZADO'


@pytest.fixture
def repasse_so_custeio(associacao, conta_associacao, acao_associacao, periodo):
    return baker.make(
        'Repasse',
        associacao=associacao,
        periodo=periodo,
        valor_custeio=1000.28,
        valor_capital=0,
        valor_livre=0,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        status='PENDENTE'
    )


def test_create_receita_repasse_custeio_com_valores_capital_e_livre_aplicacao_zerados(
    jwt_authenticated_client_p,
    tipo_receita_repasse,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    repasse_so_custeio,
):
    payload = {
        'associacao': str(associacao.uuid),
        'data': '2019-09-26',
        'valor': 1000.28,
        'categoria_receita': 'CUSTEIO',
        'conta_associacao': str(conta_associacao.uuid),
        'acao_associacao': str(acao_associacao.uuid),
        'tipo_receita': tipo_receita_repasse.id,
        'repasse': str(repasse_so_custeio.uuid)
    }
    with freeze_time('2019-11-29'):
        assert Repasse.objects.get(uuid=repasse_so_custeio.uuid).status == 'PENDENTE'

        response = jwt_authenticated_client_p.post('/api/receitas/', data=json.dumps(payload),
                                                   content_type='application/json')

        assert response.status_code == status.HTTP_201_CREATED

        result = json.loads(response.content)

        assert Receita.objects.filter(uuid=result["uuid"]).exists()

        receita = Receita.objects.get(uuid=result["uuid"])

        assert receita.associacao.uuid == associacao.uuid

        assert receita.repasse.uuid == repasse_so_custeio.uuid

        assert Repasse.objects.get(uuid=repasse_so_custeio.uuid).status == 'REALIZADO'


@pytest.fixture
def repasse_so_livre(associacao, conta_associacao, acao_associacao, periodo):
    return baker.make(
        'Repasse',
        associacao=associacao,
        periodo=periodo,
        valor_custeio=0,
        valor_capital=0,
        valor_livre=1000.28,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        status='PENDENTE'
    )


def test_create_receita_repasse_livre_aplicacao_com_valores_capital_e_custeio(
    jwt_authenticated_client_p,
    tipo_receita_repasse,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    repasse_so_livre,
):
    payload = {
        'associacao': str(associacao.uuid),
        'data': '2019-09-26',
        'valor': 1000.28,
        'categoria_receita': 'LIVRE',
        'conta_associacao': str(conta_associacao.uuid),
        'acao_associacao': str(acao_associacao.uuid),
        'tipo_receita': tipo_receita_repasse.id,
        'repasse': str(repasse_so_livre.uuid)
    }
    with freeze_time('2019-11-29'):
        assert Repasse.objects.get(uuid=repasse_so_livre.uuid).status == 'PENDENTE'

        response = jwt_authenticated_client_p.post('/api/receitas/', data=json.dumps(payload),
                                                   content_type='application/json')

        assert response.status_code == status.HTTP_201_CREATED

        result = json.loads(response.content)

        assert Receita.objects.filter(uuid=result["uuid"]).exists()

        receita = Receita.objects.get(uuid=result["uuid"])

        assert receita.associacao.uuid == associacao.uuid

        assert receita.repasse.uuid == repasse_so_livre.uuid

        assert Repasse.objects.get(uuid=repasse_so_livre.uuid).status == 'REALIZADO'


@pytest.fixture
def repasse_teste(associacao, conta_associacao, acao_associacao, periodo):
    return baker.make(
        'Repasse',
        associacao=associacao,
        periodo=periodo,
        valor_custeio=0,
        valor_capital=0,
        valor_livre=1000.28,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        status='PENDENTE'
    )


@pytest.fixture
def receita_teste(associacao, conta_associacao, acao_associacao, tipo_receita, periodo, repasse_teste):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=periodo.data_inicio_realizacao_despesas + timedelta(days=3),
        valor=1000.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita,
        repasse=repasse_teste
    )


def test_update_receita_repasse_livre_aplicacao_com_valores_capital_e_custeio(
    jwt_authenticated_client_p,
    tipo_receita_repasse,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    repasse_teste,
    receita_teste
):
    payload = {
        'associacao': str(associacao.uuid),
        'data': '2019-09-26',
        'valor': 1000.28,
        'categoria_receita': 'LIVRE',
        'conta_associacao': str(conta_associacao.uuid),
        'acao_associacao': str(acao_associacao.uuid),
        'tipo_receita': tipo_receita_repasse.id,
        'repasse': str(repasse_teste.uuid)
    }
    with freeze_time('2019-11-29'):
        assert Repasse.objects.get(uuid=repasse_teste.uuid).status == 'PENDENTE'

        response = jwt_authenticated_client_p.put(
            f'/api/receitas/{receita_teste.uuid}/?associacao_uuid={associacao.uuid}',
            data=json.dumps(payload),
            content_type='application/json')

        assert response.status_code == status.HTTP_200_OK

        result = json.loads(response.content)

        assert Receita.objects.filter(uuid=result["uuid"]).exists()

        receita = Receita.objects.get(uuid=result["uuid"])

        assert receita.associacao.uuid == associacao.uuid

        assert Repasse.objects.get(uuid=repasse_teste.uuid).status == 'REALIZADO'
