from rest_framework import viewsets, status, exceptions
from django.db.models.deletion import ProtectedError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ...models import MotivoPagamentoAntecipado
from ..serializers.motivo_pagamento_antecipado_serializer import MotivoPagamentoAntecipadoSerializer


class MotivosPagamentoAntecipadoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = MotivoPagamentoAntecipado.objects.all().order_by('motivo')
    serializer_class = MotivoPagamentoAntecipadoSerializer

    def get_queryset(self):
        if self.action == 'list':
            filtrar_motivo = self.request.query_params.get('motivo')
            if filtrar_motivo:
                return MotivoPagamentoAntecipado.objects.filter(
                    motivo__unaccent__icontains=filtrar_motivo)

        return MotivoPagamentoAntecipado.objects.all().order_by('motivo')

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        existe_despesa_vinculada = obj.despesa_set.exists()

        if existe_despesa_vinculada:
            raise exceptions.ValidationError({
                    'erro': 'ProtectedError',
                    'mensagem': 'Essa operação não pode ser realizada. Há lançamentos ' +
                    'cadastrados com esse motivo de pagamento antecipado.'
                })
        try:
            self.perform_destroy(obj)
        except ProtectedError:
            content = {
                'erro': 'ProtectedError',
                'mensagem': 'Essa operação não pode ser realizada. Há lançamentos ' +
                    'cadastrados com esse motivo de pagamento antecipado.'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)
