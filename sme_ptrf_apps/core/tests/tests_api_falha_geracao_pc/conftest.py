from datetime import date, datetime
import pytest
from model_bakery import baker
from django.contrib.auth import get_user_model

pytestmark = pytest.mark.django_db


@pytest.fixture
def usuario_dre_teste_api_falha_geracao_pc(
    dre_teste_teste_api_falha_geracao_pc,
):
    senha = 'Sgp0418'
    login = '7654321'
    email = 'teste.lauda.model@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(dre_teste_teste_api_falha_geracao_pc)
    # user.visoes.add(visao_dre_teste_lauda_model)
    user.save()
    return user


@pytest.fixture
def periodo_anterior_teste_api_falha_geracao_pc():
    return baker.make(
        'Periodo',
        referencia='2021.2',
        data_inicio_realizacao_despesas=date(2021, 6, 16),
        data_fim_realizacao_despesas=date(2021, 12, 31),
    )


@pytest.fixture
def periodo_anterior_teste_api_falha_geracao_pc_02():
    return baker.make(
        'Periodo',
        referencia='2021.3',
        data_inicio_realizacao_despesas=date(2021, 6, 16),
        data_fim_realizacao_despesas=date(2021, 12, 31),
    )


@pytest.fixture
def periodo_teste_api_falha_geracao_pc(periodo_anterior_teste_api_falha_geracao_pc):
    return baker.make(
        'Periodo',
        referencia='2022.1',
        data_inicio_realizacao_despesas=date(2022, 1, 1),
        data_fim_realizacao_despesas=date(2022, 12, 31),
        periodo_anterior=periodo_anterior_teste_api_falha_geracao_pc,
    )


@pytest.fixture
def periodo_teste_api_falha_geracao_pc_02(periodo_anterior_teste_api_falha_geracao_pc_02):
    return baker.make(
        'Periodo',
        referencia='2022.2',
        data_inicio_realizacao_despesas=date(2022, 1, 1),
        data_fim_realizacao_despesas=date(2022, 12, 31),
        periodo_anterior=periodo_anterior_teste_api_falha_geracao_pc_02,
    )


@pytest.fixture
def dre_teste_teste_api_falha_geracao_pc():
    return baker.make(
        'Unidade',
        codigo_eol='108500',
        tipo_unidade='DRE',
        nome='Dre Teste Model Consolidado Dre',
        sigla='A',
    )


@pytest.fixture
def unidade_teste_api_falha_geracao_pc(dre_teste_teste_api_falha_geracao_pc):
    return baker.make(
        'Unidade',
        nome='Escola Teste',
        tipo_unidade='CEU',
        codigo_eol='123459',
        dre=dre_teste_teste_api_falha_geracao_pc,
    )


@pytest.fixture
def associacao_teste_api_falha_geracao_pc(unidade_teste_api_falha_geracao_pc):
    return baker.make(
        'Associacao',
        nome='Escola Teste',
        cnpj='52.302.275/0001-83',
        unidade=unidade_teste_api_falha_geracao_pc,
    )


@pytest.fixture
def prestacao_conta_teste_api_falha_geracao_pc(
    periodo_teste_api_falha_geracao_pc,
    associacao_teste_api_falha_geracao_pc
):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo_teste_api_falha_geracao_pc,
        associacao=associacao_teste_api_falha_geracao_pc,
    )


@pytest.fixture
def parametros_teste_api_falha_geracao_pc():
    return baker.make(
        'Parametros',
        tempo_aguardar_conclusao_pc=1,
        permite_saldo_conta_negativo=True,
        quantidade_tentativas_concluir_pc=3,
    )


@pytest.fixture
def falha_geracao_pc_teste_api_falha_geracao_pc_01(
    usuario_dre_teste_api_falha_geracao_pc,
    associacao_teste_api_falha_geracao_pc,
    periodo_teste_api_falha_geracao_pc,
):
    data_hora_ultima_ocorrencia = '2023-03-06 09:07:19'
    date_time_obj = datetime.strptime(data_hora_ultima_ocorrencia, '%Y-%m-%d %H:%M:%S')

    return baker.make(
        'FalhaGeracaoPc',
        ultimo_usuario=usuario_dre_teste_api_falha_geracao_pc,
        associacao=associacao_teste_api_falha_geracao_pc,
        periodo=periodo_teste_api_falha_geracao_pc,
        data_hora_ultima_ocorrencia=date_time_obj.strftime("%Y-%m-%dT%H:%M:%S"),
        qtd_ocorrencias_sucessivas=1,
        resolvido=False,
    )


@pytest.fixture
def falha_geracao_pc_teste_api_falha_geracao_pc_02(
    usuario_dre_teste_api_falha_geracao_pc,
    associacao_teste_api_falha_geracao_pc,
    periodo_teste_api_falha_geracao_pc,
):
    data_hora_ultima_ocorrencia = '2023-03-06 09:07:19'
    date_time_obj = datetime.strptime(data_hora_ultima_ocorrencia, '%Y-%m-%d %H:%M:%S')

    return baker.make(
        'FalhaGeracaoPc',
        ultimo_usuario=usuario_dre_teste_api_falha_geracao_pc,
        associacao=associacao_teste_api_falha_geracao_pc,
        periodo=periodo_teste_api_falha_geracao_pc,
        data_hora_ultima_ocorrencia=date_time_obj.strftime("%Y-%m-%dT%H:%M:%S"),
        qtd_ocorrencias_sucessivas=2,
        resolvido=True,
    )


@pytest.fixture
def falha_geracao_pc_teste_api_falha_geracao_pc_nao_excede_tentativas(
    usuario_dre_teste_api_falha_geracao_pc,
    associacao_teste_api_falha_geracao_pc,
    periodo_teste_api_falha_geracao_pc,
):
    data_hora_ultima_ocorrencia = '2023-03-06 09:07:19'
    date_time_obj = datetime.strptime(data_hora_ultima_ocorrencia, '%Y-%m-%d %H:%M:%S')

    return baker.make(
        'FalhaGeracaoPc',
        ultimo_usuario=usuario_dre_teste_api_falha_geracao_pc,
        associacao=associacao_teste_api_falha_geracao_pc,
        periodo=periodo_teste_api_falha_geracao_pc,
        data_hora_ultima_ocorrencia=date_time_obj.strftime("%Y-%m-%dT%H:%M:%S"),
        qtd_ocorrencias_sucessivas=2,
        resolvido=False,
    )


@pytest.fixture
def falha_geracao_pc_teste_api_falha_geracao_pc_nao_excede_tentativas_02(
    usuario_dre_teste_api_falha_geracao_pc,
    associacao_teste_api_falha_geracao_pc,
    periodo_teste_api_falha_geracao_pc_02,
):
    data_hora_ultima_ocorrencia = '2023-03-06 09:07:19'
    date_time_obj = datetime.strptime(data_hora_ultima_ocorrencia, '%Y-%m-%d %H:%M:%S')

    return baker.make(
        'FalhaGeracaoPc',
        ultimo_usuario=usuario_dre_teste_api_falha_geracao_pc,
        associacao=associacao_teste_api_falha_geracao_pc,
        periodo=periodo_teste_api_falha_geracao_pc_02,
        data_hora_ultima_ocorrencia=date_time_obj.strftime("%Y-%m-%dT%H:%M:%S"),
        qtd_ocorrencias_sucessivas=2,
        resolvido=False,
    )


@pytest.fixture
def falha_geracao_pc_teste_api_falha_geracao_pc_excede_tentativas(
    usuario_dre_teste_api_falha_geracao_pc,
    associacao_teste_api_falha_geracao_pc,
    periodo_teste_api_falha_geracao_pc,
):
    data_hora_ultima_ocorrencia = '2023-03-06 09:07:19'
    date_time_obj = datetime.strptime(data_hora_ultima_ocorrencia, '%Y-%m-%d %H:%M:%S')

    return baker.make(
        'FalhaGeracaoPc',
        ultimo_usuario=usuario_dre_teste_api_falha_geracao_pc,
        associacao=associacao_teste_api_falha_geracao_pc,
        periodo=periodo_teste_api_falha_geracao_pc,
        data_hora_ultima_ocorrencia=date_time_obj.strftime("%Y-%m-%dT%H:%M:%S"),
        qtd_ocorrencias_sucessivas=3,
        resolvido=False,
    )


@pytest.fixture
def falha_geracao_pc_teste_api_falha_geracao_pc_nao_exibe_modal(
    usuario_dre_teste_api_falha_geracao_pc,
    associacao_teste_api_falha_geracao_pc,
    periodo_teste_api_falha_geracao_pc,
):
    data_hora_ultima_ocorrencia = '2023-03-06 09:07:19'
    date_time_obj = datetime.strptime(data_hora_ultima_ocorrencia, '%Y-%m-%d %H:%M:%S')

    return baker.make(
        'FalhaGeracaoPc',
        ultimo_usuario=usuario_dre_teste_api_falha_geracao_pc,
        associacao=associacao_teste_api_falha_geracao_pc,
        periodo=periodo_teste_api_falha_geracao_pc,
        data_hora_ultima_ocorrencia=date_time_obj.strftime("%Y-%m-%dT%H:%M:%S"),
        qtd_ocorrencias_sucessivas=3,
        resolvido=True,
    )
