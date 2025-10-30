import csv
import datetime
import logging

from tempfile import NamedTemporaryFile

from django.utils.timezone import make_aware
from django.core.files import File
from django.db.models import QuerySet

from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload
from sme_ptrf_apps.core.services.arquivo_download_service import (
    gerar_arquivo_download
)
from sme_ptrf_apps.utils.built_in_custom import get_recursive_attr
from sme_ptrf_apps.core.models.ambiente import Ambiente
from sme_ptrf_apps.core.models.unidade import Unidade


CABECALHO_UNIDADES = [
    # Título do cabeçalho, nome_do_campo, tratamento do dado
    ('Código EOL', 'codigo_eol', lambda x: str(x).replace(";", ",")),
    ('Tipo', 'tipo_unidade', lambda x: x),
    ('Nome', 'nome', lambda x: x.replace(";", ",")),
    ('CEP', 'cep', lambda x: x.replace(";", ",")),
    ('Tipo Logradouro', 'tipo_logradouro', lambda x: x.replace(";", ",")),
    ('Logradouro', 'logradouro', lambda x: x.replace(";", ",")),
    ('Bairro', 'bairro', lambda x: x.replace(";", ",")),
    ('Número', 'numero', lambda x: x.replace(";", ",")),
    ('Complemento', 'complemento', lambda x: x.replace(";", ",")),
    ('Telefone', 'telefone', lambda x: x.replace(";", ",")),
    ('E-mail', 'email', lambda x: x.replace(";", "")),
    ('Código EOL DRE', 'dre__codigo_eol', lambda x: str(x).replace(";", "") if x else ""),
    ('Nome DRE', 'dre__nome', lambda x: x.replace(";", ",") if x else ""),
    ('Sigla DRE', 'dre__sigla', lambda x: x.replace(";", ",") if x else ""),
    ('Nome Diretor Unidade', 'diretor_nome', lambda x: x.replace(";", ",")),
    ('Data e hora de criação do registro', 'criado_em', lambda x: x.strftime("%d/%m/%Y às %H:%M:%S")),
    ('Data e hora da última atualização do registro', 'alterado_em', lambda x: x.strftime("%d/%m/%Y às %H:%M:%S")),
]

logger = logging.getLogger(__name__)


class ExportacoesDadosUnidadesService:

    def __init__(self, **kwargs) -> None:
        self.queryset = kwargs.get('queryset', None)
        self.data_inicio = kwargs.get('data_inicio', None)
        self.data_final = kwargs.get('data_final', None)
        self.nome_arquivo = kwargs.get('nome_arquivo', None)
        self.user = kwargs.get('user', None)
        self.dre_codigo_eol = kwargs.get('dre_codigo_eol', None)
        self.objeto_arquivo_download = None
        self.ambiente = self.get_ambiente
        self.texto_filtro_aplicado = self.get_texto_filtro_aplicado()
        self.cabecalho = CABECALHO_UNIDADES

    @property
    def get_ambiente(self):
        ambiente = Ambiente.objects.first()
        return ambiente.prefixo if ambiente else ""

    def get_texto_filtro_aplicado(self):
        if self.data_inicio and self.data_final:
            data_inicio_formatada = datetime.datetime.strptime(f"{self.data_inicio}", '%Y-%m-%d')
            data_inicio_formatada = data_inicio_formatada.strftime("%d/%m/%Y")

            data_final_formatada = datetime.datetime.strptime(f"{self.data_final}", '%Y-%m-%d')
            data_final_formatada = data_final_formatada.strftime("%d/%m/%Y")

            return f"Filtro aplicado: {data_inicio_formatada} a {data_final_formatada} (data de criação do registro)"

        if self.data_inicio:
            data_inicio_formatada = datetime.datetime.strptime(f"{self.data_inicio}", '%Y-%m-%d')
            data_inicio_formatada = data_inicio_formatada.strftime("%d/%m/%Y")
            return f"Filtro aplicado: A partir de {data_inicio_formatada} (data de criação do registro)"

        if self.data_final:
            data_final_formatada = datetime.datetime.strptime(f"{self.data_final}", '%Y-%m-%d')
            data_final_formatada = data_final_formatada.strftime("%d/%m/%Y")
            return f"Filtro aplicado: Até {data_final_formatada} (data de criação do registro)"

        return ""

    def exporta_unidades(self):
        self.cria_registro_central_download()
        self.filtra_range_data('criado_em')
        self.exporta_unidades_csv()

    def exporta_unidades_csv(self):
        dados = self.monta_dados()

        with NamedTemporaryFile(
            mode="r+",
            newline='',
            encoding='utf-8',
            prefix=self.nome_arquivo,
            suffix='.csv'
        ) as tmp:
            write = csv.writer(tmp.file, delimiter=";")
            header_csv = [cabecalho[0] for cabecalho in self.cabecalho]
            print('cabecalho csv', header_csv)
            write.writerow(header_csv)

            for linha in dados:
                write.writerow(linha) if linha else None

            self.cria_rodape(write)
            self.envia_arquivo_central_download(tmp)

    def monta_dados(self):
        linhas_vertical = []
        for instance in self.queryset:
            logger.info(f"Iniciando extração de unidades, uuid: {instance.uuid}.")

            if not Unidade.objects.filter(uuid=instance.uuid).exists():
                logger.info("Este registro não existe mais na base de dados, portanto será pulado")
                continue

            linha_horizontal = []

            for _, campo, tratamento in self.cabecalho:
                valor = get_recursive_attr(instance, campo)
                valor_tratado = tratamento(valor)
                linha_horizontal.append(valor_tratado)

            logger.info(f"Escrevendo linha {linha_horizontal} de unidades, uuid: {instance.uuid}.")
            linhas_vertical.append(linha_horizontal)
            logger.info(f"Finalizando extração de dados de unidades, uuid: {instance.uuid}.")

        return linhas_vertical

    def filtra_range_data(self, field) -> QuerySet:
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
        logger.info("Criando registro de unidades na central de download")
        obj = gerar_arquivo_download(
            self.user,
            self.nome_arquivo,
            self.texto_filtro_aplicado,
            self.dre_codigo_eol
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
            logger.error("Erro arquivo download... %s", str(e))

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
        # Linha em branco antes do rodapé (mantida conforme padrão anterior)
        write.writerow(rodape)
        rodape.clear()
        # Linha 1: Arquivo solicitado (horário do início do processamento)
        texto_solicitado = self.texto_rodape()
        rodape.append(texto_solicitado)
        write.writerow(rodape)
        rodape.clear()

        # Linha 2: Arquivo disponibilizado em (próximo ao momento de conclusão)
        data_hora_disponibilizado = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
        rodape.append(f"Arquivo disponibilizado em {data_hora_disponibilizado}")
        write.writerow(rodape)
        rodape.clear()

        # Linha 3: Mantém linha de filtro aplicado
        rodape.append(self.texto_filtro_aplicado)
        write.writerow(rodape)
        rodape.clear()
