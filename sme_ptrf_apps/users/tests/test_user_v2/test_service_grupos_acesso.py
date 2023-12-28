import pytest
from sme_ptrf_apps.core.models.associacao import Associacao
from sme_ptrf_apps.users.models import Grupo

from sme_ptrf_apps.users.services.gestao_usuario_service import GestaoUsuarioService

pytestmark = pytest.mark.django_db

def test_remover_grupos_acesso_apos_remocao_acesso_unidade(usuario_factory, grupo_acesso_factory, visao_factory, dre_factory, acesso_concedido_sme_factory):
    visao_dre = visao_factory.create(nome="DRE")
    grupo_visao_dre = grupo_acesso_factory.create(visoes=[visao_dre], name="dre_1")

    dre = dre_factory.create()
    
    unidades = set()
    unidades.add(dre)
    
    usuario = usuario_factory.create(unidades=unidades)
    usuario.groups.set([grupo_visao_dre])
    
    acesso_concedido_sme_factory.create(unidade=dre, user=usuario)

    gestao_usuario = GestaoUsuarioService(usuario=usuario)

    assert list(gestao_usuario.tipos_unidades_usuario_tem_acesso(dre)) == ['DRE']
    assert usuario.groups.count() == 1
    
    gestao_usuario.desabilitar_acesso(dre)
    gestao_usuario.remover_grupos_acesso_apos_remocao_acesso_unidade(dre, "SME")
    
    assert list(gestao_usuario.tipos_unidades_usuario_tem_acesso(dre)) == []
    assert usuario.groups.count() == 0