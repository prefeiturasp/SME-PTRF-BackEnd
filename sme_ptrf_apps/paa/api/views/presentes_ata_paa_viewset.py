import logging
from rest_framework import mixins
from django_filters import rest_framework as filters
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError

from drf_spectacular.utils import extend_schema_view

from sme_ptrf_apps.users.permissoes import PermissaoApiUe
from sme_ptrf_apps.paa.models import ParticipanteAtaPaa, AtaPaa
from sme_ptrf_apps.paa.api.serializers.presentes_ata_paa_serializer import (
    PresentesAtaPaaSerializer,
    PresentesAtaPaaCreateSerializer
)
from sme_ptrf_apps.core.services import TerceirizadasException, TerceirizadasService, SmeIntegracaoApiException
from sme_ptrf_apps.core.choices import MembroEnum
from sme_ptrf_apps.utils.remove_digitos_str import remove_digitos
from requests import ConnectTimeout, ReadTimeout
from .docs.presentes_ata_paa_docs import DOCS

logger = logging.getLogger(__name__)


@extend_schema_view(**DOCS)
class PresentesAtaPaaViewSet(mixins.CreateModelMixin,
                             mixins.RetrieveModelMixin,
                             mixins.UpdateModelMixin,
                             mixins.DestroyModelMixin,
                             mixins.ListModelMixin,
                             GenericViewSet):
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    queryset = ParticipanteAtaPaa.objects.all()
    serializer_class = PresentesAtaPaaSerializer
    filterset_fields = ('ata_paa__uuid',)
    filter_backends = (filters.DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PresentesAtaPaaCreateSerializer
        return PresentesAtaPaaSerializer

    @action(detail=False, url_path='buscar-informacao-professor-gremio',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def buscar_informacao_professor_gremio(self, request):
        rf = request.query_params.get('rf')

        if not rf:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o RF do servidor.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            if len(rf) == 7:
                servidor = TerceirizadasService.get_informacao_servidor(rf)
                if servidor:
                    result = {
                        "mensagem": "buscando-servidor-nao-membro",
                        "nome": servidor[0]["nm_pessoa"],
                        "cargo": servidor[0]["cargo"]
                    }
                    return Response(result)
        except SmeIntegracaoApiException as e:
            logger.error(f'Erro ao buscar servidor: {str(e)}')
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except TerceirizadasException as e:
            logger.error(f'Erro ao buscar servidor: {str(e)}')
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except ReadTimeout:
            return Response({'detail': 'EOL Timeout'}, status=status.HTTP_400_BAD_REQUEST)
        except ConnectTimeout:
            return Response({'detail': 'EOL Timeout'}, status=status.HTTP_400_BAD_REQUEST)

        result = {
            "mensagem": "servidor-nao-encontrado",
            "nome": "",
            "cargo": ""
        }

        return Response(result)

    @action(detail=False, url_path='get-participantes-ordenados-por-cargo',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def get_participantes_ordenados_por_cargo(self, request):
        """
        Retorna todos os participantes de uma ata PAA ordenados pelo cargo.
        """
        ata_paa_uuid = request.query_params.get('ata_paa_uuid')

        if not ata_paa_uuid:
            return Response({'erro': 'O parâmetro "ata_paa_uuid" é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ata_paa = AtaPaa.objects.get(uuid=ata_paa_uuid)
        except AtaPaa.DoesNotExist:
            return Response({'erro': 'A ata PAA especificada não existe'}, status=status.HTTP_404_NOT_FOUND)

        participantes = ParticipanteAtaPaa.objects.filter(ata_paa=ata_paa).values()
        participantes_ordenados = sorted(participantes, key=ParticipanteAtaPaa.ordenar_por_cargo)

        # Buscar UUIDs do presidente e secretário para comparação
        presidente_uuid = str(ata_paa.presidente_da_reuniao.uuid) if ata_paa.presidente_da_reuniao else None
        secretario_uuid = str(ata_paa.secretario_da_reuniao.uuid) if ata_paa.secretario_da_reuniao else None

        response_data = []
        for participante in participantes_ordenados:
            data = {
                'uuid': participante['uuid'],
                'identificacao': participante['identificacao'],
                'nome': participante['nome'],
                'cargo': participante['cargo'],
                'membro': participante['membro'],
                'presente': participante['presente'],
                'professor_gremio': participante.get('professor_gremio', False),
                'presidente_da_reuniao': str(participante['uuid']) == presidente_uuid if presidente_uuid else False,
                'secretario_da_reuniao': str(participante['uuid']) == secretario_uuid if secretario_uuid else False
            }
            response_data.append(data)

        return Response(response_data)

    @action(detail=False, url_path='padrao-de-presentes', permission_classes=[IsAuthenticated & PermissaoApiUe])
    def padrao_presentes(self, request):
        ata_paa_uuid = request.query_params.get('ata_paa_uuid')

        if not ata_paa_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da ata PAA.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            AtaPaa.by_uuid(ata_paa_uuid)
        except (ValidationError, AtaPaa.DoesNotExist):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto ata PAA para o uuid {ata_paa_uuid} não foi encontrado na base."
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        ata_paa = AtaPaa.objects.filter(uuid=ata_paa_uuid).first()

        membros_associacao = ata_paa.paa.associacao.membros_por_cargo()

        membros = []
        for membro in membros_associacao:

            dado = {
                "ata_paa": ata_paa_uuid,
                "cargo": remove_digitos(MembroEnum[membro.cargo_associacao].value),
                "identificacao": membro.codigo_identificacao if membro.codigo_identificacao else membro.cpf,
                "nome": membro.nome,
                "editavel": False,
                "membro": True,
                "presente": True
            }

            membros.append(dado)

        return Response(membros)

