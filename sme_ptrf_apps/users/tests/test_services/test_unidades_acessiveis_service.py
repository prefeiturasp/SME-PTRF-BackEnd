import pytest
from model_bakery import baker

from sme_ptrf_apps.users.services.unidades_acessiveis_service import unidades_acessiveis_do_usuario

pytestmark = pytest.mark.django_db


def test_ue_so_acessa_unidades_vinculadas(usuario, unidade, outra_unidade):
    qs = unidades_acessiveis_do_usuario(usuario)
    assert unidade in qs
    assert outra_unidade not in qs


def test_dre_acessa_ues_da_propria_dre(usuario, dre, unidade, outra_unidade):
    usuario.unidades.clear()
    usuario.unidades.add(dre)

    qs = unidades_acessiveis_do_usuario(usuario)
    assert dre in qs
    assert unidade in qs
    assert outra_unidade in qs


def test_dre_nao_acessa_ue_de_outra_dre(usuario, dre):
    outra_dre = baker.make('Unidade', codigo_eol='888880', tipo_unidade='DRE', nome='Outra DRE')
    unidade_outra_dre = baker.make(
        'Unidade',
        codigo_eol='666660',
        tipo_unidade='CEU',
        nome='UE de outra DRE',
        dre=outra_dre,
    )
    usuario.unidades.clear()
    usuario.unidades.add(dre)

    qs = unidades_acessiveis_do_usuario(usuario)
    assert unidade_outra_dre not in qs


def test_sme_acessa_todas_as_unidades(usuario, unidade, outra_unidade):
    visao_sme = baker.make('Visao', nome='SME')
    usuario.visoes.add(visao_sme)
    usuario.unidades.clear()

    qs = unidades_acessiveis_do_usuario(usuario)
    assert unidade in qs
    assert outra_unidade in qs
