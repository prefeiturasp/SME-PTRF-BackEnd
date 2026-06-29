from decimal import Decimal
from rest_framework import serializers
from sme_ptrf_apps.core.models import Periodo
from sme_ptrf_apps.despesas.tipos_aplicacao_recurso import APLICACAO_CAPITAL


class ValidacaoDespesaService:

    @staticmethod
    def validar_rateios_serializer(
        valor_total, # Valor realizado 
        valor_original, # Valor total do documento
        raw_rateios=None,
        raw_despesas_impostos=None,
        retem_imposto=False,
        valor_recursos_proprios=0,
    ):
        """
        Regras de validação dos rateios da despesa.

        valor_original:
            Representa o valor exibido no extrato comprobatório.
            Esse campo foi criado posteriormente ao valor_rateio para armazenar o
            valor original informado no documento, mesmo quando
            ele difere do valor efetivamente pago.

        valor_rateio:
            Representa o valor efetivamente realizado/pago na operação.

        Regras:

        - A soma dos `valor_rateio` dos rateios deve ser igual ao
        valor REAL (`valor_total`) da despesa + impostos (caso haja)

        - A soma dos `valor_original` dos rateios deve ser igual ao
        `valor_original` REAL informado na despesa + impostos (caso haja)

        OBS: entende-se real por que deduz o de recursos próprios utilizado.
        Referência: #20303 [Associações] Incluir campos de "valor_realizado" no cadastro de despesa
        """

        raw_rateios = raw_rateios or []
        raw_despesas_impostos = raw_despesas_impostos or []        
    
        if not raw_rateios:
            raise serializers.ValidationError(
                "A despesa deve conter ao menos um rateio."
            )

        total_rateios = sum(
            Decimal(str(rateio.get("valor_rateio", 0)))
            for rateio in raw_rateios
        )

        total_rateios_original = sum(
            Decimal(str(rateio.get("valor_original", 0)))
            for rateio in raw_rateios
        )

        # Valor total real
        valor_total_real_despesa = Decimal(str(valor_total or 0)) - Decimal(
            str(valor_recursos_proprios or 0)
        )

        # Valor original real
        valor_original_real_despesa = Decimal(str(valor_original or 0)) - Decimal(
            str(valor_recursos_proprios or 0)
        )

        total_rateios_com_impostos = total_rateios
        total_rateios_original_com_impostos = total_rateios_original

        if retem_imposto:
            total_impostos_valor_total = sum(
                Decimal(str(imposto.get("valor_total", 0)))
                for imposto in raw_despesas_impostos
            )

            total_impostos_valor_original = sum(
                Decimal(str(imposto.get("valor_original", 0)))
                for imposto in raw_despesas_impostos
            )

            total_rateios_com_impostos += total_impostos_valor_total
            total_rateios_original_com_impostos += total_impostos_valor_original

        if total_rateios_com_impostos != valor_total_real_despesa:
            raise serializers.ValidationError(
                "A soma dos valores realizados dos rateios deve "
                "ser igual ao valor real da despesa."
            )

        if total_rateios_original_com_impostos != valor_original_real_despesa:
            raise serializers.ValidationError(
                "A soma dos valores originais dos rateios deve "
                "ser igual ao valor original da despesa."
            )

        # Valida rateios do tipo capital
        for rateio in raw_rateios:
            if rateio.get("aplicacao_recurso") != APLICACAO_CAPITAL:
                continue

            quantidade_itens_capital = rateio.get(
                "quantidade_itens_capital"
            )

            valor_item_capital = rateio.get(
                "valor_item_capital"
            )

            if quantidade_itens_capital <= 0:
                raise serializers.ValidationError({
                    "mensagem": (
                        "Rateio de capital não pode ter "
                        "quantidade menor ou igual a zero"
                    )
                })

            if not valor_item_capital:
                continue

            valor_total_item_capital = (
                Decimal(str(valor_item_capital))
                * Decimal(str(quantidade_itens_capital))
            )

            valor_original_rateio = Decimal(
                str(rateio.get("valor_original", 0))
            )

            """
            Atualmente, o campo valor total do capital (valor_original) é
            disabled e calculado com base no quantidade de unidades x valor)
            Portanto, não pode divergir do valor realizado, igual é quando CUSTEIO.
            """
            if valor_total_item_capital != valor_original_rateio:
                raise serializers.ValidationError({
                    "mensagem": (
                        "Valor total do capital diverge do valor "
                        "calculado pela quantidade de itens"
                    )
                })
        

    @staticmethod
    def validar_periodo_e_contas(
        instance,
        data_transacao,
        rateios,
        despesas_impostos,
        recurso
    ):
        if data_transacao:
            periodo = Periodo.da_data_por_recurso(data_transacao, recurso)

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

            if data_transacao and conta.data_inicio and conta.data_inicio > data_transacao:
                raise serializers.ValidationError({
                    "mensagem": (
                        "Um ou mais rateios possuem conta com data de início "
                        "posterior à data de transação."
                    )
                })

            if (data_transacao and conta.data_encerramento and conta.data_encerramento < data_transacao):
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
