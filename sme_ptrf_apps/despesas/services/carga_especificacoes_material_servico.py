import csv
import logging
import os

from django.contrib.staticfiles.storage import staticfiles_storage

from ..models import EspecificacaoMaterialServico, TipoCusteio
from ..tipos_aplicacao_recurso import APLICACAO_CAPITAL, APLICACAO_CUSTEIO

logger = logging.getLogger(__name__)


def carrega_especificacoes():
    def get_aplicacao_from_row(row):
        if ': ' in row[0]:
            nome_aplicacao, _ = row[0].split(': ', 1)
        else:
            nome_aplicacao = row[0]

        return APLICACAO_CUSTEIO if nome_aplicacao == 'Custeio' else APLICACAO_CAPITAL

    def get_tipo_custeio_from_row(row):
        if ': ' in row[0]:
            _, nome_tipo_custeio = row[0].split(': ', 1)
        else:
            nome_tipo_custeio = None

        if not nome_tipo_custeio:
            return None

        if TipoCusteio.objects.filter(nome=nome_tipo_custeio).exists():
            obj_tipo_custeio = TipoCusteio.objects.filter(nome=nome_tipo_custeio).first()
        else:
            obj_tipo_custeio = TipoCusteio.objects.create(nome=nome_tipo_custeio)
            logger.info(f'Criado o tipo de custeio {obj_tipo_custeio.id} - {obj_tipo_custeio.nome}')

        return obj_tipo_custeio

    def atualiza_ou_cria_especificacao(descricao, aplicacao_recurso, tipo_custeio):
        if EspecificacaoMaterialServico.objects.filter(descricao=descricao).exists():
            especificacao = EspecificacaoMaterialServico.objects.filter(descricao=descricao).first()
            especificacao.aplicacao_recurso = aplicacao_recurso
            especificacao.tipo_custeio = tipo_custeio
            especificacao.save()
            logger.info(
                f'Atualizada a especificação {especificacao.id} - {especificacao.descricao} - {especificacao.aplicacao_recurso} - {especificacao.tipo_custeio}')

        else:
            especificacao = EspecificacaoMaterialServico.objects.create(
                descricao=descricao,
                aplicacao_recurso=aplicacao_recurso,
                tipo_custeio=tipo_custeio,
            )
            logger.info(
                f'Criada a especificação {especificacao.id} - {especificacao.descricao} - {especificacao.aplicacao_recurso} - {especificacao.tipo_custeio}')

        return especificacao

    logger.info(f'Carregando arquivo de especificações de materiais e serviços...')

    f = staticfiles_storage.open(os.path.join('cargas', 'classificacoes_material_servico.csv'), 'r')

    reader = csv.reader(f, delimiter=',')

    lin = 0
    for row in reader:
        if lin == 0:
            lin += 1
            continue  # Pula cabeçalho.
        lin += 1
        logger.debug(f'Linha {lin}: {row}')

        aplicacao = get_aplicacao_from_row(row)
        tipo_custeio = get_tipo_custeio_from_row(row)
        descricao_especificacao = row[1]
        atualiza_ou_cria_especificacao(descricao_especificacao, aplicacao, tipo_custeio)

    f.close()

    logger.info(f'Importadas {lin} especificações de materiais e serviços.')
