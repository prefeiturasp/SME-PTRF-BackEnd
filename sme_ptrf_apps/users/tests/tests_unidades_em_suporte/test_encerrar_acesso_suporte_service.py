import pytest

from ...models import UnidadeEmSuporte
from ...services import encerrar_acesso_de_suporte, EncerraAcessoSuporteException

pytestmark = pytest.mark.django_db


def test_encerra_acesso_suporte_dre(
    unidade_dre_em_suporte,
    usuario_do_suporte_com_acesso_dre,
    dre,
    visao_ue, visao_dre, visao_sme,
):
    assert usuario_do_suporte_com_acesso_dre.unidades.filter(codigo_eol=dre.codigo_eol).exists(), "Deveria haver um acesso à DRE."
    assert usuario_do_suporte_com_acesso_dre.visoes.filter(nome='DRE').exists(), "Deveria haver a visão DRE para o usuário."
    assert UnidadeEmSuporte.objects.filter(unidade=dre, user=usuario_do_suporte_com_acesso_dre).exists(), "Deveria haver unidade em suporte."

    encerrar_acesso_de_suporte(
        unidade_do_suporte=dre,
        usuario_do_suporte=usuario_do_suporte_com_acesso_dre
    )

    assert not usuario_do_suporte_com_acesso_dre.unidades.filter(codigo_eol=dre.codigo_eol).exists(), "Não deveria haver um acesso do usuário à DRE."
    assert not usuario_do_suporte_com_acesso_dre.visoes.filter(nome='DRE').exists(), "Deveria ter sido desvinculada a visão DRE para usuário."
    assert not UnidadeEmSuporte.objects.filter(unidade=dre, user=usuario_do_suporte_com_acesso_dre).exists(), "Não deveria haver unidade em suporte."


def test_encerrar_acesso_suporte_sem_informar_unidade_do_suporte(
    unidade_do_suporte_tipo_dre,
    usuario_do_suporte,
    visao_ue, visao_dre, visao_sme
):
    with pytest.raises(EncerraAcessoSuporteException):
        encerrar_acesso_de_suporte(
            unidade_do_suporte=None,
            usuario_do_suporte=usuario_do_suporte
        )

    with pytest.raises(EncerraAcessoSuporteException):
        encerrar_acesso_de_suporte(
            unidade_do_suporte="Não objeto unidade",
            usuario_do_suporte=usuario_do_suporte
        )


def test_encerrar_acesso_suporte_sem_informar_usuario_do_suporte(
    unidade_do_suporte_tipo_dre,
    usuario_do_suporte,
    visao_ue, visao_dre, visao_sme
):
    with pytest.raises(EncerraAcessoSuporteException):
        encerrar_acesso_de_suporte(
            unidade_do_suporte=unidade_do_suporte_tipo_dre,
            usuario_do_suporte=None
        )

    with pytest.raises(EncerraAcessoSuporteException):
        encerrar_acesso_de_suporte(
            unidade_do_suporte=unidade_do_suporte_tipo_dre,
            usuario_do_suporte="Não objeto User"
        )
