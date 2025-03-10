from rest_framework import serializers

from ...models import AcaoPdde
from .categoria_pdde_serializer import CategoriaPddeSerializer


class AcaoPddeSerializer(serializers.ModelSerializer):
    categoria_objeto = CategoriaPddeSerializer(read_only=True, many=False)

    class Meta:
        model = AcaoPdde
        fields = ('id', 'uuid', 'nome', 'categoria', 'categoria_objeto',
                  'aceita_capital', 'aceita_custeio', 'aceita_livre_aplicacao')
        read_only_fields = ('id', 'uuid', 'categoria_objeto')
