import pytest

from django.contrib.auth import get_user_model
from ....core.choices import MembroEnum, RepresentacaoCargo
from datetime import date

from model_bakery import baker


@pytest.fixture
def parametros_sme():
    return baker.make('ParametrosSme', valida_unidades_login=True)


@pytest.fixture
def parametros_sme_valida_unidades_login_falso():
    return baker.make('ParametrosSme', valida_unidades_login=False)


@pytest.fixture
def tipo_unidade_administrativa():
    return baker.make('TipoUnidadeAdministrativa', tipo_unidade_administrativa='1')


@pytest.fixture
def tipo_unidade_administrativa_com_codigo_eol():
    return baker.make('TipoUnidadeAdministrativa', tipo_unidade_administrativa='2', inicio_codigo_eol='12')


@pytest.fixture
def visao_ue_gestao_usuario():
    return baker.make('Visao', nome='UE')


@pytest.fixture
def visao_dre_gestao_usuario():
    return baker.make('Visao', nome='DRE')


@pytest.fixture
def visao_sme_gestao_usuario():
    return baker.make('Visao', nome='SME')


@pytest.fixture
def periodo_gestao_usuarior(periodo_factory):
    return periodo_factory(
        referencia='2019.1',
        data_inicio_realizacao_despesas=date(2019, 1, 1),
        data_fim_realizacao_despesas=date(2019, 8, 31),
    )


@pytest.fixture
def unidade_gestao_usuario_a(dre):
    return baker.make(
        'Unidade',
        nome='Escola Teste a',
        tipo_unidade='CEU',
        codigo_eol='123456',
        dre=dre,
        sigla='ET',
        cep='5868120',
        tipo_logradouro='Travessa',
        logradouro='dos Testes',
        bairro='COHAB INSTITUTO ADVENTISTA',
        numero='200',
        complemento='fundos',
        telefone='58212627',
        email='emefjopfilho@sme.prefeitura.sp.gov.br',
        diretor_nome='Pedro Amaro',
        dre_cnpj='63.058.286/0001-86',
        dre_diretor_regional_rf='1234567',
        dre_diretor_regional_nome='Anthony Edward Stark',
        dre_designacao_portaria='Portaria nº 0.000',
        dre_designacao_ano='2017',
    )


@pytest.fixture
def unidade_gestao_usuario_b(dre_ipiranga):
    return baker.make(
        'Unidade',
        nome='Escola Teste b',
        tipo_unidade='CEU',
        codigo_eol='123457',
        dre=dre_ipiranga,
        sigla='ET',
        cep='5868120',
        tipo_logradouro='Travessa',
        logradouro='dos Testes',
        bairro='COHAB INSTITUTO ADVENTISTA',
        numero='200',
        complemento='fundos',
        telefone='58212627',
        email='emefjopfilho@sme.prefeitura.sp.gov.br',
        diretor_nome='Pedro Amaro',
        dre_cnpj='63.058.286/0001-86',
        dre_diretor_regional_rf='1234567',
        dre_diretor_regional_nome='Anthony Edward Stark',
        dre_designacao_portaria='Portaria nº 0.000',
        dre_designacao_ano='2017',
    )


@pytest.fixture
def unidade_gestao_usuario_c(dre_ipiranga):
    return baker.make(
        'Unidade',
        nome='Escola Teste C',
        tipo_unidade='CEU',
        codigo_eol='123458',
        dre=dre_ipiranga,
        sigla='ET',
        cep='5868120',
        tipo_logradouro='Travessa',
        logradouro='dos Testes',
        bairro='COHAB INSTITUTO ADVENTISTA',
        numero='200',
        complemento='fundos',
        telefone='58212627',
        email='emefjopfilho@sme.prefeitura.sp.gov.br',
        diretor_nome='Pedro Amaro',
        dre_cnpj='63.058.286/0001-86',
        dre_diretor_regional_rf='1234567',
        dre_diretor_regional_nome='Anthony Edward Stark',
        dre_designacao_portaria='Portaria nº 0.000',
        dre_designacao_ano='2017',
    )


@pytest.fixture
def associacao_gestao_usuario_a(unidade_gestao_usuario_a, periodo_gestao_usuarior):
    return baker.make(
        'Associacao',
        nome='Escola Teste',
        cnpj='52.302.275/0001-84',
        unidade=unidade_gestao_usuario_a,
        periodo_inicial=periodo_gestao_usuarior,
        ccm='0.000.00-0',
        email="ollyverottoboni@gmail.com",
        processo_regularidade='123456'
    )


@pytest.fixture
def associacao_gestao_usuario_b(unidade_gestao_usuario_b, periodo_gestao_usuarior):
    return baker.make(
        'Associacao',
        nome='Escola Teste',
        cnpj='52.302.275/0001-83',
        unidade=unidade_gestao_usuario_b,
        periodo_inicial=periodo_gestao_usuarior,
        ccm='0.000.00-0',
        email="ollyverottoboni@gmail.com",
        processo_regularidade='123456'
    )


@pytest.fixture
def membro_associacao_nao_servidor_a(associacao_gestao_usuario_a):
    return baker.make(
        'MembroAssociacao',
        nome='Arthur Nobrega',
        associacao=associacao_gestao_usuario_a,
        cargo_associacao=MembroEnum.VOGAL_1.value,
        cargo_educacao='Coordenador',
        representacao=RepresentacaoCargo.PAI_RESPONSAVEL.value,
        codigo_identificacao='',
        email='ollyverottoboni@gmail.com',
        cpf='854.041.430-96',
        telefone='11992137854',
        cep='04302000',
        bairro='Vila da Saúde',
        endereco='Rua Apotribu, 57 - apto 12'
    )


@pytest.fixture
def membro_associacao_nao_servidor_b(associacao_gestao_usuario_b):
    return baker.make(
        'MembroAssociacao',
        nome='Arthur Nobrega',
        associacao=associacao_gestao_usuario_b,
        cargo_associacao=MembroEnum.VOGAL_1.value,
        cargo_educacao='Coordenador',
        representacao=RepresentacaoCargo.PAI_RESPONSAVEL.value,
        codigo_identificacao='',
        email='ollyverottoboni@gmail.com',
        cpf='854.041.430-96',
        telefone='11992137854',
        cep='04302000',
        bairro='Vila da Saúde',
        endereco='Rua Apotribu, 57 - apto 12'
    )


@pytest.fixture
def membro_associacao_servidor_a(associacao_gestao_usuario_a):
    return baker.make(
        'MembroAssociacao',
        nome='Arthur Nobrega',
        associacao=associacao_gestao_usuario_a,
        cargo_associacao=MembroEnum.VOGAL_1.value,
        cargo_educacao='Coordenador',
        representacao=RepresentacaoCargo.PAI_RESPONSAVEL.value,
        codigo_identificacao='7210418',
        email='ollyverottoboni@gmail.com',
        cpf='',
        telefone='11992137854',
        cep='04302000',
        bairro='Vila da Saúde',
        endereco='Rua Apotribu, 57 - apto 12'
    )


@pytest.fixture
def membro_associacao_servidor_b(associacao_gestao_usuario_b):
    return baker.make(
        'MembroAssociacao',
        nome='Arthur Nobrega',
        associacao=associacao_gestao_usuario_b,
        cargo_associacao=MembroEnum.VOGAL_1.value,
        cargo_educacao='Coordenador',
        representacao=RepresentacaoCargo.PAI_RESPONSAVEL.value,
        codigo_identificacao='7210418',
        email='ollyverottoboni@gmail.com',
        cpf='',
        telefone='11992137854',
        cep='04302000',
        bairro='Vila da Saúde',
        endereco='Rua Apotribu, 57 - apto 12'
    )


@pytest.fixture
def usuario_nao_servidor_service_gestao_usuario(
    unidade_gestao_usuario_a,
    visao_ue_gestao_usuario,
    dre,
    visao_dre_gestao_usuario
):

    senha = 'Sgp0418'
    login = '85404143096'
    email = 'sme@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(unidade_gestao_usuario_a)
    user.unidades.add(dre)
    user.visoes.add(visao_ue_gestao_usuario)
    user.visoes.add(visao_dre_gestao_usuario)
    user.save()
    return user


@pytest.fixture
def usuario_nao_servidor_sem_visao_dre_service_gestao_usuario(
    unidade_gestao_usuario_a,
    visao_ue_gestao_usuario,
    unidade_gestao_usuario_b
):

    senha = 'Sgp0418'
    login = '85404143096'
    email = 'sme@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(unidade_gestao_usuario_a)
    user.unidades.add(unidade_gestao_usuario_b)
    user.visoes.add(visao_ue_gestao_usuario)
    user.pode_acessar_sme = True
    user.save()
    return user


@pytest.fixture
def usuario_servidor_service_gestao_usuario(
    unidade_gestao_usuario_a,
    unidade_gestao_usuario_b,
    visao_ue_gestao_usuario,
    visao_sme_gestao_usuario
):

    senha = 'Sgp0418'
    login = '7210418'
    email = 'sme@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email, e_servidor=True)
    user.unidades.add(unidade_gestao_usuario_a)
    user.unidades.add(unidade_gestao_usuario_b)
    user.visoes.add(visao_ue_gestao_usuario)
    user.visoes.add(visao_sme_gestao_usuario)
    user.save()
    return user


@pytest.fixture
def usuario_servidor_sem_visao_sme_service_gestao_usuario(
    unidade_gestao_usuario_a,
    visao_ue_gestao_usuario,
):

    senha = 'Sgp0418'
    login = '7210418'
    email = 'sme@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email, e_servidor=True)
    user.unidades.add(unidade_gestao_usuario_a)
    user.visoes.add(visao_ue_gestao_usuario)
    user.pode_acessar_sme = True
    user.save()
    return user


@pytest.fixture
def unidade_em_suporte_gestao_usuarios(unidade_gestao_usuario_b, usuario_servidor_service_gestao_usuario):
    return baker.make(
        'UnidadeEmSuporte',
        unidade=unidade_gestao_usuario_b,
        user=usuario_servidor_service_gestao_usuario,
    )


@pytest.fixture
def tecnico_dre_gestao_usuario(
    dre,
    usuario_servidor_service_gestao_usuario
):
    return baker.make(
        'TecnicoDre',
        dre=dre,
        nome='teste tecnico dre',
        rf=usuario_servidor_service_gestao_usuario.username,
    )
