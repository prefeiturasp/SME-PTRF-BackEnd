from decimal import Decimal
from rest_framework import serializers

from sme_ptrf_apps.despesas.api.serializers.rateio_despesa_serializer import (
    RateioDespesaCreateSerializer
)
from sme_ptrf_apps.core.models import Periodo


class ValidacaoDespesaService:

    @staticmethod
    def validar_rateios(
        raw_rateios,
        valor_total,
        valor_recursos_proprios=0
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

        if total_rateios != valor_real:
            raise serializers.ValidationError(
                "A soma dos rateios deve ser igual ao valor real da despesa."
            )

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
