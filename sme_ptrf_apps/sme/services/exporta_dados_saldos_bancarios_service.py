import csv
from datetime import datetime
import logging
from django.utils.timezone import make_aware
from django.db.models import QuerySet
from django.core.files import File
from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload
from sme_ptrf_apps.core.models.ambiente import Ambiente
from sme_ptrf_apps.core.models.observacao_conciliacao import ObservacaoConciliacao
from sme_ptrf_apps.core.services.arquivo_download_service import (
    gerar_arquivo_download
)
from sme_ptrf_apps.utils.built_in_custom import get_recursive_attr

from tempfile import NamedTemporaryFile

logger = logging.getLogger(__name__)

CABECALHO = [
    ('Código EOL da Unidade', 'associacao__unidade__codigo_eol'),
    ('Nome Unidade', 'associacao__unidade__nome'),
    ('Tipo da unidade', 'associacao__unidade__tipo_unidade'),
    ('Nome Associação', 'associacao__nome'),
    ('DRE', 'associacao__unidade__dre__nome'),
    ('Data extrato', 'data_extrato'),
    ('Valor extrato', 'saldo_extrato'),
    ('Período', 'periodo__referencia'),
    ('Conta', 'conta_associacao__tipo_conta'),
    ('Comprovante do saldo da conta', 'comprovante_extrato'),
    ('Última atualização', 'alterado_em')
]


class ExportacaoDadosSaldosBancariosService:

    def __init__(self, **kwargs):
        self.queryset = kwargs.get('queryset', None)
        self.nome_arquivo = kwargs.get('nome_arquivo', None)
        self.data_inicio = kwargs.get("data_inicio", None)
        self.data_final = kwargs.get("data_final", None)
        self.user = kwargs.get('user', None)
        self.cabecalho = CABECALHO
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

    def exportar(self):
        self.cria_registro_central_download()
        self.filtra_range_data("criado_em")
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
            logger.info(f"Iniciando extração de dados de saldos bancarios, id: {instance.id}.")

            if not ObservacaoConciliacao.objects.filter(id=instance.id).exists():
                logger.info("Este registro não existe mais na base de dados, portanto será pulado")
                continue

            linha_horizontal = []

            for _, campo in self.cabecalho:
                campo_valor = get_recursive_attr(instance, campo)

                if campo == "data_extrato":
                    campo = get_recursive_attr(instance, campo)
                    if campo:
                        data_data_extrato_formatada = campo.strftime("%d/%m/%Y")
                        linha_horizontal.append(data_data_extrato_formatada)
                        continue

                if campo == "alterado_em":
                    campo = get_recursive_attr(instance, campo)
                    if campo:
                        alterado_em_formatada = campo.strftime("%d/%m/%Y às %H:%M:%S")
                        linha_horizontal.append(alterado_em_formatada)
                        continue

                if campo == "saldo_extrato":
                    saldo_extrato = str(getattr(instance, campo)).replace(".", ",")
                    linha_horizontal.append(saldo_extrato)
                    continue

                if campo == "comprovante_extrato":
                    campo = get_recursive_attr(instance, campo)
                    url = ""

                    if campo:
                        if self.ambiente == "local":
                            url = f"http://127.0.0.1:8000{campo.url}"
                        else:
                            url = f"https://{self.ambiente}.sme.prefeitura.sp.gov.br{campo.url}"

                    linha_horizontal.append(url)
                    continue

                campo_valor = "" if not campo_valor else str(campo_valor).replace(";", ",")
                linha_horizontal.append(campo_valor)

            logger.info(f"Escrevendo linha {linha_horizontal}, id: {instance.id}.")
            linhas_vertical.append(linha_horizontal)
            logger.info(f"Finalizando extração de dados, id: {instance.id}.")

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
        logger.info("Criando registro na central de download")
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

    def texto_info_arquivo_gerado(self):
        data_hora_geracao = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
        texto = f"Arquivo gerado via {self.ambiente} pelo usuário {self.user} em {data_hora_geracao}"

        return texto
