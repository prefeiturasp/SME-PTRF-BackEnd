
import pytest

from sme_ptrf_apps.core.models import PrestacaoConta
from sme_ptrf_apps.dre.models import ConsolidadoDRE
from sme_ptrf_apps.dre.services.consolidado_dre_service import update_retificacao

pytestmark = pytest.mark.django_db


def test_update_retificacao_sem_motivo_deve_levantar_excecao(
    retificacao_dre,
    prestacao_conta_pc1
):

    with pytest.raises(Exception) as excinfo:
        update_retificacao(
            retificacao=retificacao_dre,
            prestacoes_de_conta_a_retificar=[prestacao_conta_pc1.uuid],
            motivo="",
        )
    assert 'É necessário informar o motivo da retificação' in str(excinfo.value)


def test_update_retificacao_sem_pcs_deve_levantar_excecao(
    retificacao_dre,
    prestacao_conta_pc1,
):
    with pytest.raises(Exception) as excinfo:
        update_retificacao(
            retificacao=retificacao_dre,
            prestacoes_de_conta_a_retificar=[],
            motivo="Teste",
        )
    assert 'Nenhuma prestação de conta selecionada para retificação.' in str(excinfo.value)


def test_update_retificacao(
    jwt_authenticated_client_dre,
    retificacao_dre,
    prestacao_conta_pc1,
    prestacao_conta_pc3
):
    consolidado_original = retificacao_dre.consolidado_retificado

    assert consolidado_original.prestacoes_de_conta_do_consolidado_dre.all().count() == 1
    assert retificacao_dre.prestacoes_de_conta_do_consolidado_dre.all().count() == 1


    update_retificacao(
        retificacao=retificacao_dre,
        prestacoes_de_conta_a_retificar=[prestacao_conta_pc1.uuid],
        motivo="novo motivo"
    )

    retificacao_dre.refresh_from_db()

    # PC foi retirada do consolidado original
    assert consolidado_original.prestacoes_de_conta_do_consolidado_dre.all().count() == 0

    # PC foi inserida na retificacao
    assert retificacao_dre.prestacoes_de_conta_do_consolidado_dre.all().count() == 2

    prestacao_conta_pc1.refresh_from_db()
    assert prestacao_conta_pc1.consolidado_dre == retificacao_dre
    assert prestacao_conta_pc1.publicada is False
    assert prestacao_conta_pc1.status == PrestacaoConta.STATUS_RECEBIDA

