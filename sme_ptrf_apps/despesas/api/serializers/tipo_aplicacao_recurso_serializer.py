from rest_framework import serializers

from ...models import TipoAplicacaoRecurso


class TipoAplicacaoRecursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoAplicacaoRecurso
        fields = ('id', 'nome')
