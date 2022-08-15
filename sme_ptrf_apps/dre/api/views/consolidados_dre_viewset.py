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

from ..serializers.consolidado_dre_serializer import ConsolidadoDreSerializer

from sme_ptrf_apps.users.permissoes import (
    PermissaoApiDre,
    PermissaoAPIApenasDreComLeituraOuGravacao
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
