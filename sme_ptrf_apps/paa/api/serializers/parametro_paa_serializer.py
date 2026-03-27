from sme_ptrf_apps.paa.models import ParametroPaa
from rest_framework import serializers


class ParametroPaaSerializer(serializers.ModelSerializer):
    texto_pagina_paa_ue = serializers.CharField(allow_blank=True, error_messages={
        'null': ('O campo Explicação sobre o PAA não foi informado.')})

    texto_atividades_previstas = serializers.CharField(allow_blank=True, error_messages={
        'null': ('O campo Atividades previstas não foi informado.')})

    texto_levantamento_prioridades = serializers.CharField(allow_blank=True, error_messages={
        'null': ('O campo Levantamento de Prioridades não foi informado.')})

    introducao_do_paa_ue_1 = serializers.CharField(allow_blank=True, error_messages={
        'null': ('O campo Introdução 1 da aba Relatórios não foi informado.')})

    introducao_do_paa_ue_2 = serializers.CharField(allow_blank=True, error_messages={
        'null': ('O campo Introdução 2 da aba Relatórios não foi informado.')})

    conclusao_do_paa_ue_1 = serializers.CharField(allow_blank=True, error_messages={
        'null': ('O campo Conclusão do PAA 1 não foi informado.')})

    conclusao_do_paa_ue_2 = serializers.CharField(allow_blank=True, error_messages={
        'null': ('O campo Conclusão da aba Relatórios não foi informado.')})

    """
    Serializer para o modelo ParametroPaa.
    """
    class Meta:
        model = ParametroPaa
        fields = ('texto_pagina_paa_ue', 'texto_atividades_previstas',
                  'texto_levantamento_prioridades', 'introducao_do_paa_ue_1',
                  'introducao_do_paa_ue_2', 'conclusao_do_paa_ue_1',
                  'conclusao_do_paa_ue_2',
                  )
