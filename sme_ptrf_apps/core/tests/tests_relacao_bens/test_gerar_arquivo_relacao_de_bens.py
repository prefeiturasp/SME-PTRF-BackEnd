import pytest
from rest_framework import status
from sme_ptrf_apps.core.services.relacao_bens import gerar_arquivo_relacao_de_bens
from sme_ptrf_apps.core.models import RelacaoBens

pytestmark = pytest.mark.django_db


def test_nao_gerar_relacao_bens(periodo, conta_associacao, prestacao_conta):
    assert not RelacaoBens.objects.filter(conta_associacao=conta_associacao, prestacao_conta=prestacao_conta).first()
