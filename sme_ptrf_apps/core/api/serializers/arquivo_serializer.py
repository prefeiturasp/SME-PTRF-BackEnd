from rest_framework import serializers

from sme_ptrf_apps.core.models import Arquivo
from sme_ptrf_apps.users.api.serializers import UserLookupSerializer


class ArquivoSerializer(serializers.ModelSerializer):
    usuario = UserLookupSerializer()

    class Meta:
        model = Arquivo
        fields = '__all__'
