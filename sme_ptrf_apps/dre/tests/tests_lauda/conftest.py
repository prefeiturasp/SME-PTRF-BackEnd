from datetime import date
import pytest
from model_bakery import baker
from django.contrib.auth import get_user_model
from ...models import ConsolidadoDRE, Lauda

pytestmark = pytest.mark.django_db


@pytest.fixture
def dre_teste_model_lauda():
    return baker.make(
        'Unidade',
        codigo_eol='108500',
        tipo_unidade='DRE',
        nome='Dre Teste Model Lauda',
        sigla='A'
    )


@pytest.fixture
def periodo_anterior_teste_model_lauda():
    return baker.make(
        'Periodo',
        referencia='2021.2',
        data_inicio_realizacao_despesas=date(2021, 6, 16),
        data_fim_realizacao_despesas=date(2021, 12, 31),
    )


@pytest.fixture
def periodo_teste_model_lauda(periodo_anterior_teste_model_lauda):
    return baker.make(
        'Periodo',
        referencia='2022.1',
        data_inicio_realizacao_despesas=date(2022, 1, 1),
        data_fim_realizacao_despesas=date(2022, 12, 31),
        periodo_anterior=periodo_anterior_teste_model_lauda,
    )


@pytest.fixture
def consolidado_dre_teste_model_lauda(dre_teste_model_lauda, periodo_teste_model_lauda):
    return baker.make(
        'ConsolidadoDRE',
        dre=dre_teste_model_lauda,
        periodo=periodo_teste_model_lauda,
        status=ConsolidadoDRE.STATUS_GERADOS_TOTAIS
    )


@pytest.fixture
def tipo_conta_cartao_teste_model_lauda():
    return baker.make('TipoConta', nome='Cartão')


@pytest.fixture
def visao_dre_teste_lauda_model():
    return baker.make('Visao', nome='DRE')


@pytest.fixture
def usuario_dre_teste_lauda_model(
    dre_teste_model_lauda,
    visao_dre_teste_lauda_model,
):
    senha = 'Sgp0418'
    login = '7654321'
    email = 'teste.lauda.model@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(dre_teste_model_lauda)
    user.visoes.add(visao_dre_teste_lauda_model)
    user.save()
    return user


@pytest.fixture
def lauda_teste_model_lauda(
    dre_teste_model_lauda,
    periodo_teste_model_lauda,
    consolidado_dre_teste_model_lauda,
    tipo_conta_cartao_teste_model_lauda,
    usuario_dre_teste_lauda_model
):
    return baker.make(
        'Lauda',
        arquivo_lauda_txt=None,
        consolidado_dre=consolidado_dre_teste_model_lauda,
        dre=dre_teste_model_lauda,
        periodo=periodo_teste_model_lauda,
        tipo_conta=tipo_conta_cartao_teste_model_lauda,
        usuario=usuario_dre_teste_lauda_model,
        status=Lauda.STATUS_NAO_GERADA
    )
