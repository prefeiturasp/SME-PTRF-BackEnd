from rest_framework import serializers
from ....core.models import FechamentoPeriodo
from ....core.api.serializers.associacao_serializer import AssociacaoListSerializer
from ....core.api.serializers.periodo_serializer import PeriodoLookUpSerializer
from ...models import ParametrosDre


class ValoresReprogramadosListSerializer(serializers.ModelSerializer):
    associacao = AssociacaoListSerializer()
    periodo = PeriodoLookUpSerializer()

    total_conta_cheque = serializers.SerializerMethodField('get_total_conta_cheque')
    total_conta_cartao = serializers.SerializerMethodField('get_total_conta_cartao')

    def get_total_conta_cheque(self, obj):
        uuid_conta_cheque = None
        total = 0

        if ParametrosDre.objects.all():
            if ParametrosDre.get().tipo_conta_um:
                uuid_conta_cheque = ParametrosDre.get().tipo_conta_um.uuid

        if uuid_conta_cheque is not None:
            todos_fechamentos = obj.associacao.fechamentos_associacao.filter(
                status='IMPLANTACAO').filter(conta_associacao__tipo_conta__uuid=uuid_conta_cheque).exclude(
                associacao__periodo_inicial=None)

            for fechamentos in todos_fechamentos:
                total = total + fechamentos.saldo_reprogramado

        return total

    def get_total_conta_cartao(self, obj):
        uuid_conta_cartao = None
        total = 0

        if ParametrosDre.objects.all():
            if ParametrosDre.get().tipo_conta_dois:
                uuid_conta_cartao = ParametrosDre.get().tipo_conta_dois.uuid

        if uuid_conta_cartao is not None:
            todos_fechamentos = obj.associacao.fechamentos_associacao.filter(
                status='IMPLANTACAO').filter(conta_associacao__tipo_conta__uuid=uuid_conta_cartao).exclude(
                associacao__periodo_inicial=None)

            for fechamentos in todos_fechamentos:
                total = total + fechamentos.saldo_reprogramado

        return total

    class Meta:
        model = FechamentoPeriodo
        fields = [
            "associacao",
            "periodo",
            "total_conta_cheque",
            "total_conta_cartao"
        ]
        read_only_fields = [
            "associacao",
            "periodo",
            "total_conta_cheque",
            "total_conta_cartao"
        ]
