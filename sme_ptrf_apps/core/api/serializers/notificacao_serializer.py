from rest_framework import serializers

from sme_ptrf_apps.core.models import Categoria, Notificacao, Remetente, TipoNotificacao


class NotificacaoSerializer(serializers.ModelSerializer):
    tipo = serializers.SerializerMethodField(method_name='get_tipo')
    remetente = serializers.SerializerMethodField(method_name='get_remetente')
    categoria = serializers.SerializerMethodField(method_name='get_categoria')
    hora = serializers.SerializerMethodField(method_name='get_hora')

    def get_tipo(self, obj):
        return obj.tipo.nome if obj.tipo else ''

    def get_remetente(self, obj):
        return obj.remetente.nome if obj.remetente else ''

    def get_categoria(self, obj):
        return obj.categoria.nome if obj.categoria else ''

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
            'categoria'
        ]


class TipoNotificacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoNotificacao
        fields = [
            'id',
            'nome'
        ]


class RemetenteNotificacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Remetente
        fields = [
            'id',
            'nome'
        ]


class CategoriatificacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = [
            'id',
            'nome'
        ]
