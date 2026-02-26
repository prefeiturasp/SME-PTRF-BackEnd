import csv
import logging
from datetime import datetime
from django.core.files import File
from sme_ptrf_apps.core.models.ambiente import Ambiente
from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload
from sme_ptrf_apps.core.models.associacao import Associacao
from sme_ptrf_apps.core.models.periodo import Periodo
from sme_ptrf_apps.core.models.prestacao_conta import PrestacaoConta
from sme_ptrf_apps.core.services.arquivo_download_service import (
    gerar_arquivo_download
)
from sme_ptrf_apps.utils.built_in_custom import get_recursive_attr
from django.db.models import Q

from tempfile import NamedTemporaryFile

logger = logging.getLogger(__name__)

CABECALHO = [
    ('Recurso', 'periodo__recurso__nome'),
    ('Código EOL', 'associacao__unidade__codigo_eol'),
    ('Nome Unidade', 'associacao__unidade__nome'),
    ('Nome Associação', 'associacao__nome'),
    ('DRE', 'associacao__unidade__dre__nome'),
    ('Referência do Período da PC', 'periodo__referencia'),
    ('Status da PC', 'status'),
    ('Descrição do motivo aprovação com ressalvas', 'motivos_aprovacao_ressalva'),
    ('Recomendações da aprovação com resalvas', 'recomendacoes'),
    ('Descrição do motivo de reprovação', 'motivos_reprovacao'),
],

def get_informacoes_download(data_inicio, data_final):
    """
    Retorna uma string com as informações do download conforme a data de início e final de extração.
    """

    data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d").strftime("%d/%m/%Y") if data_inicio else None
    data_final = datetime.strptime(data_final, "%Y-%m-%d").strftime("%d/%m/%Y") if data_final else None

    if data_inicio and data_final:
        return f"Filtro aplicado: {data_inicio} a {data_final} (data de criação do registro)"

    if data_inicio and not data_final:
        return f"Filtro aplicado: A partir de {data_inicio} (data de criação do registro)"

    if data_final and not data_inicio:
        return f"Filtro aplicado: Até {data_final} (data de criação do registro)"

    return ""

class ExportacoesStatusPrestacoesContaService:

    def __init__(self, **kwargs):
        self.queryset = kwargs.get('queryset', None)
        self.data_inicio = kwargs.get('data_inicio', None)
        self.data_final = kwargs.get('data_final', None)
        self.nome_arquivo = kwargs.get('nome_arquivo', None)
        self.user = kwargs.get('user', None)
        self.dre_codigo_eol = kwargs.get('dre_codigo_eol', None)
        self.cabecalho = CABECALHO[0]
        self.objeto_arquivo_download = None
        self.ambiente = self.get_ambiente
        self.periodos = None
        self.dre_uuid = kwargs.get('dre_uuid', None)

    @property
    def get_ambiente(self):
        ambiente = Ambiente.objects.first()
        return ambiente.prefixo if ambiente else ""

    def exporta_status_prestacoes_conta(self):

        self.filtra_range_data('criado_em')
        self.cria_registro_central_download()
        self.define_periodos_selecionados_no_range_do_filtro_de_data()
        self.exporta_status_prestacoes_conta_csv()

    def exporta_status_prestacoes_conta_csv(self):
        dados = self.monta_dados()
        dados_pcs_nao_apresentadas = self.monta_dados_pcs_nao_apresentadas()

        with NamedTemporaryFile(
            mode="r+",
            newline='',
            encoding='utf-8',
            prefix=self.nome_arquivo,
            suffix='.csv'
        ) as tmp:
            write = csv.writer(tmp.file, delimiter=";")
            write.writerow([cabecalho[0] for cabecalho in self.cabecalho])

            for linha in dados:
                write.writerow(linha) if linha else None

            for linha in dados_pcs_nao_apresentadas:
                write.writerow(linha) if linha else None

            self.cria_rodape(write)
            self.envia_arquivo_central_download(tmp)

    def monta_dados(self):
        linhas_vertical = []

        for instance in self.queryset:

            linha_horizontal = []

            if not PrestacaoConta.objects.filter(id=instance.id).exists():
                logger.info(f"Este fechamento não existe mais na base de dados, portanto será pulado")
                continue

            for _, campo in self.cabecalho:
                motivos_concatenados = ""

                if campo != 'motivos_reprovacao' and campo != 'motivos_aprovacao_ressalva':
                    campo = get_recursive_attr(instance, campo)
                    linha_horizontal.append(campo)
                elif campo == 'motivos_aprovacao_ressalva' or campo == 'motivos_reprovacao':
                    linha_horizontal.append('')

                if campo == 'motivos_aprovacao_ressalva' and getattr(instance, 'status') == 'APROVADA_RESSALVA':
                    motivosAprovacaoRessalva = instance.motivos_aprovacao_ressalva.values_list('motivo', flat=True)

                    if len(motivosAprovacaoRessalva) > 0:
                        motivos_concatenados = '; '.join(motivosAprovacaoRessalva)

                    outros_motivos = getattr(instance, 'outros_motivos_aprovacao_ressalva')
                    if outros_motivos.strip():
                        motivos_concatenados += "; " + outros_motivos

                    linha_horizontal[7] = motivos_concatenados

                if campo == 'motivos_reprovacao' and getattr(instance, 'status') == 'REPROVADA':
                    motivosReprovacao = instance.motivos_reprovacao.values_list('motivo', flat=True)

                    if len(motivosReprovacao) > 0:
                        motivos_concatenados = '; '.join(motivosReprovacao)

                    outros_motivos = getattr(instance, 'outros_motivos_reprovacao')
                    if outros_motivos.strip():
                        motivos_concatenados += "; " + outros_motivos

                    linha_horizontal[9] = motivos_concatenados

            logger.info(
                f"Escrevendo linha {linha_horizontal} de status de prestação de conta de custeio {instance.id}.")
            linhas_vertical.append(linha_horizontal)

        return linhas_vertical

    def monta_dados_pcs_nao_apresentadas(self):

        if self.dre_uuid:
            associacoes_com_periodo_inicial = Associacao.objects.filter(
                unidade__dre__uuid=self.dre_uuid
            ).exclude(periodo_inicial=None)
        else:
            associacoes_com_periodo_inicial = Associacao.objects.exclude(periodo_inicial=None)

        dados_pcs_nao_apresentadas = []

        for associacao in associacoes_com_periodo_inicial:
            for periodo in self.periodos:

                # Verifica se associação já foi iniciada nesse periodo
                if periodo.data_inicio_realizacao_despesas > associacao.periodo_inicial.data_inicio_realizacao_despesas:

                    periodo_encerramento = None
                    if associacao.data_de_encerramento:
                        periodo_encerramento = Periodo.objects.get(
                            data_inicio_realizacao_despesas__lte=associacao.data_de_encerramento,
                            data_fim_realizacao_despesas__gte=associacao.data_de_encerramento
                        ).proximo_periodo

                        if periodo_encerramento and periodo.data_fim_realizacao_despesas > periodo_encerramento.data_inicio_realizacao_despesas:
                            # associacao encerrada nesse periodo
                            continue


                    # Verifica se não tem PC nesse periodo, se não existir é uma "PC não entregue"
                    if not PrestacaoConta.objects.filter(associacao=associacao, periodo=periodo).exists():
                        linha_horizontal = []

                        for _, campo in self.cabecalho:
                            if campo == 'associacao__unidade__codigo_eol':
                                linha_horizontal.append(associacao.unidade.codigo_eol)
                            elif campo == 'associacao__unidade__nome':
                                linha_horizontal.append(associacao.unidade.nome)
                            elif campo == 'associacao__nome':
                                linha_horizontal.append(associacao.nome)
                            elif campo == 'associacao__unidade__dre__nome':
                                linha_horizontal.append(associacao.unidade.dre.nome if associacao.unidade.dre else '')
                            elif campo == 'periodo__referencia':
                                linha_horizontal.append(periodo.referencia)
                            elif campo == 'status':
                                linha_horizontal.append('NAO_APRESENTADA')

                        logger.info(f"Escrevendo linha {linha_horizontal} de status de prestação de conta não apresentada da associacao {associacao.id} do periodo {periodo}.")
                        dados_pcs_nao_apresentadas.append(linha_horizontal)

        return dados_pcs_nao_apresentadas

    def filtra_range_data(self, field):
        if self.data_inicio and self.data_final:
            data_inicio = datetime.strptime(f"{self.data_inicio} 00:00:00", '%Y-%m-%d %H:%M:%S')
            data_final = datetime.strptime(f"{self.data_final} 23:59:59", '%Y-%m-%d %H:%M:%S')

            self.queryset = self.queryset.filter(
                **{f'{field}__range': [data_inicio, data_final]}
            )
        elif self.data_inicio and not self.data_final:
            data_inicio = datetime.strptime(f"{self.data_inicio} 00:00:00", '%Y-%m-%d %H:%M:%S')

            self.queryset = self.queryset.filter(
                **{f'{field}__gt': data_inicio}
            )

        elif self.data_final and not self.data_inicio:
            data_final = datetime.strptime(f"{self.data_final} 23:59:59", '%Y-%m-%d %H:%M:%S')

            self.queryset = self.queryset.filter(
                **{f'{field}__lt': data_final}
            )
        return self.queryset

    def define_periodos_selecionados_no_range_do_filtro_de_data(self):
        if self.data_inicio and self.data_final:
            periodos = Periodo.objects.filter(
                Q(data_inicio_realizacao_despesas__lte=self.data_inicio, data_fim_realizacao_despesas__gte=self.data_inicio) |
                Q(data_inicio_realizacao_despesas__lte=self.data_final, data_fim_realizacao_despesas__gte=self.data_final) |
                Q(data_inicio_realizacao_despesas__gte=self.data_inicio, data_fim_realizacao_despesas__lte=self.data_final)
            ).order_by('data_inicio_realizacao_despesas')
        elif self.data_inicio and not self.data_final:
            periodos = Periodo.objects.filter(data_fim_realizacao_despesas__gte=self.data_inicio).order_by('data_inicio_realizacao_despesas')
        elif self.data_final and not self.data_inicio:
            periodos = Periodo.objects.filter(data_inicio_realizacao_despesas__lte=self.data_final).order_by('data_inicio_realizacao_despesas')
        else:
            periodos = Periodo.objects.all().order_by('data_inicio_realizacao_despesas')

        self.periodos = periodos

        return periodos

    def cria_registro_central_download(self):
        logger.info(f"Criando registro na central de download")

        obj = gerar_arquivo_download(
            self.user,
            self.nome_arquivo,
            informacoes=get_informacoes_download(self.data_inicio, self.data_final),
            dre_codigo_eol=self.dre_codigo_eol
        )
        self.objeto_arquivo_download = obj

    def envia_arquivo_central_download(self, tmp):
        try:
            logger.info("Salvando arquivo download...")
            self.objeto_arquivo_download.arquivo.save(
                name=self.objeto_arquivo_download.identificador,
                content=File(tmp)
            )
            self.objeto_arquivo_download.status = ArquivoDownload.STATUS_CONCLUIDO
            self.objeto_arquivo_download.save()
            logger.info("Arquivo salvo com sucesso...")

        except Exception as e:
            self.objeto_arquivo_download.status = ArquivoDownload.STATUS_ERRO
            self.objeto_arquivo_download.msg_erro = str(e)
            self.objeto_arquivo_download.save()
            logger.error("Erro arquivo download...")

    def texto_rodape(self):
        data_hora_geracao = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
        texto = f"Arquivo gerado pelo {self.ambiente} em {data_hora_geracao}"

        return texto

    def texto_info_arquivo_gerado(self):
        # Usa o horário de início do processamento (criado_em do registro na central de download)
        inicio = None
        if self.objeto_arquivo_download and getattr(self.objeto_arquivo_download, 'criado_em', None):
            inicio = self.objeto_arquivo_download.criado_em
        else:
            inicio = datetime.now()

        data_hora_inicio = inicio.strftime("%d/%m/%Y às %H:%M:%S")
        texto = f"Arquivo solicitado via {self.ambiente} pelo usuário {self.user} em {data_hora_inicio}"

        return texto

    def cria_rodape(self, write):
        rodape = []
        texto_info_arquivo_gerado = self.texto_info_arquivo_gerado()

        rodape.append(" ")
        write.writerow(rodape)
        rodape.clear()

        rodape.append(texto_info_arquivo_gerado)
        write.writerow(rodape)
        rodape.clear()

        # Linha 2: Arquivo disponibilizado em
        data_hora_disponibilizado = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
        rodape.append(f"Arquivo disponibilizado em {data_hora_disponibilizado}")
        write.writerow(rodape)
        rodape.clear()

        rodape.append(get_informacoes_download(self.data_inicio, self.data_final))
        write.writerow(rodape)
        rodape.clear()
