import csv
from datetime import datetime
import logging

from django.core.files import File
from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload
from sme_ptrf_apps.core.models.ambiente import Ambiente
from sme_ptrf_apps.core.services.arquivo_download_service import (
    gerar_arquivo_download
)
from sme_ptrf_apps.utils.built_in_custom import get_recursive_attr

from tempfile import NamedTemporaryFile

logger = logging.getLogger(__name__)

CABECALHO_RATEIOS = [
        ('Código EOL', 'associacao__unidade__codigo_eol'),
        ('Nome Unidade', 'associacao__unidade__nome'),
        ('Nome Associação', 'associacao__nome'),
        ('ID do Gasto', 'despesa__id'),
        ('Número do documento', 'despesa__numero_documento'),
        ('Tipo de documento', 'despesa__tipo_documento__nome'),
        ('Data do documento', 'despesa__data_documento'),
        ('CPF_CNPJ do fornecedor', 'despesa__cpf_cnpj_fornecedor'),
        ('Nome do fornecedor', 'despesa__nome_fornecedor'),
        ('Tipo de transação', 'despesa__tipo_transacao__nome'),
        ('Número do documento da transação', 'despesa__documento_transacao'),
        ('Data da transação', 'despesa__data_transacao'),
        ('Tipo de aplicação do recurso', 'aplicacao_recurso'),
        ('Nome do Tipo de Custeio', 'tipo_custeio__nome'),
        ('Descrição da Especificação de Material ou Serviço', 'especificacao_material_servico__descricao'),
        ('Nome do tipo de Conta', 'conta_associacao__tipo_conta__nome'),
        ('Nome da Ação', 'acao_associacao__acao__nome'),
        ('Quantidade de itens', 'quantidade_itens_capital'),
        ('Valor unitário', 'valor_item_capital'),
        ('Número do processo de incorporação', 'numero_processo_incorporacao_capital'),
        ('Valor', 'valor_rateio'),
        ('Valor realizado', 'valor_original'),
        ('Status do rateio', 'status'),
        ('Conferido', 'conferido'),
        ('Referência do período de conciliação', 'periodo_conciliacao__referencia'),
        ('Descrição da tag', 'tag__nome'),
        ('É saída de recurso externo?', 'saida_de_recurso_externo'),
        ('É gasto sem comprovação fiscal?', 'eh_despesa_sem_comprovacao_fiscal'),
        ('É pagamento antecipado?', 'PAGAMENTO_ANTECIPADO'),
        ('Tem estorno cadastrado?', 'POSSUI_ESTORNO'),
        ('Data e hora de criação', 'criado_em'),
        ('Data e hora da última atualização', 'alterado_em'),
        ('UUID do rateio', 'uuid'),
]


class ExportacoesRateiosService:

    def __init__(self, **kwargs):
        self.queryset = kwargs.get('queryset', None)
        self.data_inicio = kwargs.get('data_inicio', None)
        self.data_final = kwargs.get('data_final', None)
        self.nome_arquivo = kwargs.get('nome_arquivo', None)
        self.user = kwargs.get('user', None)
        self.cabecalho = CABECALHO_RATEIOS
        self.ambiente = self.get_ambiente
        self.objeto_arquivo_download = None

    @property
    def get_ambiente(self):
        ambiente = Ambiente.objects.first()
        return ambiente.prefixo if ambiente else ""

    def exporta_rateios(self):
        self.cria_registro_central_download()
        self.filtra_range_data('despesa__criado_em')
        self.exporta_rateios_csv()

    def exporta_rateios_csv(self):
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
            logger.info(f"Iniciando extração de dados de rateios, rateio id: {instance.id}.")
            linha_horizontal = []

            for _, campo in self.cabecalho:
                if campo == "despesa__data_documento":
                    campo = get_recursive_attr(instance, campo)
                    data_documento_formatado = campo.strftime("%d/%m/%Y") if campo else ""
                    linha_horizontal.append(data_documento_formatado)
                    continue

                if campo == "despesa__data_transacao":
                    campo = get_recursive_attr(instance, campo)
                    data_transacao_formatado = campo.strftime("%d/%m/%Y") if campo else ""
                    linha_horizontal.append(data_transacao_formatado)
                    continue

                if campo == "valor_item_capital":
                    valor_capital = str(getattr(instance, campo)).replace(".", ",")
                    linha_horizontal.append(valor_capital)
                    continue

                if campo == "valor_rateio":
                    valor_rateio = str(getattr(instance, campo)).replace(".", ",")
                    linha_horizontal.append(valor_rateio)
                    continue

                if campo == "valor_original":
                    valor_original = str(getattr(instance, campo)).replace(".", ",")
                    linha_horizontal.append(valor_original)
                    continue

                if campo == "status":
                    campo = get_recursive_attr(instance, campo)
                    status = "Completo" if campo == "COMPLETO" else "Rascunho"
                    linha_horizontal.append(status)
                    continue

                if campo == "conferido":
                    campo = get_recursive_attr(instance, campo)
                    conferido = "Sim" if campo else "Não"
                    linha_horizontal.append(conferido)
                    continue

                if campo == "saida_de_recurso_externo":
                    campo = get_recursive_attr(instance, campo)
                    saido_recurso_externo = "Sim" if campo else "Não"
                    linha_horizontal.append(saido_recurso_externo)
                    continue

                if campo == "eh_despesa_sem_comprovacao_fiscal":
                    campo = get_recursive_attr(instance, campo)
                    eh_despesa_sem_comprovao = "Sim" if campo else "Não"
                    linha_horizontal.append(eh_despesa_sem_comprovao)
                    continue

                if campo == "PAGAMENTO_ANTECIPADO":
                    pagamento_antecipado = "Sim" if instance.despesa and instance.despesa.teve_pagamento_antecipado() else "Não"
                    linha_horizontal.append(pagamento_antecipado)
                    continue

                if campo == "POSSUI_ESTORNO":
                    estorno = "Sim" if instance.despesa and instance.despesa.possui_estornos() else "Não"
                    linha_horizontal.append(estorno)
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

                campo = get_recursive_attr(instance, campo)
                linha_horizontal.append(campo)

            logger.info(f"Escrevendo linha {linha_horizontal} de rateios, rateio id: {instance.id}.")
            linhas_vertical.append(linha_horizontal)
            logger.info(f"Finalizando extração de dados de rateios, rateio id: {instance.id}.")

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
            self.nome_arquivo
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
        texto = f"Arquivo gerado pelo {self.ambiente} em {data_hora_geracao}"

        return texto

    def cria_rodape(self, write):
        rodape = []
        texto = self.texto_rodape()

        rodape.append("\n")
        write.writerow(rodape)
        rodape.clear()

        rodape.append(texto)
        write.writerow(rodape)
        rodape.clear()
