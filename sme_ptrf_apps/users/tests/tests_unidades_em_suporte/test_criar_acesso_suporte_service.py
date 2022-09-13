import pytest

from ...models import UnidadeEmSuporte
from ...services import criar_acesso_de_suporte, CriaAcessoSuporteException

pytestmark = pytest.mark.django_db


def test_criar_acesso_suporte_ue_quando_ainda_nao_existe_e_user_nao_tem_visao_ue(
    unidade_do_suporte,
    usuario_do_suporte,
    visao_ue, visao_dre, visao_sme
):
    assert not usuario_do_suporte.unidades.filter(codigo_eol=unidade_do_suporte.codigo_eol).exists(), "Não deveria haver um acesso à unidade ainda."
    assert not usuario_do_suporte.visoes.filter(nome='UE').exists(), "Não deveria haver a visão UE para o usuário ainda."
    assert not UnidadeEmSuporte.objects.exists(), "Não deveria haver unidades em suporte ainda."

    novo_unidade_em_suporte_retornada = criar_acesso_de_suporte(
        unidade_do_suporte=unidade_do_suporte,
        usuario_do_suporte=usuario_do_suporte
    )

    assert usuario_do_suporte.unidades.filter(codigo_eol=unidade_do_suporte.codigo_eol).exists(), "Deveria haver um acesso do usuário à unidade."
    assert UnidadeEmSuporte.objects.filter(unidade=unidade_do_suporte).exists(), "A unidade deveria estar registrada como unidade em suporte."
    assert novo_unidade_em_suporte_retornada == UnidadeEmSuporte.objects.filter(unidade=unidade_do_suporte).first(), "Deveria retornar a UnidadeEmSuporte criada."
    assert usuario_do_suporte.visoes.filter(nome='UE').exists(), "Deveria ter sido vinculada a visão UE ao usuário."


def test_criar_acesso_suporte_dre_quando_ainda_nao_existe_e_user_nao_tem_visao_dre(
    unidade_do_suporte_tipo_dre,
    usuario_do_suporte,
    visao_ue, visao_dre, visao_sme
):
    assert not usuario_do_suporte.unidades.filter(codigo_eol=unidade_do_suporte_tipo_dre.codigo_eol).exists(), "Não deveria haver um acesso à unidade DRE ainda."
    assert not usuario_do_suporte.visoes.filter(nome='DRE').exists(), "Não deveria haver a visão DRE para o usuário ainda."
    assert not UnidadeEmSuporte.objects.exists(), "Não deveria haver unidades em suporte ainda."

    novo_unidade_em_suporte_retornada = criar_acesso_de_suporte(
        unidade_do_suporte=unidade_do_suporte_tipo_dre,
        usuario_do_suporte=usuario_do_suporte
    )

    assert usuario_do_suporte.unidades.filter(codigo_eol=unidade_do_suporte_tipo_dre.codigo_eol).exists(), "Deveria haver um acesso do usuário à DRE."
    assert UnidadeEmSuporte.objects.filter(unidade=unidade_do_suporte_tipo_dre).exists(), "A DRE deveria estar registrada como unidade em suporte."
    assert novo_unidade_em_suporte_retornada == UnidadeEmSuporte.objects.filter(unidade=unidade_do_suporte_tipo_dre).first(), "Deveria retornar a UnidadeEmSuporte criada."
    assert usuario_do_suporte.visoes.filter(nome='DRE').exists(), "Deveria ter sido vinculada a visão DRE ao usuário."


def test_criar_acesso_suporte_sem_informar_unidade_do_suporte(
    unidade_do_suporte_tipo_dre,
    usuario_do_suporte,
    visao_ue, visao_dre, visao_sme
):
    with pytest.raises(CriaAcessoSuporteException):
        criar_acesso_de_suporte(
            unidade_do_suporte=None,
            usuario_do_suporte=usuario_do_suporte
        )

    with pytest.raises(CriaAcessoSuporteException):
        criar_acesso_de_suporte(
            unidade_do_suporte="Não objeto unidade",
            usuario_do_suporte=usuario_do_suporte
        )


def test_criar_acesso_suporte_sem_informar_usuario_do_suporte(
    unidade_do_suporte_tipo_dre,
    usuario_do_suporte,
    visao_ue, visao_dre, visao_sme
):
    with pytest.raises(CriaAcessoSuporteException):
        criar_acesso_de_suporte(
            unidade_do_suporte=unidade_do_suporte_tipo_dre,
            usuario_do_suporte=None
        )

    with pytest.raises(CriaAcessoSuporteException):
        criar_acesso_de_suporte(
            unidade_do_suporte=unidade_do_suporte_tipo_dre,
            usuario_do_suporte="Não objeto User"
        )
