import csv
from datetime import datetime
import logging

from django.core.files import File

from sme_ptrf_apps.core.models import ObservacaoConciliacao
from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload
from sme_ptrf_apps.core.models.ambiente import Ambiente
from sme_ptrf_apps.core.services.arquivo_download_service import (
    gerar_arquivo_download
)
from sme_ptrf_apps.utils.built_in_custom import get_recursive_attr

from tempfile import NamedTemporaryFile

logger = logging.getLogger(__name__)

CABECALHO_DEMONSTATIVOS_FINANCEIROS = [
    ('Código EOL', 'conta_associacao__associacao__unidade__codigo_eol'),
    ('Nome Unidade', 'conta_associacao__associacao__unidade__nome'),
    ('Nome Associação', 'conta_associacao__associacao__nome'),
    ('Referência do Período da PC', 'prestacao_conta__periodo__referencia'),
    ('Nome do tipo de Conta', 'conta_associacao__tipo_conta__nome'),
    ('Data (Saldo bancário)', 'DATA_SALDO_BANCARIO'),
    ('Saldo bancário', 'SALDO_BANCARIO'),
    ('Justificativa e informações adicionais (Informações de conciliação)', 'JUSTIFICATIVA_CONCILIACAO'),
    ('URL do arquivo PDF', 'arquivo_pdf'),
    ('Status', 'status'),
    ('Versão', 'versao'),
    ('Data e hora de criação', 'criado_em'),
    ('Data e hora da última atualização', 'alterado_em'),
]

class ExportaDemonstrativosFinanceirosService:

    def __init__(self, **kwargs):
        self.queryset = kwargs.get('queryset', None)
        self.data_inicio = kwargs.get('data_inicio', None)
        self.data_final = kwargs.get('data_final', None)
        self.nome_arquivo = kwargs.get('nome_arquivo', None)
        self.user = kwargs.get('user', None)
        self.cabecalho = CABECALHO_DEMONSTATIVOS_FINANCEIROS
        self.ambiente = self.get_ambiente
        self.objeto_arquivo_download = None

    @property
    def get_ambiente(self):
        ambiente = Ambiente.objects.first()
        return ambiente.prefixo if ambiente else ""

    def exporta_demonstrativos_financeiros(self):
        self.cria_registro_central_download()
        self.filtra_range_data('criado_em')
        self.exporta_demonstrativos_financeiros_csv()


    def cria_registro_central_download(self):
        logger.info(f"Criando registro na central de download")
        obj = gerar_arquivo_download(
            self.user,
            self.nome_arquivo
        )

        self.objeto_arquivo_download = obj


    def filtra_range_data(self, field):
        if self.data_inicio and self.data_final:
            self.data_inicio = datetime.strptime(f"{self.data_inicio} 00:00:00", '%Y-%m-%d %H:%M:%S')
            self.data_final = datetime.strptime(f"{self.data_final} 23:59:59", '%Y-%m-%d %H:%M:%S')

            self.queryset = self.queryset.filter(
                **{f'{field}__range': [self.data_inicio, self.data_final]}
            )
        elif self.data_inicio and not self.data_final:
            self.data_inicio = datetime.strptime(f"{self.data_inicio} 00:00:00", '%Y-%m-%d %H:%M:%S')

            self.queryset = self.queryset.filter(
                **{f'{field}__gt': self.data_inicio}
            )

        elif self.data_final and not self.data_inicio:
            self.data_final = datetime.strptime(f"{self.data_final} 23:59:59", '%Y-%m-%d %H:%M:%S')

            self.queryset = self.queryset.filter(
                **{f'{field}__lt': self.data_final}
            )
        return self.queryset


    def exporta_demonstrativos_financeiros_csv(self):
        dados = self.monta_dados()

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

            self.cria_rodape(write)
            self.envia_arquivo_central_download(tmp)


    def get_periodo_demonstrativo_financeiro(self, instance):
        if instance and instance.prestacao_conta:
            periodo = instance.prestacao_conta.periodo if instance.prestacao_conta.periodo else None
        else:
            periodo = instance.periodo_previa if instance.periodo_previa else None

        return periodo

    def get_periodo_referencia_demonstrativo_financeiro(self, instance):
        if instance and instance.prestacao_conta:
            periodo =  instance.prestacao_conta.periodo.referencia if instance.prestacao_conta.periodo else ''
        else:
            periodo =  instance.periodo_previa.referencia if instance.periodo_previa else ''

        return periodo

    def monta_dados(self):
        linhas_vertical = []

        for instance in self.queryset:
            logger.info(f"Iniciando extração de dados do demonstrativo financeiro : {instance.id}.")
            linha_horizontal = []

            for _, campo in self.cabecalho:

                if campo == "arquivo_pdf":
                    campo = get_recursive_attr(instance, campo)
                    url = ""

                    if campo:
                        if self.ambiente == "local":
                            url = f"http://127.0.0.1:8000{campo.url}"
                        else:
                            url = f"https://{self.ambiente}.sme.prefeitura.sp.gov.br{campo.url}"

                    linha_horizontal.append(url)
                    continue

                if campo == "criado_em":
                    campo = get_recursive_attr(instance, campo)
                    criado_em_formatado = campo.strftime("%d/%m/%Y às %H:%M:%S")
                    linha_horizontal.append(criado_em_formatado)
                    continue

                if campo == "alterado_em":
                    campo = get_recursive_attr(instance, campo)
                    alterado_em_formatado = campo.strftime("%d/%m/%Y às %H:%M:%S")
                    linha_horizontal.append(alterado_em_formatado)
                    continue

                if campo == 'prestacao_conta__periodo__referencia':
                    periodo = self.get_periodo_referencia_demonstrativo_financeiro(instance)
                    linha_horizontal.append(periodo)
                    continue

                if campo == 'DATA_SALDO_BANCARIO':
                    periodo = self.get_periodo_demonstrativo_financeiro(instance)
                    observacao = None

                    if periodo:
                        observacao = ObservacaoConciliacao.objects.filter(
                            periodo=periodo,
                            conta_associacao=instance.conta_associacao,
                            associacao=instance.conta_associacao.associacao,
                        ).first()

                    data_saldo_bancario = observacao.data_extrato if observacao and observacao.data_extrato else ''
                    linha_horizontal.append(data_saldo_bancario)
                    continue

                if campo == 'SALDO_BANCARIO':
                    periodo = self.get_periodo_demonstrativo_financeiro(instance)
                    observacao = None

                    if periodo:
                        observacao = ObservacaoConciliacao.objects.filter(
                            periodo=periodo,
                            conta_associacao=instance.conta_associacao,
                            associacao=instance.conta_associacao.associacao,
                        ).first()

                    saldo_extrato = observacao.saldo_extrato if observacao and observacao.saldo_extrato else ''
                    linha_horizontal.append(saldo_extrato)
                    continue

                if campo == 'JUSTIFICATIVA_CONCILIACAO':
                    periodo = self.get_periodo_demonstrativo_financeiro(instance)
                    observacao = None

                    if periodo:
                        observacao = ObservacaoConciliacao.objects.filter(
                            periodo=periodo,
                            conta_associacao=instance.conta_associacao,
                            associacao=instance.conta_associacao.associacao,
                        ).first()

                    texto = observacao.texto if observacao and observacao.texto else ''
                    linha_horizontal.append(texto)
                    continue


                campo = get_recursive_attr(instance, campo)
                linha_horizontal.append(campo)

            logger.info(f"Escrevendo linha {linha_horizontal} do demonstrativo financeiro : {instance.id}.")
            linhas_vertical.append(linha_horizontal)
            logger.info(f"Finalizado extração de dados do demonstrativo financeiro : {instance.id}.")

        return linhas_vertical


    def texto_rodape(self):
        data_hora_geracao = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
        texto = f"Arquivo gerado pelo {self.ambiente} em {data_hora_geracao}"

        return texto

    def cria_rodape(self, write):
        rodape = []
        texto = self.texto_rodape()

        rodape.append("\n")
        write.writerow(rodape)
        rodape.clear()

        rodape.append(texto)
        write.writerow(rodape)
        rodape.clear()

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
