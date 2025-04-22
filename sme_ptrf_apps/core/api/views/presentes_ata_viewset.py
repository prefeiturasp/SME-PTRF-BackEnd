import re
from rest_framework import mixins
from django_filters import rest_framework as filters
from rest_framework.viewsets import GenericViewSet
from sme_ptrf_apps.mandatos.models.cargo_composicao import CargoComposicao
from sme_ptrf_apps.mandatos.models.ocupante_cargo import OcupanteCargo
from sme_ptrf_apps.mandatos.services.composicao_service import ServicoRecuperaComposicaoPorData
from sme_ptrf_apps.users.permissoes import (
    PermissaoApiUe
)
from rest_framework.permissions import IsAuthenticated
from ...models import Participante, Ata, MembroAssociacao
from ..serializers.presentes_ata_serializer import PresentesAtaSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from sme_ptrf_apps.core.choices import MembroEnum, RepresentacaoCargo
from rest_framework import status
from django.core.exceptions import ValidationError
from sme_ptrf_apps.utils.remove_digitos_str import remove_digitos
from waffle import get_waffle_flag_model


class PresentesAtaViewSet(mixins.CreateModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.DestroyModelMixin,
                          mixins.ListModelMixin,
                          GenericViewSet):
    permission_classes = [IsAuthenticated & PermissaoApiUe]
    queryset = Participante.objects.all()
    serializer_class = PresentesAtaSerializer
    filterset_fields = ('ata__uuid',)
    filter_backends = (filters.DjangoFilterBackend,)

    @action(detail=False, url_path='membros-e-nao-membros',
            permission_classes=[IsAuthenticated & PermissaoApiUe])
    def membros_e_nao_membros(self, request):
        from ...services.membro_associacao_service import retorna_membros_do_conselho_fiscal_por_associacao

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
        presentes_ata_membros = Participante.objects.filter(ata=ata).filter(membro=True).values()
        presentes_ata_nao_membros = Participante.objects.filter(ata=ata).filter(membro=False).order_by('nome').values()

        associacao = ata.associacao

        flags = get_waffle_flag_model()
        if flags.objects.filter(name='historico-de-membros', everyone=True).exists():   
            if not presentes_ata_membros or not ata.data_reuniao:
                result = {
                    'presentes_membros': [],
                    'presentes_nao_membros': [],
                    'presentes_ata_conselho_fiscal': []
                }
                return Response(result)
            else:
                presentes_ata_membros_conselho_fiscal = Participante.objects.filter(ata=ata).filter(membro=True, conselho_fiscal=True).values()
                presentes_ata_membros_conselho_fiscal_ordenados = sorted(presentes_ata_membros_conselho_fiscal, key=Participante.ordenar_por_cargo)
                
                presentes_ata_membros_ordenados = sorted(presentes_ata_membros, key=Participante.ordenar_por_cargo)
                
                presentes_ata_nao_membros_ordenados = sorted(presentes_ata_nao_membros, key=Participante.ordenar_por_cargo)
                
                result = {
                    'presentes_membros': presentes_ata_membros_ordenados,
                    'presentes_nao_membros': presentes_ata_nao_membros_ordenados,
                    'presentes_ata_conselho_fiscal': presentes_ata_membros_conselho_fiscal_ordenados
                }
                return Response(result)
            
        else:
            if not presentes_ata_membros:
                membros_associacao = ata.associacao.membros_por_cargo()
                presentes_ata_membros = []
                for membro in membros_associacao:

                    dado = {
                        "ata": ata_uuid,
                        "cargo": remove_digitos(MembroEnum[membro.cargo_associacao].value),
                        "identificacao": membro.codigo_identificacao if membro.codigo_identificacao else membro.cpf,
                        "nome": membro.nome,
                        "editavel": False,
                        "membro": True,
                        "presente": True
                    }

                    presentes_ata_membros.append(dado)

                presentes_ata_conselho_fiscal = retorna_membros_do_conselho_fiscal_por_associacao(associacao)
            else:
                presentes_ata_conselho_fiscal = Participante.objects.filter(ata=ata).filter(membro=True, conselho_fiscal=True).values()


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

        membros_associacao = ata.associacao.membros_por_cargo()

        membros = []
        for membro in membros_associacao:

            dado = {
                "ata": ata_uuid,
                "cargo": remove_digitos(MembroEnum[membro.cargo_associacao].value),
                "identificacao": membro.codigo_identificacao if membro.codigo_identificacao else membro.cpf,
                "nome": membro.nome,
                "editavel": False,
                "membro": True,
                "presente": True
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

        flags = get_waffle_flag_model()
        if flags.objects.filter(name='historico-de-membros', everyone=True).exists():
            data = request.query_params.get('data')
            
            if data and valida_ata and valida_ata.associacao and valida_ata.associacao.id:

                servico_composicao = ServicoRecuperaComposicaoPorData()
                composicao = servico_composicao.get_composicao_por_data_e_associacao(data, valida_ata.associacao.id)
  
                try:
                    ocupante_existe = OcupanteCargo.objects.filter(
                        Q(codigo_identificacao=identificador) | Q(cpf_responsavel=identificador)
                    ).get()
                
                    if composicao.cargos_da_composicao_da_composicao.filter(ocupante_do_cargo__codigo_identificacao=identificador).exists() or composicao.cargos_da_composicao_da_composicao.filter(ocupante_do_cargo__cpf_responsavel=identificador).exists():
                        # Ocupante encontrado na composição
                        cargo = CargoComposicao.objects.get(composicao=composicao, ocupante_do_cargo=ocupante_existe)
                        
                        result = {
                            "mensagem": "membro-encontrado",
                            "nome": ocupante_existe.nome,
                            "cargo": re.sub(r'\d+', '', MembroEnum[cargo.cargo_associacao].value).strip()
                        }
                    else:
                        result = Participante.get_informacao_servidor(identificador)
                    return Response(result)
                except:
                    result = Participante.get_informacao_servidor(identificador)
                    return Response(result) 
            else:
                result = Participante.get_informacao_servidor(identificador)
                return Response(result)  
        else:
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
                result = Participante.get_informacao_servidor(identificador)

            return Response(result)


    @action(detail=False, url_path='get-participantes-ordenados-por-cargo', permission_classes=[IsAuthenticated & PermissaoApiUe])
    def get_participantes_ordenados_por_cargo(self, request):
        ata_uuid = request.query_params.get('ata_uuid')
        
        if not ata_uuid:
            return Response({'erro': 'O parâmetro "ata_uuid" é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            ata = Ata.objects.get(uuid=ata_uuid)
        except Ata.DoesNotExist:
            return Response({'erro': 'A ata especificada não existe'}, status=status.HTTP_404_NOT_FOUND)

        participantes = Participante.objects.filter(ata=ata).values()
        participantes_ordenados = sorted(participantes, key=Participante.ordenar_por_cargo)
        
        response_data = []
        for participante in participantes_ordenados:           
            data = {
                'id': participante["id"],
                'identificacao': participante["identificacao"],
                'nome': participante["nome"],
                'cargo': participante["cargo"],
                'membro': participante["membro"],
                'presente': participante["presente"],
                'presidente_da_reuniao': participante["id"] == ata.presidente_da_reuniao.id if ata.presidente_da_reuniao else False,
                'secretario_da_reuniao': participante["id"] == ata.secretario_da_reuniao.id if ata.secretario_da_reuniao else False
            }
            response_data.append(data)
        
        return Response(response_data)