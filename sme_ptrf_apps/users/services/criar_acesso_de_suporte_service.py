from ..models import UnidadeEmSuporte


class CriaAcessoSuporteException(Exception):
    pass


def criar_acesso_de_suporte(unidade_do_suporte, usuario_do_suporte):
    from sme_ptrf_apps.core.models import Unidade
    from django.contrib.auth import get_user_model

    if not unidade_do_suporte or not isinstance(unidade_do_suporte, Unidade):
        raise CriaAcessoSuporteException('É necessário informar uma unidade pelo parâmetro unidade_do_suporte')

    if not usuario_do_suporte or not isinstance(usuario_do_suporte, get_user_model()):
        raise CriaAcessoSuporteException('É necessário informar um usuário do suporte pelo parâmetro usuário_do_suporte')

    if usuario_do_suporte.unidades.filter(codigo_eol=unidade_do_suporte.codigo_eol).exists():
        return usuario_do_suporte.unidades.filter(codigo_eol=unidade_do_suporte.codigo_eol).first()

    usuario_do_suporte.add_unidade_se_nao_existir(codigo_eol=unidade_do_suporte.codigo_eol)

    if unidade_do_suporte.tipo_unidade == 'DRE':
        usuario_do_suporte.add_visao_se_nao_existir(visao='DRE')
    else:
        usuario_do_suporte.add_visao_se_nao_existir(visao='UE')

    novo_unidade_em_suporte = UnidadeEmSuporte.objects.create(
        unidade=unidade_do_suporte,
        user=usuario_do_suporte,
    )
    return novo_unidade_em_suporte
