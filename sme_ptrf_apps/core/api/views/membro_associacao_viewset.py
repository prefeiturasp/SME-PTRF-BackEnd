from requests import ConnectTimeout, ReadTimeout
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from sme_ptrf_apps.core.api.serializers import MembroAssociacaoCreateSerializer, MembroAssociacaoListSerializer
from sme_ptrf_apps.core.models import MembroAssociacao
from sme_ptrf_apps.core.services import TerceirizadasException, TerceirizadasService, SmeIntegracaoApiService, SmeIntegracaoApiException
from sme_ptrf_apps.users.permissoes import PermissaoApiUe, PermissaoAPITodosComLeituraOuGravacao


class MembroAssociacaoViewSet(mixins.RetrieveModelMixin,
                              mixins.ListModelMixin,
                              mixins.CreateModelMixin,
                              mixins.UpdateModelMixin,
                              mixins.DestroyModelMixin,
                              GenericViewSet):

    lookup_field = 'uuid'
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    serializer_class = MembroAssociacaoListSerializer
    queryset = MembroAssociacao.objects.all()
    filter_backends = (filters.DjangoFilterBackend, SearchFilter)
    filter_fields = ('cpf', 'codigo_identificacao', 'email')

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return MembroAssociacaoListSerializer
        else:
            return MembroAssociacaoCreateSerializer

    def get_queryset(self):
        associacao_uuid = self.request.query_params.get('associacao_uuid')
        if associacao_uuid is None:
            erro = {
                'erro': 'parametros_requerido',
                'mensagem': 'É necessário enviar o uuid da associação como parâmetro..'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        qs = MembroAssociacao.objects.filter(associacao__uuid=associacao_uuid)

        return qs

    @action(detail=False, methods=['get'], url_path='membros-cargos',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def get_membros_cargos(self, request):
        associacao_uuid = self.request.query_params.get('associacao_uuid')

        if associacao_uuid is None:
            erro = {
                'erro': 'parametros_requerido',
                'mensagem': 'É necessário enviar o uuid da associação como parâmetro..'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        result = MembroAssociacao.objects.filter(associacao__uuid=associacao_uuid).all()
        lista_content = []

        for membro in result:
            content = {
                'uuid': membro.uuid,
                'nome': membro.nome,
                'cargo_associacao_key': membro.cargo_associacao,
                'cargo_associacao_value': membro.get_cargo_associacao_display()
            }

            lista_content.append(content)

        return Response(lista_content)

    @action(detail=False, url_path='cargos-diretoria-executiva',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def cargos_diretoria_executiva(self, request):
        lista_cargos = MembroAssociacao.cargos_diretoria_executiva_to_json()
        return Response(lista_cargos)

    @action(detail=False, methods=['get'], url_path='codigo-identificacao',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def consulta_codigo_identificacao(self, request):
        rf = self.request.query_params.get('rf')
        codigo_eol = self.request.query_params.get('codigo-eol')
        associacao_uuid = self.request.query_params.get('associacao_uuid')

        if not rf and not codigo_eol:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o rf ou código eol.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            filtro = {}
            if associacao_uuid:
                filtro['associacao__uuid'] = associacao_uuid

            if codigo_eol:
                filtro["codigo_identificacao__iexact"] = codigo_eol
                self.membro_ja_cadastrado(**filtro)
                result = SmeIntegracaoApiService.get_informacao_aluno(codigo_eol)
                return Response(result)
            else:
                filtro["codigo_identificacao__iexact"] = rf
                self.membro_ja_cadastrado(**filtro)
                result = TerceirizadasService.get_informacao_servidor(rf)
                return Response(result)
        except SmeIntegracaoApiException as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except TerceirizadasException as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ReadTimeout:
            return Response({'detail': 'EOL Timeout'}, status=status.HTTP_400_BAD_REQUEST)
        except ConnectTimeout:
            return Response({'detail': 'EOL Timeout'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='cpf-responsavel',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def consulta_cpf_responsavel(self, request):
        cpf = self.request.query_params.get('cpf')
        associacao_uuid = self.request.query_params.get('associacao_uuid')

        if not cpf:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o cpf do responsável.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            filtro = {}
            if associacao_uuid:
                filtro['associacao__uuid'] = associacao_uuid

            filtro["cpf__iexact"] = cpf
            self.membro_ja_cadastrado(**filtro)

            return Response({'detail': "Pode ser cadastrado."}, status.HTTP_200_OK)
        except SmeIntegracaoApiException as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def membro_ja_cadastrado(self, **kwargs):
        if MembroAssociacao.objects.filter(**kwargs).exists():
            raise SmeIntegracaoApiException('Membro já cadastrado.')
