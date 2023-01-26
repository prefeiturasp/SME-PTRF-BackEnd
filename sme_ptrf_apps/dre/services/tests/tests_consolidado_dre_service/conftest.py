import pytest
from model_bakery import baker


from sme_ptrf_apps.dre.models import ConsolidadoDRE

pytestmark = pytest.mark.django_db


@pytest.fixture
def consolidado_dre_publicado_no_diario_oficial(dre, periodo):
    return baker.make(
        'ConsolidadoDRE',
        dre=dre,
        periodo=periodo,
        status_sme=ConsolidadoDRE.STATUS_SME_PUBLICADO,
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
def prestacao_conta_pc2(periodo, associacao, retificacao_dre):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=associacao,
        consolidado_dre=retificacao_dre,
        publicada=False,
        status_anterior_a_retificacao="APROVADA"
    )

@pytest.fixture
def prestacao_conta_pc3(periodo, outra_associacao, retificacao_dre):
    return baker.make(
        'PrestacaoConta',
        periodo=periodo,
        associacao=outra_associacao,
        consolidado_dre=retificacao_dre,
        publicada=False,
        status_anterior_a_retificacao="APROVADA"
    )
