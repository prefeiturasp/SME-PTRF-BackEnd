import csv
import logging

from datetime import datetime

from django.core.files import File
from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload
from sme_ptrf_apps.core.models.conta_associacao import ContaAssociacao
from sme_ptrf_apps.core.models.ambiente import Ambiente
from sme_ptrf_apps.core.services.arquivo_download_service import gerar_arquivo_download
from django.utils.timezone import make_aware
from django.db.models import QuerySet

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
        ("Motivo de rejeição do encerramento", "motivo_rejeicao_encerramento"),
    ],
)

logger = logging.getLogger(__name__)


class ExportacaoDadosContasService:
    def __init__(self, **kwargs) -> None:
        self.cabecalho = CABECALHO_CONTA[0]
        self.queryset = kwargs.get("queryset", None)
        self.data_inicio = kwargs.get("data_inicio", None)
        self.data_final = kwargs.get("data_final", None)
        self.nome_arquivo = kwargs.get("nome_arquivo", None)
        self.user = kwargs.get("user", None)
        self.ambiente = self.get_ambiente
        self.objeto_arquivo_download = None
        self.texto_filtro_aplicado = self.get_texto_filtro_aplicado()

    @property
    def get_ambiente(self):
        ambiente = Ambiente.objects.first()
        return ambiente.prefixo if ambiente else ""

    def get_texto_filtro_aplicado(self):
        if self.data_inicio and self.data_final:
            data_inicio_formatada = datetime.strptime(f"{self.data_inicio}", '%Y-%m-%d')
            data_inicio_formatada = data_inicio_formatada.strftime("%d/%m/%Y")

            data_final_formatada = datetime.strptime(f"{self.data_final}", '%Y-%m-%d')
            data_final_formatada = data_final_formatada.strftime("%d/%m/%Y")

            return f"Filtro aplicado: {data_inicio_formatada} a {data_final_formatada} (data de criação do registro)"

        if self.data_inicio:
            data_inicio_formatada = datetime.strptime(f"{self.data_inicio}", '%Y-%m-%d')
            data_inicio_formatada = data_inicio_formatada.strftime("%d/%m/%Y")
            return f"Filtro aplicado: A partir de {data_inicio_formatada} (data de criação do registro)"

        if self.data_final:
            data_final_formatada = datetime.strptime(f"{self.data_final}", '%Y-%m-%d')
            data_final_formatada = data_final_formatada.strftime("%d/%m/%Y")
            return f"Filtro aplicado: Até {data_final_formatada} (data de criação do registro)"

        return ""

    def exporta_contas_principal(self):
        self.cria_registro_central_download()
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

                if not ContaAssociacao.objects.filter(id=instance.id).exists():
                    logger.info(f"Este registro não existe mais na base de dados, portanto será pulado")
                    continue

                for _, campo in self.cabecalho:
                    if campo in ["data_inicio", "criado_em", "data_encerramento"]:
                        campo = getattr(instance, campo)
                        linha.append(
                            datetime.strftime(campo, "%d/%m/%Y") if campo else ""
                        )

                    elif campo == "saldo_atual":

                        if instance.associacao:
                            campo = str(getattr(instance, campo)).replace(".", ",")
                        else:
                            campo = ""

                        linha.append(campo)

                    else:
                        linha.append(get_recursive_attr(instance, campo))

                logger.info(
                    f"Escrevendo linha {linha} da conta associação {instance.id}."
                )
                write.writerow(linha) if linha else None
                linha.clear()

            self.cria_rodape(write)

            self.envia_arquivo_central_download(tmp)

    def filtra_range_data(self, field) -> QuerySet:
        import datetime

        # Converte as datas inicial e final de texto para date
        inicio = datetime.datetime.strptime(self.data_inicio, "%Y-%m-%d").date() if self.data_inicio else None
        final = datetime.datetime.strptime(self.data_final, "%Y-%m-%d").date() if self.data_final else None

        # Define o horário da data_final para o último momento do dia
        # Sem isso o filtro pode não incluir todos os registros do dia
        final = make_aware(datetime.datetime.combine(final, datetime.time.max)) if final else None

        if inicio and final:
            self.queryset = self.queryset.filter(
                **{f'{field}__gte': inicio, f'{field}__lte': final}
            )
        elif inicio and not final:
            self.queryset = self.queryset.filter(
                **{f'{field}__gte': inicio}
            )
        elif final and not inicio:
            self.queryset = self.queryset.filter(
                **{f'{field}__lte': final}
            )
        return self.queryset

    def cria_registro_central_download(self):
        logger.info(f"Criando registro na central de download")
        obj = gerar_arquivo_download(
            self.user,
            self.nome_arquivo,
            self.texto_filtro_aplicado
        )

        self.objeto_arquivo_download = obj

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

        rodape.append(self.texto_filtro_aplicado)
        write.writerow(rodape)
        rodape.clear()

    def envia_arquivo_central_download(self, tmp) -> None:
        try:
            logger.info("Salvando arquivo download...")
            self.objeto_arquivo_download.arquivo.save(
                name=self.objeto_arquivo_download.identificador, content=File(tmp)
            )
            self.objeto_arquivo_download.status = ArquivoDownload.STATUS_CONCLUIDO
            self.objeto_arquivo_download.save()
            logger.info("Arquivo salvo com sucesso...")

        except Exception as e:
            self.objeto_arquivo_download.status = ArquivoDownload.STATUS_ERRO
            self.objeto_arquivo_download.msg_erro = str(e)
            self.objeto_arquivo_download.save()
            logger.error("Erro arquivo download...")
