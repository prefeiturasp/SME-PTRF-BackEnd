from django.db.models import Q

from django_filters import rest_framework as filters

from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.decorators import action

from sme_ptrf_apps.core.api.serializers import AcaoAssociacaoCreateSerializer, AcaoAssociacaoRetrieveSerializer
from sme_ptrf_apps.core.models import AcaoAssociacao
from sme_ptrf_apps.users.permissoes import PermissaoAssociacao


class AcaoAssociacaoViewSet(mixins.RetrieveModelMixin,
                            mixins.CreateModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin,
                            mixins.ListModelMixin,
                            GenericViewSet):
    lookup_field = 'uuid'
    permission_classes = [IsAuthenticated & PermissaoAssociacao]
    serializer_class = AcaoAssociacaoRetrieveSerializer
    queryset = AcaoAssociacao.objects.all().order_by('associacao__nome', 'acao__nome')
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('acao__uuid', 'status')

    def get_queryset(self):
        qs = AcaoAssociacao.objects.all()

        nome = self.request.query_params.get('nome')
        if nome is not None:
            qs = qs.filter(Q(associacao__nome__unaccent__icontains=nome) | Q(
                associacao__unidade__nome__unaccent__icontains=nome) | Q(
                associacao__unidade__codigo_eol__icontains=nome))

        return qs.order_by('associacao__nome', 'acao__nome')

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return AcaoAssociacaoRetrieveSerializer
        else:
            return AcaoAssociacaoCreateSerializer

    def destroy(self, request, *args, **kwargs):
        from django.db.models.deletion import ProtectedError

        obj = self.get_object()

        try:
            self.perform_destroy(obj)
        except ProtectedError:
            content = {
                'erro': 'ProtectedError',
                'mensagem': 'Essa ação de associação não pode ser excluida porque está sendo usada na aplicação.'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], url_path='excluir-lote')
    def excluir_em_lote(self, request, *args, **kwrgs):
        if not request.data.get('lista_uuids'):
            content = {
                'erro': 'Falta de informações',
                'mensagem': 'É necessário enviar a lista de uuids a serem apagados (lista_uuids).'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        try:
            erros = AcaoAssociacao.excluir_em_lote(request.data.get('lista_uuids'))
            if erros:
                mensagem = f'Alguns vínculos não puderam ser desfeitos por já estarem sendo usados na aplicação.'
            else:
                mensagem = 'Unidades desvinculadas da ação com sucesso.'
            return Response({
                'erros': erros,
                'mensagem': mensagem
            }, status=status.HTTP_201_CREATED)

        except Exception as err:
            error = {
                'erro': "problema_ao_excluir_acoes_associacoes",
                'mensagem': str(err)
            }

            return Response(error, status=status.HTTP_400_BAD_REQUEST)

