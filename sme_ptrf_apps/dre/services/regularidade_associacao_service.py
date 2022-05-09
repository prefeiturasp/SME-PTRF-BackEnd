import logging

from django.db.models import Q

from rest_framework.exceptions import ValidationError

from ..models import (
    GrupoVerificacaoRegularidade,
    VerificacaoRegularidadeAssociacao,
    ItemVerificacaoRegularidade,
    AnaliseRegularidadeAssociacao,
    AnoAnaliseRegularidade
)
from ...core.models import Associacao

logger = logging.getLogger(__name__)


def get_verificacao_regularidade_associacao(associacao_uuid, ano):

    analise_regularidade_ano = AnaliseRegularidadeAssociacao.objects.filter(
        associacao__uuid=associacao_uuid,
        ano_analise__ano=ano
    ).first()

    grupos = []
    for grupo in GrupoVerificacaoRegularidade.objects.all():
        listas = []
        for lista in grupo.listas_de_verificacao.all().order_by('-id'):
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
        'motivo_nao_regularidade': analise_regularidade_ano.motivo_nao_regularidade if analise_regularidade_ano else ""

    }
    return result


def get_lista_associacoes_e_status_regularidade_no_ano(
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


def atualiza_itens_verificacao(associacao_uuid, ano, itens_verificacao, motivo_nao_regularidade):

    def valida_itens_verificacao():
        if not itens_verificacao:
            raise ValidationError({
                'erro': 'campo_requerido',
                'mensagem': 'É necessário enviar os itens de verificacao com o seu status.'
            })

    def get_associacao_obj():
        try:
            return Associacao.by_uuid(associacao_uuid)
        except Associacao.DoesNotExist:
            result_error = {
                'erro': 'objeto_nao_encontrado',
                'mensagem': f'Não foi encontrada uma Associação de uuid {associacao_uuid}.'
            }
            raise ValidationError(result_error)

    def get_ano_analise_obj():
        try:
            return AnoAnaliseRegularidade.objects.get(ano=ano)
        except AnoAnaliseRegularidade.DoesNotExist:
            result_error = {
                'erro': 'objeto_nao_encontrado',
                'mensagem': f'Não foi encontrada o ano de Análise de Regularidade {ano}.'
            }
            raise ValidationError(result_error)

    def apaga_analise_anterior(associacao, ano_analise):
        analise = AnaliseRegularidadeAssociacao.objects.filter(
            associacao=associacao,
            ano_analise=ano_analise,
        ).first()

        if analise:
            for verificacao in analise.verificacoes_da_analise.all():
                verificacao.delete()
            analise.delete()

    def get_novo_analise_obj(associacao, ano_analise):
        return AnaliseRegularidadeAssociacao.objects.create(
            associacao=associacao,
            ano_analise=ano_analise,
            motivo_nao_regularidade=motivo_nao_regularidade
        )

    def marca_item_verificacao_associacao(analise_regularidade, item_verificacao_uuid):

        item_verificacao = ItemVerificacaoRegularidade.by_uuid(item_verificacao_uuid)

        if not item_verificacao:
            msgError = f'Item de verificação não encontrado. UUID:{item_verificacao_uuid}'
            logger.info(msgError)
            raise ValidationError(msgError)

        result = VerificacaoRegularidadeAssociacao.objects.get_or_create(
            analise_regularidade=analise_regularidade,
            item_verificacao=item_verificacao,
            defaults={
                'regular': True,
            }
        ) if analise_regularidade and item_verificacao else None

        logger.info(f'Item de verificação marcado {result}')

        return result

    def desmarca_item_verificacao_associacao(analise_regularidade, item_verificacao_uuid):
        item_verificacao = ItemVerificacaoRegularidade.by_uuid(item_verificacao_uuid)

        VerificacaoRegularidadeAssociacao.objects.filter(
            analise_regularidade=analise_regularidade,
            item_verificacao=item_verificacao
        ).delete()

        return 'OK' if analise_regularidade and item_verificacao else None

    def atualiza_status_regularidade(analise_regularidade, motivo=''):
        status = AnaliseRegularidadeAssociacao.STATUS_REGULARIDADE_PENDENTE

        if analise_regularidade.verificacoes_da_analise.count() == ItemVerificacaoRegularidade.objects.count():
            if all(analise_regularidade.verificacoes_da_analise.values_list('regular', flat=True)):
                status = AnaliseRegularidadeAssociacao.STATUS_REGULARIDADE_REGULAR

        if status == AnaliseRegularidadeAssociacao.STATUS_REGULARIDADE_PENDENTE:
            analise_regularidade.motivo_nao_regularidade = motivo
        else:
            analise_regularidade.motivo_nao_regularidade = ''

        analise_regularidade.status_regularidade = status
        analise_regularidade.save()

    valida_itens_verificacao()
    associacao = get_associacao_obj()
    ano_analise = get_ano_analise_obj()
    apaga_analise_anterior(associacao, ano_analise)
    analise_regularidade = get_novo_analise_obj(associacao, ano_analise)

    for item in itens_verificacao:
        logging.info(f"======> item[regula]={item['regular']}")
        if item['regular']:
            marca_item_verificacao_associacao(
                analise_regularidade=analise_regularidade,
                item_verificacao_uuid=item['uuid']
            )
        else:
            desmarca_item_verificacao_associacao(
                analise_regularidade=analise_regularidade,
                item_verificacao_uuid=item['uuid']
            )

    atualiza_status_regularidade(analise_regularidade=analise_regularidade, motivo=motivo_nao_regularidade)

    return {
        'associacao': f'{associacao_uuid}',
        'mensagem': 'Itens de verificação atualizados.'
    }
