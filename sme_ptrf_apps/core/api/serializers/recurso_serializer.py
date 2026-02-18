from rest_framework import serializers
from sme_ptrf_apps.core.models import Recurso


class RecursoSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Recurso
        fields = (
            'id',
            'uuid',
            'nome',
            'nome_exibicao',
            'criado_em',
            'alterado_em',
            'cor',
            'logo',
            'icone',
            'ativo',
            'legado'
        )
        read_only_fields = (
            'id',
            'uuid',
            'nome',
            'nome_exibicao',
            'criado_em',
            'alterado_em',
            'cor',
            'logo',
            'icone',
            'ativo',
            'legado'
        )
