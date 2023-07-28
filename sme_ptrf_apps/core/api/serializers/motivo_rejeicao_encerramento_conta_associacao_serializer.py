from datetime import datetime
from django.db import IntegrityError
from rest_framework import serializers

from ...models import MotivoRejeicaoEncerramentoContaAssociacao


class MotivoRejeicaoEncerramentoContaAssociacaoSerializer(serializers.ModelSerializer):

    class Meta:
        model = MotivoRejeicaoEncerramentoContaAssociacao
        fields = (
            'uuid',
            'nome',
            'criado_em',
            'id'
        )

