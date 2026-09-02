from rest_framework import serializers
from ...exceptions import CargoComposicaoVacanciaValidationError
from ...models import CargoComposicaoVacancia, OcupanteCargo, ComposicaoVacancia
from .ocupante_cargo_serializer import OcupanteCargoCreateSerializer, OcupanteCargoSerializer
from ...services import ServicoHistoricoCargoComposicao


class CargoComposicaoVacanciaCreateSerializer(serializers.ModelSerializer):
    composicao = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=ComposicaoVacancia.objects.all()
    )
    ocupante_do_cargo = OcupanteCargoCreateSerializer()

    class Meta:
        model = CargoComposicaoVacancia
        fields = (
            'id',
            'uuid',
            'composicao',
            'ocupante_do_cargo',
            'cargo_associacao',
            'data_inicio_no_cargo'
        )

    def create(self, validated_data) -> CargoComposicaoVacancia:
        composicao_vacancia = validated_data.get('composicao')
        dados_ocupante = validated_data.pop('ocupante_do_cargo')

        ocupante_do_cargo, _ = OcupanteCargo.objects.update_or_create(
            codigo_identificacao=dados_ocupante.get('codigo_identificacao'),
            cpf_responsavel=dados_ocupante.get('cpf_responsavel'),
            defaults={**dados_ocupante},
        )

        try:
            return ServicoHistoricoCargoComposicao.registrar_entrada(
                composicao_vacancia=composicao_vacancia,
                ocupante_do_cargo=ocupante_do_cargo,
                cargo_associacao=validated_data.get('cargo_associacao'),
                data_entrada=validated_data.get('data_inicio_no_cargo')
            )
        except CargoComposicaoVacanciaValidationError as e:
            raise serializers.ValidationError(e.detail)


class RegistrarSaidaSerializer(serializers.Serializer):
    data_saida = serializers.DateField(required=True)


class CargoComposicaoVacanciaSerializer(serializers.ModelSerializer):
    ocupante_do_cargo = OcupanteCargoSerializer(allow_null=True)
    cargo_associacao_label = serializers.CharField(source='get_cargo_associacao_display')
    vago = serializers.SerializerMethodField()

    def get_vago(self, obj):
        return obj.ocupante_do_cargo_id is None

    class Meta:
        model = CargoComposicaoVacancia
        fields = (
            'id', 'uuid',
            'ocupante_do_cargo',
            'cargo_associacao', 'cargo_associacao_label',
            'data_inicio_no_cargo', 'data_fim_no_cargo',
            'vago', 'substituto', 'substituido', 'substituido_por'
        )


class CargoComposicaoVacanciaEditarOcupanteSerializer(serializers.ModelSerializer):
    """ Edição dos dados do ocupante já existente.

    Não permite alterar `cargo_associacao`, datas e vínculos, são fonte verdade no cargo da composição.
    Essas mudanças passam exclusivamente pelas ações dedicadas de entrada/saída/cancelar/corrigir, que
    aplicam os validators.
    """
    ocupante_do_cargo = OcupanteCargoCreateSerializer(required=False)

    class Meta:
        model = CargoComposicaoVacancia
        fields = ('id', 'uuid', 'ocupante_do_cargo')
        read_only_fields = ('id', 'uuid')

    def update(self, instance, validated_data) -> CargoComposicaoVacancia:
        dados_ocupante = validated_data.pop('ocupante_do_cargo')

        try:
            return ServicoHistoricoCargoComposicao.editar_ocupante(
                cargo_composicao_vacancia=instance,
                dados_ocupante=dados_ocupante,
            )
        except CargoComposicaoVacanciaValidationError as e:
            raise serializers.ValidationError(e.detail)
