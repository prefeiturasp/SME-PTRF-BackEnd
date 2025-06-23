from rest_framework import serializers

from sme_ptrf_apps.paa.models import Paa, PrioridadePaa, ProgramaPdde, AcaoPdde
from sme_ptrf_apps.paa.models.prioridade_paa import SimNaoChoices
from sme_ptrf_apps.core.models import AcaoAssociacao
from sme_ptrf_apps.despesas.models import TipoCusteio, EspecificacaoMaterialServico
from sme_ptrf_apps.paa.enums import RecursoOpcoesEnum, TipoAplicacaoOpcoesEnum


class PrioridadePaaCreateSerializer(serializers.ModelSerializer):
    prioridade = serializers.ChoiceField(
        choices=SimNaoChoices.choices,
        error_messages={
            'invalid_choice': 'Valor inválido para prioridade.',
            'null': 'Prioridade não foi informada.',
            'required': 'Prioridade não foi informada.'
        },
        required=True
    )
    tipo_aplicacao = serializers.ChoiceField(
        choices=TipoAplicacaoOpcoesEnum.choices(),
        error_messages={
            'invalid_choice': 'Valor inválido para tipo de aplicação.',
            'null': 'Tipo de aplicação não foi informada.',
            'required': 'Tipo de aplicação não foi informada.'
        },
        required=True
    )
    recurso = serializers.ChoiceField(
        choices=RecursoOpcoesEnum.choices(),
        error_messages={
            'invalid_choice': 'Valor inválido para Recurso.',
            'null': 'Recurso não foi informado.',
            'required': 'Recurso não foi informado.'
        },
        required=True
    )
    paa = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,  # Definido como false para validação manual no validate()
        queryset=Paa.objects.all())

    programa_pdde = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        error_messages={'null': 'Programa PDDE não foi informado.'},
        queryset=ProgramaPdde.objects.all())

    acao_pdde = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        error_messages={'null': 'Ação PDDE não foi informado.'},
        queryset=AcaoPdde.objects.all())

    acao_associacao = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        error_messages={'null': 'Ação da Associação não foi informada.'},
        queryset=AcaoAssociacao.objects.all())

    tipo_despesa_custeio = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        error_messages={'null': 'Tipo de despesa não foi informado.'},
        queryset=TipoCusteio.objects.all())

    especificacao_material = serializers.SlugRelatedField(
        slug_field='uuid',
        required=True,
        error_messages={
            'null': 'Especificação de material/serviço não foi informada.',
            'required': 'Especificação de material/serviço não foi informada.'
        },
        queryset=EspecificacaoMaterialServico.objects.all())

    valor_total = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0,
        error_messages={
            'min_value': 'O valor total não pode ser negativo.',
            'required': 'O valor total não foi informado.',
            'null': 'O valor total não foi informado.'
        },
        required=True
    )

    class Meta:
        model = PrioridadePaa
        fields = ('uuid', 'paa', 'prioridade', 'recurso', 'acao_associacao', 'programa_pdde', 'acao_pdde',
                  'tipo_aplicacao', 'tipo_despesa_custeio', 'especificacao_material', 'valor_total')

    def validate(self, attrs):
        if not attrs.get('paa'):
            raise serializers.ValidationError({'paa': 'PAA não informado.'})

        if attrs.get('recurso') == RecursoOpcoesEnum.PTRF.name:
            # Requer Ação associacao quando o Recurso é PTRF
            if not attrs.get('acao_associacao'):
                raise serializers.ValidationError(
                    {'acao_associacao': 'Ação de Associação não informada quando o tipo de Recurso é PTRF.'})
        else:
            # Limpa Ação associacao quando o Recurso é diferente de PTRF
            attrs['acao_associacao'] = None

        if attrs.get('recurso') == RecursoOpcoesEnum.PDDE.name:
            # Requer Programa e Ação PDDE quando o Recurso é PDDE
            if not attrs.get('programa_pdde'):
                raise serializers.ValidationError(
                    {'programa_pdde': 'Programa PDDE não foi informado quando o tipo de Recurso é PDDE.'})

            if not attrs.get('acao_pdde'):
                raise serializers.ValidationError(
                    {'acao_pdde': 'Ação PDDE não foi informado quando o tipo de Recurso é PDDE.'})
        else:
            # Limpa Ação PDDE e Programa quando o Recurso é diferente de PDDE
            attrs['programa_pdde'] = None
            attrs['acao_pdde'] = None

        if attrs.get('tipo_aplicacao') == TipoAplicacaoOpcoesEnum.CUSTEIO.name:
            # Requer Tipo de despesa quando o tipo de aplicação é Custeio
            if not attrs.get('tipo_despesa_custeio'):
                raise serializers.ValidationError(
                    {'tipo_despesa_custeio': 'Tipo de despesa não informado quando o tipo de aplicação é Custeio.'})
        else:
            # Limpa Tipo de despesa quando o tipo de aplicação é diferente de Custeio
            attrs['tipo_despesa_custeio'] = None

        if not attrs.get('especificacao_material'):
            raise serializers.ValidationError(
                {'especificacao_material': 'Especificação de Material e Serviço não informado.'})
        return super().validate(attrs)


class PrioridadePaaListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrioridadePaa
        fields = ('uuid', 'paa', 'prioridade', 'recurso', 'acao_associacao', 'programa_pdde', 'acao_pdde',
                  'tipo_aplicacao', 'tipo_despesa_custeio', 'especificacao_material', 'valor_total')
