from rest_framework import serializers
from sme_ptrf_apps.core.api.serializers.unidade_serializer import DreSerializer
from sme_ptrf_apps.core.api.serializers import PeriodoLookUpSerializer
from sme_ptrf_apps.users.api.serializers import UserLookupSerializer
from .analise_consolidado_dre_serializer import AnaliseConsolidadoDreSerializer
from ..serializers.relatorio_consolidado_dre_serializer import RelatorioConsolidadoDreSerializer
from ..serializers.ata_parecer_tecnico_serializer import AtaParecerTecnicoLookUpSerializer
from ...models import ConsolidadoDRE


class ConsolidadoDreSerializer(serializers.ModelSerializer):
    dre = DreSerializer()
    periodo = PeriodoLookUpSerializer()

    class Meta:
        model = ConsolidadoDRE
        fields = ('uuid', 'dre', 'periodo', 'status', 'versao', 'status_sme', 'data_publicacao', 'pagina_publicacao')


class ConsolidadoDreComDocumentosSerializer(serializers.ModelSerializer):
    from ..serializers.lauda_serializer import LaudaLookupSerializer
    relatorios_consolidados_dre_do_consolidado_dre = RelatorioConsolidadoDreSerializer(many=True)
    atas_de_parecer_tecnico_do_consolidado_dre = AtaParecerTecnicoLookUpSerializer(many=True)
    laudas_do_consolidado_dre = LaudaLookupSerializer(many=True)

    class Meta:
        model = ConsolidadoDRE
        fields = (
            'uuid',
            'status',
            'relatorios_consolidados_dre_do_consolidado_dre',
            'atas_de_parecer_tecnico_do_consolidado_dre',
            'laudas_do_consolidado_dre',
        )


class ConsolidadoDreDetalhamentoSerializer(serializers.ModelSerializer):
    tipo_relatorio = serializers.SerializerMethodField('get_tipo_relatorio')
    exibe_reabrir_relatorio = serializers.SerializerMethodField('get_exibe_reabrir_relatorio')
    exibe_analisar = serializers.SerializerMethodField('get_exibe_analisar')
    permite_edicao = serializers.SerializerMethodField('get_permite_edicao')
    responsavel_pela_analise = UserLookupSerializer(many=False, allow_null=True, required=False)
    analise_atual = AnaliseConsolidadoDreSerializer(many=False, allow_null=True, required=False)
    analises_do_consolidado_dre = AnaliseConsolidadoDreSerializer(many=True, allow_null=True, required=False)
    botoes_avancar_e_retroceder = serializers.SerializerMethodField('get_botoes_avancar_e_retroceder')

    dre = DreSerializer()
    periodo = PeriodoLookUpSerializer()

    def get_botoes_avancar_e_retroceder(self, obj):
        obj_botoes = {
            "texto_botao_avancar": None,
            "habilita_botao_avancar": False,
            "texto_botao_retroceder": None,
            "habilita_botao_retroceder": False,
        }
        if obj.status_sme == obj.STATUS_SME_NAO_PUBLICADO:
            obj_botoes = {
                "texto_botao_avancar": None,
                "habilita_botao_avancar": False,
                "texto_botao_retroceder": 'Reabrir para DRE',
                "habilita_botao_retroceder": True,
            }
        elif obj.status_sme == obj.STATUS_SME_PUBLICADO:
            obj_botoes = {
                "texto_botao_avancar": 'Analisar',
                "habilita_botao_avancar": True,
                "texto_botao_retroceder": None,
                "habilita_botao_retroceder": False,
            }
        elif obj.status_sme == obj.STATUS_SME_EM_ANALISE:
            # TODO implementar verificações se existem solicitações de acertos em documentos
            obj_botoes = {
                "texto_botao_avancar": 'Concluir',
                "habilita_botao_avancar": True,
                "texto_botao_retroceder": "Voltar para Publicado no D.O.",
                "habilita_botao_retroceder": True,
            }
        elif obj.status_sme == obj.STATUS_SME_DEVOLVIDO:
            obj_botoes = {
                "texto_botao_avancar": 'Analisar',
                "habilita_botao_avancar": True,
                "texto_botao_retroceder": None,
                "habilita_botao_retroceder": False,
            }

        elif obj.status_sme == obj.STATUS_SME_ANALISADO:
            obj_botoes = {
                "texto_botao_avancar": None,
                "habilita_botao_avancar": False,
                "texto_botao_retroceder": 'Voltar para análise',
                "habilita_botao_retroceder": True,
            }

        return obj_botoes

    def get_tipo_relatorio(self, obj):
        return obj.referencia

    def get_exibe_reabrir_relatorio(self, obj):
        if obj.pode_reabrir():
            return True

        return False

    def get_exibe_analisar(self, obj):
        if obj.status_sme == ConsolidadoDRE.STATUS_SME_PUBLICADO:
            return True

        return False

    def get_permite_edicao(self, obj):
        if obj.permite_edicao():
            return True

        return False

    class Meta:
        model = ConsolidadoDRE
        fields = (
            'uuid',
            'dre',
            'periodo',
            'status',
            'versao',
            'status_sme',
            'data_publicacao',
            'pagina_publicacao',
            'sequencia_de_publicacao',
            'tipo_relatorio',
            'exibe_reabrir_relatorio',
            'exibe_analisar',
            'permite_edicao',
            'responsavel_pela_analise',
            'data_de_inicio_da_analise',
            'analise_atual',
            'analises_do_consolidado_dre',
            'botoes_avancar_e_retroceder',
        )
