import csv
from datetime import datetime
import logging

from django.core.files import File
from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload
from sme_ptrf_apps.core.models.ambiente import Ambiente
from sme_ptrf_apps.core.models.proccessos_associacao import ProcessoAssociacao
from sme_ptrf_apps.core.services.arquivo_download_service import (
    gerar_arquivo_download
)
from sme_ptrf_apps.utils.built_in_custom import get_recursive_attr

from tempfile import NamedTemporaryFile

logger = logging.getLogger(__name__)

CABECALHO = [
    ('Código EOL', 'associacao__unidade__codigo_eol'),
    ('Nome Unidade', 'associacao__unidade__nome'),
    ('Nome Associação', 'associacao__nome'),
    ("CNPj da Associação", "associacao__cnpj"),
    ('DRE', 'associacao__unidade__dre__nome'),
    ('Número do processo SEI', 'numero_processo'),
    ('Ano', 'ano'),
    ('Períodos', 'periodos'),
]


class ExportacaoDadosProcessosSEIPrestacaoContasService:

    def __init__(self, **kwargs):
        self.queryset = kwargs.get('queryset', None)
        self.nome_arquivo = kwargs.get('nome_arquivo', None)
        self.user = kwargs.get('user', None)
        self.cabecalho = CABECALHO
        self.ambiente = self.get_ambiente
        self.objeto_arquivo_download = None

    @property
    def get_ambiente(self):
        ambiente = Ambiente.objects.first()
        return ambiente.prefixo if ambiente else ""

    def exportar(self):
        self.cria_registro_central_download()
        self.exportar_csv()

    def exportar_csv(self):
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

    def monta_dados(self):
        linhas_vertical = []

        for instance in self.queryset:
            logger.info(f"Iniciando extração de dados de processos associação, id: {instance.id}.")

            if not ProcessoAssociacao.objects.filter(id=instance.id).exists():
                logger.info(f"Este registro não existe mais na base de dados, portanto será pulado")
                continue

            linha_horizontal = []

            for _, campo in self.cabecalho:
                campo_valor = get_recursive_attr(instance, campo)
                if campo == "periodos":
                    periodos_strings = []

                    for periodo in instance.periodos.all():
                        periodos_strings.append(periodo.referencia)

                    periodos_concat = ', '.join(periodos_strings)

                    linha_horizontal.append(periodos_concat)

                    continue

                campo_valor = "" if not campo_valor else str(campo_valor).replace(";", ",")
                linha_horizontal.append(campo_valor)

            logger.info(f"Escrevendo linha {linha_horizontal}, id: {instance.id}.")
            linhas_vertical.append(linha_horizontal)
            logger.info(f"Finalizando extração de dados, id: {instance.id}.")

        return linhas_vertical

    def cria_registro_central_download(self):
        logger.info(f"Criando registro na central de download")
        obj = gerar_arquivo_download(
            self.user,
            self.nome_arquivo,
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
        texto = f"Arquivo gerado via {self.ambiente} pelo usuário {self.user} em {data_hora_geracao}"

        return texto

    def cria_rodape(self, write):
        rodape = []
        texto = self.texto_rodape()

        write.writerow(rodape)
        rodape.clear()

        rodape.append(texto)
        write.writerow(rodape)
        rodape.clear()

    def texto_info_arquivo_gerado(self):
        data_hora_geracao = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
        texto = f"Arquivo gerado via {self.ambiente} pelo usuário {self.user} em {data_hora_geracao}"

        return texto
