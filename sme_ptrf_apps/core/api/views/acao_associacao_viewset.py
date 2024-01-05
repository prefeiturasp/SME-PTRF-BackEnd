from django.db.models import Q
from django.core.exceptions import ValidationError
from django_filters import rest_framework as filters

from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework.decorators import action

from sme_ptrf_apps.core.api.serializers import AcaoAssociacaoCreateSerializer, AcaoAssociacaoRetrieveSerializer
from sme_ptrf_apps.core.choices.filtro_informacoes_associacao import FiltroInformacoesAssociacao
from sme_ptrf_apps.core.models import AcaoAssociacao, Acao, Associacao
from sme_ptrf_apps.users.permissoes import PermissaoApiUe, PermissaoAPITodosComGravacao


class AcaoAssociacaoViewSet(mixins.RetrieveModelMixin,
                            mixins.CreateModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin,
                            mixins.ListModelMixin,
                            GenericViewSet):
    lookup_field = 'uuid'
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    serializer_class = AcaoAssociacaoRetrieveSerializer
    queryset = AcaoAssociacao.objects.all().order_by('associacao__nome', 'acao__nome')
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('acao__uuid', 'status', 'associacao__uuid')

    def get_queryset(self):
        qs = AcaoAssociacao.objects.all()

        nome = self.request.query_params.get('nome')
        filtro_informacoes = self.request.query_params.get('filtro_informacoes')
        filtro_informacoes_list = filtro_informacoes.split(',') if filtro_informacoes else []

        encerradas = FiltroInformacoesAssociacao.FILTRO_INFORMACOES_ENCERRADAS
        nao_encerradas = FiltroInformacoesAssociacao.FILTRO_INFORMACOES_NAO_ENCERRADAS

        if nome is not None:
            qs = qs.filter(Q(associacao__nome__unaccent__icontains=nome) | Q(
                associacao__unidade__nome__unaccent__icontains=nome) | Q(
                associacao__unidade__codigo_eol__icontains=nome))

        if filtro_informacoes_list:
            if encerradas in filtro_informacoes_list and nao_encerradas in filtro_informacoes_list:
                qs = qs
            elif nao_encerradas in filtro_informacoes_list:
                qs = qs.filter(associacao__data_de_encerramento__isnull=True)

            elif encerradas in filtro_informacoes_list:
                qs = qs.filter(associacao__data_de_encerramento__isnull=False)

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
                'mensagem': 'Essa operação não pode ser realizada. Há dados vinculados a essa ação da referida Associação'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], url_path='excluir-lote',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComGravacao])
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

    @action(detail=False, methods=['post'], url_path='incluir-lote',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComGravacao])
    def incluir_lote(self, request, *args, **kwrgs):
        acao_uuid = request.data.get('acao_uuid')
        associacoes_uuids = request.data.get('associacoes_uuids')

        if not acao_uuid or not associacoes_uuids:
            content = {
                'erro': 'Falta de informações',
                'mensagem': 'É necessário enviar a acao_uuid e lista associacoes_uuids.'
            }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        try:
            acao = Acao.objects.get(uuid=acao_uuid)
        except Acao.DoesNotExist:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto ação para o uuid {acao_uuid} não foi encontrado na base."
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        associacoes = []
        erros_parametros = []
        for associacao_uuid in associacoes_uuids:
            try:
                associacao = Associacao.objects.get(uuid=associacao_uuid)
                associacoes.append(associacao)
            except Associacao.DoesNotExist:
                erro = {
                    'erro': 'Associação não encontrada',
                    'mensagem': f"O objeto associação para o uuid {associacao_uuid} não foi encontrado na base."
                }
                erros_parametros.append(erro)

        try:
            erros_criacao = AcaoAssociacao.incluir_em_lote(acao=acao, associacoes=associacoes)
            if erros_parametros or erros_criacao:
                mensagem = f'Alguns vínculos não puderam ser feitos.'
            else:
                mensagem = 'Unidades vinculadas à ação com sucesso.'
            return Response({
                'erros': erros_parametros + erros_criacao,
                'mensagem': mensagem
            }, status=status.HTTP_201_CREATED)

        except Exception as err:
            error = {
                'erro': "problema_ao_incluir_acoes_associacoes",
                'mensagem': str(err)
            }

            return Response(error, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            erro = {
                'erro': 'validation_error',
                'mensagem': e
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance=instance, data=request.data)

        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            erro = {
                'erro': 'validation_error',
                'mensagem': e
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)
