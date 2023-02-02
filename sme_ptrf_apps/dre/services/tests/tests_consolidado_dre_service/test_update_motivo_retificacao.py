
import pytest

from sme_ptrf_apps.core.models import PrestacaoConta
from sme_ptrf_apps.dre.models import ConsolidadoDRE
from sme_ptrf_apps.dre.services.consolidado_dre_service import update_motivo_retificacao

pytestmark = pytest.mark.django_db

import logging


logger = logging.getLogger(__name__)

def test_update_motivo_retificacao_em_branco_deve_levantar_excecao(retificacao_dre):
    with pytest.raises(Exception) as excinfo:
        update_motivo_retificacao(
            retificacao=retificacao_dre,
            motivo="",
        )
    assert 'É necessário informar o motivo da retificação' in str(excinfo.value)

def test_update_motivo_retificacao(retificacao_dre):
    update_motivo_retificacao(
            retificacao=retificacao_dre,
            motivo="Testando12345#",
        )

    assert retificacao_dre.motivo_retificacao == "Testando12345#"
