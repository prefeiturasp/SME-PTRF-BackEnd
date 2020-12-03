import logging
from datetime import date
from sme_ptrf_apps.core.choices import MembroEnum
from sme_ptrf_apps.core.models import (
    Associacao,
    Categoria,
    ComentarioAnalisePrestacao,
    MembroAssociacao,
    Notificacao,
    Periodo,
    Remetente,
    TipoNotificacao,
)

logger = logging.getLogger(__name__)


def formata_data(data):
    meses = ('Jan.', 'Fev.', 'Mar.', 'Abr.', 'Mai.', 'Jun.', 'Jul.', 'Ago.', 'Set.', 'Out.', 'Nov.', 'Dez.')
    diasemana = ('Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo')
    ds = diasemana[date.weekday(data)] if data != date.today() else 'Hoje'
    ms = meses[data.month-1]

    return f"{ds} {data.day:0>2} {ms} {data.year}"


def notificar_usuario(dado):
    logging.info("Criando notificações.")

    associacao = Associacao.by_uuid(dado['associacao'])
    periodo = Periodo.by_uuid(dado['periodo'])
    comentarios = [ComentarioAnalisePrestacao.by_uuid(uuid) for uuid in dado['comentarios']]

    tipo = TipoNotificacao.objects.filter(nome="Aviso").first()
    categoria = Categoria.objects.filter(nome="Comentário na prestação de contas").first()
    remetente = Remetente.objects.filter(nome="DRE").first()
    titulo = f"Comentário feito em sua prestação de contas de {periodo.referencia}."

    cargos = [MembroEnum.PRESIDENTE_DIRETORIA_EXECUTIVA.value, MembroEnum.VICE_PRESIDENTE_DIRETORIA_EXECUTIVA.value]
    membros = associacao.cargos.filter(cargo_associacao__in=cargos)

    for membro in membros:
        for comentario in comentarios:
            Notificacao.objects.create(
                tipo=tipo,
                categoria=categoria,
                remetente=remetente,
                titulo=titulo,
                descricao=comentario.comentario,
                usuario=membro.usuario
            )
    logger.info("Notificações criadas com sucesso.")
