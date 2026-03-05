from decimal import Decimal
from rest_framework import serializers
from sme_ptrf_apps.core.models import Periodo
from sme_ptrf_apps.despesas.tipos_aplicacao_recurso import APLICACAO_CAPITAL

from sme_ptrf_apps.despesas.api.serializers.rateio_despesa_serializer import (
    RateioDespesaCreateSerializer
)


class ValidacaoDespesaService:

    @staticmethod
    def validar_rateios_serializer(
        valor_total,
        raw_rateios = [],
        raw_despesas_impostos = [],
        retem_imposto = False,
        valor_recursos_proprios = 0,
    ):
        if not raw_rateios:
            raise serializers.ValidationError(
                "A despesa deve conter ao menos um rateio."
            )

        serializer = RateioDespesaCreateSerializer(
            data=raw_rateios,
            many=True
        )
        serializer.is_valid(raise_exception=True)       

        total_rateios = sum(
            Decimal(str(r.get("valor_rateio", 0)))
            for r in raw_rateios
        )

        valor_real = Decimal(str(valor_total or 0)) - Decimal(
            str(valor_recursos_proprios or 0)
        )

        total_rateios_impostos = total_rateios

        if retem_imposto:
            total_impostos = sum(
                Decimal(str(r.get("valor_total", 0)))
                for r in raw_despesas_impostos
            )

            total_rateios_impostos += total_impostos

        if total_rateios_impostos != valor_real:
            raise serializers.ValidationError(
                "A soma dos rateios deve ser igual ao valor real da despesa."
            )
        
        # Valida rateios do tipo capital
        for rateio in raw_rateios:
            if rateio.get('aplicacao_recurso') == APLICACAO_CAPITAL:
                quantidade_itens_capital = rateio.get('quantidade_itens_capital')
                valor_item_capital = rateio.get('valor_item_capital')

                if quantidade_itens_capital <= 0:
                    raise serializers.ValidationError({
                        'mensagem': 'Rateio de capital não pode ter quantidade menor ou igual a zero'
                    })
                
                if valor_item_capital:
                    valor_total_item_capital = valor_item_capital * quantidade_itens_capital
                    valor_rateio = rateio.get('valor_rateio')

                    if valor_total_item_capital != valor_rateio:
                        raise serializers.ValidationError({
                            'mensagem': 'Valor do rateio capital diverge do valor calculado pela quantidade de itens'
                        })

    @staticmethod
    def validar_periodo_e_contas(
        instance,
        data_transacao,
        rateios,
        despesas_impostos
    ):
        if data_transacao:
            periodo = Periodo.da_data(data_transacao)

            if (
                instance and instance.prestacao_conta and
                instance.prestacao_conta.devolvida_para_acertos and
                periodo and
                periodo.referencia != instance.prestacao_conta.periodo.referencia
            ):
                raise serializers.ValidationError({
                    "mensagem": (
                        "Permitido apenas datas dentro do período referente à devolução."
                    )
                })

        ValidacaoDespesaService._validar_contas_rateios(
            rateios, data_transacao
        )

        ValidacaoDespesaService._validar_contas_impostos(
            despesas_impostos
        )

        for rateio in rateios:
            conta_associacao = rateio['conta_associacao']
            acao_associacao = rateio['acao_associacao']

            if conta_associacao and acao_associacao:
                if conta_associacao.tipo_conta.recurso != acao_associacao.acao.recurso:
                    raise serializers.ValidationError({"mensagem": "Conta e Ação devem ser do mesmo recurso."})

    @staticmethod
    def _validar_contas_rateios(rateios, data_transacao):
        for rateio in rateios:
            conta = rateio.get("conta_associacao")

            if not conta:
                continue

            if conta.data_inicio > data_transacao:
                raise serializers.ValidationError({
                    "mensagem": (
                        "Um ou mais rateios possuem conta com data de início "
                        "posterior à data de transação."
                    )
                })

            if (
                conta.data_encerramento and
                conta.data_encerramento < data_transacao
            ):
                raise serializers.ValidationError({
                    "mensagem": (
                        "Um ou mais rateios possuem conta com data de "
                        "encerramento anterior à data de transação."
                    )
                })

    @staticmethod
    def _validar_contas_impostos(despesas_impostos):
        for imposto in despesas_impostos:
            data_transacao = imposto.get("data_transacao")
            if not data_transacao:
                continue

            for rateio in imposto.get("rateios", []):
                conta = rateio.get("conta_associacao")

                if not conta:
                    continue

                if conta.data_inicio > data_transacao:
                    raise serializers.ValidationError({
                        "mensagem": (
                            "Um ou mais rateios de imposto possuem conta com "
                            "data de início posterior à data de transação."
                        )
                    })

                if (
                    conta.data_encerramento and
                    conta.data_encerramento < data_transacao
                ):
                    raise serializers.ValidationError({
                        "mensagem": (
                            "Um ou mais rateios de imposto possuem conta com "
                            "data de encerramento anterior à data de transação."
                        )
                    })

