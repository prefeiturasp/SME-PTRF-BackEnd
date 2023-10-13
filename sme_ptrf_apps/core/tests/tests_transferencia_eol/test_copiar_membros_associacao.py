import pytest

from sme_ptrf_apps.core.choices import MembroEnum

pytestmark = pytest.mark.django_db


def test_copiar_membros_associacao_da_original_para_a_nova(
    transf_eol_unidade_eol_transferido,
    transferencia_eol,
    transf_eol_associacao_eol_transferido,
    transf_eol_acao_associacao_ptrf,
    transf_eol_acao_associacao_role,
    transf_eol_associacao_nova,
    transf_eol_acao_ptrf,
    transf_eol_acao_role,
    transf_membro_associacao_presidente,
    transf_membro_associacao_vice_presidente
):
    assert transf_eol_associacao_eol_transferido.cargos.count() == 2
    assert transf_eol_associacao_nova.acoes.count() == 0

    transferencia_eol.copiar_membros_associacao(transf_eol_associacao_eol_transferido, transf_eol_associacao_nova)

    assert transf_eol_associacao_nova.cargos.count() == 2, "Deve ter a mesma quantidade de membros da associação original"
    assert transf_eol_associacao_eol_transferido.cargos.count() == 2, "Deve continuar com os membros originais"

    assert transf_eol_associacao_nova.cargos.filter(cargo_associacao=MembroEnum.PRESIDENTE_DIRETORIA_EXECUTIVA.value).count() == 1
    assert transf_eol_associacao_nova.cargos.filter(cargo_associacao=MembroEnum.VICE_PRESIDENTE_DIRETORIA_EXECUTIVA.value).count() == 1

