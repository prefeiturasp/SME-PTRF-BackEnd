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

    esperado = {
        'tipos_receita': [
            {
                'id': tipo_receita.id,
                'nome': tipo_receita.nome,
                'aceita_capital': tipo_receita.aceita_capital,
                'aceita_custeio': tipo_receita.aceita_custeio,
                'aceita_livre': tipo_receita.aceita_livre,
                'e_repasse': tipo_receita.e_repasse,
                'e_devolucao': False,
                'e_recursos_proprios': False,
                'e_estorno': False,
                'mensagem_usuario': tipo_receita.mensagem_usuario,
                'possui_detalhamento': tipo_receita.possui_detalhamento,
                'tipos_conta': [{
                    'uuid': f'{tipo_conta.uuid}',
                    'id': tipo_conta.id,
                    'nome': tipo_conta.nome,
                    'apenas_leitura': False
                }],
                'detalhes_tipo_receita': [
                    {
                        'id': detalhe_tipo_receita.id,
                        'nome': detalhe_tipo_receita.nome
                    },
                ]
            },
        ],
        "categorias_receita": [
            {
                "id": "CAPITAL",
                "nome": "Capital"
            },
            {
                "id": "CUSTEIO",
                "nome": "Custeio"
            },
            {
                "id": "LIVRE",
                "nome": "Livre Aplicação"
            }
        ],
        'acoes_associacao': [
            {
                'uuid': f'{acao_associacao.uuid}',
                'id': acao_associacao.id,
                'nome': acao_associacao.acao.nome,
                'e_recursos_proprios': False,
                'acao': {
                    'id': acao_associacao.acao.id,
                    'uuid': f'{acao_associacao.acao.uuid}',
                    'nome': acao_associacao.acao.nome,
                    'e_recursos_proprios': False,
                    'posicao_nas_pesquisas': acao_associacao.acao.posicao_nas_pesquisas,
                    'aceita_capital': acao_associacao.acao.aceita_capital,
                    'aceita_custeio': acao_associacao.acao.aceita_custeio,
                    'aceita_livre': acao_associacao.acao.aceita_livre
                }
            },
        ],

        'contas_associacao': [
            {
                'uuid': f'{conta_associacao.uuid}',
                'nome': conta_associacao.tipo_conta.nome
            },
        ],

        'periodos': [
            {'data_fim_realizacao_despesas': '2019-08-31',
             'data_inicio_realizacao_despesas': '2019-01-01',
             'referencia': '2019.1',
             'referencia_por_extenso': '1° repasse de 2019',
             'uuid': str(associacao.periodo_inicial.uuid)
             }
        ]
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


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

    results = [
        {
            'uuid': str(receita.uuid),
            'data': '2020-03-26',
            'valor': '100.00',
            'repasse': None,
            'saida_do_recurso':
                {
                    'associacao': str(despesa_saida_recurso.associacao.uuid),
                    'cpf_cnpj_fornecedor': '11.478.276/0001-04',
                    'data_documento': '2019-09-10',
                    'data_transacao': '2019-09-10',
                    'documento_transacao': '',
                    'nome_fornecedor': 'Fornecedor SA',
                    'numero_documento': '123456',
                    'tipo_documento': {
                        'id': despesa_saida_recurso.tipo_documento.id,
                        'nome': despesa_saida_recurso.tipo_documento.nome
                    },
                    'tipo_transacao': {
                        'id': despesa_saida_recurso.tipo_transacao.id,
                        'nome': despesa_saida_recurso.tipo_transacao.nome,
                        'tem_documento': despesa_saida_recurso.tipo_transacao.tem_documento
                    },
                    'uuid': str(despesa_saida_recurso.uuid),
                    'valor_ptrf': 100.0,
                    'valor_total': '100.00'
                },
            'tipo_receita': {
                'id': tipo_receita.id,
                'nome': tipo_receita.nome,
                'e_repasse': tipo_receita.e_repasse,
                'aceita_capital': tipo_receita.aceita_capital,
                'aceita_custeio': tipo_receita.aceita_custeio,
                'aceita_livre': tipo_receita.aceita_livre,
                'e_devolucao': False,
                'e_recursos_proprios': False
            },
            'referencia_devolucao': None,
            "acao_associacao": {
                "uuid": str(acao_associacao.uuid),
                "id": acao_associacao.id,
                "nome": acao_associacao.acao.nome,
                'e_recursos_proprios': False,
                'acao': {
                    'id': acao_associacao.acao.id,
                    'uuid': f'{acao_associacao.acao.uuid}',
                    'nome': acao_associacao.acao.nome,
                    'e_recursos_proprios': False,
                    'posicao_nas_pesquisas': acao_associacao.acao.posicao_nas_pesquisas,
                    'aceita_capital': acao_associacao.acao.aceita_capital,
                    'aceita_custeio': acao_associacao.acao.aceita_custeio,
                    'aceita_livre': acao_associacao.acao.aceita_livre
                }
            },
            'conta_associacao': {
                "uuid": str(conta_associacao.uuid),
                "nome": conta_associacao.tipo_conta.nome
            },
            'conferido': True,
            'categoria_receita': receita.categoria_receita,
            'detalhe_tipo_receita': {
                'id': detalhe_tipo_receita.id,
                'nome': detalhe_tipo_receita.nome
            },
            'detalhe_outros': receita.detalhe_outros,
            'notificar_dias_nao_conferido': 0,
            'rateio_estornado': None,
        },
    ]

    esperado = results

    assert response.status_code == status.HTTP_200_OK
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


def test_deleta_receita(
    jwt_authenticated_client_p,
    tipo_receita,
    acao,
    acao_associacao,
    associacao,
    tipo_conta,
    conta_associacao,
    receita,
    payload_receita):
    assert Receita.objects.filter(uuid=receita.uuid).exists()

    response = jwt_authenticated_client_p.delete(
        f'/api/receitas/{receita.uuid}/?associacao_uuid={associacao.uuid}', content_type='application/json')

    assert response.status_code == status.HTTP_204_NO_CONTENT

    assert not Receita.objects.filter(uuid=receita.uuid).exists()


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
        f'/api/receitas/{receita.uuid}/?associacao_uuid={associacao.uuid}', content_type='application/json')
    result = json.loads(response.content)

    esperado = {
        'uuid': str(receita.uuid),
        'data': '2020-03-26',
        'valor': '100.00',
        'tipo_receita': {
            'id': tipo_receita.id,
            'nome': tipo_receita.nome,
            'e_repasse': tipo_receita.e_repasse,
            'aceita_capital': tipo_receita.aceita_capital,
            'aceita_custeio': tipo_receita.aceita_custeio,
            'aceita_livre': tipo_receita.aceita_livre,
            'e_devolucao': False,
            'e_recursos_proprios': False
        },
        'referencia_devolucao': None,
        'repasse': None,
        'saida_do_recurso':
            {
                'associacao': str(despesa_saida_recurso.associacao.uuid),
                'cpf_cnpj_fornecedor': '11.478.276/0001-04',
                'data_documento': '2019-09-10',
                'data_transacao': '2019-09-10',
                'documento_transacao': '',
                'nome_fornecedor': 'Fornecedor SA',
                'numero_documento': '123456',
                'tipo_documento': {
                    'id': despesa_saida_recurso.tipo_documento.id,
                    'nome': despesa_saida_recurso.tipo_documento.nome
                },
                'tipo_transacao': {
                    'id': despesa_saida_recurso.tipo_transacao.id,
                    'nome': despesa_saida_recurso.tipo_transacao.nome,
                    'tem_documento': despesa_saida_recurso.tipo_transacao.tem_documento
                },
                'uuid': str(despesa_saida_recurso.uuid),
                'valor_ptrf': 100.0,
                'valor_total': '100.00'
            },
        "acao_associacao": {
            "uuid": str(acao_associacao.uuid),
            "id": acao_associacao.id,
            "nome": acao_associacao.acao.nome,
            'e_recursos_proprios': False,
            'acao': {
                'id': acao_associacao.acao.id,
                'uuid': f'{acao_associacao.acao.uuid}',
                'nome': acao_associacao.acao.nome,
                'e_recursos_proprios': False,
                'posicao_nas_pesquisas': acao_associacao.acao.posicao_nas_pesquisas,
                'aceita_capital': acao_associacao.acao.aceita_capital,
                'aceita_custeio': acao_associacao.acao.aceita_custeio,
                'aceita_livre': acao_associacao.acao.aceita_livre
            }
        },
        'conta_associacao': {
            "uuid": str(conta_associacao.uuid),
            "nome": conta_associacao.tipo_conta.nome
        },
        'conferido': True,
        'categoria_receita': 'CUSTEIO',
        'detalhe_tipo_receita': {
            'id': detalhe_tipo_receita.id,
            'nome': detalhe_tipo_receita.nome
        },
        'detalhe_outros': receita.detalhe_outros,
        'notificar_dias_nao_conferido': 0,
        'rateio_estornado': None,
    }

    assert response.status_code == status.HTTP_200_OK
    assert result == esperado


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
