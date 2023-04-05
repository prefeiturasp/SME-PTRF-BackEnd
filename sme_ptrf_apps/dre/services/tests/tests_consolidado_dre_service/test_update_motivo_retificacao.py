
import pytest

from sme_ptrf_apps.dre.services.consolidado_dre_service import update_motivo_retificacao

pytestmark = pytest.mark.django_db


def test_update_motivo_retificacao_em_branco_deve_levantar_excecao__motivo_nao_eh_mais_obrigatorio(retificacao_dre):
    try:
        update_motivo_retificacao(
                retificacao=retificacao_dre,
                motivo="",
            )
    except Exception as exc:
        assert False, f"'É necessário informar o motivo da retificação {exc}"

def test_update_motivo_retificacao(retificacao_dre):
    assert retificacao_dre.motivo_retificacao == "motivo retificacao"

    update_motivo_retificacao(
            retificacao=retificacao_dre,
            motivo="Testando12345#",
        )

    assert retificacao_dre.motivo_retificacao == "Testando12345#"
