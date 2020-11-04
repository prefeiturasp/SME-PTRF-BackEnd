import logging
from datetime import date

from rest_framework.exceptions import ValidationError

from sme_ptrf_apps.core.models import Periodo
from ..tipos_aplicacao_recurso_receitas import APLICACAO_CAPITAL, APLICACAO_CUSTEIO, APLICACAO_LIVRE

from ..models import Repasse

logger = logging.getLogger(__name__)


def atualiza_repasse_para_realizado(receita_validated_data):
    periodo = Periodo.da_data(receita_validated_data['data'])
    repasse = Repasse.objects\
                .filter(acao_associacao__uuid=receita_validated_data['acao_associacao'].uuid,
                        status='PENDENTE',
                        periodo=periodo)\
                .order_by('-criado_em').last()

    if not repasse:
        msgError = "Repasse não encontrado."
        logger.info(msgError)
        raise ValidationError(msgError)

    data_fim_realizacao_despesas = repasse.periodo.data_fim_realizacao_despesas

    if data_fim_realizacao_despesas and data_fim_realizacao_despesas <= receita_validated_data['data']:
        msgError = "Data da receita maior que a data fim da realização de despesas."
        logger.info(msgError)
        raise ValidationError(msgError)

    if date.today() < receita_validated_data['data']:
        msgError = "Data da receita maior que a data atual."
        logger.info(msgError)
        raise ValidationError(msgError)

    if receita_validated_data['categoria_receita'] == APLICACAO_CAPITAL and receita_validated_data['valor'] == repasse.valor_capital:
        repasse.realizado_capital = True

    elif receita_validated_data['categoria_receita'] == APLICACAO_CUSTEIO and receita_validated_data['valor'] == repasse.valor_custeio:
        repasse.realizado_custeio = True

    elif receita_validated_data['categoria_receita'] == APLICACAO_LIVRE and receita_validated_data['valor'] == repasse.valor_livre:
        repasse.realizado_livre = True

    else:
        msgError = f"Valor do payload não é igual ao valor do {receita_validated_data['categoria_receita']}."
        logger.info(msgError)
        raise ValidationError(msgError)

    if (repasse.realizado_capital or repasse.valor_capital == 0) and (repasse.realizado_custeio or repasse.valor_custeio == 0) and (repasse.realizado_livre or repasse.valor_livre == 0):
        repasse.status = 'REALIZADO'

    repasse.save()

    return repasse


def atualiza_repasse_para_pendente(receita):
    repasse = receita.repasse

    if repasse:
        logger.info("Atualizando status do repasse %s para PENDENTE.", repasse.uuid)
        repasse.status = 'PENDENTE'
        if receita.categoria_receita == 'CAPITAL':
            repasse.realizado_capital = False
        elif receita.categoria_receita == 'CUSTEIO':
            repasse.realizado_custeio = False
        else:
            repasse.realizado_livre = False

        repasse.save()
