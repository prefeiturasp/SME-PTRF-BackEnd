from django.contrib.auth import get_user_model
from rest_framework import serializers
from sme_ptrf_apps.users.models import Grupo

User = get_user_model()

class GruposDisponiveisPorAcessoVisaoSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    
    def validate_username(self, value): # noqa
        try:
            usuario = User.objects.get(username=value)
        except User.DoesNotExist: # noqa
            raise serializers.ValidationError(f"Não foi encontrado um objeto para o username {value}.")

        return value
    
class HabilitarGrupoAcessoSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    id_grupo = serializers.CharField(required=True)
    
    def validate_username(self, value): # noqa
        try:
            usuario = User.objects.get(username=value)
        except User.DoesNotExist: # noqa
            raise serializers.ValidationError(f"Não foi encontrado um objeto para o username {value}.")

        return value
    
    def validate_id_grupo(self, value): # noqa
        try:
            unidade = Grupo.objects.get(id=value)
        except Grupo.DoesNotExist:  # noqa
            raise serializers.ValidationError(f"Não foi encontrado um objeto para o id {value}.")

        return value
    
class DesabilitarGrupoAcessoSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    id_grupo = serializers.CharField(required=True)
    
    def validate_username(self, value): # noqa
        try:
            usuario = User.objects.get(username=value)
        except User.DoesNotExist: # noqa
            raise serializers.ValidationError(f"Não foi encontrado um objeto para o username {value}.")

        return value
    
    def validate_id_grupo(self, value): # noqa
        try:
            unidade = Grupo.objects.get(id=value)
        except Grupo.DoesNotExist:  # noqa
            raise serializers.ValidationError(f"Não foi encontrado um objeto para o id {value}.")

        return value