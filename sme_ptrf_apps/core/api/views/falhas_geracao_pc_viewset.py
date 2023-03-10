from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from ..serializers.falha_geracao_pc_serializer import FalhaGeracaoPcSerializer
from ...models import FalhaGeracaoPc, Associacao, Periodo


class FalhaGeracaoPcViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = FalhaGeracaoPc.objects.all()
    serializer_class = FalhaGeracaoPcSerializer

    @action(detail=False, methods=['get'], url_path='info-registro-falha-geracao-pc',
            permission_classes=[IsAuthenticated])
    def info_registro_falha_geracao_pc(self, request):
        from ..serializers.validation_serializers.falha_geracao_pc_validation_serializer import FalhaGeracaoPcValidationSerializer
        from ...services.falha_geracao_pc_service import InfoRegistroFalhaGeracaoPc

        query = FalhaGeracaoPcValidationSerializer(data=self.request.query_params)
        query.is_valid(raise_exception=True)

        associacao = Associacao.by_uuid(self.request.query_params.get('associacao'))
        usuario = request.user

        registros = InfoRegistroFalhaGeracaoPc(
            associacao=associacao,
            usuario=usuario
        ).info_registro_falha_geracao_pc()

        return Response(registros, status=status.HTTP_200_OK)
