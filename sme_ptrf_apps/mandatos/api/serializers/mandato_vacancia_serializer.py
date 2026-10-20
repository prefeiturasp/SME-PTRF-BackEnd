from datetime import date, timedelta
from typing import Optional

from rest_framework import serializers
from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_400_BAD_REQUEST

from ...models import Mandato
from ...services import ServicoMandatoVacancia


class CustomError(APIException):
    """ Erro de validação de regra de negócio, sempre HTTP 400. """

    def __init__(self, msg: dict) -> None:
        APIException.__init__(self, msg)
        self.status_code = HTTP_400_BAD_REQUEST
        self.message = msg


class MandatoVacanciaSerializer(serializers.ModelSerializer):
    editavel = serializers.SerializerMethodField('get_editavel')
    data_inicial_proximo_mandato = serializers.SerializerMethodField('get_data_inicial_proximo_mandato')
    data_final_mandato_anterior_ao_mais_recente = serializers.SerializerMethodField(
        'get_data_final_mandato_anterior_ao_mais_recente')
    limite_min_data_inicial = serializers.SerializerMethodField('get_limite_min_data_inicial')

    def get_editavel(self, obj: Mandato) -> bool:
        """Retorna True se o mandato é o vigente ou futuro (editável), False caso contrário."""
        return obj.eh_mandato_vacancia_vigente() or obj.eh_mandato_vacancia_futuro()

    def get_data_inicial_proximo_mandato(self, obj: Mandato) -> Optional[date]:
        """Retorna a data inicial do próximo mandato, caso exista, ou None caso contrário."""
        servico_mandato = ServicoMandatoVacancia()
        mandato_mais_recente = servico_mandato.get_mandato_mais_recente()
        if obj == mandato_mais_recente:
            return obj.data_final + timedelta(days=1)
        else:
            return None

    def get_data_final_mandato_anterior_ao_mais_recente(self, obj: Mandato) -> Optional[date]:
        """Retorna o dia seguinte ao término do mandato anterior ao mais recente, ou None."""
        servico_mandato = ServicoMandatoVacancia()
        mandato_anterior_ao_mais_recente = servico_mandato.get_mandato_anterior_ao_mais_recente()
        result = None
        if mandato_anterior_ao_mais_recente:
            result = mandato_anterior_ao_mais_recente.data_final + timedelta(days=1)
        return result

    def get_limite_min_data_inicial(self, obj: Mandato) -> Optional[date]:
        """Retorna o dia seguinte ao término do mandato imediatamente anterior a este, ou None."""
        mandato_anterior = Mandato.objects.filter(
            data_final__lt=obj.data_inicial
        ).order_by('id').last()

        result = None
        if mandato_anterior:
            result = mandato_anterior.data_final + timedelta(days=1)

        return result

    def update(self, instance: Mandato, validated_data: dict) -> Mandato:
        data_inicial = validated_data["data_inicial"]
        data_final = validated_data["data_final"]
        referencia_mandato = validated_data["referencia_mandato"]

        if instance.data_inicial != data_inicial:
            instance.att_data_inicio_composicao_vacancia(
                data_inicial_antiga=instance.data_inicial,
                nova_data=data_inicial
            )

        if instance.data_final != data_final:
            instance.att_data_fim_composicao_vacancia(
                data_final_antiga=instance.data_final,
                nova_data=data_final
            )

        instance.data_inicial = data_inicial
        instance.data_final = data_final
        instance.referencia_mandato = referencia_mandato
        instance.save()

        return instance

    class Meta:
        model = Mandato
        fields = ('id', 'uuid', 'referencia_mandato', 'data_inicial', 'data_final', 'editavel',
                  'data_inicial_proximo_mandato', 'data_final_mandato_anterior_ao_mais_recente',
                  'limite_min_data_inicial')

    def validate(self, data: dict) -> dict:
        data_inicial = data.get('data_inicial')
        data_final = data.get('data_final')

        servico_mandato = ServicoMandatoVacancia()
        mandato_mais_recente = servico_mandato.get_mandato_mais_recente()

        if self.instance:
            if data_final and self.instance.possui_cargo_vacancia_incompativel_com_nova_data_final(data_final):
                raise CustomError({
                    "detail": (
                        "Não é possível editar a data final do mandato. Há registros de "
                        "composição de membros com data incompatível com a nova data final."
                    )
                })

            if data_inicial and self.instance.possui_cargo_vacancia_incompativel_com_nova_data_inicial(data_inicial):  # noqa
                raise CustomError({
                    "detail": (
                        "Não é possível editar a data inicial do mandato. Há registros de "
                        "composição de membros com data incompatível com a nova data inicial."
                    )
                })

        # Verificar se a data inicial é maior que a data final do mandato mais recente no caso de uma inclusão
        if data_inicial and not self.instance and mandato_mais_recente:
            data_final_mandato_recente = mandato_mais_recente.data_final
            if data_inicial <= data_final_mandato_recente:
                raise CustomError({
                    "detail": (
                        "A data inicial do período de mandato deve ser maior que a data final do mandato anterior"
                    )
                })

        # Verificar se a data final é menor que a data inicial
        if data_inicial and data_final and data_final < data_inicial:
            raise CustomError({"detail": "A data final não pode ser menor que a data inicial"})

        # Verificar se a data inicial está dentro de outro mandato existente
        if data_inicial and data_final:
            mandatos = Mandato.objects.filter(
                data_inicial__lte=data_inicial, data_final__gte=data_inicial)

            if self.instance:
                # Excluir o próprio objeto atual ao verificar colisões
                mandatos = mandatos.exclude(uuid=self.instance.uuid)

            if mandatos.exists():
                raise CustomError({"detail": "A data inicial informada é de vigência de outro mandato cadastrado."})

            # Verificar se as datas estão dentro do intervalo de outros mandatos
            overlapped_mandatos = Mandato.objects.filter(
                data_inicial__lte=data_final, data_final__gte=data_inicial)

            if self.instance:
                # Exclui o próprio mandato atual, caso esteja sendo atualizado
                overlapped_mandatos = overlapped_mandatos.exclude(uuid=self.instance.uuid)

            if overlapped_mandatos.exists():
                raise CustomError({"detail": "As datas do mandato se sobrepõem com outros mandatos já cadastrados."})

        return data
