from rest_framework import mixins
from django_filters import rest_framework as filters
from rest_framework.viewsets import GenericViewSet
from sme_ptrf_apps.users.permissoes import (
    PermissaoApiUe
)
from rest_framework.permissions import IsAuthenticated
from ...models import PresenteAta, Ata, MembroAssociacao
from ..serializers.presentes_ata_serializer import PresentesAtaSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from sme_ptrf_apps.core.choices import MembroEnum, RepresentacaoCargo
from rest_framework import status
from django.core.exceptions import ValidationError


class PresentesAtaViewSet(mixins.CreateModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.DestroyModelMixin,
                          mixins.ListModelMixin,
                          GenericViewSet):
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    queryset = PresenteAta.objects.all()
    serializer_class = PresentesAtaSerializer
    filter_fields = ('ata__uuid',)
    filter_backends = (filters.DjangoFilterBackend,)

    @action(detail=False, url_path='membros-e-nao-membros',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def membros_e_nao_membros(self, request):
        ata_uuid = request.query_params.get('ata_uuid')

        if not ata_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da ata.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            valida_ata = Ata.by_uuid(ata_uuid)
        except ValidationError:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto ata para o uuid {ata_uuid} não foi encontrado na base."
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        ata = Ata.objects.filter(uuid=ata_uuid).first()
        presentes_ata_membros = PresenteAta.objects.filter(ata=ata).filter(membro=True).values()
        presentes_ata_nao_membros = PresenteAta.objects.filter(ata=ata).filter(membro=False).values()
        presentes_ata_conselho_fiscal = PresenteAta.objects.filter(
            ata=ata).filter(membro=True).filter(conselho_fiscal=True).values()

        result = {
            'presentes_membros': presentes_ata_membros,
            'presentes_nao_membros': presentes_ata_nao_membros,
            'presentes_ata_conselho_fiscal': presentes_ata_conselho_fiscal
        }

        return Response(result)

    @action(detail=False, url_path='padrao-de-presentes', permission_classes=[IsAuthenticated & PermissaoApiUe])
    def padrao_presentes(self, request):
        ata_uuid = request.query_params.get('ata_uuid')

        if not ata_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da ata.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            valida_ata = Ata.by_uuid(ata_uuid)
        except ValidationError:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto ata para o uuid {ata_uuid} não foi encontrado na base."
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        ata = Ata.objects.filter(uuid=ata_uuid).first()

        membros_associacao = MembroAssociacao.objects.filter(associacao=ata.associacao)

        membros = []
        for membro in membros_associacao:

            dado = {
                "ata": ata_uuid,
                "cargo": MembroEnum[membro.cargo_associacao].value,
                "identificacao": membro.codigo_identificacao if membro.codigo_identificacao != "" else membro.cpf,
                "nome": membro.nome,
                "editavel": False,
                "membro": True
            }

            membros.append(dado)

        return Response(membros)

    @action(detail=False, url_path='presentes-padrao-conselho-fiscal', permission_classes=[IsAuthenticated & PermissaoApiUe])
    def presentes_padrao_conselho_fiscal(self, request):
        ata_uuid = request.query_params.get('ata_uuid')

        if not ata_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da ata.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            valida_ata = Ata.by_uuid(ata_uuid)
        except ValidationError:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto ata para o uuid {ata_uuid} não foi encontrado na base."
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        ata = Ata.objects.filter(uuid=ata_uuid).first()
        membros_associacao = MembroAssociacao.objects.filter(associacao=ata.associacao)

        presidente_conselho_fiscal = membros_associacao.filter(cargo_associacao="PRESIDENTE_CONSELHO_FISCAL").values()
        conselheiro_1 = membros_associacao.filter(cargo_associacao="CONSELHEIRO_1").values()
        conselheiro_2 = membros_associacao.filter(cargo_associacao="CONSELHEIRO_2").values()
        conselheiro_3 = membros_associacao.filter(cargo_associacao="CONSELHEIRO_3").values()
        conselheiro_4 = membros_associacao.filter(cargo_associacao="CONSELHEIRO_4").values()
        conselheiro_5 = membros_associacao.filter(cargo_associacao="CONSELHEIRO_5").values()

        result = {
            "presidente_conselho_fiscal": presidente_conselho_fiscal,
            "conselheiro_1": conselheiro_1,
            "conselheiro_2": conselheiro_2,
            "conselheiro_3": conselheiro_3,
            "conselheiro_4": conselheiro_4,
            "conselheiro_5": conselheiro_5,
        }

        return Response(result)

    @action(detail=False, url_path='get-nome-cargo-membro-associacao', permission_classes=[IsAuthenticated & PermissaoApiUe])
    def get_nome_cargo_membro_associacao(self, request):
        ata_uuid = request.query_params.get('ata_uuid')
        identificador = request.query_params.get('identificador')

        if not identificador:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o identificador.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        if not ata_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da ata e o identificador.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            valida_ata = Ata.by_uuid(ata_uuid)
        except ValidationError:
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto ata para o uuid {ata_uuid} não foi encontrado na base."
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        ata = Ata.objects.filter(uuid=ata_uuid).first()
        membros_associacao = MembroAssociacao.objects.filter(associacao=ata.associacao)

        membro = membros_associacao.filter(
            Q(codigo_identificacao=identificador) |
            Q(cpf=identificador)
        ).first()

        if membro:
            result = {
                "mensagem": "membro-encontrado",
                "nome": membro.nome,
                "cargo": MembroEnum[membro.cargo_associacao].value
            }
        else:
            result = {
                "mensagem": "membro-nao-encontrado",
                "nome": "",
                "cargo": ""
            }

        return Response(result)

