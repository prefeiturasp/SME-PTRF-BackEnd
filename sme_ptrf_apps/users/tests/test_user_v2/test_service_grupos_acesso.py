import pytest
from sme_ptrf_apps.users.models import Grupo

from sme_ptrf_apps.users.services.gestao_usuario_service import GestaoUsuarioService

pytestmark = pytest.mark.django_db

import pytest

def test_remover_grupos_acesso_apos_remocao_acesso_unidade(usuario_factory, grupo_acesso_factory, visao_factory, dre_factory):
    visao_ue = visao_factory.create(nome="UE")
    visao_dre = visao_factory.create(nome="DRE")
    visao_sme = visao_factory.create(nome="SME")

    grupo_todas_visoes = grupo_acesso_factory.create(visoes=[visao_ue, visao_dre, visao_sme])

    grupo_visao_dre = grupo_acesso_factory.create(visoes=[visao_dre])

    grupo_visao_ue = grupo_acesso_factory.create(visoes=[visao_ue])

    dre = dre_factory.create()

    usuario = usuario_factory.create()
    usuario.groups.set([grupo_todas_visoes, grupo_visao_dre, grupo_visao_ue])
    usuario.unidades.set([dre])

    gestao_usuario = GestaoUsuarioService(usuario=usuario)

    assert list(gestao_usuario.tipos_unidades_usuario_tem_acesso()) == ["DRE"]
    usuario.unidades.remove(dre)
    gestao_usuario.remover_grupos_acesso_apos_remocao_acesso_unidade(dre)
    assert list(gestao_usuario.tipos_unidades_usuario_tem_acesso()) == []

    assert usuario.groups.all().filter(name=grupo_visao_dre.name).exists() == False
    assert usuario.groups.all().filter(name=grupo_visao_ue.name).exists() == True


