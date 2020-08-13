import logging

from rest_framework.exceptions import ValidationError

from ..models import (GrupoVerificacaoRegularidade, VerificacaoRegularidadeAssociacao, ItemVerificacaoRegularidade)
from ...core.models import Associacao

logger = logging.getLogger(__name__)

def verifica_regularidade_associacao(associacao_uuid):
    associacao = Associacao.by_uuid(associacao_uuid)

    grupos = []
    for grupo in GrupoVerificacaoRegularidade.objects.all():
        listas = []
        for lista in grupo.listas_de_verificacao.all():
            itens = []
            qtd_irregulares = 0
            for item in lista.itens_de_verificacao.all():
                verificacao = VerificacaoRegularidadeAssociacao.objects.filter(associacao=associacao,
                                                                               item_verificacao=item).first()
                if not verificacao or not verificacao.regular:
                    qtd_irregulares += 1

                itens.append(
                    {
                        'descricao': item.descricao,
                        'regular': verificacao.regular if verificacao else False,
                        'uuid': f'{item.uuid}'
                    }
                )
            listas.append(
                {
                    'itens_verificacao': itens,
                    'status_lista_verificacao': 'Regular' if qtd_irregulares == 0 else 'Pendente',
                    'titulo': lista.titulo,
                    'uuid': f'{lista.uuid}'
                }
            )
        grupos.append(
            {
                'listas_verificacao': listas,
                'titulo': grupo.titulo,
                'uuid': f'{grupo.uuid}'
            }
        )

    result = {
        'uuid': f'{associacao.uuid}',
        'verificacao_regularidade': {
            'grupos_verificacao': grupos
        }
    }
    return result


def marca_item_verificacao_associacao(associacao_uuid, item_verificacao_uuid):
    associacao = Associacao.by_uuid(associacao_uuid)

    if not associacao:
        msgError = f'Associacao não encontrada. UUID:{associacao_uuid}'
        logger.info(msgError)
        raise ValidationError(msgError)

    item_verificacao = ItemVerificacaoRegularidade.by_uuid(item_verificacao_uuid)

    if not item_verificacao:
        msgError = f'Item de verificação não encontrado. UUID:{item_verificacao_uuid}'
        logger.info(msgError)
        raise ValidationError(msgError)

    result = VerificacaoRegularidadeAssociacao.objects.get_or_create(
        associacao=associacao,
        item_verificacao=item_verificacao,
        defaults={
            'grupo_verificacao': item_verificacao.lista.grupo,
            'lista_verificacao': item_verificacao.lista,
            'regular': True,
        }
    ) if associacao and item_verificacao else None

    logger.info(f'Item de verificação marcado {result}')

    return result


def desmarca_item_verificacao_associacao(associacao_uuid, item_verificacao_uuid):
    associacao = Associacao.by_uuid(associacao_uuid)
    item_verificacao = ItemVerificacaoRegularidade.by_uuid(item_verificacao_uuid)

    VerificacaoRegularidadeAssociacao.objects.filter(
        associacao=associacao,
        item_verificacao=item_verificacao
    ).delete()

    return 'OK' if associacao and item_verificacao else None

