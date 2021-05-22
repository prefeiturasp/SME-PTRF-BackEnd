import pytest

from ...services.unidades_e_permissoes_service import unidades_do_usuario_e_permissoes_na_visao

pytestmark = pytest.mark.django_db


def test_unidades_e_permissoes_na_visao_ue_unidade_igual_a_logada(
    usuario_unidade_a_dre_a,
    visao_ue,
    unidade_ue_a_dre_a
):
    """ Na visão UE, vínculos com a unidade UE logada pode ser excluídos."""

    unidades_e_permissoes = unidades_do_usuario_e_permissoes_na_visao(
        usuario=usuario_unidade_a_dre_a,
        visao=visao_ue.nome,
        unidade_logada=unidade_ue_a_dre_a
    )

    resultado_esperado = [
        {
            'uuid': f'{unidade_ue_a_dre_a.uuid}',
            'nome': unidade_ue_a_dre_a.nome,
            'codigo_eol': unidade_ue_a_dre_a.codigo_eol,
            'tipo_unidade': unidade_ue_a_dre_a.tipo_unidade,
            'pode_excluir': True
        }
    ]

    assert unidades_e_permissoes == resultado_esperado


def test_unidades_e_permissoes_na_visao_ue_unidade_diferente_da_logada(
    usuario_unidade_a_dre_a,
    visao_ue,
    unidade_ue_a_dre_a,
    unidade_ue_b_dre_b
):
    """ Na visão UE, vínculos com unidades UE diferentes da logada não podem ser excluidos."""

    unidades_e_permissoes = unidades_do_usuario_e_permissoes_na_visao(
        usuario=usuario_unidade_a_dre_a,
        visao=visao_ue.nome,
        unidade_logada=unidade_ue_b_dre_b
    )

    resultado_esperado = [
        {
            'uuid': f'{unidade_ue_a_dre_a.uuid}',
            'nome': unidade_ue_a_dre_a.nome,
            'codigo_eol': unidade_ue_a_dre_a.codigo_eol,
            'tipo_unidade': unidade_ue_a_dre_a.tipo_unidade,
            'pode_excluir': False
        }
    ]

    assert unidades_e_permissoes == resultado_esperado


def test_unidades_e_permissoes_na_visao_dre_unidade_da_dre_logada(
    usuario_unidade_a_dre_a,
    visao_dre,
    unidade_ue_a_dre_a,
    unidade_ue_b_dre_b,
    dre_a
):
    """ Na visão DRE, vínculos com UEs da DRE logada podem ser excluidos."""

    unidades_e_permissoes = unidades_do_usuario_e_permissoes_na_visao(
        usuario=usuario_unidade_a_dre_a,
        visao=visao_dre.nome,
        unidade_logada=dre_a
    )

    resultado_esperado = [
        {
            'uuid': f'{unidade_ue_a_dre_a.uuid}',
            'nome': unidade_ue_a_dre_a.nome,
            'codigo_eol': unidade_ue_a_dre_a.codigo_eol,
            'tipo_unidade': unidade_ue_a_dre_a.tipo_unidade,
            'pode_excluir': True
        }
    ]

    assert unidades_e_permissoes == resultado_esperado


def test_unidades_e_permissoes_na_visao_dre_unidade_nao_da_dre_logada(
    usuario_unidade_a_dre_a,
    visao_dre,
    unidade_ue_a_dre_a,
    unidade_ue_b_dre_b,
    dre_a,
    dre_b
):
    """ Na visão DRE, vínculos com UEs de outras DREs que não a logada não podem ser excluidos."""

    unidades_e_permissoes = unidades_do_usuario_e_permissoes_na_visao(
        usuario=usuario_unidade_a_dre_a,
        visao=visao_dre.nome,
        unidade_logada=dre_b
    )

    resultado_esperado = [
        {
            'uuid': f'{unidade_ue_a_dre_a.uuid}',
            'nome': unidade_ue_a_dre_a.nome,
            'codigo_eol': unidade_ue_a_dre_a.codigo_eol,
            'tipo_unidade': unidade_ue_a_dre_a.tipo_unidade,
            'pode_excluir': False
        }
    ]

    assert unidades_e_permissoes == resultado_esperado


def test_unidades_e_permissoes_na_visao_dre_unidade_dre_igual_a_dre_logada(
    usuario_dre_a,
    visao_dre,
    dre_a,
    dre_b
):
    """ Na visão DRE, vínculos com a DRE logada podem ser excluidos."""

    unidades_e_permissoes = unidades_do_usuario_e_permissoes_na_visao(
        usuario=usuario_dre_a,
        visao=visao_dre.nome,
        unidade_logada=dre_a
    )

    resultado_esperado = [
        {
            'uuid': f'{dre_a.uuid}',
            'nome': dre_a.nome,
            'codigo_eol': dre_a.codigo_eol,
            'tipo_unidade': dre_a.tipo_unidade,
            'pode_excluir': True
        }
    ]

    assert unidades_e_permissoes == resultado_esperado


def test_unidades_e_permissoes_na_visao_dre_unidade_dre_diferente_da_dre_logada(
    usuario_dre_a,
    visao_dre,
    dre_a,
    dre_b
):
    """ Na visão DRE, vínculos com outras DREs que não a DRE logada, não podem ser excluidos."""

    unidades_e_permissoes = unidades_do_usuario_e_permissoes_na_visao(
        usuario=usuario_dre_a,
        visao=visao_dre.nome,
        unidade_logada=dre_b
    )

    resultado_esperado = [
        {
            'uuid': f'{dre_a.uuid}',
            'nome': dre_a.nome,
            'codigo_eol': dre_a.codigo_eol,
            'tipo_unidade': dre_a.tipo_unidade,
            'pode_excluir': False
        }
    ]

    assert unidades_e_permissoes == resultado_esperado


def test_unidades_e_permissoes_na_visao_sme_unidade_ue(
    usuario_unidade_a_dre_a,
    visao_sme,
    unidade_ue_a_dre_a
):
    """ Na visão SME qualquer vínculo com UEs pode ser excluido."""

    unidades_e_permissoes = unidades_do_usuario_e_permissoes_na_visao(
        usuario=usuario_unidade_a_dre_a,
        visao=visao_sme.nome,
    )

    resultado_esperado = [
        {
            'uuid': f'{unidade_ue_a_dre_a.uuid}',
            'nome': unidade_ue_a_dre_a.nome,
            'codigo_eol': unidade_ue_a_dre_a.codigo_eol,
            'tipo_unidade': unidade_ue_a_dre_a.tipo_unidade,
            'pode_excluir': True
        }
    ]

    assert unidades_e_permissoes == resultado_esperado


def test_unidades_e_permissoes_na_visao_sme_unidade_dre(
    usuario_dre_a,
    visao_sme,
    dre_a
):
    """ Na visão SME qualquer vínculo com DREs pode ser excluido."""

    unidades_e_permissoes = unidades_do_usuario_e_permissoes_na_visao(
        usuario=usuario_dre_a,
        visao=visao_sme.nome,
    )

    resultado_esperado = [
        {
            'uuid': f'{dre_a.uuid}',
            'nome': dre_a.nome,
            'codigo_eol': dre_a.codigo_eol,
            'tipo_unidade': dre_a.tipo_unidade,
            'pode_excluir': True
        }
    ]

    assert unidades_e_permissoes == resultado_esperado
