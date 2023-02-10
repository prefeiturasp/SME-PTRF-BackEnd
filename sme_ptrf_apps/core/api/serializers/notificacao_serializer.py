from rest_framework import serializers

from sme_ptrf_apps.core.models import Notificacao, Unidade


class NotificacaoSerializer(serializers.ModelSerializer):
    tipo = serializers.SerializerMethodField(method_name='get_tipo')
    remetente = serializers.SerializerMethodField(method_name='get_remetente')
    categoria = serializers.SerializerMethodField(method_name='get_categoria')
    hora = serializers.SerializerMethodField(method_name='get_hora')
    periodo = serializers.SerializerMethodField(method_name='get_periodo')

    def get_periodo(self, obj):
        obj_periodo = None
        if obj.periodo:
            obj_periodo = {
                "periodo_uuid": obj.periodo.uuid,
                "data_final": obj.periodo.data_fim_realizacao_despesas,
                "data_inicial": obj.periodo.data_inicio_realizacao_despesas,
                "referencia": obj.periodo.referencia,
            }
        return obj_periodo

    unidade = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Unidade.objects.all()
    )

    def get_tipo(self, obj):
        return Notificacao.TIPO_NOTIFICACAO_NOMES[obj.tipo] if obj.tipo else ''

    def get_remetente(self, obj):
        return Notificacao.REMETENTE_NOTIFICACAO_NOMES[obj.remetente] if obj.remetente else ''

    def get_categoria(self, obj):
        return Notificacao.CATEGORIA_NOTIFICACAO_NOMES[obj.categoria] if obj.categoria else ''

    def get_hora(self, obj):
        return obj.hora.strftime("%H:%M")

    class Meta:
        model = Notificacao
        fields = [
            'uuid',
            'titulo',
            'descricao',
            'lido',
            'hora',
            'tipo',
            'remetente',
            'categoria',
            'unidade',
            'periodo',
        ]
