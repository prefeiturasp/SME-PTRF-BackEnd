import csv
from datetime import datetime
import logging

from django.utils.timezone import make_aware
from django.db.models import QuerySet
from django.core.files import File
from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload
from sme_ptrf_apps.core.models.prestacao_conta import PrestacaoConta
from sme_ptrf_apps.core.models.ambiente import Ambiente
from sme_ptrf_apps.core.models.relacao_bens import RelacaoBens
from sme_ptrf_apps.core.services.arquivo_download_service import (
    gerar_arquivo_download
)
from sme_ptrf_apps.utils.built_in_custom import get_recursive_attr

from tempfile import NamedTemporaryFile

logger = logging.getLogger(__name__)

CABECALHO_RELACAO_BENS = [
        ('Código EOL', 'conta_associacao__associacao__unidade__codigo_eol'),
        ('Nome Unidade', 'conta_associacao__associacao__unidade__nome'),
        ('Nome Associação', 'conta_associacao__associacao__nome'),
        ('DRE', 'conta_associacao__associacao__unidade__dre__nome'),
        ('Referência do Período da PC', 'prestacao_conta__periodo__referencia'),
        ('Status da PC', 'prestacao_conta__status'),
        ('Nome do tipo de Conta', 'conta_associacao__tipo_conta__nome'),
        ('URL do arquivo PDF', 'arquivo_pdf'),
        ('Status', 'status'),
        ('Versão', 'versao'),
        ('Data e hora de criação', 'criado_em'),
        ('Data e hora da última atualização', 'alterado_em'),
]


class ExportacoesDadosRelacaoBensService:

    def __init__(self, **kwargs):
        self.queryset = kwargs.get('queryset', None)
        self.data_inicio = kwargs.get('data_inicio', None)
        self.data_final = kwargs.get('data_final', None)
        self.nome_arquivo = kwargs.get('nome_arquivo', None)
        self.user = kwargs.get('user', None)
        self.cabecalho = CABECALHO_RELACAO_BENS
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

    def exporta_relacao_bens(self):
        self.cria_registro_central_download()
        self.filtra_range_data('criado_em')
        self.exporta_relacao_bens_csv()

    def exporta_relacao_bens_csv(self):
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
            logger.info(f"Iniciando extração de dados de relação de bens : {instance.id}.")

            if not RelacaoBens.objects.filter(id=instance.id).exists():
                logger.info(f"Este registro não existe mais na base de dados, portanto será pulado")
                continue

            linha_horizontal = []

            for _, campo in self.cabecalho:

                if campo == "conta_associacao__associacao__unidade__nome":
                    campo = get_recursive_attr(instance, campo)
                    linha_horizontal.append(campo.replace(";", ",") if campo else "")
                    continue

                if campo == "conta_associacao__associacao__nome":
                    campo = get_recursive_attr(instance, campo)
                    linha_horizontal.append(campo.replace(";", ",") if campo else "")
                    continue

                if campo == "conta_associacao__associacao__unidade__dre__nome":
                    campo = get_recursive_attr(instance, campo)
                    linha_horizontal.append(campo.replace(";", ",") if campo else "")
                    continue

                if campo == "conta_associacao__tipo_conta__nome":
                    campo = get_recursive_attr(instance, campo)
                    linha_horizontal.append(campo.replace(";", ",") if campo else "")
                    continue

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

                if campo == "prestacao_conta__status":
                    campo = get_recursive_attr(instance, campo)
                    status_pc = campo if campo else PrestacaoConta.STATUS_NAO_APRESENTADA
                    linha_horizontal.append(status_pc)
                    continue

                campo = get_recursive_attr(instance, campo)
                linha_horizontal.append(campo)

            logger.info(f"Escrevendo linha {linha_horizontal} de relação de bens : {instance.id}.")
            linhas_vertical.append(linha_horizontal)
            logger.info(f"Finalizado extração de dados de relação de bens : {instance.id}.")

        return linhas_vertical

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

        rodape.append(self.texto_filtro_aplicado)
        write.writerow(rodape)
        rodape.clear()
