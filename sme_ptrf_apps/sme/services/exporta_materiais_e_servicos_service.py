import csv
import datetime
import logging

from django.core.files import File
from django.db.models import QuerySet
from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload
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

    def exporta_materiais_e_servicos(self):
        self.cabecalho = CABECALHO_MATERIAIS_E_SERVICOS[0]
        self.filtra_range_data('criado_em')
        self.exporta_materiais_e_servicos_csv()

    def exporta_tipos_de_custeio(self):
        self.cabecalho = CABECALHO_TIPOS_DE_CUSTEIOS[0]
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
    
    def envia_arquivo_central_download(self, tmp) -> None:
        logger.info("Gerando arquivo download...")
        obj_arquivo_download = gerar_arquivo_download(
            self.user,
            self.nome_arquivo
        )

        try:
            logger.info("Salvando arquivo download...")
            obj_arquivo_download.arquivo.save(
                name=obj_arquivo_download.identificador,
                content=File(tmp)
            )
            obj_arquivo_download.status = ArquivoDownload.STATUS_CONCLUIDO
            obj_arquivo_download.save()
            logger.info("Arquivo salvo com sucesso...")

        except Exception as e:
            obj_arquivo_download.status = ArquivoDownload.STATUS_ERRO
            obj_arquivo_download.msg_erro = str(e)
            obj_arquivo_download.save()
            logger.error("Erro arquivo download...")