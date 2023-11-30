from rest_framework import serializers
from ...models import CargoComposicao, Composicao, OcupanteCargo
from sme_ptrf_apps.utils.update_instance_from_dict import update_instance_from_dict


class CargoComposicaoSerializer(serializers.ModelSerializer):
    from sme_ptrf_apps.mandatos.api.serializers.ocupante_cargo_serializer import OcupanteCargoSerializer
    from sme_ptrf_apps.mandatos.api.serializers.composicao_serializer import ComposicaoSerializer

    composicao = ComposicaoSerializer()
    ocupante_do_cargo = OcupanteCargoSerializer()

    class Meta:
        model = CargoComposicao
        fields = (
            'id',
            'uuid',
            'composicao',
            'ocupante_do_cargo',
            'cargo_associacao',
            'substituto',
            'substituido',
        )


class CargoComposicaoLookupSerializer(serializers.ModelSerializer):
    from sme_ptrf_apps.mandatos.api.serializers.ocupante_cargo_serializer import OcupanteCargoSerializer

    cargo_associacao_label = serializers.CharField(source='get_cargo_associacao_display')

    ocupante_do_cargo = OcupanteCargoSerializer()

    class Meta:
        model = CargoComposicao
        fields = (
            'id',
            'uuid',
            'ocupante_do_cargo',
            'cargo_associacao',
            'cargo_associacao_label',
            'substituto',
            'substituido',
        )


class CargoComposicaoCreateSerializer(serializers.ModelSerializer):
    from sme_ptrf_apps.mandatos.api.serializers.ocupante_cargo_serializer import OcupanteCargoCreateSerializer

    composicao = serializers.SlugRelatedField(
        slug_field='uuid',
        queryset=Composicao.objects.all()
    )

    ocupante_do_cargo = OcupanteCargoCreateSerializer()

    def validate(self, data):
        super().validate(data)
        composicao = data['composicao']
        data_inicial_composicao = composicao.data_inicial
        data_final_composicao = composicao.data_final

        data_inicio_no_cargo = data['data_inicio_no_cargo']
        data_fim_no_cargo = data['data_fim_no_cargo']

        if data_inicio_no_cargo < data_inicial_composicao:
            raise serializers.ValidationError(
                "Não é permitido informar período inicial de ocupação anterior ao período inicial do mandato")

        if data_final_composicao and data_inicio_no_cargo > data_final_composicao:
            raise serializers.ValidationError(
                "Não é permitido informar período inicial de ocupação posterior ao período final do mandato.")

        if data_inicio_no_cargo > data_fim_no_cargo:
            raise serializers.ValidationError(
                "Não é permitido informar período inicial de ocupação posterior ao período final de ocupação")

        ocupante_do_cargo_data = data['ocupante_do_cargo']

        """
        A verificações abaixo foram duplicadas propositalmente para retornar uma mensagem mais específica para o usuário,
        a depender da duplicidade de codigo_identificacao ou cpf_responsavel.
        """
        # Verifica se já existe um registro com o mesmo codigo_identificacao na mesma composição
        existing_records = CargoComposicao.objects.filter(
            composicao=composicao,
            ocupante_do_cargo__codigo_identificacao=ocupante_do_cargo_data['codigo_identificacao']
        ).exclude(ocupante_do_cargo__codigo_identificacao__exact='')

        # Se estamos atualizando, exclui o registro atual da verificação de duplicidade
        if self.instance:
            existing_records = existing_records.exclude(id=self.instance.id)

        if existing_records.exists():
            raise serializers.ValidationError(
                "Já existe um Membro cadastrado nessa composição com o mesmo Codigo de identificação. "
                "Verifique por favor."
            )

        # Verifica se já existe um registro com o mesmo cpf_responsavel na mesma composição
        existing_records = (CargoComposicao.objects.filter(
            composicao=composicao,
            ocupante_do_cargo__cpf_responsavel=ocupante_do_cargo_data['cpf_responsavel']
        ).exclude(ocupante_do_cargo__cpf_responsavel__exact=''))

        # Se estamos atualizando, exclui o registro atual da verificação de duplicidade
        if self.instance:
            existing_records = existing_records.exclude(id=self.instance.id)

        if existing_records.exists():
            raise serializers.ValidationError(
                "Já existe um Membro cadastrado nessa composição com o mesmo CPF. Verifique por favor."
            )

        return data

    def create(self, validated_data):
        dados_ocupante_do_cargo = validated_data.pop('ocupante_do_cargo')

        ocupante_do_cargo, created = OcupanteCargo.objects.update_or_create(
            codigo_identificacao=dados_ocupante_do_cargo['codigo_identificacao'],
            cpf_responsavel=dados_ocupante_do_cargo['cpf_responsavel'],
            defaults={**dados_ocupante_do_cargo},
        )

        validated_data['ocupante_do_cargo'] = ocupante_do_cargo

        cargo = CargoComposicao.objects.create(**validated_data)

        return cargo

    def update(self, instance, validated_data):
        # Primeiro valida e depois remove o ocupante_do_cargo
        validated_data.get('ocupante_do_cargo')
        ocupante_do_cargo_data = validated_data.pop('ocupante_do_cargo')

        # Atualiza os campos do CargoComposicao
        update_instance_from_dict(instance, validated_data)

        # Atualiza os campos do OcupanteDoCargo
        if ocupante_do_cargo_data:
            ocupante_do_cargo_instance = instance.ocupante_do_cargo

            update_instance_from_dict(ocupante_do_cargo_instance, ocupante_do_cargo_data)
            ocupante_do_cargo_instance.save()

        instance.save()

        return instance

    class Meta:
        model = CargoComposicao
        fields = (
            'id',
            'uuid',
            'composicao',
            'ocupante_do_cargo',
            'cargo_associacao',
            'data_inicio_no_cargo',
            'data_fim_no_cargo',
            'substituto',
            'substituido',
        )
