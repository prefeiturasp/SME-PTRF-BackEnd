import csv
from datetime import datetime, time, date
import logging
from django.db.models.fields.files import FieldFile
from django.core.files import File
from django.utils.timezone import make_aware
from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload
from sme_ptrf_apps.core.models.ambiente import Ambiente
from sme_ptrf_apps.core.services.arquivo_download_service import (
    gerar_arquivo_download
)
from sme_ptrf_apps.utils.built_in_custom import get_recursive_attr

from tempfile import NamedTemporaryFile

logger = logging.getLogger(__name__)


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


CABECALHO_ATAS = [
    ('Código EOL', 'associacao__unidade__codigo_eol'),
    ('Nome unidade', 'associacao__unidade__nome'),
    ('Nome associação', 'associacao__nome'),
    ('DRE', 'associacao__unidade__dre__nome'),
    ('Referência do período da PC', 'periodo__referencia'),
    ('Tipo de ata', 'tipo_ata'),
    ('Tipo de reunião', 'tipo_reuniao'),
    ('Data da reunião', 'data_reuniao'),
    ('Hora da reunião', 'hora_reuniao'),
    ('Local da reunião', 'local_reuniao'),
    ('Convocação', 'convocacao'),
    ('Presidente da reunião', 'presidente_reuniao'),
    ('Cargo do presidente', 'cargo_presidente_reuniao'),
    ('Secretário da reunião', 'secretario_reuniao'),
    ('Cargo do secretário', 'cargo_secretaria_reuniao'),
    ('Justificativas de repasses pendentes', 'justificativa_repasses_pendentes'),
    ('Manifestações', 'comentarios'),
    ('Retificações', 'retificacoes'),
    ('Parecer dos presentes', 'parecer_conselho'),
    ('Data e hora de preenchimento', 'preenchida_em'),
    ('URL do arquivo PDF', 'arquivo_pdf'),
    ('Status', 'status_geracao_pdf'),
    ('Data e hora de criação', 'criado_em'),
    ('Data e hora da última atualização', 'alterado_em')
]


class ExportacoesAtasService:

    def __init__(self, **kwargs):
        self.queryset = kwargs.get('queryset', None)
        self.data_inicio = kwargs.get('data_inicio', None)
        self.data_final = kwargs.get('data_final', None)
        self.nome_arquivo = kwargs.get('nome_arquivo', None)
        self.user = kwargs.get('user', None)
        self.dre_codigo_eol = kwargs.get('dre_codigo_eol', None)
        self.cabecalho = CABECALHO_ATAS
        self.ambiente = self.get_ambiente
        self.objeto_arquivo_download = None

    @property
    def get_ambiente(self):
        ambiente = Ambiente.objects.first()
        return ambiente.prefixo if ambiente else ""

    def exporta_atas(self):
        self.cria_registro_central_download()
        self.filtra_range_data('criado_em')
        self.exporta_atas_csv()

    def exporta_atas_csv(self):
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

    def formata_dado(self, valor):

        if isinstance(valor, datetime):
            if valor.strftime("%H:%M:%S") == "00:00:00":
                valor = valor.strftime("%d/%m/%Y")
            else:
                valor = valor.strftime("%d/%m/%Y às %H:%M:%S")
        if isinstance(valor, date):
            valor = valor.strftime("%d/%m/%Y")
        if isinstance(valor, time):
            valor = valor.strftime("%H:%M")
            valor = "" if valor == "00:00" else valor
        if isinstance(valor, FieldFile) and valor:
            if valor.url:
                if self.ambiente == "local":
                    valor = f"http://127.0.0.1:8000{valor.url}"
                else:
                    valor = f"https://{self.ambiente}.sme.prefeitura.sp.gov.br{valor.url}"

        valor = "" if not valor else str(valor).replace(";", ",")
        return valor

    def monta_dados(self):
        linhas_vertical = []

        for instance in self.queryset:
            logger.info(f"Iniciando extração de dados de atas, ata id: {instance.id}.")
            linha_horizontal = []

            for _, campo in self.cabecalho:
                campo_valor = get_recursive_attr(instance, campo)
                campo_valor = self.formata_dado(campo_valor)
                linha_horizontal.append(campo_valor)

            logger.info(f"Escrevendo linha {linha_horizontal} de atas, ata id: {instance.id}.")
            linhas_vertical.append(linha_horizontal)
            logger.info(f"Finalizando extração de dados de atas, ata id: {instance.id}.")

        return linhas_vertical

    def filtra_range_data(self, field):
        # Converte as datas inicial e final de texto para date
        inicio = datetime.strptime(self.data_inicio, "%Y-%m-%d").date() if self.data_inicio else None
        final = datetime.strptime(self.data_final, "%Y-%m-%d").date() if self.data_final else None

        # Define o horário da data_final para o último momento do dia
        # Sem isso o filtro pode não incluir todos os registros do dia
        final = make_aware(datetime.combine(final, time.max)) if final else None

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

        data_hora_disponibilizado = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
        rodape.append(f"Arquivo disponibilizado em {data_hora_disponibilizado}")
        write.writerow(rodape)
        rodape.clear()

        rodape.append(get_informacoes_download(self.data_inicio, self.data_final))
        write.writerow(rodape)
        rodape.clear()
