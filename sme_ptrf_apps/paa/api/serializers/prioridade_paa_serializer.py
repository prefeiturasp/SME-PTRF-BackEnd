from rest_framework import serializers

from sme_ptrf_apps.paa.models import Paa, PrioridadePaa, ProgramaPdde, AcaoPdde
from sme_ptrf_apps.paa.models.prioridade_paa import SimNaoChoices
from sme_ptrf_apps.core.models import AcaoAssociacao
from sme_ptrf_apps.despesas.models import TipoCusteio, EspecificacaoMaterialServico
from sme_ptrf_apps.paa.enums import RecursoOpcoesEnum, TipoAplicacaoOpcoesEnum
from sme_ptrf_apps.paa.api import serializers as serializers_paa
from sme_ptrf_apps.despesas.api.serializers import especificacao_material_servico_serializer as especif_serializer
from sme_ptrf_apps.despesas.api.serializers import tipo_custeio_serializer


class PrioridadePaaCreateUpdateSerializer(serializers.ModelSerializer):
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
        required=False
    )

    copia_de = serializers.SlugRelatedField(
        slug_field='uuid',
        required=False,
        queryset=PrioridadePaa.objects.all())

    class Meta:
        model = PrioridadePaa
        fields = ('uuid', 'paa', 'prioridade', 'recurso', 'acao_associacao', 'programa_pdde', 'acao_pdde',
                  'tipo_aplicacao', 'tipo_despesa_custeio', 'especificacao_material', 'valor_total', 'copia_de')

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

        # Valida se o valor da prioridade não excede os recursos disponíveis
        # Para recursos PTRF, PDDE e Recursos Próprios
        if (attrs.get('valor_total') and
            attrs.get('tipo_aplicacao') and
            ((attrs.get('recurso') == RecursoOpcoesEnum.PTRF.name and attrs.get('acao_associacao')) or
             (attrs.get('recurso') == RecursoOpcoesEnum.PDDE.name and attrs.get('acao_pdde')) or
             (attrs.get('recurso') == RecursoOpcoesEnum.RECURSO_PROPRIO.name))):
            from sme_ptrf_apps.paa.services import ResumoPrioridadesService
            resumo_service = ResumoPrioridadesService(attrs.get('paa'))

            # Determina o UUID da ação baseado no tipo de recurso
            acao_uuid = None
            if attrs.get('recurso') == RecursoOpcoesEnum.PTRF.name:
                acao_uuid = str(attrs.get('acao_associacao').uuid)
            elif attrs.get('recurso') == RecursoOpcoesEnum.PDDE.name:
                acao_uuid = str(attrs.get('acao_pdde').uuid)
            # Para Recursos Próprios, acao_uuid permanece None

            # Se estamos atualizando uma prioridade existente, passa o UUID e valor atual da prioridade
            prioridade_uuid = None
            valor_atual_prioridade = None
            if self.instance and hasattr(self.instance, 'uuid'):
                prioridade_uuid = str(self.instance.uuid)

                # OR 0 evita os registros de Cópia com valores = None
                valor_atual_prioridade = self.instance.valor_total or 0
            resumo_service.validar_valor_prioridade(
                attrs.get('valor_total'),
                acao_uuid,
                attrs.get('tipo_aplicacao'),
                attrs.get('recurso'),
                prioridade_uuid,
                valor_atual_prioridade
            )

        return super().validate(attrs)


class PrioridadePaaListSerializer(serializers.ModelSerializer):
    paa = serializers.SlugRelatedField(slug_field='uuid', queryset=Paa.objects.all())
    especificacao_material = serializers.SlugRelatedField(
        slug_field='uuid', queryset=EspecificacaoMaterialServico.objects.all())
    especificacao_material_objeto = especif_serializer.EspecificacaoMaterialServicoSimplesSerializer(
        source='especificacao_material')

    tipo_despesa_custeio = serializers.SlugRelatedField(
        slug_field='uuid', queryset=TipoCusteio.objects.all())
    tipo_despesa_custeio_objeto = tipo_custeio_serializer.TipoCusteioSimplesSerializer(
        source='tipo_despesa_custeio')

    acao_pdde = serializers.SlugRelatedField(
        slug_field='uuid', queryset=AcaoPdde.objects.all())
    acao_pdde_objeto = serializers_paa.AcaoPddeSimplesSerializer(
        source='acao_pdde')

    programa_pdde = serializers.SlugRelatedField(
        slug_field='uuid', queryset=ProgramaPdde.objects.all())
    programa_pdde_objeto = serializers_paa.ProgramaPddeSimplesSerializer(
        source='programa_pdde')

    prioridade_objeto = serializers.SerializerMethodField()
    recurso_objeto = serializers.SerializerMethodField()

    tipo_aplicacao_objeto = serializers.SerializerMethodField()

    acao_associacao = serializers.SerializerMethodField()
    acao_associacao_objeto = serializers.SerializerMethodField()

    outro_recurso = serializers.SerializerMethodField()
    outro_recurso_objeto = serializers.SerializerMethodField()

    def get_acao_associacao(self, obj):
        if obj.acao_associacao:
            return obj.acao_associacao.uuid

    def get_acao_associacao_objeto(self, obj):
        if obj.acao_associacao:
            return {
                'uuid': obj.acao_associacao.uuid,
                'nome': obj.acao_associacao.acao.nome
            }

    def get_recurso_objeto(self, obj):
        return {
            'name': RecursoOpcoesEnum[obj.recurso].name,
            'value': RecursoOpcoesEnum[obj.recurso].value,
        }

    def get_tipo_aplicacao_objeto(self, obj):
        return {
            'name': TipoAplicacaoOpcoesEnum[obj.tipo_aplicacao].name,
            'value': TipoAplicacaoOpcoesEnum[obj.tipo_aplicacao].value,
        }

    def get_prioridade_objeto(self, obj):
        return list(filter(lambda x: x.get('key') == obj.prioridade, SimNaoChoices.to_dict()))[0]

    def get_outro_recurso(self, obj):
        if obj.outro_recurso:
            return obj.outro_recurso.uuid

    def get_outro_recurso_objeto(self, obj):
        if obj.outro_recurso:
            return {
                'uuid': obj.outro_recurso.uuid,
                'nome': obj.outro_recurso.nome
            }

    class Meta:
        model = PrioridadePaa
        fields = (
            'uuid',
            'paa',
            'prioridade',
            'prioridade_objeto',
            'recurso',
            'recurso_objeto',
            'acao_associacao',
            'acao_associacao_objeto',
            'programa_pdde',
            'programa_pdde_objeto',
            'acao_pdde',
            'acao_pdde_objeto',
            'tipo_aplicacao',
            'tipo_aplicacao_objeto',
            'tipo_despesa_custeio',
            'tipo_despesa_custeio_objeto',
            'especificacao_material',
            'especificacao_material_objeto',
            'valor_total',
            'outro_recurso',
            'outro_recurso_objeto'
        )
