import csv
import copy
from datetime import datetime
import logging

from django.utils.timezone import make_aware
from django.db.models import QuerySet
from django.core.files import File
from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload
from sme_ptrf_apps.core.models.ambiente import Ambiente
from sme_ptrf_apps.despesas.models.rateio_despesa import RateioDespesa
from sme_ptrf_apps.despesas.status_cadastro_completo import STATUS_NOMES
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
        ('DRE', 'associacao__unidade__dre__nome'),
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
        ('Status do rateio', 'despesa__status'),
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
        self.dre_codigo_eol = kwargs.get('dre_codigo_eol', None)
        self.cabecalho = CABECALHO_RATEIOS
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

            if not RateioDespesa.objects.filter(id=instance.id).exists():
                logger.info(f"Este registro não existe mais na base de dados, portanto será pulado")
                continue

            linha_horizontal = []

            for _, campo in self.cabecalho:

                # Removendo ponto e vírgula e substituindo por vírgula
                if campo == "associacao__unidade__nome":
                    campo = get_recursive_attr(instance, campo)
                    linha_horizontal.append(campo.replace(";", ",") if campo else "")
                    continue

                if campo == "associacao__nome":
                    campo = get_recursive_attr(instance, campo)
                    linha_horizontal.append(campo.replace(";", ",") if campo else "")
                    continue

                if campo == "associacao__unidade__dre__nome":
                    campo = get_recursive_attr(instance, campo)
                    linha_horizontal.append(campo.replace(";", ",") if campo else "")
                    continue

                if campo == "despesa__numero_documento":
                    campo = get_recursive_attr(instance, campo)
                    linha_horizontal.append(campo.replace(";", ",") if campo else "")
                    continue

                if campo == "despesa__tipo_documento__nome":
                    campo = get_recursive_attr(instance, campo)
                    linha_horizontal.append(campo.replace(";", ",") if campo else "")
                    continue

                if campo == "despesa__nome_fornecedor":
                    campo = get_recursive_attr(instance, campo)
                    linha_horizontal.append(campo.replace(";", ",") if campo else "")
                    continue

                if campo == "despesa__tipo_transacao__nome":
                    campo = get_recursive_attr(instance, campo)
                    linha_horizontal.append(campo.replace(";", ",") if campo else "")
                    continue

                if campo == "despesa__documento_transacao":
                    campo = get_recursive_attr(instance, campo)
                    linha_horizontal.append(campo.replace(";", ",") if campo else "")
                    continue

                if campo == "aplicacao_recurso":
                    campo = get_recursive_attr(instance, campo)
                    linha_horizontal.append(campo.replace(";", ",") if campo else "")
                    continue

                if campo == "tipo_custeio__nome":
                    campo = get_recursive_attr(instance, campo)
                    linha_horizontal.append(campo.replace(";", ",") if campo else "")
                    continue

                if campo == "especificacao_material_servico__descricao":
                    campo = get_recursive_attr(instance, campo)
                    linha_horizontal.append(campo.replace(";", ",") if campo else "")
                    continue

                if campo == "conta_associacao__tipo_conta__nome":
                    campo = get_recursive_attr(instance, campo)
                    linha_horizontal.append(campo.replace(";", ",") if campo else "")
                    continue

                if campo == "acao_associacao__acao__nome":
                    campo = get_recursive_attr(instance, campo)
                    linha_horizontal.append(campo.replace(";", ",") if campo else "")
                    continue

                if campo == "numero_processo_incorporacao_capital":
                    campo = get_recursive_attr(instance, campo)
                    linha_horizontal.append(campo.replace(";", ",") if campo else "")
                    continue

                if campo == "tag__nome":
                    campo = get_recursive_attr(instance, campo)
                    linha_horizontal.append(campo.replace(";", ",") if campo else "")
                    continue

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

                if campo == "despesa__status":
                    campo = get_recursive_attr(instance, campo)
                    status_dict = copy.deepcopy(STATUS_NOMES)
                    status_dict["INCOMPLETO"] = "Incompleto"
                    status = status_dict.get(campo, campo)
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
            logger.error("Erro arquivo download...")

    def texto_rodape(self):
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
        texto = self.texto_rodape()

        write.writerow(rodape)
        rodape.clear()

        rodape.append(texto)
        write.writerow(rodape)
        rodape.clear()

        data_hora_disponibilizado = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
        rodape.append(f"Arquivo disponibilizado em {data_hora_disponibilizado}")
        write.writerow(rodape)
        rodape.clear()

        rodape.append(self.texto_filtro_aplicado)
        write.writerow(rodape)
        rodape.clear()
