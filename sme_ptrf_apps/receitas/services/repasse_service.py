import logging
from datetime import date

from rest_framework.exceptions import ValidationError

from ..models import Repasse

logger = logging.getLogger(__name__)


def atualiza_repasse_para_realizado(receita_validated_data):
    repasse = Repasse.objects\
                .filter(acao_associacao__uuid=receita_validated_data['acao_associacao'].uuid,
                        status='PENDENTE',
                        periodo__data_inicio_realizacao_despesas__lte=receita_validated_data['data'])\
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

    if date.today() <= receita_validated_data['data']:
        msgError = "Data da receita maior que a data atual."
        logger.info(msgError)
        raise ValidationError(msgError)

    valores_iguais = receita_validated_data['valor'] == repasse.valor_total

    if not valores_iguais:
        msgError = "Valor do payload não é igual ao valor total do repasse."
        logger.info(msgError)
        raise ValidationError(msgError)

    repasse.status = 'REALIZADO'
    repasse.save()


def atualiza_repasse_para_pendente(acao_associacao):
    repasse = Repasse.objects\
                .filter(acao_associacao__uuid=acao_associacao.uuid, status='REALIZADO').last()

    if repasse:
        logger.info("Atualizando status do repasse %s para PENDENTE.", repasse.uuid)
        repasse.status = 'PENDENTE'
        repasse.save()
