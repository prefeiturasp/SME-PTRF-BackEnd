from rest_framework import mixins, status
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from ...models import MotivoEstorno
from ..serializers import MotivoEstornoSerializer
from rest_framework.response import Response


class MotivosEstornoViewSet(mixins.ListModelMixin,
                            mixins.RetrieveModelMixin,
                            mixins.CreateModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin,
                            GenericViewSet):
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'
    queryset = MotivoEstorno.objects.all().order_by('motivo')
    serializer_class = MotivoEstornoSerializer

    def get_queryset(self):
        qs = MotivoEstorno.objects.all()

        motivo = self.request.query_params.get('motivo')
        if motivo is not None:
            qs = qs.filter(motivo__unaccent__icontains=motivo)

        return qs.order_by('motivo')

    def destroy(self, request, *args, **kwargs):
        motivo = self.get_object()

        if motivo.receitas_do_motivo.all():
            content = {
                'erro': 'ProtectedError',
                'mensagem': 'Esse motivo não pode ser excluído, pois existem estornos já cadastrados com o mesmo.'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            self.perform_destroy(motivo)

        return Response(status=status.HTTP_204_NO_CONTENT)

