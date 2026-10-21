from rest_framework import serializers
from ....core.models import FechamentoPeriodo
from ....core.api.serializers.associacao_serializer import AssociacaoListSerializer
from ....core.api.serializers.periodo_serializer import PeriodoLookUpSerializer


class ValoresReprogramadosListSerializer(serializers.ModelSerializer):
    associacao = AssociacaoListSerializer()
    periodo = PeriodoLookUpSerializer()

    total_conta_cheque = serializers.SerializerMethodField('get_total_conta_cheque')
    total_conta_cartao = serializers.SerializerMethodField('get_total_conta_cartao')

    def _get_recurso(self, obj):
        request = self.context.get("request")
        if request and hasattr(request, "recurso") and request.recurso:
            return request.recurso
        if obj and obj.periodo and obj.periodo.recurso:
            return obj.periodo.recurso
        return None

    def _get_total_por_tipo_conta(self, obj, tipo_conta):
        if not tipo_conta:
            return 0

        recurso = self._get_recurso(obj)
        todos_fechamentos = obj.associacao.fechamentos_associacao.filter(
            status='IMPLANTACAO',
            conta_associacao__tipo_conta=tipo_conta,
        )

        if recurso:
            todos_fechamentos = todos_fechamentos.filter(periodo__recurso=recurso)

        total = 0
        for fechamento in todos_fechamentos:
            total += fechamento.saldo_reprogramado

        return total

    def get_total_conta_cheque(self, obj):
        recurso = self._get_recurso(obj)
        tipo_conta_um = recurso.tipo_conta_um if recurso else None
        return self._get_total_por_tipo_conta(obj, tipo_conta_um)

    def get_total_conta_cartao(self, obj):
        recurso = self._get_recurso(obj)
        tipo_conta_dois = recurso.tipo_conta_dois if recurso else None
        return self._get_total_por_tipo_conta(obj, tipo_conta_dois)

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
