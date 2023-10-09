from rest_framework import viewsets, status
from sme_ptrf_apps.core.api.utils.pagination import CustomPagination
from sme_ptrf_apps.core.models import Associacao
from sme_ptrf_apps.users.permissoes import PermissaoApiSME, PermissaoApiUe
from ...models import Mandato
from ..serializers.mandato_serializer import MandatoSerializer, MandatoVigenteComComposicoesSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from ...services import ServicoMandatoVigente


class MandatosViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated & PermissaoApiSME]
    lookup_field = 'uuid'
    queryset = Mandato.objects.all().order_by('-referencia_mandato')
    serializer_class = MandatoSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        qs = self.queryset

        filtro_referencia = self.request.query_params.get('referencia', None)

        if filtro_referencia is not None:
            qs = qs.filter(referencia_mandato__unaccent__icontains=filtro_referencia)

        return qs

    @action(detail=False, methods=['get'], url_path='mandato-vigente',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def mandato_vigente(self, request):
        from ..serializers.validation_serializers.mandato_validate_serializer import MandatoVigenteValidateSerializer

        query = MandatoVigenteValidateSerializer(data=request.query_params)
        query.is_valid(raise_exception=True)

        associacao_uuid = request.query_params.get('associacao_uuid')
        associacao = Associacao.objects.get(uuid=associacao_uuid)

        servico_mandato_vigente = ServicoMandatoVigente()
        mandato_vigente = servico_mandato_vigente.get_mandato_vigente()

        if mandato_vigente:
            mandato_vigente = MandatoSerializer(mandato_vigente, many=False).data
            result = MandatoVigenteComComposicoesSerializer(mandato_vigente, context={'associacao': associacao}).data
        else:
            result = {
                "composicoes": []
            }

        return Response(result, status=status.HTTP_200_OK)



    def destroy(self, request, *args, **kwargs):
        from django.db.models.deletion import ProtectedError

        obj = self.get_object()

        if obj.composicoes_do_mandato.filter(cargos_da_composicao_da_composicao__isnull=False).exists():
            content = {
                'erro': 'ProtectedError',
                'mensagem': 'Não é possível excluir o período de mandato pois já existem membros cadastrados nas associações.'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        try:
            self.perform_destroy(obj)
        except ProtectedError:
            content = {
                'erro': 'ProtectedError',
                'mensagem': 'Essa operação não pode ser realizada. Há dados vinculados a essa ação da referida Associação'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)
