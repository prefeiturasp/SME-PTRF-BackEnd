import datetime

import pytest
from model_bakery import baker
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from sme_ptrf_apps.users.models import Grupo
from datetime import date


@pytest.fixture
def tipo_receita(tipo_conta):
    return baker.make('TipoReceita', nome='Estorno', e_repasse=False, aceita_capital=False, aceita_custeio=False,
                      e_devolucao=False, tipos_conta=[tipo_conta])


@pytest.fixture
def tipo_receita_estorno(tipo_receita):
    return tipo_receita


@pytest.fixture
def tipo_receita_repasse(tipo_conta):
    return baker.make('TipoReceita', nome='Repasse', e_repasse=True, aceita_capital=True, aceita_custeio=True, tipos_conta=[tipo_conta])


@pytest.fixture
def tipo_receita_devolucao(tipo_conta):
    return baker.make('TipoReceita', nome='Devolução', e_devolucao=True, aceita_capital=True, aceita_custeio=True, tipos_conta=[tipo_conta])


@pytest.fixture
def receita(associacao, conta_associacao, acao_associacao, tipo_receita, prestacao_conta_iniciada,
            detalhe_tipo_receita, periodo_2020_1):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 26),
        valor=100.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita,
        update_conferido=True,
        conferido=True,
        categoria_receita='CUSTEIO',
        detalhe_tipo_receita=detalhe_tipo_receita,
        detalhe_outros='teste',
        periodo_conciliacao=periodo_2020_1,
    )


@pytest.fixture
def receita_devolucao(associacao, conta_associacao, acao_associacao, tipo_receita_devolucao, prestacao_conta_iniciada,
                      detalhe_tipo_receita, periodo):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 26),
        valor=100.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita_devolucao,
        update_conferido=True,
        conferido=True,
        categoria_receita='CUSTEIO',
        detalhe_tipo_receita=detalhe_tipo_receita,
        detalhe_outros='teste',
        referencia_devolucao=periodo,
        periodo_conciliacao=periodo
    )


@pytest.fixture
def receita_sem_detalhe_tipo_receita(associacao, conta_associacao, acao_associacao, tipo_receita,
                                     periodo_2020_1):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 26),
        valor=100.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita,
        update_conferido=True,
        conferido=True,
        categoria_receita='CUSTEIO',
        detalhe_outros='teste',
        periodo_conciliacao=periodo_2020_1
    )


@pytest.fixture
def payload_receita(associacao, conta_associacao, acao_associacao, tipo_conta, tipo_receita, detalhe_tipo_receita):
    payload = {
        'associacao': str(associacao.uuid),
        'data': '2020-03-26',
        'valor': 100.00,
        'categoria_receita': 'CUSTEIO',
        'conta_associacao': str(conta_associacao.uuid),
        'acao_associacao': str(acao_associacao.uuid),
        'tipo_receita': tipo_receita.id,
        'detalhe_tipo_receita': detalhe_tipo_receita.id,
        'detalhe_outros': 'teste',
    }
    return payload


@pytest.fixture
def payload_receita_livre_aplicacao(associacao, conta_associacao, acao_associacao, tipo_receita, detalhe_tipo_receita):
    payload = {
        'associacao': str(associacao.uuid),
        'data': '2020-03-26',
        'valor': 100.00,
        'categoria_receita': 'LIVRE',
        'conta_associacao': str(conta_associacao.uuid),
        'acao_associacao': str(acao_associacao.uuid),
        'tipo_receita': tipo_receita.id,
        'detalhe_tipo_receita': detalhe_tipo_receita.id,
        'detalhe_outros': 'teste',
    }
    return payload


@pytest.fixture
def payload_receita_repasse(associacao, conta_associacao, acao_associacao, tipo_receita_repasse, repasse):
    payload = {
        'associacao': str(associacao.uuid),
        'data': '2019-09-26',
        'valor': 1000.28,
        'categoria_receita': 'CAPITAL',
        'conta_associacao': str(conta_associacao.uuid),
        'acao_associacao': str(acao_associacao.uuid),
        'tipo_receita': tipo_receita_repasse.id,
        'repasse': str(repasse.uuid)
    }
    return payload


@pytest.fixture
def payload_receita_repasse_livre_aplicacao(associacao, conta_associacao, acao_associacao, tipo_receita_repasse, repasse_2020_1_livre_aplicacao_pendente):
    payload = {
        'associacao': str(associacao.uuid),
        'data': '2020-02-26',
        'valor': 1000.00,
        'categoria_receita': 'LIVRE',
        'conta_associacao': str(conta_associacao.uuid),
        'acao_associacao': str(acao_associacao.uuid),
        'tipo_receita': tipo_receita_repasse.id,
        'repasse': str(repasse_2020_1_livre_aplicacao_pendente.uuid)
    }
    return payload


@pytest.fixture
def receita_xxx_estorno(associacao, conta_associacao_cheque, acao_associacao_ptrf, tipo_receita_estorno):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 26),
        valor=100.00,
        detalhe_outros="Receita XXXÇ",
        conta_associacao=conta_associacao_cheque,
        acao_associacao=acao_associacao_ptrf,
        tipo_receita=tipo_receita_estorno,
        update_conferido=True,
        conferido=True,
    )


@pytest.fixture
def receita_yyy_repasse(associacao, conta_associacao_cartao, acao_associacao_role_cultural, tipo_receita_repasse,
                        repasse_realizado, detalhe_tipo_receita_repasse):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 26),
        valor=100.00,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        tipo_receita=tipo_receita_repasse,
        conferido=False,
        repasse=repasse_realizado,
        detalhe_tipo_receita=detalhe_tipo_receita_repasse
    )


@pytest.fixture
def receita_repasse_livre_aplicacao(associacao, conta_associacao_cartao, acao_associacao_role_cultural,
                                    tipo_receita_repasse,
                                    repasse_realizado_livre_aplicacao, detalhe_tipo_receita_repasse):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 26),
        valor=100.00,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        tipo_receita=tipo_receita_repasse,
        conferido=False,
        repasse=repasse_realizado_livre_aplicacao,
        detalhe_tipo_receita=detalhe_tipo_receita_repasse,
        categoria_receita='LIVRE',
    )


@pytest.fixture
def receita_conferida(receita_xxx_estorno):
    return receita_xxx_estorno


@pytest.fixture
def receita_nao_conferida(receita_yyy_repasse):
    return receita_yyy_repasse


@pytest.fixture
def receita_nao_conferida_desde_01_03_2020(associacao, conta_associacao_cartao, acao_associacao_role_cultural,
                                           tipo_receita_repasse,
                                           repasse_realizado, detalhe_tipo_receita_repasse):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 1),
        valor=100.00,
        conta_associacao=conta_associacao_cartao,
        acao_associacao=acao_associacao_role_cultural,
        tipo_receita=tipo_receita_repasse,
        conferido=False,
        repasse=repasse_realizado,
        detalhe_tipo_receita=detalhe_tipo_receita_repasse
    )


@pytest.fixture
def receita_2020_3_10(associacao, conta_associacao_cheque, acao_associacao_ptrf, tipo_receita_estorno):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 10),
        valor=100.00,
        conta_associacao=conta_associacao_cheque,
        acao_associacao=acao_associacao_ptrf,
        tipo_receita=tipo_receita_estorno,
        conferido=True,
    )


@pytest.fixture
def receita_2020_3_11(associacao, conta_associacao_cheque, acao_associacao_ptrf, tipo_receita_estorno):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 11),
        valor=100.00,
        conta_associacao=conta_associacao_cheque,
        acao_associacao=acao_associacao_ptrf,
        tipo_receita=tipo_receita_estorno,
        conferido=True,
    )


@pytest.fixture
def repasse(associacao, conta_associacao, acao_associacao, periodo):
    return baker.make(
        'Repasse',
        associacao=associacao,
        periodo=periodo,
        valor_custeio=1000.40,
        valor_capital=1000.28,
        valor_livre=0,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        status='PENDENTE'
    )


@pytest.fixture
def repasse_2020_1_capital_pendente(associacao, conta_associacao, acao_associacao, periodo_2020_1):
    return baker.make(
        'Repasse',
        associacao=associacao,
        periodo=periodo_2020_1,
        valor_custeio=1000.00,
        valor_capital=1000.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        status='PENDENTE',
        realizado_capital=False,
        realizado_custeio=True
    )


@pytest.fixture
def repasse_2020_1_custeio_pendente(associacao, conta_associacao, acao_associacao, periodo_2020_1):
    return baker.make(
        'Repasse',
        associacao=associacao,
        periodo=periodo_2020_1,
        valor_custeio=1000.00,
        valor_capital=1000.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        status='PENDENTE',
        realizado_capital=True,
        realizado_custeio=False
    )


@pytest.fixture
def repasse_2020_1_livre_aplicacao_pendente(associacao, conta_associacao, acao_associacao, periodo_2020_1):
    return baker.make(
        'Repasse',
        associacao=associacao,
        periodo=periodo_2020_1,
        valor_livre=1000.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        status='PENDENTE',
        realizado_capital=True,
        realizado_custeio=True,
        realizado_livre=False,
    )


@pytest.fixture
def repasse_2020_1_pendente(associacao, conta_associacao, acao_associacao, periodo_2020_1):
    return baker.make(
        'Repasse',
        associacao=associacao,
        periodo=periodo_2020_1,
        valor_custeio=1000.00,
        valor_capital=1000.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        status='PENDENTE',
        realizado_capital=False,
        realizado_custeio=False
    )


@pytest.fixture
def repasse_2020_1_realizado(associacao, conta_associacao, acao_associacao, periodo_2020_1):
    return baker.make(
        'Repasse',
        associacao=associacao,
        periodo=periodo_2020_1,
        valor_custeio=1000.00,
        valor_capital=1000.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        status='REALIZADO',
        realizado_capital=True,
        realizado_custeio=True
    )


@pytest.fixture
def repasse_realizado(associacao, conta_associacao, acao_associacao_role_cultural, periodo):
    return baker.make(
        'Repasse',
        associacao=associacao,
        periodo=periodo,
        valor_custeio=1000.40,
        valor_capital=1000.28,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_role_cultural,
        status='REALIZADO'
    )


@pytest.fixture
def repasse_realizado_livre_aplicacao(associacao, conta_associacao, acao_associacao_role_cultural, periodo):
    return baker.make(
        'Repasse',
        associacao=associacao,
        periodo=periodo,
        valor_livre=1000.00,
        realizado_capital=True,
        realizado_custeio=True,
        realizado_livre=True,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_role_cultural,
        status='REALIZADO'
    )


@pytest.fixture
def permissoes_receitas():
    permissoes = [
        Permission.objects.filter(codename='ue_leitura').first(),
        Permission.objects.filter(codename='ue_gravacao').first()
    ]

    return permissoes


@pytest.fixture
def grupo_receita(permissoes_receitas):
    g = Grupo.objects.create(name="receita")
    g.permissions.add(*permissoes_receitas)
    return g


@pytest.fixture
def usuario_permissao(unidade, grupo_receita):
    from django.contrib.auth import get_user_model
    senha = 'Sgp0418'
    login = '7210418'
    email = 'sme@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(unidade)
    user.groups.add(grupo_receita)
    user.save()
    return user


@pytest.fixture
def jwt_authenticated_client_p(client, usuario_permissao):
    from unittest.mock import patch
    from rest_framework.test import APIClient
    api_client = APIClient()
    with patch('sme_ptrf_apps.users.api.views.login.AutenticacaoService.autentica') as mock_post:
        data = {
            "nome": "LUCIA HELENA",
            "cpf": "62085077072",
            "email": "luh@gmail.com",
            "login": "7210418"
        }
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = data
        resp = api_client.post('/api/login', {'login': usuario_permissao.username, 'senha': usuario_permissao.password}, format='json')
        resp_data = resp.json()
        api_client.credentials(HTTP_AUTHORIZATION='JWT {0}'.format(resp_data['token']))
    return api_client


@pytest.fixture
def tipo_transacao_saida_recurso():
    return baker.make('TipoTransacao', nome='Boleto')


@pytest.fixture
def tipo_documento_saida_recurso():
    return baker.make('TipoDocumento', nome='NFe')


@pytest.fixture
def associacao_saida_recurso(unidade, periodo_anterior):
    return baker.make(
        'Associacao',
        nome='Escola Teste Saida Recurso',
        cnpj='74.718.557/0001-07',
        unidade=unidade,
        periodo_inicial=periodo_anterior,
        ccm='0.000.00-0',
        email="ollyverottoboni@gmail.com",
        processo_regularidade='123456'
    )


@pytest.fixture
def despesa_saida_recurso(associacao_saida_recurso, tipo_documento_saida_recurso, tipo_transacao_saida_recurso):
    return baker.make(
        'Despesa',
        associacao=associacao_saida_recurso,
        numero_documento='123456',
        data_documento=date(2019, 9, 10),
        tipo_documento=tipo_documento_saida_recurso,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao_saida_recurso,
        data_transacao=date(2019, 9, 10),
        valor_total=100.00,
    )


@pytest.fixture
def receita_saida_recurso(associacao, conta_associacao, acao_associacao, tipo_receita, prestacao_conta_iniciada,
            detalhe_tipo_receita, periodo_2020_1):
    return baker.make(
        'Receita',
        associacao=associacao,
        data=datetime.date(2020, 3, 26),
        valor=100.00,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        tipo_receita=tipo_receita,
        update_conferido=True,
        conferido=True,
        categoria_receita='CUSTEIO',
        detalhe_tipo_receita=detalhe_tipo_receita,
        detalhe_outros='teste',
        periodo_conciliacao=periodo_2020_1,
        saida_do_recurso="",
    )
