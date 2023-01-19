import datetime

import pytest
from django.contrib.auth.models import Permission
from sme_ptrf_apps.users.models import Grupo
from django.contrib.contenttypes.models import ContentType
from model_bakery import baker

from ..tipos_aplicacao_recurso import APLICACAO_CAPITAL, APLICACAO_CUSTEIO


@pytest.fixture
def permissoes_api_ue():
    permissoes = [
        Permission.objects.filter(codename='ue_leitura').first(),
        Permission.objects.filter(codename='ue_gravacao').first()
    ]

    return permissoes


@pytest.fixture
def permissoes_api_dre():
    permissoes = [
        Permission.objects.filter(codename='dre_leitura').first(),
        Permission.objects.filter(codename='dre_gravacao').first()
    ]

    return permissoes


@pytest.fixture
def permissoes_api_sme():
    permissoes = [
        Permission.objects.filter(codename='sme_leitura').first(),
        Permission.objects.filter(codename='sme_gravacao').first()
    ]

    return permissoes



@pytest.fixture
def tipo_documento():
    return baker.make('TipoDocumento', nome='NFe', apenas_digitos=False, numero_documento_digitado=False)


@pytest.fixture
def tipo_documento_numero_documento_digitado():
    return baker.make('TipoDocumento', nome='NFe', apenas_digitos=False, numero_documento_digitado=True)


@pytest.fixture
def tipo_transacao():
    return baker.make('TipoTransacao', nome='Boleto')


@pytest.fixture
def tipo_transacao_cheque_com_documento():
    return baker.make('TipoTransacao', nome='Cheque', tem_documento=True)


@pytest.fixture
def tipo_transacao_boleto_sem_documento():
    return baker.make('TipoTransacao', nome='Boleto', tem_documento=False)


@pytest.fixture
def tipo_aplicacao_recurso():
    return APLICACAO_CUSTEIO


@pytest.fixture
def tipo_aplicacao_recurso_custeio():
    return APLICACAO_CUSTEIO


@pytest.fixture
def tipo_aplicacao_recurso_capital():
    return APLICACAO_CAPITAL


@pytest.fixture
def tipo_custeio():
    return baker.make('TipoCusteio', nome='Material')


@pytest.fixture
def tipo_custeio_material():
    return baker.make('TipoCusteio', nome='Material 02')


@pytest.fixture
def tipo_custeio_servico():
    return baker.make('TipoCusteio', nome='Servico')


@pytest.fixture
def especificacao_material_servico(tipo_aplicacao_recurso, tipo_custeio):
    return baker.make(
        'EspecificacaoMaterialServico',
        descricao='Material elétrico',
        aplicacao_recurso=tipo_aplicacao_recurso,
        tipo_custeio=tipo_custeio,
    )


@pytest.fixture
def especificacao_custeio_material(tipo_aplicacao_recurso_custeio, tipo_custeio_material):
    return baker.make(
        'EspecificacaoMaterialServico',
        descricao='Material elétrico',
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_material,
    )


@pytest.fixture
def especificacao_custeio_servico(tipo_aplicacao_recurso_custeio, tipo_custeio_servico):
    return baker.make(
        'EspecificacaoMaterialServico',
        descricao='Instalação elétrica',
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
    )


@pytest.fixture
def especificacao_material_eletrico(especificacao_custeio_material):
    return especificacao_custeio_material


@pytest.fixture
def especificacao_instalacao_eletrica(especificacao_custeio_servico):
    return especificacao_custeio_servico


@pytest.fixture
def especificacao_capital(tipo_aplicacao_recurso_capital):
    return baker.make(
        'EspecificacaoMaterialServico',
        descricao='Ar condicionado',
        aplicacao_recurso=tipo_aplicacao_recurso_capital,
        tipo_custeio=None,
    )


@pytest.fixture
def especificacao_ar_condicionado(especificacao_capital):
    return especificacao_capital


@pytest.fixture
def despesa(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='123456',
        data_documento=datetime.date(2020, 3, 10),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        documento_transacao='',
        data_transacao=datetime.date(2020, 3, 10),
        valor_total=100.00,
        valor_recursos_proprios=10.00,
        valor_original=90.00,
    )


@pytest.fixture
def despesa_cheque_com_documento_transacao(associacao, tipo_documento, tipo_transacao_cheque_com_documento):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='123456',
        data_documento=datetime.date(2020, 3, 10),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao_cheque_com_documento,
        documento_transacao='123456789',
        data_transacao=datetime.date(2020, 3, 10),
        valor_total=100.00,
        valor_recursos_proprios=10.00,
    )


@pytest.fixture
def despesa_cheque_sem_documento_transacao(associacao, tipo_documento, tipo_transacao_cheque_com_documento):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='123456',
        data_documento=datetime.date(2020, 3, 10),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao_cheque_com_documento,
        documento_transacao='',
        data_transacao=datetime.date(2020, 3, 10),
        valor_total=100.00,
        valor_recursos_proprios=10.00,
    )


@pytest.fixture
def despesa_boleto_sem_documento_transacao(associacao, tipo_documento, tipo_transacao_boleto_sem_documento):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='123456',
        data_documento=datetime.date(2020, 3, 10),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao_boleto_sem_documento,
        documento_transacao='',
        data_transacao=datetime.date(2020, 3, 10),
        valor_total=100.00,
        valor_recursos_proprios=10.00,
    )


@pytest.fixture
def rateio_despesa_capital(associacao, despesa, conta_associacao, acao, tipo_aplicacao_recurso, tipo_custeio,
                           especificacao_material_servico, acao_associacao, periodo_2020_1):
    return baker.make(
        'RateioDespesa',
        despesa=despesa,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao,
        aplicacao_recurso=tipo_aplicacao_recurso,
        tipo_custeio=tipo_custeio,
        especificacao_material_servico=especificacao_material_servico,
        valor_rateio=100.00,
        quantidade_itens_capital=2,
        valor_item_capital=50.00,
        numero_processo_incorporacao_capital='Teste123456',
        update_conferido=True,
        conferido=True,
        periodo_conciliacao=periodo_2020_1,
        valor_original=90.00,
    )


@pytest.fixture
def rateio_despesa_instalacao_eletrica_ptrf(associacao, despesa, conta_associacao, acao, tipo_aplicacao_recurso_custeio,
                                            tipo_custeio_servico,
                                            especificacao_instalacao_eletrica, acao_associacao_ptrf):
    return baker.make(
        'RateioDespesa',
        despesa=despesa,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_ptrf,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_servico,
        especificacao_material_servico=especificacao_instalacao_eletrica,
        valor_rateio=100.00,
        update_conferido=True,
        conferido=True,

    )


@pytest.fixture
def rateio_despesa_material_eletrico_role_cultural(associacao, despesa, conta_associacao, acao,
                                                   tipo_aplicacao_recurso_custeio,
                                                   tipo_custeio_material,
                                                   especificacao_material_eletrico, acao_associacao_role_cultural):
    return baker.make(
        'RateioDespesa',
        despesa=despesa,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_role_cultural,
        aplicacao_recurso=tipo_aplicacao_recurso_custeio,
        tipo_custeio=tipo_custeio_material,
        especificacao_material_servico=especificacao_material_eletrico,
        valor_rateio=100.00,
        conferido=False,

    )


@pytest.fixture
def rateio_despesa_ar_condicionado_ptrf(associacao, despesa, conta_associacao, acao, tipo_aplicacao_recurso_capital,
                                        especificacao_ar_condicionado, acao_associacao_ptrf):
    return baker.make(
        'RateioDespesa',
        despesa=despesa,
        associacao=associacao,
        conta_associacao=conta_associacao,
        acao_associacao=acao_associacao_ptrf,
        aplicacao_recurso=tipo_aplicacao_recurso_capital,
        tipo_custeio=None,
        especificacao_material_servico=especificacao_ar_condicionado,
        valor_rateio=100.00,
        quantidade_itens_capital=2,
        valor_item_capital=50.00,
        numero_processo_incorporacao_capital='Teste123456'

    )


@pytest.fixture
def rateio_despesa_conferido(rateio_despesa_instalacao_eletrica_ptrf):
    return rateio_despesa_instalacao_eletrica_ptrf


@pytest.fixture
def rateio_despesa_nao_conferido(rateio_despesa_material_eletrico_role_cultural):
    return rateio_despesa_material_eletrico_role_cultural


@pytest.fixture
def rateio_despesa_nao_conferido2(rateio_despesa_ar_condicionado_ptrf):
    return rateio_despesa_ar_condicionado_ptrf


@pytest.fixture
def fornecedor_jose():
    return baker.make('Fornecedor', nome='José', cpf_cnpj='079.962.460-84')


@pytest.fixture
def fornecedor_industrias_teste():
    return baker.make('Fornecedor', nome='Indústrias Teste', cpf_cnpj='80.554.237/0001-53')


@pytest.fixture
def permissoes_despesa():
    permissoes = [
        Permission.objects.filter(codename='add_despesa').first(),
        Permission.objects.filter(codename='view_despesa').first(),
        Permission.objects.filter(codename='change_despesa').first(),
        Permission.objects.filter(codename='delete_despesa').first(),
        Permission.objects.create(
            name="Editar conciliação bancária",
            codename='change_conciliacao_bancaria',
            content_type=ContentType.objects.filter(app_label="auth").first()
        )
    ]

    return permissoes

@pytest.fixture
def permissoes_rateios():
    permissoes = [
        Permission.objects.filter(codename='add_rateiodespesa').first(),
        Permission.objects.filter(codename='view_rateiodespesa').first(),
        Permission.objects.filter(codename='change_rateiodespesa').first(),
        Permission.objects.filter(codename='delete_rateiodespesa').first()
    ]

    return permissoes


@pytest.fixture
def grupo_despesa(permissoes_despesa, permissoes_api_ue):
    g = Grupo.objects.create(name="despesa")
    g.permissions.add(*permissoes_api_ue)
    return g


@pytest.fixture
def usuario_permissao_despesa(unidade, grupo_despesa):
    from django.contrib.auth import get_user_model
    senha = 'Sgp0418'
    login = '7210418'
    email = 'sme@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(unidade)
    user.groups.add(grupo_despesa)
    user.save()
    return user


@pytest.fixture
def jwt_authenticated_client_d(client, usuario_permissao_despesa):
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
        resp = api_client.post('/api/login', {'login': usuario_permissao_despesa.username,
                                              'senha': usuario_permissao_despesa.password}, format='json')
        resp_data = resp.json()
        api_client.credentials(HTTP_AUTHORIZATION='JWT {0}'.format(resp_data['token']))
    return api_client



@pytest.fixture
def grupo_sem_permissao_criar_receita():
    content_type = ContentType.objects.filter(model='despesa').first()
    g = Grupo.objects.create(name="despesa")
    g.permissions.add(
        Permission.objects.create(codename='algo_despesa', name='Can Algo', content_type=content_type)
    )
    return g


@pytest.fixture
def usuario_sem_permissao(unidade, grupo_sem_permissao_criar_receita):
    from django.contrib.auth import get_user_model
    senha = 'Sgp0418'
    login = '7210418'
    email = 'sme@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(unidade)
    user.groups.add(grupo_sem_permissao_criar_receita)
    user.save()
    return user


@pytest.fixture
def jwt_authenticated_client_sem_permissao(client, usuario_sem_permissao):
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
        resp = api_client.post('/api/login', {'login': usuario_sem_permissao.username,
                                              'senha': usuario_sem_permissao.password}, format='json')
        resp_data = resp.json()
        api_client.credentials(HTTP_AUTHORIZATION='JWT {0}'.format(resp_data['token']))
    return api_client

# Motivos pagamento antecipado

@pytest.fixture
def motivo_pagamento_adiantado_01():
    return baker.make(
        'MotivoPagamentoAntecipado',
        motivo="Motivo de pagamento adiantado 01"
    )

@pytest.fixture
def motivo_pagamento_adiantado_02():
    return baker.make(
        'MotivoPagamentoAntecipado',
        motivo="Motivo de pagamento adiantado 02"
    )

@pytest.fixture
def despesa_inativa(associacao, tipo_documento, tipo_transacao):
    return baker.make(
        'Despesa',
        associacao=associacao,
        numero_documento='123456',
        data_documento=datetime.date(2019, 9, 10),
        tipo_documento=tipo_documento,
        cpf_cnpj_fornecedor='11.478.276/0001-04',
        nome_fornecedor='Fornecedor SA',
        tipo_transacao=tipo_transacao,
        data_transacao=datetime.date(2019, 9, 10),
        valor_total=100.00,
        data_e_hora_de_inativacao=datetime.datetime(2022, 9, 6, 10, 0, 0)
    )
