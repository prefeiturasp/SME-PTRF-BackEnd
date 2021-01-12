from rest_framework import serializers

from sme_ptrf_apps.core.api.serializers import AssociacaoLookupSerializer
from sme_ptrf_apps.core.models import MembroAssociacao, Associacao
from sme_ptrf_apps.users.api.serializers import UserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class MembroAssociacaoCreateSerializer(serializers.ModelSerializer):
    associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=Associacao.objects.all()
    )

    class Meta:
        model = MembroAssociacao
        exclude = ('id',)


class MembroAssociacaoListSerializer(serializers.ModelSerializer):
    associacao = AssociacaoLookupSerializer()

    class Meta:
        model = MembroAssociacao
        fields = '__all__'
