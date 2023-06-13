import logging

from django.contrib.auth import get_user_model

from sme_ptrf_apps.core.models import Unidade

from ..models import UnidadeEmSuporte, User

logger = logging.getLogger(__name__)


class CriaAcessoSuporteException(Exception):
    pass


def criar_acesso_de_suporte(unidade_do_suporte: Unidade, usuario_do_suporte: User):
    logger.info('Criação de acesso de suporte.')

    if not unidade_do_suporte or not isinstance(unidade_do_suporte, Unidade):
        logger.error('Não informado a unidade para criação de acesso de suporte.')
        raise CriaAcessoSuporteException('É necessário informar uma unidade pelo parâmetro unidade_do_suporte')

    if not usuario_do_suporte or not isinstance(usuario_do_suporte, get_user_model()):
        logger.error('Não informado o usuário para criação de acesso de suporte.')
        raise CriaAcessoSuporteException('É necessário informar um usuário do suporte pelo parâmetro usuário_do_suporte')

    logger.info(f'Acesso de suporte solicitado por {usuario_do_suporte.username} para a unidade {unidade_do_suporte.codigo_eol}')

    if usuario_do_suporte.unidades.filter(codigo_eol=unidade_do_suporte.codigo_eol).exists():
        logger.info('Usuário já tem acesso à unidade. Acesso de suporte não criado.')
        return usuario_do_suporte.unidades.filter(codigo_eol=unidade_do_suporte.codigo_eol).first()

    usuario_do_suporte.add_unidade_se_nao_existir(codigo_eol=unidade_do_suporte.codigo_eol)

    if unidade_do_suporte.tipo_unidade == 'DRE':
        usuario_do_suporte.add_visao_se_nao_existir(visao='DRE')
    else:
        usuario_do_suporte.add_visao_se_nao_existir(visao='UE')

    novo_unidade_em_suporte = UnidadeEmSuporte.criar_acesso_suporte_se_nao_existir(unidade=unidade_do_suporte, user=usuario_do_suporte)

    return novo_unidade_em_suporte
