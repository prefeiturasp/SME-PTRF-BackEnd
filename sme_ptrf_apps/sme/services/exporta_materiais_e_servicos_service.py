import csv
import datetime
import logging

from django.core.files import File
from django.db.models import QuerySet
from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload
from sme_ptrf_apps.core.models.ambiente import Ambiente
from sme_ptrf_apps.core.services.arquivo_download_service import (
    gerar_arquivo_download
)
from sme_ptrf_apps.utils.built_in_custom import get_recursive_attr

from tempfile import NamedTemporaryFile
from typing import BinaryIO

logger = logging.getLogger(__name__)

CABECALHO_MATERIAIS_E_SERVICOS = [
        ('ID', 'id'),
        ('Descrição', 'descricao'),
        ('Aplicação', 'aplicacao_recurso'),
        ('ID do tipo de Custeio', 'tipo_custeio_id'),
        ('Nome do tipo de Custeio', 'tipo_custeio__nome'),
        ('Ativa', 'ativa')
    ],
CABECALHO_TIPOS_DE_CUSTEIOS = [
        ('ID', 'id'),
        ('Tipo de custeio', 'nome')
    ],

class ExportacoesDadosMateriaisEServicosService:
    
    def __init__(self, **kwargs) -> None:
        self.queryset = kwargs.get('queryset', None)
        self.data_inicio = kwargs.get('data_inicio', None)
        self.data_final = kwargs.get('data_final', None)
        self.nome_arquivo = kwargs.get('nome_arquivo', None)
        self.user = kwargs.get('user', None)
        self.objeto_arquivo_download = None
        self.ambiente = self.get_ambiente
        self.informacoes_download = self.get_informacoes_download()

    @property
    def get_ambiente(self):
        ambiente = Ambiente.objects.first()
        return ambiente.prefixo if ambiente else ""

    def get_informacoes_download(self):
        """
        Retorna uma string com as informações do download conforme a data de início e final de extração.
        """

        data_inicio = datetime.datetime.strptime(self.data_inicio, "%Y-%m-%d").strftime("%d/%m/%Y") if self.data_inicio else None
        data_final = datetime.datetime.strptime(self.data_final, "%Y-%m-%d").strftime("%d/%m/%Y") if self.data_final else None

        if data_inicio and data_final:
            return f"Filtro aplicado: {data_inicio} a {data_final} (data de criação do registro)"

        if data_inicio and not data_final:
            return f"Filtro aplicado: A partir de {data_inicio} (data de criação do registro)"

        if data_final and not data_inicio:
            return f"Filtro aplicado: Até {data_final} (data de criação do registro)"

        return ""

    def exporta_materiais_e_servicos(self):
        self.cabecalho = CABECALHO_MATERIAIS_E_SERVICOS[0]
        self.cria_registro_central_download()
        self.filtra_range_data('criado_em')
        self.exporta_materiais_e_servicos_csv()

    def exporta_tipos_de_custeio(self):
        self.cabecalho = CABECALHO_TIPOS_DE_CUSTEIOS[0]
        self.cria_registro_central_download()
        self.filtra_range_data('criado_em')
        self.exporta_materiais_e_servicos_csv()

    def exporta_materiais_e_servicos_csv(self) -> BinaryIO:
        linha = []
        with NamedTemporaryFile(
            mode="r+",
            newline='',
            encoding='utf-8',
            prefix=self.nome_arquivo,
            suffix='.csv'
        ) as tmp:
            write = csv.writer(tmp.file, delimiter=";")
            write.writerow([cabecalho[0] for cabecalho in self.cabecalho])

            for instance in self.queryset:
                for _, campo in self.cabecalho:

                    if campo == "ativa":
                        campo = get_recursive_attr(instance, campo)
                        linha.append("Sim" if campo else "Não")
                        continue

                    campo = get_recursive_attr(instance, campo)
                    linha.append(campo)

                logger.info(f"Escrevendo linha {linha} de materiais e servicos/tipos de custeio {instance.id}.")
                write.writerow(linha) if linha else None
                linha.clear()
            # Rodapé
            self.cria_rodape(write)

            self.envia_arquivo_central_download(tmp)

    def filtra_range_data(self, field) -> QuerySet:
        if self.data_inicio and self.data_final:
            self.queryset = self.queryset.filter(
                **{f'{field}__range': [self.data_inicio, self.data_final]}
            )
        elif self.data_inicio and not self.data_final:
            self.queryset = self.queryset.filter(
                **{f'{field}__gt': self.data_inicio}
            )
        elif self.data_final and not self.data_inicio:
            self.queryset = self.queryset.filter(
                **{f'{field}__lt': self.data_final}
            )
        return self.queryset
    
    def cria_registro_central_download(self):
        logger.info("Gerando arquivo download...")
        obj = gerar_arquivo_download(
            self.user,
            self.nome_arquivo,
            informacoes=self.informacoes_download
        )
        self.objeto_arquivo_download = obj

    def envia_arquivo_central_download(self, tmp) -> None:
        try:
            logger.info("Salvando arquivo download...")
            objeto = self.objeto_arquivo_download
            if not objeto:
                objeto = gerar_arquivo_download(
                    self.user,
                    self.nome_arquivo,
                    informacoes=self.informacoes_download
                )
            objeto.arquivo.save(
                name=objeto.identificador,
                content=File(tmp)
            )
            objeto.status = ArquivoDownload.STATUS_CONCLUIDO
            objeto.save()
            logger.info("Arquivo salvo com sucesso...")

        except Exception as e:
            if objeto:
                objeto.status = ArquivoDownload.STATUS_ERRO
                objeto.msg_erro = str(e)
                objeto.save()
            logger.error("Erro arquivo download...")

    def texto_rodape(self):
        # Usa o horário de início do processamento (criado_em do registro na central de download)
        inicio = None
        if self.objeto_arquivo_download and getattr(self.objeto_arquivo_download, 'criado_em', None):
            inicio = self.objeto_arquivo_download.criado_em
        else:
            inicio = datetime.datetime.now()

        data_hora_inicio = inicio.strftime("%d/%m/%Y às %H:%M:%S")
        texto = f"Arquivo solicitado via {self.ambiente} pelo usuário {self.user} em {data_hora_inicio}"

        return texto

    def cria_rodape(self, write):
        rodape = []
        # Para exportação de tipos de custeio, o rodapé deve ir na segunda coluna
        col_offset = 1 if getattr(self, 'cabecalho', None) == CABECALHO_TIPOS_DE_CUSTEIOS[0] else 0
        # Linha em branco
        write.writerow(rodape)
        rodape.clear()

        # Linha 1: Arquivo solicitado
        texto = self.texto_rodape()
        rodape = ([""] * col_offset) + [texto]
        write.writerow(rodape)
        rodape = []

        # Linha 2: Arquivo disponibilizado em
        data_hora_disponibilizado = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
        rodape = ([""] * col_offset) + [f"Arquivo disponibilizado em {data_hora_disponibilizado}"]
        write.writerow(rodape)
        rodape = []

        # Linha 3: Informações de filtro aplicado (se houver)
        if self.informacoes_download:
            rodape = ([""] * col_offset) + [self.informacoes_download]
            write.writerow(rodape)
            rodape = []
