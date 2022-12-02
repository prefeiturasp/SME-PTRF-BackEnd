import pytest


from ..dre_service import DreService

pytestmark = pytest.mark.django_db


def test_get_comissao_contas(
    dre_valida,
    jose_membro_comissao_exame_contas_da_dre,
    ana_membro_comissao_exame_contas_da_dre,
    pedro_membro_outra_comissao_da_dre,
    maria_membro_comissao_exame_contas_de_outra_dre,
    parametros_dre_comissoes,
):
    dre_service = DreService(dre_valida)

    comissao = dre_service.get_comissao_exame_contas()

    assert comissao.count() == 2
    assert comissao.filter(nome=jose_membro_comissao_exame_contas_da_dre.nome).exists()
    assert comissao.filter(nome=ana_membro_comissao_exame_contas_da_dre.nome).exists()
    assert not comissao.filter(nome=pedro_membro_outra_comissao_da_dre.nome).exists()
    assert not comissao.filter(nome=maria_membro_comissao_exame_contas_de_outra_dre.nome).exists()
