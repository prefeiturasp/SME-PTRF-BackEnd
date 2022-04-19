from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ...models import MotivoPagamentoAntecipado
from ..serializers.motivo_pagamento_antecipado_serializer import MotivoPagamentoAntecipadoSerializer


class MotivosPagamentoAntecipadoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = MotivoPagamentoAntecipado.objects.all().order_by('motivo')
    serializer_class = MotivoPagamentoAntecipadoSerializer
