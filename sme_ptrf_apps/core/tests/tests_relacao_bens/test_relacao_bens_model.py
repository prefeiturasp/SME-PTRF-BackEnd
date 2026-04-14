import pytest
from sme_ptrf_apps.core.models import RelacaoBens

pytestmark = pytest.mark.django_db


def test_arquivo_concluido_atualiza_status(relacao_bens_em_processamento):
    relacao_bens_em_processamento.arquivo_concluido()
    relacao_bens_em_processamento.refresh_from_db()

    assert relacao_bens_em_processamento.status == RelacaoBens.STATUS_CONCLUIDO


def test_arquivo_a_processar_atualiza_status(relacao_bens_previa):
    relacao_bens_previa.arquivo_a_processar()
    relacao_bens_previa.refresh_from_db()

    assert relacao_bens_previa.status == RelacaoBens.STATUS_A_PROCESSAR


def test_previa_property_true_para_versao_previa(relacao_bens_previa):
    assert relacao_bens_previa.previa is True


def test_previa_property_false_para_versao_final(relacao_bens_final):
    assert relacao_bens_final.previa is False


def test_str_quando_concluido(relacao_bens_previa):
    result = str(relacao_bens_previa)

    assert "Documento" in result
    assert "prévio" in result
    assert "gerado dia" in result


def test_str_quando_em_processamento(relacao_bens_em_processamento):
    result = str(relacao_bens_em_processamento)

    assert "sendo gerado" in result
    assert "Aguarde" in result


def test_str_versao_final_concluido(relacao_bens_final):
    result = str(relacao_bens_final)

    assert "final" in result
    assert "gerado dia" in result


def test_status_choices_disponiveis():
    choices_values = [c[0] for c in RelacaoBens.STATUS_CHOICES]

    assert RelacaoBens.STATUS_EM_PROCESSAMENTO in choices_values
    assert RelacaoBens.STATUS_CONCLUIDO in choices_values
    assert RelacaoBens.STATUS_A_PROCESSAR in choices_values


def test_versao_choices_disponiveis():
    choices_values = [c[0] for c in RelacaoBens.VERSAO_CHOICES]

    assert RelacaoBens.VERSAO_FINAL in choices_values
    assert RelacaoBens.VERSAO_PREVIA in choices_values
