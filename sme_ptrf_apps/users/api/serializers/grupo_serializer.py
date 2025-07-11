from rest_framework import serializers

from sme_ptrf_apps.users.models import Grupo, Visao


class VisaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visao
        fields = ['nome', 'id']


class GrupoSerializer(serializers.ModelSerializer):
    visoes = VisaoSerializer(many=True)

    class Meta:
        model = Grupo
        fields = ['id', 'name', 'descricao', 'visoes']


class DocAPIResponseGruposSerializer(serializers.Serializer):
    id = serializers.CharField()
    nome = serializers.CharField()
    descricao = serializers.CharField()
    visao = serializers.CharField()
