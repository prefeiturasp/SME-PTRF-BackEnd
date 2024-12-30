import csv
from datetime import datetime
import logging
from tempfile import NamedTemporaryFile

from django.core.files import File
from django.utils.timezone import make_aware
from django.db.models import QuerySet

from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload
from sme_ptrf_apps.core.models.ambiente import Ambiente
from sme_ptrf_apps.core.models.associacao import Associacao
from sme_ptrf_apps.core.services.arquivo_download_service import (
    gerar_arquivo_download
)
from sme_ptrf_apps.utils.built_in_custom import get_recursive_attr


logger = logging.getLogger(__name__)

CABECALHO_ASSOCIACOES = [
    ('Código EOL', 'unidade__codigo_eol', lambda x: str(x).replace(";", ",") if x else ""),
    ('Nome Unidade', 'unidade__nome', lambda x: x.replace(";", ",") if x else ""),
    ('Nome Associação', 'nome', lambda x: x.replace(";", ",") if x else ""),
    ('DRE', 'unidade__dre__nome', lambda x: x.replace(";", ",") if x else ""),
    ('CNPJ', 'cnpj', lambda x: x.replace(";", ",") if x else ""),
    ('ID do Período Inicial', 'periodo_inicial__uuid', lambda x: str(x).replace(";", ",") if x else ""),
    ('Referência do Período inicial', 'periodo_inicial__referencia', lambda x: x.replace(";", ",") if x else ""),
    ('Data de encerramento', 'data_de_encerramento', lambda x: x.strftime("%d/%m/%Y") if x else ""),
    ('CCM', 'ccm', lambda x: x.replace(";", ",") if x else ""),
    ('E-mail', 'email', lambda x: x.replace(";", ",") if x else ""),
    ('Número do processo de regularidade', 'processo_regularidade', lambda x: x.replace(";", ",") if x else ""),
    ('Status do presidente', 'status_presidente', lambda x: x.replace(";", ",") if x else ""),
    ('Cargo substituto do presidente', 'cargo_substituto_presidente_ausente', lambda x: x.replace(";", ",") if x else ""),
    ('Data e hora de criação', 'criado_em', lambda x: x.strftime("%d/%m/%Y às %H:%M:%S")),
    ('Data e hora da última atualização', 'alterado_em', lambda x: x.strftime("%d/%m/%Y às %H:%M:%S")),
]


class ExportaAssociacoesService:

    def __init__(self, **kwargs):
        self.queryset = kwargs.get('queryset', None)
        self.data_inicio = kwargs.get('data_inicio', None)
        self.data_final = kwargs.get('data_final', None)
        self.nome_arquivo = kwargs.get('nome_arquivo', None)
        self.user = kwargs.get('user', None)
        self.cabecalho = CABECALHO_ASSOCIACOES
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

    def exporta_associacoes(self):
        self.cria_registro_central_download()
        self.filtra_range_data('criado_em')
        self.exporta_associacoes_csv()

    def cria_registro_central_download(self):
        logger.info(f"Criando registro na central de download")
        obj = gerar_arquivo_download(
            self.user,
            self.nome_arquivo,
            self.texto_filtro_aplicado
        )

        self.objeto_arquivo_download = obj

    def filtra_range_data(self, field) -> QuerySet:
        from django.db.models import Q
        import datetime

        # Converte as datas inicial e final de texto para date
        inicio = datetime.datetime.strptime(self.data_inicio, "%Y-%m-%d").date() if self.data_inicio else None
        final = datetime.datetime.strptime(self.data_final, "%Y-%m-%d").date() if self.data_final else None

        # Define o horário da data_final para o último momento do dia
        # Sem isso o filtro pode não incluir todos os registros do dia
        final = make_aware(datetime.datetime.combine(final, datetime.time.max)) if final else None
        filtros = Q()
        if inicio:
            filtros &= Q(**{f'{field}__gte': inicio})
        if final:
            filtros &= Q(**{f'{field}__lte': final})

        self.queryset = self.queryset.filter(filtros)
        return self.queryset

    def exporta_associacoes_csv(self):
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
            logger.info(f"Iniciando extração de asscociacao: {instance.id}.")

            if not Associacao.objects.filter(id=instance.id).exists():
                logger.info(f"Este registro não existe mais na base de dados, portanto será pulado")
                continue

            linha_horizontal = []

            for _, campo, tratamento  in self.cabecalho:
                valor = get_recursive_attr(instance, campo)
                valor_tratado = tratamento(valor)
                linha_horizontal.append(valor_tratado)

            logger.info(f"Escrevendo linha {linha_horizontal} da associacao: {instance.id}.")
            linhas_vertical.append(linha_horizontal)
            logger.info(f"Finalizado extração de dados da associacao: {instance.id}.")

        return linhas_vertical

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
