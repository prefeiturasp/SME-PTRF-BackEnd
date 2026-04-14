import pytest
from model_bakery import baker
from sme_ptrf_apps.core.models import RelacaoBens
from sme_ptrf_apps.core.admin import RelacaoBensAdmin
from django.contrib.admin.sites import site


@pytest.fixture
def relacao_bens_admin():
    return RelacaoBensAdmin(model=RelacaoBens, admin_site=site)


@pytest.fixture
def relacao_bens_previa(conta_associacao, periodo):
    return baker.make(
        'RelacaoBens',
        conta_associacao=conta_associacao,
        periodo_previa=periodo,
        prestacao_conta=None,
        versao=RelacaoBens.VERSAO_PREVIA,
        status=RelacaoBens.STATUS_CONCLUIDO,
    )


@pytest.fixture
def relacao_bens_final(conta_associacao, prestacao_conta):
    return baker.make(
        'RelacaoBens',
        conta_associacao=conta_associacao,
        prestacao_conta=prestacao_conta,
        periodo_previa=None,
        versao=RelacaoBens.VERSAO_FINAL,
        status=RelacaoBens.STATUS_CONCLUIDO,
    )


@pytest.fixture
def relacao_bens_em_processamento(conta_associacao, periodo):
    return baker.make(
        'RelacaoBens',
        conta_associacao=conta_associacao,
        periodo_previa=periodo,
        prestacao_conta=None,
        versao=RelacaoBens.VERSAO_PREVIA,
        status=RelacaoBens.STATUS_EM_PROCESSAMENTO,
    )
