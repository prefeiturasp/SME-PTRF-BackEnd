from rest_framework import serializers

from sme_ptrf_apps.paa.models import ReplicaPaa, Paa


class HistoricoObjetivoSerializer(serializers.Serializer):
    nome = serializers.CharField()


class HistoricoReceitaSerializer(serializers.Serializer):
    previsao_valor_capital = serializers.CharField(required=False)
    previsao_valor_custeio = serializers.CharField(required=False)
    previsao_valor_livre = serializers.CharField(required=False)
    saldo_custeio = serializers.CharField(required=False)
    saldo_capital = serializers.CharField(required=False)
    saldo_livre = serializers.CharField(required=False)
    saldo_congelado_custeio = serializers.CharField(required=False)
    saldo_congelado_capital = serializers.CharField(required=False)
    saldo_congelado_livre = serializers.CharField(required=False)


class HistoricoPrioridadeSerializer(serializers.Serializer):
    recurso = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    prioridade = serializers.IntegerField(required=False, allow_null=True)
    tipo_aplicacao = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    valor_total = serializers.CharField(required=False, allow_null=True)
    acao_associacao_uuid = serializers.UUIDField(required=False, allow_null=True)
    programa_pdde_uuid = serializers.UUIDField(required=False, allow_null=True)
    acao_pdde_uuid = serializers.UUIDField(required=False, allow_null=True)
    outro_recurso_uuid = serializers.UUIDField(required=False, allow_null=True)
    tipo_despesa_custeio_uuid = serializers.UUIDField(required=False, allow_null=True)
    especificacao_material_uuid = serializers.UUIDField(required=False, allow_null=True)


class HistoricoPaaSerializer(serializers.Serializer):
    CAMPOS_OBRIGATORIOS = {
        'texto_introducao', 'texto_conclusao', 'objetivos',
        'receitas_ptrf', 'receitas_pdde', 'receitas_outros_recursos', 'prioridades',
    }

    texto_introducao = serializers.CharField(required=True, allow_blank=True, allow_null=True)
    texto_conclusao = serializers.CharField(required=True, allow_blank=True, allow_null=True)
    objetivos = serializers.DictField(child=HistoricoObjetivoSerializer(), required=True)
    receitas_ptrf = serializers.DictField(child=HistoricoReceitaSerializer(), required=True)
    receitas_pdde = serializers.DictField(child=HistoricoReceitaSerializer(), required=True)
    receitas_outros_recursos = serializers.DictField(child=HistoricoReceitaSerializer(), required=True)
    prioridades = serializers.DictField(child=HistoricoPrioridadeSerializer(), required=True)

    def validate(self, data):
        ausentes = self.CAMPOS_OBRIGATORIOS - set(data.keys())
        if ausentes:
            raise serializers.ValidationError(
                dict.fromkeys(ausentes, "Este campo é obrigatório.")
            )
        return data

    def validate_objetivos(self, value):
        for uuid_key, dados in value.items():
            if not isinstance(dados, dict) or 'nome' not in dados:
                raise serializers.ValidationError(
                    f"Objetivo '{uuid_key}' deve conter o campo 'nome'."
                )
        return value

    def validate_receitas_ptrf(self, value):
        return self._validar_receitas(value, 'receitas_ptrf')

    def validate_receitas_pdde(self, value):
        return self._validar_receitas(value, 'receitas_pdde')

    def validate_receitas_outros_recursos(self, value):
        return self._validar_receitas(value, 'receitas_outros_recursos')

    def _validar_receitas(self, value, campo):
        campos_receita = {
            'previsao_valor_capital', 'previsao_valor_custeio', 'previsao_valor_livre'
        }
        for uuid_key, dados in value.items():
            if not isinstance(dados, dict):
                raise serializers.ValidationError(
                    f"Receita '{uuid_key}' em '{campo}' deve ser um objeto."
                )
            ausentes = campos_receita - set(dados.keys())
            if ausentes:
                raise serializers.ValidationError(
                    f"Receita '{uuid_key}' em '{campo}' está faltando os campos: {ausentes}."
                )
        return value


class ReplicaPaaSerializer(serializers.ModelSerializer):
    paa = serializers.SlugRelatedField(queryset=Paa.objects.all(), slug_field='uuid')
    historico = HistoricoPaaSerializer()

    class Meta:
        model = ReplicaPaa
        fields = ('uuid', 'paa', 'historico', 'criado_em', 'alterado_em')
        read_only_fields = ('uuid', 'criado_em', 'alterado_em')

    def validate_historico(self, value):
        serializer = HistoricoPaaSerializer(data=value)
        if not serializer.is_valid():
            raise serializers.ValidationError(serializer.errors)
        return value

    def create(self, validated_data):
        historico_data = validated_data.pop('historico')
        return ReplicaPaa.objects.create(historico=historico_data, **validated_data)
