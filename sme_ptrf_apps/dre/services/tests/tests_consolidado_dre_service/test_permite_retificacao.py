
import pytest

pytestmark = pytest.mark.django_db


def test_permite_retificacao_consolidado_sem_retificacoes(
    jwt_authenticated_client_dre,
    consolidado_dre_publicado_no_diario_oficial,
    prestacao_conta_pc1,
):
    result = consolidado_dre_publicado_no_diario_oficial.permite_retificacao

    assert result["permite"] is True
    assert result["tooltip"] == ""


def test_permite_retificacao_consolidado_com_retificacoes_nao_geradas(
    jwt_authenticated_client_dre,
    consolidado_dre_publicado_no_diario_oficial,
    retificacao_dre,
    prestacao_conta_pc1,
    prestacao_conta_pc2,
    prestacao_conta_pc3
):
    result = consolidado_dre_publicado_no_diario_oficial.permite_retificacao

    assert result["permite"] is False
    assert result["tooltip"] == "As PCs habilitadas para retificação estão disponíveis na edição " \
                                "da retificação desta publicação."


def test_permite_retificacao_consolidado_com_retificacoes_geradas(
    jwt_authenticated_client_dre,
    consolidado_dre_publicado_no_diario_oficial,
    retificacao_dre,
    prestacao_conta_pc1,
    prestacao_conta_pc2,
    prestacao_conta_pc3,
    lauda_vinculada_a_retificacao
):
    result = consolidado_dre_publicado_no_diario_oficial.permite_retificacao

    assert result["permite"] is True
    assert result["tooltip"] == ""


def test_permite_retificacao_consolidado_com_pcs_retificaveis(
    jwt_authenticated_client_dre,
    consolidado_dre_publicado_no_diario_oficial,
    prestacao_conta_pc1,
    retificacao_dre,
    prestacao_conta_pc2,
    prestacao_conta_pc3,
    lauda_vinculada_a_retificacao
):
    result = consolidado_dre_publicado_no_diario_oficial.permite_retificacao

    assert result["permite"] is True
    assert result["tooltip"] == ""


def test_permite_retificacao_consolidado_sem_pcs_retificaveis(
    jwt_authenticated_client_dre,
    consolidado_dre_publicado_no_diario_oficial,
    retificacao_dre,
    prestacao_conta_pc2,
    prestacao_conta_pc3,
    lauda_vinculada_a_retificacao
):
    result = consolidado_dre_publicado_no_diario_oficial.permite_retificacao

    assert result["permite"] is False
    assert result["tooltip"] == "Esta publicação não possui PCs disponíveis para retificação"


def test_tooltip_permite_retificar_pc(
    jwt_authenticated_client_dre,
    consolidado_dre_publicado_no_diario_oficial,
    retificacao_dre,
    prestacao_conta_pc1,
    prestacao_conta_pc2,
    prestacao_conta_pc3,
):

    assert prestacao_conta_pc1.get_tooltip_nao_pode_retificar is None
    assert prestacao_conta_pc2.get_tooltip_nao_pode_retificar == "Esta PC foi retificada em outra publicação."
    assert prestacao_conta_pc3.get_tooltip_nao_pode_retificar == "Esta PC foi retificada em outra publicação."


