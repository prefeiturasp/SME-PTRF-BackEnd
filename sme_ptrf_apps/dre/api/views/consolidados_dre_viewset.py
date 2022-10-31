import logging

from django.http import HttpResponse
from rest_framework import mixins, status
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from sme_ptrf_apps.core.models import Unidade, Periodo, Associacao
from ..serializers.ata_parecer_tecnico_serializer import AtaParecerTecnicoLookUpSerializer
from ...models import ConsolidadoDRE, RelatorioConsolidadoDRE, AnoAnaliseRegularidade, AtaParecerTecnico, Lauda

from ..serializers.consolidado_dre_serializer import ConsolidadoDreSerializer, ConsolidadoDreDetalhamentoSerializer

from sme_ptrf_apps.users.permissoes import (
    PermissaoApiDre,
    PermissaoAPIApenasDreComLeituraOuGravacao,
    PermissaoAPIApenasDreComGravacao,
    PermissaoAPITodosComLeituraOuGravacao
)

from ...services import concluir_consolidado_dre, \
    verificar_se_status_parcial_ou_total_e_retornar_sequencia_de_publicacao, \
    status_consolidado_dre, \
    retornar_trilha_de_status, \
    gerar_previa_consolidado_dre, \
    retornar_consolidados_dre_ja_criados_e_proxima_criacao, \
    criar_ata_e_atribuir_ao_consolidado_dre, \
    concluir_consolidado_de_publicacoes_parciais

import mimetypes

from django.contrib.auth import get_user_model
User = get_user_model()

logger = logging.getLogger(__name__)


class ConsolidadosDreViewSet(mixins.RetrieveModelMixin,
                             mixins.ListModelMixin,
                             GenericViewSet):
    permission_classes = [IsAuthenticated & PermissaoApiDre]
    lookup_field = 'uuid'
    queryset = ConsolidadoDRE.objects.all()
    serializer_class = ConsolidadoDreSerializer

    def get_queryset(self):
        qs = self.queryset
        dre_uuid = self.request.query_params.get('dre')
        periodo_uuid = self.request.query_params.get('periodo')

        if dre_uuid is not None:
            qs = qs.filter(dre__uuid=dre_uuid)

        if periodo_uuid is not None:
            qs = qs.filter(periodo__uuid=periodo_uuid)

        return qs

    @action(detail=False, methods=['post'], url_path='criar-ata-e-atelar-ao-consolidado',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComLeituraOuGravacao])
    def criar_ata_e_atrelar_consolidado_dre(self, request):
        dados = request.data

        if (
            not dados
            or not dados.get('dre')
            or not dados.get('periodo')
        ):
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar os uuids da dre e período'
            }
            logger.info('Erro ao gerar Consolidado DRE: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        dre_uuid, periodo_uuid, consolidado_uuid = dados['dre'], dados['periodo'], dados['consolidado']

        try:
            dre = Unidade.dres.get(uuid=dre_uuid)
        except (Unidade.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            periodo = Periodo.objects.get(uuid=periodo_uuid)
        except (Periodo.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        consolidado_dre = None
        if consolidado_uuid:
            try:
                consolidado_dre = ConsolidadoDRE.objects.get(uuid=consolidado_uuid)
            except (ConsolidadoDRE.DoesNotExist, ValidationError):
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': f"O objeto ConsolidadoDRE para o uuid {consolidado_uuid} não foi encontrado na base."
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        sequencia_de_publicacao = verificar_se_status_parcial_ou_total_e_retornar_sequencia_de_publicacao(dre_uuid,
                                                                                                          periodo_uuid)

        ata = criar_ata_e_atribuir_ao_consolidado_dre(dre=dre, periodo=periodo, consolidado_dre=consolidado_dre,
                                                      sequencia_de_publicacao=sequencia_de_publicacao)

        return Response(AtaParecerTecnicoLookUpSerializer(ata, many=False).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='consolidado-dre-por-ata-uuid',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComLeituraOuGravacao])
    def consolidados_dre_por_ata_uuid(self, request):
        ata_uuid = request.query_params.get('ata')

        if not ata_uuid:
            erro = {
                'erro': 'parametros_requeridos - consolidados_dre_por_ata_uuid',
                'mensagem': 'É necessário enviar o uuid da Ata de Parecer Técnico'
            }
            logger.info('Erro recuperar Consolidado DRE pelo uuid da Ata de Parecer Técnico: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            ata_parecer_tecnico = AtaParecerTecnico.objects.get(uuid=ata_uuid)
        except (ValidationError, Exception):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto ata para o uuid {ata_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        consolidado_dre = ata_parecer_tecnico.consolidado_dre

        return Response(ConsolidadoDreSerializer(consolidado_dre, many=False).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='publicados-e-proxima-publicacao',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComLeituraOuGravacao])
    def consolidados_dre_ja_criados_e_proxima_criacao(self, request):

        dre_uuid = request.query_params.get('dre')
        periodo_uuid = request.query_params.get('periodo')

        if not dre_uuid or not periodo_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar os uuids da dre e período'
            }
            logger.info('Erro ao gerar Consolidado DRE: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            dre = Unidade.dres.get(uuid=dre_uuid)
        except (Unidade.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            periodo = Periodo.objects.get(uuid=periodo_uuid)
        except (Periodo.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        consolidados_ja_criados_e_proxima = retornar_consolidados_dre_ja_criados_e_proxima_criacao(dre=dre,
                                                                                                   periodo=periodo)

        return Response(consolidados_ja_criados_e_proxima, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['post'],
        url_path='gerar-previa',
        permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComLeituraOuGravacao]
    )
    def gerar_previa_consolidado_dre(self, request):
        dados = request.data

        if (
            not dados
            or not dados.get('dre_uuid')
            or not dados.get('periodo_uuid')
        ):
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar os uuids da dre e período'
            }
            logger.info('Erro ao gerar Consolidado DRE: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        dre_uuid, periodo_uuid = dados['dre_uuid'], dados['periodo_uuid']

        try:
            dre = Unidade.dres.get(uuid=dre_uuid)
        except (Unidade.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            periodo = Periodo.objects.get(uuid=periodo_uuid)
        except (Periodo.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            ano = str(periodo.data_inicio_realizacao_despesas.year)
            ano_analise_regularidade = AnoAnaliseRegularidade.objects.get(ano=ano)
        except (AnoAnaliseRegularidade.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"Não foi possível publicar o Consolidado Dre, pois o AnoAnaliseRegularidade para o ano {ano} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        parcial = verificar_se_status_parcial_ou_total_e_retornar_sequencia_de_publicacao(dre_uuid, periodo_uuid)

        try:
            consolidado_dre = gerar_previa_consolidado_dre(
                dre=dre,
                periodo=periodo,
                parcial=parcial,
                usuario=request.user.username,
            )
            logger.info(f"Consolidado DRE finalizado. Status: {consolidado_dre.get_valor_status_choice()}")

        except(IntegrityError):
            erro = {
                'erro': 'consolidado_dre_ja_criado',
                'mensagem': 'Você não pode criar um Consolidado DRE que já existe'
            }
            return Response(erro, status=status.HTTP_409_CONFLICT)

        return Response(ConsolidadoDreSerializer(consolidado_dre, many=False).data,
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'],
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComLeituraOuGravacao])
    def publicar(self, request):
        dados = request.data

        if (
            not dados
            or not dados.get('dre_uuid')
            or not dados.get('periodo_uuid')
        ):
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar os uuids da dre e período'
            }
            logger.info('Erro ao gerar Consolidado DRE: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        dre_uuid, periodo_uuid = dados['dre_uuid'], dados['periodo_uuid']

        try:
            dre = Unidade.dres.get(uuid=dre_uuid)
        except (Unidade.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            periodo = Periodo.objects.get(uuid=periodo_uuid)
        except (Periodo.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        parcial = verificar_se_status_parcial_ou_total_e_retornar_sequencia_de_publicacao(dre_uuid, periodo_uuid)

        try:
            sequencia_de_publicacao_atual = parcial['sequencia_de_publicacao_atual']
            ata_parecer_tecnico = AtaParecerTecnico.objects.filter(dre=dre, periodo=periodo,
                                                                   sequencia_de_publicacao=sequencia_de_publicacao_atual).last()
            if not ata_parecer_tecnico:
                raise ValidationError(f"O objeto Ata para a DRE {dre} e Período {periodo} não foi encontrado na base.")
        except (AtaParecerTecnico.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Erro método Consolidado Dre ViewSet publicar',
                'mensagem': f"O objeto Ata para a DRE {dre} e Período {periodo} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        alterado_em = ata_parecer_tecnico.preenchida_em

        if not alterado_em:
            erro = {
                'erro': 'Ata não preenchida',
                'mensagem': f"Para fazer a publicação você precisa preencher as informações da ata."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            ano = str(periodo.data_inicio_realizacao_despesas.year)
            ano_analise_regularidade = AnoAnaliseRegularidade.objects.get(ano=ano)
        except (AnoAnaliseRegularidade.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"Não foi possível publicar o Consolidado Dre, pois o AnoAnaliseRegularidade para o ano {ano} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            consolidado_dre = concluir_consolidado_dre(
                dre=dre,
                periodo=periodo,
                parcial=parcial,
                usuario=request.user.username,
            )
            logger.info(f"Consolidado DRE finalizado. Status: {consolidado_dre.get_valor_status_choice()}")

        except(IntegrityError):
            erro = {
                'erro': 'consolidado_dre_ja_criado',
                'mensagem': 'Você não pode criar um Consolidado DRE que já existe'
            }
            return Response(erro, status=status.HTTP_409_CONFLICT)

        return Response(ConsolidadoDreSerializer(consolidado_dre, many=False).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'],
            url_path='gerar-consolidado-de-publicacoes-parciais',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComLeituraOuGravacao])
    def gerar_consolidado_de_publicacoes_parciais(self, request):
        dados = request.data

        if (
            not dados
            or not dados.get('dre_uuid')
            or not dados.get('periodo_uuid')
        ):
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar os uuids da dre e período'
            }
            logger.info('Erro ao gerar Consolidado DRE: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        dre_uuid, periodo_uuid = dados['dre_uuid'], dados['periodo_uuid']

        try:
            dre = Unidade.dres.get(uuid=dre_uuid)
        except (Unidade.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            periodo = Periodo.objects.get(uuid=periodo_uuid)
        except (Periodo.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            concluir_consolidado_de_publicacoes_parciais(
                dre,
                periodo,
                usuario=request.user.username,
            )

            return Response({"data": "Consolidado de publicações parciais gerados com sucesso"},
                            status=status.HTTP_200_OK)
        except:
            erro = {
                'erro': 'erro_ao_gerar_consolidado_de_publicacoes_parciais',
                'mensagem': f"Erro ao gerar Consolidado de publicações parciais"
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['get'],
            url_path='retorna-status-relatorio-consolidado-de-publicacoes-parciais',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComLeituraOuGravacao])
    def retornar_status_relatorio_consolidado_de_publicacoes_parciais(self, request):
        dre_uuid = request.query_params.get('dre')
        periodo_uuid = request.query_params.get('periodo')

        if not dre_uuid or not periodo_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar os uuids da dre e período'
            }
            logger.info('Erro ao gerar Consolidado DRE: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            dre = Unidade.dres.get(uuid=dre_uuid)
        except (Unidade.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            periodo = Periodo.objects.get(uuid=periodo_uuid)
        except (Periodo.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        relatorio_consolidado_publicacoes_parciais = RelatorioConsolidadoDRE.objects.filter(dre=dre, periodo=periodo, versao="CONSOLIDADA").last()
        status_relatorio_consolidado_publicacoes_parciais = {
            'status': None
        }

        if relatorio_consolidado_publicacoes_parciais:
            status_relatorio_consolidado_publicacoes_parciais = {
                'status': relatorio_consolidado_publicacoes_parciais.status
            }

        return Response(status_relatorio_consolidado_publicacoes_parciais, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='documentos',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComLeituraOuGravacao])
    def documentos(self, request, uuid):

        from ..serializers.consolidado_dre_serializer import ConsolidadoDreComDocumentosSerializer

        consolidado_dre_uuid = uuid

        if not consolidado_dre_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid do Consolidado DRE'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            consolidado_dre = ConsolidadoDRE.objects.get(uuid=consolidado_dre_uuid)
        except (ConsolidadoDRE.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto Consolidado DRE para o uuid {consolidado_dre_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        return Response(ConsolidadoDreComDocumentosSerializer(consolidado_dre, many=False).data,
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='status-consolidado-dre',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComLeituraOuGravacao])
    def status_consolidado_dre(self, request):

        dre_uuid = request.query_params.get('dre')
        periodo_uuid = request.query_params.get('periodo')

        if not dre_uuid or not periodo_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar os uuids da dre e período'
            }
            logger.info('Erro ao gerar Consolidado DRE: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            dre = Unidade.dres.get(uuid=dre_uuid)
        except (Unidade.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            periodo = Periodo.objects.get(uuid=periodo_uuid)
        except (Periodo.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        status_do_consolidado_da_dre = status_consolidado_dre(dre, periodo)

        return Response(status_do_consolidado_da_dre)

    @action(detail=True, methods=['get'], url_path='download-relatorio-consolidado',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComLeituraOuGravacao])
    def download_relatorio_consolidado(self, request, uuid):
        relatorio_fisico_financeiro_uuid = uuid

        if not relatorio_fisico_financeiro_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid do Relatório Físico Financeiro e a Versão'
            }
            logger.info('Erro ao fazer o download do Relatório Físico Financeiro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            relatorio_fisico_financeiro = RelatorioConsolidadoDRE.by_uuid(relatorio_fisico_financeiro_uuid)
        except (RelatorioConsolidadoDRE.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto Relatório Físico Financeiro para o uuid {relatorio_fisico_financeiro_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            ano = str(relatorio_fisico_financeiro.periodo.data_inicio_realizacao_despesas.year)
            ano_analise_regularidade = AnoAnaliseRegularidade.objects.get(ano=ano)
        except (AnoAnaliseRegularidade.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto AnoAnalise Regularidade para o ano {ano} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            arquivo = relatorio_fisico_financeiro.arquivo.path
        except (ValueError,):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"Não foi encontrado o arquivo solicitado"
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        filename = 'relatorio_fisico_financeiro_dre.pdf' if relatorio_fisico_financeiro.versao == RelatorioConsolidadoDRE.VERSAO_FINAL else 'previa_relatorio_fisico_financeiro_dre.pdf'

        response = HttpResponse(
            open(relatorio_fisico_financeiro.arquivo.path, 'rb'),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response

    @action(detail=False, methods=['get'], url_path='download-ata-parecer-tecnico',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComLeituraOuGravacao])
    def download_ata_parecer_tecnico(self, request):
        logger.info("Download da Ata de Parecer Técnico.")

        ata_uuid = request.query_params.get('ata')

        if not ata_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da Ata.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            ata = AtaParecerTecnico.objects.get(uuid=ata_uuid)
        except (ValidationError, Exception):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto ata para o uuid {ata_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            filename = 'ata_parecer_tecnico.pdf'
            response = HttpResponse(
                open(ata.arquivo_pdf.path, 'rb'),
                content_type='application/pdf'
            )
            response['Content-Disposition'] = 'attachment; filename=%s' % filename
        except Exception as err:
            erro = {
                'erro': 'arquivo_nao_gerado',
                'mensagem': str(err)
            }
            logger.info("Erro: %s", str(err))
            return Response(erro, status=status.HTTP_404_NOT_FOUND)

        return response

    @action(detail=False, methods=['get'], url_path='download-lauda',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComLeituraOuGravacao])
    def download_lauda(self, request):
        logger.info("Download da Ata de Parecer Técnico.")

        lauda_uuid = request.query_params.get('lauda')

        if not lauda_uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid da Lauda.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            lauda = Lauda.objects.get(uuid=lauda_uuid)
        except (ValidationError, Exception):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto Lauda para o uuid {lauda_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        if lauda and lauda.arquivo_lauda_txt and lauda.arquivo_lauda_txt.name:
            arquivo_nome = lauda.arquivo_lauda_txt.name
            arquivo_path = lauda.arquivo_lauda_txt.path
            arquivo_file_mime = mimetypes.guess_type(lauda.arquivo_lauda_txt.name)[0]

            try:
                response = HttpResponse(
                    open(arquivo_path, 'rb'),
                    content_type=arquivo_file_mime
                )
                response['Content-Disposition'] = 'attachment; filename=%s' % arquivo_nome
            except Exception as err:
                erro = {
                    'erro': 'arquivo_nao_gerado',
                    'mensagem': str(err)
                }
                return Response(erro, status=status.HTTP_404_NOT_FOUND)

            return response
        else:
            erro = {
                'erro': 'arquivo_nao_encontrado',
                'mensagem': 'Arquivo não encontrado'
            }
            return Response(erro, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], url_path='trilha-de-status',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComLeituraOuGravacao])
    def trilha_de_status(self, request):
        dre_uuid = request.query_params.get('dre')
        periodo_uuid = request.query_params.get('periodo')
        par_add_aprovados_ressalva = request.query_params.get('add_aprovadas_ressalva')
        add_aprovados_ressalva = par_add_aprovados_ressalva == 'SIM'

        if not dre_uuid or not periodo_uuid:
            erro = {
                'erro': 'parametros_requerido',
                'mensagem': 'É necessário enviar o uuid da dre (dre_uuid) e o periodo como parâmetros.'
            }
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            dre = Unidade.dres.get(uuid=dre_uuid)
        except (Unidade.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            periodo = Periodo.objects.get(uuid=periodo_uuid)
        except (Periodo.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        total_associacoes_dre = Associacao.objects.filter(unidade__dre__uuid=dre_uuid).exclude(cnpj__exact='').count()

        cards = retornar_trilha_de_status(
            dre_uuid=dre_uuid,
            periodo_uuid=periodo_uuid,
            add_aprovado_ressalva=add_aprovados_ressalva,
            add_info_devolvidas_retornadas=True
        )

        trilha_de_status = {
            "total_associacoes_dre": total_associacoes_dre,
            "cards": cards
        }

        return Response(trilha_de_status)

    @action(detail=False, methods=['get'],
            url_path='detalhamento',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComLeituraOuGravacao])
    def detalhamento_relatorio_consolidado(self, request):
        uuid = request.query_params.get('uuid')

        if not uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid do Consolidado DRE'
            }
            logger.info('Erro ao gerar Consolidado DRE: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            consolidado_dre = ConsolidadoDRE.by_uuid(uuid)
        except (ConsolidadoDRE.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto ConsolidadoDRE para o uuid {uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        return Response(ConsolidadoDreDetalhamentoSerializer(consolidado_dre, many=False).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'],
            url_path='detalhamento-conferencia-documentos',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComLeituraOuGravacao])
    def detalhamento_relatorio_consolidado_conferencia_documentos(self, request):
        uuid = request.query_params.get('uuid')

        if not uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid do Consolidado DRE'
            }
            logger.info('Erro ao gerar Consolidado DRE: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            consolidado_dre = ConsolidadoDRE.by_uuid(uuid)
            lista_documentos = consolidado_dre.documentos_detalhamento()

            result = {
                "lista_documentos": lista_documentos
            }

            return Response(result, status=status.HTTP_200_OK)
        except (ConsolidadoDRE.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto ConsolidadoDRE para o uuid {uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='acompanhamento-de-relatorios-consolidados-sme',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def acompanhamento_de_relatorios_consolidados_sme(self, request):

        from ...services.consolidado_dre_service import Dashboard

        # Determina o período
        periodo_uuid = request.query_params.get('periodo')

        if not periodo_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'acompanhamento-de-relatorios-consolidados-sme',
                'mensagem': 'Faltou informar o uuid do período. ?periodo=uuid_do_periodo'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            periodo = Periodo.objects.get(uuid=periodo_uuid)
        except (Periodo.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        acompanhamento_dashboard = Dashboard(periodo).retorna_dashboard()

        return Response(acompanhamento_dashboard, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='listagem-de-relatorios-consolidados-sme-por-status',
            permission_classes=[IsAuthenticated & PermissaoAPITodosComLeituraOuGravacao])
    def listagem_de_relatorios_consolidados_sme_por_status(self, request):

        from ...services.consolidado_dre_service import ListagemPorStatusComFiltros

        # Determina o período
        periodo_uuid = request.query_params.get('periodo')

        if not periodo_uuid:
            erro = {
                'erro': 'falta_de_informacoes',
                'operacao': 'listagem-de-relatorios-consolidados-sme-por-status',
                'mensagem': 'Faltou informar o uuid do período. ?periodo=uuid_do_periodo'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            periodo = Periodo.objects.get(uuid=periodo_uuid)
        except (Periodo.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto período para o uuid {periodo_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        # Pega filtros por DRE, Tipo de Relatorio e Status SME
        dre_uuid = request.query_params.get('dre')
        tipo_relatorio = request.query_params.get('tipo_relatorio')
        status_sme = request.query_params.get('status_sme')
        status_sme_list = status_sme.split(',') if status_sme else []

        dre = None
        if dre_uuid:
            try:
                dre = Unidade.dres.get(uuid=dre_uuid)
            except (Unidade.DoesNotExist, ValidationError):
                erro = {
                    'erro': 'Objeto não encontrado.',
                    'mensagem': f"O objeto dre para o uuid {dre_uuid} não foi encontrado na base."
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        if tipo_relatorio and tipo_relatorio not in ['PARCIAL', 'UNICO']:
            erro = {
                'erro': 'tipo_relatorio_invalido',
                'operacao': 'listagem-de-relatorios-consolidados-sme-por-status',
                'mensagem': 'As opções são PARCIAL ou UNICO'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        for status_str in status_sme_list:
            if status_str == 'NAO_GERADO':
                continue

            if status_str not in ConsolidadoDRE.STATUS_SME_NOMES.keys():
                erro = {
                    'erro': 'status-invalido',
                    'operacao': 'listagem-de-relatorios-consolidados-sme-por-status',
                    'mensagem': 'Passe um status sme válido ou NAO_GERADO.'
                }
                logger.info('Erro: %r', erro)
                return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            listagem = ListagemPorStatusComFiltros(
                periodo=periodo,
                dre=dre,
                tipo_relatorio=tipo_relatorio,
                status_sme=status_sme_list
            ).retorna_listagem()

            return Response(listagem, status=status.HTTP_200_OK)

        except:
            erro = {
                'erro': 'ListagemPorStatusComFiltros().retorna_listagem()',
                'operacao': 'listagem-de-relatorios-consolidados-sme-por-status',
                'mensagem': 'Erro ao retornar a Listagem de Relatórios Consolidados por Status e Filtros'
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'],
            url_path='devolver-consolidado',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComGravacao])
    def devolver(self, request, uuid):
        from sme_ptrf_apps.dre.api.validation_serializers.consolidado_dre_devolver_serializer import ConsolidadoDreDevolverSerializer
        consolidado: ConsolidadoDRE = self.get_object()

        query = ConsolidadoDreDevolverSerializer(data=self.request.data)

        query.is_valid(raise_exception=True)
        try:
            consolidado.devolver_consolidado(data_limite=request.data.get('data_limite'))
            response = {
                'uuid': f'{uuid}',
                'mensagem': 'Consolidado dre devolvido com sucesso.'
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            erro = {
                'erro': 'Erro de devolução',
                'mensagem': f"Houve um erro ao tentar devolver o relatório consolidado {uuid}.",
                'exception': str(e)
            }
            logger.info('Erro ao devolver consolidado: %r', str(e))
            return Response(erro, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'],
            url_path='marcar-como-publicado-no-diario-oficial',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComLeituraOuGravacao])
    def marcar_como_publicado_no_diario_oficial(self, request):
        dados = request.data

        if (
            not dados
            or not dados.get('consolidado_dre')
            or not dados.get('data_publicacao')
            or not dados.get('pagina_publicacao')
        ):
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid do Consolidado DRE, a data e a página de publicação'
            }
            logger.info('Erro ao gerar Consolidado DRE: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        consolidado_dre_uuid, data_publicacao, pagina_publicacao = dados['consolidado_dre'], dados['data_publicacao'], \
                                                                   dados['pagina_publicacao']

        try:
            consolidado_dre = ConsolidadoDRE.by_uuid(consolidado_dre_uuid)
        except (ConsolidadoDRE.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto ConsolidadoDRE para o uuid {consolidado_dre_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            consolidado_dre = consolidado_dre.marcar_status_sme_como_publicado(
                data_publicacao=data_publicacao,
                pagina_publicacao=pagina_publicacao
            )
        except:
            erro = {
                'erro': 'Erro ao passar o relatório para status_sme_publicado',
                'mensagem': f"Não foi possível passar o relarório para o status de publicado no Diário Oficial"
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        return Response(ConsolidadoDreSerializer(consolidado_dre, many=False).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'],
            url_path='marcar-como-nao-publicado-no-diario-oficial',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComLeituraOuGravacao])
    def marcar_como_nao_publicado_no_diario_oficial(self, request):
        dados = request.data

        if (
            not dados
            or not dados.get('consolidado_dre')
        ):
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid do Consolidado DRE'
            }
            logger.info('Erro ao gerar Consolidado DRE: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        consolidado_dre_uuid = dados['consolidado_dre']

        try:
            consolidado_dre = ConsolidadoDRE.by_uuid(consolidado_dre_uuid)
        except (ConsolidadoDRE.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto ConsolidadoDRE para o uuid {consolidado_dre_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            consolidado_dre = consolidado_dre.marcar_status_sme_como_nao_publicado()
        except:
            erro = {
                'erro': 'Erro ao passar o relatório para status_sme_nao_publicado',
                'mensagem': f"Não foi possível passar o relarório para o status de Não Publicado no Diário Oficial"
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        return Response(ConsolidadoDreSerializer(consolidado_dre, many=False).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'],
            url_path='reabrir-consolidado',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComGravacao])
    def reabrir(self, request):
        uuid = request.query_params.get('uuid')

        if not uuid:
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid do Consolidado DRE'
            }
            logger.info('Erro ao gerar Consolidado DRE: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            consolidado_dre = ConsolidadoDRE.by_uuid(uuid)
        except (ConsolidadoDRE.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto ConsolidadoDRE para o uuid {uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        if not consolidado_dre.pode_reabrir():
            mensagem = f"Consolidado dre só pode ser reaberto " \
                       f"no status sme: {ConsolidadoDRE.STATUS_SME_NAO_PUBLICADO}." \
                       f" Status sme atual: {consolidado_dre.status_sme}."
            response = {
                'uuid': f'{uuid}',
                'mensagem': mensagem
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        reaberto = consolidado_dre.reabrir_consolidado()

        if reaberto:
            response = {
                'uuid': f'{uuid}',
                'mensagem': 'Consolidado dre reaberto com sucesso. Todos os seus registros foram apagados.'
            }
            return Response(response, status=status.HTTP_204_NO_CONTENT)
        else:
            response = {
                'uuid': f'{uuid}',
                'mensagem': 'Houve algum erro ao tentar reabrir o consolidado dre.'
            }
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'],
            url_path='analisar',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComLeituraOuGravacao])
    def analisar(self, request):

        dados = request.data

        if (
            not dados
            or not dados.get('consolidado_dre')
            or not dados.get('usuario')
        ):
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid do Consolidado DRE e o Usuário (username)'
            }
            logger.info('Erro ao gerar Consolidado DRE: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        consolidado_dre_uuid = dados['consolidado_dre']
        usuario_username = dados['usuario']

        try:
            consolidado_dre = ConsolidadoDRE.objects.get(uuid=consolidado_dre_uuid)
        except (ConsolidadoDRE.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto Consolidado DRE para o uuid {consolidado_dre_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            usuario = User.objects.filter(username=usuario_username).first()
        except (User.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto User para o uuid {usuario_username} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            consolidado_dre.analisar_consolidado(usuario)
            return Response("Consolidado DRE foi passado para o status Em Análise com Sucesso!", status=status.HTTP_200_OK)
        except:
            erro = {
                'erro': 'Erro ao analisar o Consolidado Dre',
                'mensagem': f"Não foi possível passar o status do Consolidado DRE para EM_ANALISE"
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'],
            url_path='marcar-como-analisado',
            permission_classes=[IsAuthenticated & PermissaoAPIApenasDreComLeituraOuGravacao])
    def marcar_como_analisado(self, request):
        dados = request.data

        if (
            not dados
            or not dados.get('consolidado_dre')
        ):
            erro = {
                'erro': 'parametros_requeridos',
                'mensagem': 'É necessário enviar o uuid do Consolidado DRE'
            }
            logger.info('Erro ao gerar Consolidado DRE: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        consolidado_dre_uuid = dados['consolidado_dre']

        try:
            consolidado_dre = ConsolidadoDRE.by_uuid(consolidado_dre_uuid)
        except (ConsolidadoDRE.DoesNotExist, ValidationError):
            erro = {
                'erro': 'Objeto não encontrado.',
                'mensagem': f"O objeto ConsolidadoDRE para o uuid {consolidado_dre_uuid} não foi encontrado na base."
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        try:
            consolidado_dre = consolidado_dre.concluir_analise_consolidado()
        except:
            erro = {
                'erro': 'Erro ao passar o relatório para status_sme_analisado',
                'mensagem': f"Não foi possível passar o relarório para o status de Analisado"
            }
            logger.info('Erro: %r', erro)
            return Response(erro, status=status.HTTP_400_BAD_REQUEST)

        return Response(ConsolidadoDreSerializer(consolidado_dre, many=False).data, status=status.HTTP_200_OK)
