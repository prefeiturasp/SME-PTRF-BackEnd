import logging
from datetime import date

from rest_framework.exceptions import ValidationError

from sme_ptrf_apps.core.models import Periodo
from ..tipos_aplicacao_recurso_receitas import APLICACAO_CAPITAL, APLICACAO_CUSTEIO, APLICACAO_LIVRE

from ..models import Repasse

logger = logging.getLogger(__name__)


def atualiza_repasse_para_realizado(receita_validated_data):
    if receita_validated_data['categoria_receita'] == APLICACAO_CAPITAL and receita_validated_data['valor'] == receita_validated_data['repasse'].valor_capital:
        receita_validated_data['repasse'].realizado_capital = True

    elif receita_validated_data['categoria_receita'] == APLICACAO_CUSTEIO and receita_validated_data['valor'] == receita_validated_data['repasse'].valor_custeio:
        receita_validated_data['repasse'].realizado_custeio = True

    elif receita_validated_data['categoria_receita'] == APLICACAO_LIVRE and receita_validated_data['valor'] == receita_validated_data['repasse'].valor_livre:
        receita_validated_data['repasse'].realizado_livre = True

    else:
        msgError = f"Valor do payload não é igual ao valor do {receita_validated_data['categoria_receita']}."
        logger.info(msgError)
        raise ValidationError(msgError)

    if (receita_validated_data['repasse'].realizado_capital or receita_validated_data['repasse'].valor_capital == 0) and (receita_validated_data['repasse'].realizado_custeio or receita_validated_data['repasse'].valor_custeio == 0) and (receita_validated_data['repasse'].realizado_livre or receita_validated_data['repasse'].valor_livre == 0):
        receita_validated_data['repasse'].status = 'REALIZADO'

    receita_validated_data['repasse'].save()


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
