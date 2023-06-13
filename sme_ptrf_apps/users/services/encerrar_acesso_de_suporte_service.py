import logging

from ..models import UnidadeEmSuporte

logger = logging.getLogger(__name__)


class EncerraAcessoSuporteException(Exception):
    pass


def encerrar_acesso_de_suporte(unidade_do_suporte, usuario_do_suporte):
    from sme_ptrf_apps.core.models import Unidade
    from django.contrib.auth import get_user_model

    logger.info('Encerramento de acesso de suporte.')

    if not unidade_do_suporte or not isinstance(unidade_do_suporte, Unidade):
        logger.error('Não informado a unidade para encerramento de acesso de suporte.')
        raise EncerraAcessoSuporteException('É necessário informar uma unidade pelo parâmetro unidade_do_suporte')

    if not usuario_do_suporte or not isinstance(usuario_do_suporte, get_user_model()):
        logger.error('Não informado o usuário para encerramento de acesso de suporte.')
        raise EncerraAcessoSuporteException('É necessário informar um usuário do suporte pelo parâmetro usuário_do_suporte')

    logger.info(f'Encerramento de acesso de suporte solicitado por {usuario_do_suporte.username} para a unidade {unidade_do_suporte.codigo_eol}')

    usuario_do_suporte.remove_unidade_se_existir(codigo_eol=unidade_do_suporte.codigo_eol)

    if unidade_do_suporte.tipo_unidade == 'DRE' and not usuario_do_suporte.unidades.filter(tipo_unidade='DRE').exists():
        usuario_do_suporte.remove_visao_se_existir(visao='DRE')

    if unidade_do_suporte.tipo_unidade == 'UE' and not usuario_do_suporte.unidades.exclude(tipo_unidade='DRE').exists():
        usuario_do_suporte.remove_visao_se_existir(visao='UE')

    UnidadeEmSuporte.remover_acesso_suporte_se_existir(unidade=unidade_do_suporte, user=usuario_do_suporte)

    return
