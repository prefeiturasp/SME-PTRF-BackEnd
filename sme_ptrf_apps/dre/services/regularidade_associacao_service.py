import logging

from django.db.models import Q

from rest_framework.exceptions import ValidationError

from ..models import (
    GrupoVerificacaoRegularidade,
    VerificacaoRegularidadeAssociacao,
    ItemVerificacaoRegularidade,
    ListaVerificacaoRegularidade,
    AnaliseRegularidadeAssociacao
)
from ...core.models import Associacao

logger = logging.getLogger(__name__)


def verifica_regularidade_associacao(associacao_uuid, ano):

    analise_regularidade_ano = AnaliseRegularidadeAssociacao.objects.filter(
        associacao__uuid=associacao_uuid,
        ano_analise__ano=ano
    ).first()

    grupos = []
    for grupo in GrupoVerificacaoRegularidade.objects.all():
        listas = []
        for lista in grupo.listas_de_verificacao.all():
            itens = []
            qtd_irregulares = 0
            for item in lista.itens_de_verificacao.all():
                item_esta_regular = False
                if analise_regularidade_ano:
                    verificacao = analise_regularidade_ano.verificacoes_da_analise.filter(item_verificacao=item).first()
                    item_esta_regular = verificacao.regular if verificacao else False

                if not item_esta_regular:
                    qtd_irregulares += 1

                itens.append(
                    {
                        'descricao': item.descricao,
                        'regular': item_esta_regular,
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
        'uuid': f'{associacao_uuid}',
        'verificacao_regularidade': {
            'grupos_verificacao': grupos
        },
        'motivo_nao_regularidade': ''

    }
    return result


def marca_item_verificacao_associacao(associacao_uuid, item_verificacao_uuid, motivo=''):
    #TODO Implementar nova estrutura de regularidade por ano
    result = {}
    # associacao = Associacao.by_uuid(associacao_uuid)
    #
    # if not associacao:
    #     msgError = f'Associacao não encontrada. UUID:{associacao_uuid}'
    #     logger.info(msgError)
    #     raise ValidationError(msgError)
    #
    # item_verificacao = ItemVerificacaoRegularidade.by_uuid(item_verificacao_uuid)
    #
    # if not item_verificacao:
    #     msgError = f'Item de verificação não encontrado. UUID:{item_verificacao_uuid}'
    #     logger.info(msgError)
    #     raise ValidationError(msgError)
    #
    # result = VerificacaoRegularidadeAssociacao.objects.get_or_create(
    #     associacao=associacao,
    #     item_verificacao=item_verificacao,
    #     defaults={
    #         'grupo_verificacao': item_verificacao.lista.grupo,
    #         'lista_verificacao': item_verificacao.lista,
    #         'regular': True,
    #     }
    # ) if associacao and item_verificacao else None
    #
    # if associacao:
    #     atualiza_status_regularidade(associacao, motivo)
    #
    # logger.info(f'Item de verificação marcado {result}')

    return result


def desmarca_item_verificacao_associacao(associacao_uuid, item_verificacao_uuid, motivo=''):
    #TODO Implementar nova estrutura de regularidade por ano
    return None
    # associacao = Associacao.by_uuid(associacao_uuid)
    # item_verificacao = ItemVerificacaoRegularidade.by_uuid(item_verificacao_uuid)
    #
    # VerificacaoRegularidadeAssociacao.objects.filter(
    #     associacao=associacao,
    #     item_verificacao=item_verificacao
    # ).delete()
    #
    # if associacao:
    #     atualiza_status_regularidade(associacao, motivo=motivo)
    #
    # return 'OK' if associacao and item_verificacao else None


def atualiza_status_regularidade(associacao, motivo=''):
    #TODO Implementar nova estrutura de regularidade por ano
    ...
    # status = Associacao.STATUS_REGULARIDADE_PENDENTE
    #
    # if associacao.verificacoes_regularidade.count() == ItemVerificacaoRegularidade.objects.count():
    #     if all(associacao.verificacoes_regularidade.values_list('regular', flat=True)):
    #         status = Associacao.STATUS_REGULARIDADE_REGULAR
    #
    # if status == Associacao.STATUS_REGULARIDADE_PENDENTE:
    #     associacao.motivo_nao_regularidade = motivo
    # else:
    #     associacao.motivo_nao_regularidade = ''
    #
    # associacao.status_regularidade = status
    # associacao.save()


def marca_lista_verificacao_associacao(associacao_uuid, lista_verificacao_uuid):
    # TODO Implementar nova estrutura de regularidade por ano
    return None
    # associacao = Associacao.by_uuid(associacao_uuid)
    #
    # if not associacao:
    #     msgError = f'Associacao não encontrada. UUID:{associacao_uuid}'
    #     logger.info(msgError)
    #     raise ValidationError(msgError)
    #
    # lista_verificacao = ListaVerificacaoRegularidade.by_uuid(lista_verificacao_uuid)
    #
    # if not lista_verificacao:
    #     msgError = f'Lista de verificação não encontrada. UUID:{lista_verificacao_uuid}'
    #     logger.info(msgError)
    #     raise ValidationError(msgError)
    #
    # logger.info(f'Marcando itens da lista de verificação...')
    # for item in lista_verificacao.itens_de_verificacao.all():
    #     marca_item_verificacao_associacao(associacao_uuid=associacao_uuid, item_verificacao_uuid=item.uuid)
    #
    # return 'OK' if associacao and lista_verificacao else None


def desmarca_lista_verificacao_associacao(associacao_uuid, lista_verificacao_uuid):
    # TODO Implementar nova estrutura de regularidade por ano
    return None
    # associacao = Associacao.by_uuid(associacao_uuid)
    #
    # if not associacao:
    #     msgError = f'Associacao não encontrada. UUID:{associacao_uuid}'
    #     logger.info(msgError)
    #     raise ValidationError(msgError)
    #
    # lista_verificacao = ListaVerificacaoRegularidade.by_uuid(lista_verificacao_uuid)
    #
    # if not lista_verificacao:
    #     msgError = f'Lista de verificação não encontrada. UUID:{lista_verificacao_uuid}'
    #     logger.info(msgError)
    #     raise ValidationError(msgError)
    #
    # logger.info(f'Desmarcando itens da lista de verificação...')
    # for item in lista_verificacao.itens_de_verificacao.all():
    #     desmarca_item_verificacao_associacao(associacao_uuid=associacao_uuid, item_verificacao_uuid=item.uuid)
    #
    # return 'OK' if associacao and lista_verificacao else None


def lista_status_regularidade_associacoes_no_ano(
    dre,
    ano_analise_regularidade,
    filtro_nome,
    filtro_tipo_unidade,
    filtro_status
):
    from sme_ptrf_apps.core.api.serializers.associacao_serializer import AssociacaoListSerializer

    qs = Associacao.objects.filter(unidade__dre=dre).order_by('nome')

    if filtro_nome:
        qs = qs.filter(
            Q(nome__unaccent__icontains=filtro_nome) |
            Q(unidade__nome__unaccent__icontains=filtro_nome)
        )

    if filtro_tipo_unidade:
        qs = qs.filter(unidade__tipo_unidade=filtro_tipo_unidade)

    associacoes_status = []
    for associacao in qs:
        analise_regularidade = associacao.analises_regularidade_da_associacao.filter(
            ano_analise=ano_analise_regularidade
        ).first()

        status_regularidade = analise_regularidade.status_regularidade if analise_regularidade else 'PENDENTE'

        if not filtro_status or status_regularidade == filtro_status:
            associacoes_status.append(
                {
                    'associacao': AssociacaoListSerializer(associacao).data,
                    'status_regularidade': status_regularidade,
                }
            )

    return associacoes_status
