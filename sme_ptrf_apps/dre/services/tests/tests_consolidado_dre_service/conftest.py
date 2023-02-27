import pytest
from model_bakery import baker
from sme_ptrf_apps.core.models import PrestacaoConta
from sme_ptrf_apps.dre.models import Lauda
from django.contrib.auth import get_user_model

from sme_ptrf_apps.dre.models import ConsolidadoDRE

pytestmark = pytest.mark.django_db


@pytest.fixture
def consolidado_dre_publicado_no_diario_oficial(dre, periodo):
    return baker.make(
        'ConsolidadoDRE',
        dre=dre,
        periodo=periodo,
        status_sme=ConsolidadoDRE.STATUS_SME_PUBLICADO,
        gerou_uma_retificacao=True
    )


@pytest.fixture
def consolidado_dre_nao_publicado_no_diario_oficial(dre, periodo):
    return baker.make(
        'ConsolidadoDRE',
        dre=dre,
        periodo=periodo,
        status_sme=ConsolidadoDRE.STATUS_SME_NAO_PUBLICADO,
    )


@pytest.fixture
def prestacao_conta_pc1(periodo, associacao, consolidado_dre_publicado_no_diario_oficial):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        consolidado_dre=consolidado_dre_publicado_no_diario_oficial,
        publicada=True,
    )

@pytest.fixture
def prestacao_conta_pc1_com_status_anterior(periodo, associacao, consolidado_dre_publicado_no_diario_oficial):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        consolidado_dre=consolidado_dre_publicado_no_diario_oficial,
        publicada=True,
        status_anterior_a_retificacao="APROVADA",
    )

@pytest.fixture
def retificacao_dre(periodo, dre, consolidado_dre_publicado_no_diario_oficial):
    return baker.make(
        'ConsolidadoDRE',
        dre=dre,
        periodo=periodo,
        status=ConsolidadoDRE.STATUS_NAO_GERADOS,
        consolidado_retificado=consolidado_dre_publicado_no_diario_oficial,
        motivo_retificacao="motivo retificacao"
    )


@pytest.fixture
def prestacao_conta_pc2(periodo, associacao_status_nao_finalizado, retificacao_dre):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao_status_nao_finalizado,
        consolidado_dre=retificacao_dre,
        publicada=False,
        status_anterior_a_retificacao="APROVADA",
        status=PrestacaoConta.STATUS_RECEBIDA
    )

@pytest.fixture
def prestacao_conta_pc3(periodo, outra_associacao, retificacao_dre):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=outra_associacao,
        consolidado_dre=retificacao_dre,
        publicada=False,
        status_anterior_a_retificacao="APROVADA",
        status=PrestacaoConta.STATUS_EM_ANALISE
    )

@pytest.fixture
def tipo_conta_cartao_teste_model_lauda_vinculada_a_retificacao():
    return baker.make('TipoConta', nome='Cartão')


@pytest.fixture
def visao_dre_teste_lauda_model_lauda_vinculada_a_retificacao():
    return baker.make('Visao', nome='DRE')


@pytest.fixture
def usuario_dre_teste_lauda_model_lauda_vinculada_a_retificacao(
    dre,
    visao_dre_teste_lauda_model_lauda_vinculada_a_retificacao,
):
    senha = 'Sgp0418'
    login = '7654321'
    email = 'teste.lauda.model@amcom.com.br'
    User = get_user_model()
    user = User.objects.create_user(username=login, password=senha, email=email)
    user.unidades.add(dre)
    user.visoes.add(visao_dre_teste_lauda_model_lauda_vinculada_a_retificacao)
    user.save()
    return user

@pytest.fixture
def lauda_vinculada_a_retificacao(
    dre,
    periodo,
    retificacao_dre,
    tipo_conta_cartao_teste_model_lauda_vinculada_a_retificacao,
    usuario_dre_teste_lauda_model_lauda_vinculada_a_retificacao
):
    return baker.make(
        'Lauda',
        arquivo_lauda_txt=None,
        consolidado_dre=retificacao_dre,
        dre=dre,
        periodo=periodo,
        tipo_conta=tipo_conta_cartao_teste_model_lauda_vinculada_a_retificacao,
        usuario=usuario_dre_teste_lauda_model_lauda_vinculada_a_retificacao,
        status=Lauda.STATUS_GERADA_TOTAL
    )
