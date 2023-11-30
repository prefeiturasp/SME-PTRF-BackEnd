import csv
import logging

from datetime import datetime

from django.core.files import File
from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload
from sme_ptrf_apps.core.services.arquivo_download_service import gerar_arquivo_download

from sme_ptrf_apps.utils.built_in_custom import get_recursive_attr
from tempfile import NamedTemporaryFile
from typing import BinaryIO

CABECALHO_CONTA = (
    [
        ("Código EOL", "associacao__unidade__codigo_eol"),
        ("Nome Unidade", "associacao__unidade__nome"),
        ("Nome Associação", "associacao__nome"),
        ("DRE", "associacao__unidade__dre__nome"),
        ("Nome do tipo de conta", "tipo_conta__nome"),
        ("Data de criação da conta", "criado_em"),
        ("Data de início da conta", "data_inicio"),
        ("Banco", "banco_nome"),
        ("Agência", "agencia"),
        ("Nº da conta com o dígito", "numero_conta"),
        ("Saldo_atual", "saldo_atual"),
        ("Status", "status"),
        ("Data do encerramento", "data_encerramento"),
        ("Status do encerramento", "status_encerramento"),
        ("Motivo do encerramento", "motivo_encerramento"),
    ],
)

logger = logging.getLogger(__name__)


class ExportacaoDadosContasService:
    def __init__(self, **kwargs) -> None:
        self.queryset = kwargs.get("queryset", None)
        self.data_inicio = kwargs.get("data_inicio", None)
        self.data_final = kwargs.get("data_final", None)
        self.nome_arquivo = kwargs.get("nome_arquivo", None)
        self.user = kwargs.get("user", None)

    def exporta_contas_principal(self):
        self.cabecalho = CABECALHO_CONTA[0]
        self.filtra_range_data("criado_em")
        self.exporta_contas_csv()

    def exporta_contas_csv(self) -> BinaryIO:
        linha = []
        with NamedTemporaryFile(
            mode="r+",
            newline="",
            encoding="utf-8",
            prefix=self.nome_arquivo,
            suffix=".csv",
        ) as tmp:
            write = csv.writer(tmp.file, delimiter=";")
            write.writerow([cabecalho[0] for cabecalho in self.cabecalho])

            for instance in self.queryset:
                for _, campo in self.cabecalho:
                    if campo in ["data_inicio", "criado_em", "data_encerramento"]:
                        campo = getattr(instance, campo)
                        linha.append(
                            datetime.strftime(campo, "%d/%m/%Y")
                            if campo
                            else ""
                        )

                    elif campo == "saldo_atual":
                        campo = str(getattr(instance, campo)).replace(".", ",")
                        linha.append(campo)

                    else:
                        linha.append(get_recursive_attr(instance, campo))

                logger.info(
                    f"Escrevendo linha {linha} da conta associação {instance.id}."
                )
                write.writerow(linha) if linha else None
                linha.clear()
            self.envia_arquivo_central_download(tmp)

    def filtra_range_data(self, field):
        if self.data_inicio and self.data_final:
            self.data_inicio = datetime.strptime(
                f"{self.data_inicio} 00:00:00", "%Y-%m-%d %H:%M:%S"
            )
            self.data_final = datetime.strptime(
                f"{self.data_final} 23:59:59", "%Y-%m-%d %H:%M:%S"
            )

            self.queryset = self.queryset.filter(
                **{f"{field}__range": [self.data_inicio, self.data_final]}
            )
        elif self.data_inicio and not self.data_final:
            self.data_inicio = datetime.strptime(
                f"{self.data_inicio} 00:00:00", "%Y-%m-%d %H:%M:%S"
            )

            self.queryset = self.queryset.filter(**{f"{field}__gt": self.data_inicio})

        elif self.data_final and not self.data_inicio:
            self.data_final = datetime.strptime(
                f"{self.data_final} 23:59:59", "%Y-%m-%d %H:%M:%S"
            )

            self.queryset = self.queryset.filter(**{f"{field}__lt": self.data_final})
        return self.queryset

    def envia_arquivo_central_download(self, tmp) -> None:
        logger.info("Gerando arquivo download...")
        obj_arquivo_download = gerar_arquivo_download(self.user, self.nome_arquivo)

        try:
            logger.info("Salvando arquivo download...")
            obj_arquivo_download.arquivo.save(
                name=obj_arquivo_download.identificador, content=File(tmp)
            )
            obj_arquivo_download.status = ArquivoDownload.STATUS_CONCLUIDO
            obj_arquivo_download.save()
            logger.info("Arquivo salvo com sucesso...")

        except Exception as e:
            obj_arquivo_download.status = ArquivoDownload.STATUS_ERRO
            obj_arquivo_download.msg_erro = str(e)
            obj_arquivo_download.save()
            logger.error("Erro arquivo download...")
