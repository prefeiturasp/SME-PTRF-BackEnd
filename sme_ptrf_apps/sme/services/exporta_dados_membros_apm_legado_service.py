import csv
import logging

from datetime import datetime

from django.core.files import File
from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload
from sme_ptrf_apps.core.models import MembroAssociacao
from sme_ptrf_apps.core.choices import RepresentacaoCargo
from sme_ptrf_apps.core.models.ambiente import Ambiente
from sme_ptrf_apps.core.services.arquivo_download_service import gerar_arquivo_download

from sme_ptrf_apps.utils.built_in_custom import get_recursive_attr
from tempfile import NamedTemporaryFile

CABECALHO_MEMBROS_APM = (
    [
        ("Código EOL", "associacao__unidade__codigo_eol"),
        ("Tipo da unidade", "associacao__unidade__tipo_unidade"),
        ("Nome da Unidade", "associacao__unidade__nome"),
        ("Nome da Associação", "associacao__nome"),
        ("CNPJ", "associacao__cnpj"),
        ("DRE", "associacao__unidade__dre__nome"),
        ("Cargo", "cargo_associacao"),
        ("Nome", "nome"),
        ("Número de identificação", "cpf"),
        ("Representação", "representacao"),
    ],
)

logger = logging.getLogger(__name__)


class ExportacaoDadosMembrosApmLegadoService:
    def __init__(self, **kwargs) -> None:
        self.cabecalho = CABECALHO_MEMBROS_APM[0]
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

    def exporta_membros_apm(self):
        self.cria_registro_central_download()
        self.filtra_range_data("criado_em")
        self.exporta_membros_apm_csv()

    def exporta_membros_apm_csv(self):
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
            logger.info(f"Iniciando extração de dados de membros apm, id: {instance.id}.")

            if not MembroAssociacao.objects.filter(id=instance.id).exists():
                logger.info(f"Este registro não existe mais na base de dados, portanto será pulado")
                continue

            linha_horizontal = []

            for _, campo in self.cabecalho:
                if campo == "cpf":
                    representacao = get_recursive_attr(instance, 'representacao')
                    if representacao == RepresentacaoCargo.SERVIDOR.name:
                        valor = get_recursive_attr(instance, 'codigo_identificacao')
                        linha_horizontal.append(valor)
                        continue

                    valor = get_recursive_attr(instance, 'cpf')
                    if valor:
                        valor = valor.replace(".", "").replace("-", "").replace(" ", "")
                        if len(valor) < 10:
                            masked_cpf = ""
                        else:
                            start = valor[:3]
                            end = valor[-2:]
                            middle = "X" * (len(valor) - len(start) - len(end))
                            masked_cpf = start + middle + end
                        linha_horizontal.append(masked_cpf)
                    else:
                        linha_horizontal.append("")
                    continue

                valor = get_recursive_attr(instance, campo)
                linha_horizontal.append(valor)

            logger.info(f"Escrevendo linha {linha_horizontal} de membros apm, id: {instance.id}.")
            linhas_vertical.append(linha_horizontal)
            logger.info(f"Finalizando extração de dados de membros apm, id: {instance.id}.")

        return linhas_vertical

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

    def cria_registro_central_download(self):
        logger.info(f"Criando registro na central de download")

        obj = gerar_arquivo_download(
            self.user,
            self.nome_arquivo,
            self.texto_filtro_aplicado
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

    def cria_rodape(self, write):
        rodape = []
        texto_info_arquivo_gerado = self.texto_info_arquivo_gerado()

        write.writerow(rodape)
        rodape.clear()

        rodape.append(texto_info_arquivo_gerado)
        write.writerow(rodape)
        rodape.clear()

        rodape.append(self.texto_filtro_aplicado)
        write.writerow(rodape)
        rodape.clear()

    def texto_info_arquivo_gerado(self):
        data_hora_geracao = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
        texto = f"Arquivo gerado via {self.ambiente} pelo usuário {self.user} em {data_hora_geracao}"

        return texto
