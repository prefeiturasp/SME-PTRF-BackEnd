from rest_framework import serializers

from sme_ptrf_apps.paa.models import PeriodoPaa
from sme_ptrf_apps.paa.utils import ajustar_data_inicial_e_final, validar_data_final


class PeriodoPaaSerializer(serializers.ModelSerializer):
    data_inicial = serializers.DateField(required=True)
    data_final = serializers.DateField(required=True)

    class Meta:
        model = PeriodoPaa
        fields = ('uuid', 'id', 'referencia', 'data_inicial', 'data_final', 'editavel')

    def create(self, validated_data):
        referencia = validated_data.get('referencia')
        data_inicial = validated_data.get('data_inicial')
        data_final = validated_data.get('data_final')

        # Ajustar as datas para alterar os dias
        data_inicial_ajustada, data_final_ajustada = ajustar_data_inicial_e_final(data_inicial, data_final)

        # Validar se a data final é maior ou igual à data inicial ou se tem o mesmo mês com dias diferentes
        data_final_e_valida, mensagem = validar_data_final(data_inicial_ajustada, data_final_ajustada)
        if not data_final_e_valida:
            raise serializers.ValidationError({
                'non_field_errors': mensagem
            })

        if PeriodoPaa.objects.filter(
            referencia=referencia,
            data_inicial__year=data_inicial_ajustada.year,
            data_inicial__month=data_inicial_ajustada.month,
            data_final__year=data_final_ajustada.year,
            data_final__month=data_final_ajustada.month,
            ).exists():
            raise serializers.ValidationError({
                'non_field_errors': 'Referência do PAA já existe.'
                })

        validated_data['data_inicial'] = data_inicial_ajustada
        validated_data['data_final'] = data_final_ajustada
        instance = super().create(validated_data)
        return instance

    def update(self, instance, validated_data):
        referencia = validated_data.get('referencia')
        data_inicial = validated_data.get('data_inicial') or instance.data_inicial
        data_final = validated_data.get('data_final') or instance.data_final

        # Ajustar as datas para alterar os dias
        data_inicial_ajustada, data_final_ajustada = ajustar_data_inicial_e_final(data_inicial, data_final)

        # Validar se a data final é maior ou igual à data inicial ou se tem o mesmo mês com dias diferentes
        data_final_e_valida, mensagem = validar_data_final(data_inicial_ajustada, data_final_ajustada)
        if not data_final_e_valida:
            raise serializers.ValidationError({
                'non_field_errors': mensagem
            })

        if PeriodoPaa.objects.filter(
            referencia=referencia,
            data_inicial__year=data_inicial_ajustada.year,
            data_inicial__month=data_inicial_ajustada.month,
            data_final__year=data_final_ajustada.year,
            data_final__month=data_final_ajustada.month,).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError({
                'non_field_errors': 'Referência do PAA já existe.'
                })

        validated_data['data_inicial'] = data_inicial_ajustada
        validated_data['data_final'] = data_final_ajustada
        instance = super().update(instance, validated_data)
        return instance
