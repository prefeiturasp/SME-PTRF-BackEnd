import pytest
from model_bakery import baker
from sme_ptrf_apps.core.models import RelacaoBens
from sme_ptrf_apps.core.services.relacao_bens import (
    apagar_previas_relacao_de_bens,
    gerar_arquivo_relacao_de_bens_dados_persistidos,
    _persistir_arquivo_relacao_de_bens,
)

pytestmark = pytest.mark.django_db


def test_nao_gerar_relacao_bens(periodo, conta_associacao, prestacao_conta):
    assert not RelacaoBens.objects.filter(conta_associacao=conta_associacao, prestacao_conta=prestacao_conta).first()


def test_apagar_previas_remove_relacao_bens(periodo, conta_associacao):
    baker.make(
        'RelacaoBens',
        conta_associacao=conta_associacao,
        periodo_previa=periodo,
        versao=RelacaoBens.VERSAO_PREVIA,
    )
    assert RelacaoBens.objects.filter(periodo_previa=periodo, conta_associacao=conta_associacao).exists()

    apagar_previas_relacao_de_bens(periodo=periodo, conta_associacao=conta_associacao)

    assert not RelacaoBens.objects.filter(periodo_previa=periodo, conta_associacao=conta_associacao).exists()


def test_apagar_previas_sem_relacao_bens_nao_falha(periodo, conta_associacao):
    # Deve executar sem erros quando não há nada para apagar
    apagar_previas_relacao_de_bens(periodo=periodo, conta_associacao=conta_associacao)


def test_persistir_arquivo_sem_rateios_retorna_none(periodo, conta_associacao):
    result = _persistir_arquivo_relacao_de_bens(
        periodo=periodo,
        conta_associacao=conta_associacao,
        usuario='test_user',
    )

    assert result is None


def test_gerar_arquivo_dados_persistidos_sem_relatorio_nao_falha(relacao_bens_final):
    # Quando não há RelatorioRelacaoBens associado, não deve lançar exceção
    gerar_arquivo_relacao_de_bens_dados_persistidos(relacao_bens=relacao_bens_final)
