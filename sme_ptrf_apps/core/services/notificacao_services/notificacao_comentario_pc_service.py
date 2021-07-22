import logging
from datetime import date

from django.contrib.auth import get_user_model

from sme_ptrf_apps.core.choices import MembroEnum
from sme_ptrf_apps.core.models import (
    Associacao,
    ComentarioAnalisePrestacao,
    Notificacao,
    Periodo,
)

User = get_user_model()

logger = logging.getLogger(__name__)


def notificar_comentario_pc(dado):
    logging.info("Criando notificações.")

    associacao = Associacao.by_uuid(dado['associacao'])
    periodo = Periodo.by_uuid(dado['periodo'])
    comentarios = [ComentarioAnalisePrestacao.by_uuid(uuid) for uuid in dado['comentarios']]

    tipo = Notificacao.TIPO_NOTIFICACAO_AVISO
    categoria = Notificacao.CATEGORIA_NOTIFICACAO_COMENTARIO_PC
    remetente = Notificacao.REMETENTE_NOTIFICACAO_DRE
    titulo = f"Comentário feito em sua prestação de contas de {periodo.referencia}."

    cargos = [MembroEnum.PRESIDENTE_DIRETORIA_EXECUTIVA.name, MembroEnum.VICE_PRESIDENTE_DIRETORIA_EXECUTIVA.name]
    membros = associacao.cargos.filter(cargo_associacao__in=cargos)

    for membro in membros:
        usuario = None
        if membro.codigo_identificacao:
            usuario = User.objects.filter(username=membro.codigo_identificacao).first()
        else:
            usuario = User.objects.filter(username=membro.cpf).first()

        if usuario:
            for comentario in comentarios:
                Notificacao.notificar(
                    tipo=tipo,
                    categoria=categoria,
                    remetente=remetente,
                    titulo=titulo,
                    descricao=comentario.comentario,
                    usuario=usuario,
                    renotificar=False,
                )
            logger.info("Notificações criadas com sucesso.")
