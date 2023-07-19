from datetime import datetime
from django.db import IntegrityError
from rest_framework import serializers

from ...models import SolicitacaoEncerramentoContaAssociacao, ContaAssociacao


class SolicitacaoEncerramentoContaAssociacaoSerializer(serializers.ModelSerializer):
    conta_associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        queryset=ContaAssociacao.objects.all()
    )
    data_de_encerramento_na_agencia = serializers.DateField(
        required=True,
    )


    class Meta:
        model = SolicitacaoEncerramentoContaAssociacao
        fields = (
            'uuid',
            'conta_associacao',
            'status',
            'data_de_encerramento_na_agencia',
            'criado_em',
        )

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError({"mensagem": "Já existe uma solicitação para essa conta de associação."})

    def validate_data_de_encerramento_na_agencia(self, value):
        if value > datetime.today().date():
            raise serializers.ValidationError({"mensagem": "Não é permitido informar datas futuras."})
        return value

    def validate(self, data):
        conta_associacao = data['conta_associacao']
        data_de_encerramento_na_agencia = data['data_de_encerramento_na_agencia']
        associacao = conta_associacao.associacao

        if conta_associacao.get_saldo_atual_conta() != 0:
            raise serializers.ValidationError({"mensagem": "Não é permitido encerrar conta com saldo diferente de 0."})

        if associacao and associacao.periodo_inicial:
            if data_de_encerramento_na_agencia <= associacao.periodo_inicial.data_fim_realizacao_despesas:
                raise serializers.ValidationError({"mensagem": "Data de encerramento deve ser posterior ao periodo inicial da associação."})

        if not conta_associacao.pode_encerrar(data_de_encerramento_na_agencia):
            raise serializers.ValidationError({"mensagem": "Existem movimentações cadastradas após a data informada. Favor alterar a data das movimentações ou a data de encerramento da conta."})

        return data

