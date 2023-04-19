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

CABECALHO_DOCS = [
        ('Código EOL', 'associacao__unidade__codigo_eol'),
        ('Nome unidade', 'associacao__unidade__nome'),
        ('Nome associação', 'associacao__nome'),
        ('ID do gasto', 'id'),
        ('É despesa sem comprovação fiscal?', 'eh_despesa_sem_comprovacao_fiscal'),
        ('É despesa reconhecida pela Associação?', 'eh_despesa_reconhecida_pela_associacao'),
        ('Número do documento', 'numero_documento'),
        ('Tipo de documento', 'tipo_documento__nome'),
        ('Data do documento', 'data_documento'),
        ('CPF_CNPJ do fornecedor', 'cpf_cnpj_fornecedor'),
        ('Nome do fornecedor', 'nome_fornecedor'),
        ('Tipo de transação', 'tipo_transacao__nome'),
        ('Número do documento de transação', 'documento_transacao'),
        ('Data da transação', 'data_transacao'),
        ('Valor total do documento', 'valor_total'),
        ('Valor realizado', 'valor_original'),
        ('Valor pago com recursos próprios', 'valor_recursos_proprios'),
        ('Número do Boletim de Ocorrência', 'numero_boletim_de_ocorrencia'),
        ('Retem impostos?', 'retem_imposto'),
        ('Descrição do motivo de pagamento antecipado', 'motivos'),
        ('É saída de recurso externo?', 'saida_recurso_externo'),
        ('Status do gasto', 'status'),
        ('Data e hora de criação', 'criado_em'),
        ('Data e hora da última atualização', 'alterado_em'),
        ('UUID do gasto', 'uuid')
]

class ExportacoesDocumentosDespesasService:

    def __init__(self, **kwargs):
        self.queryset = kwargs.get('queryset', None)
        self.data_inicio = kwargs.get('data_inicio', None)
        self.data_final = kwargs.get('data_final', None)
        self.nome_arquivo = kwargs.get('nome_arquivo', None)
        self.user = kwargs.get('user', None)
        self.cabecalho = CABECALHO_DOCS
        self.ambiente = self.get_ambiente
        self.objeto_arquivo_download = None

    @property
    def get_ambiente(self):
        ambiente = Ambiente.objects.first()
        return ambiente.prefixo if ambiente else ""

    def exporta_despesas(self):
        self.cria_registro_central_download()
        self.filtra_range_data('criado_em')
        self.exporta_despesas_csv()

    def exporta_despesas_csv(self):
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

            logger.info(f"Iniciando extração de dados de despesas, despesa id: {instance.id}.")
            linha_horizontal = []

            motivos = list(instance.motivos_pagamento_antecipado.all())

            for _, campo in self.cabecalho:
                if campo == "eh_despesa_sem_comprovacao_fiscal":
                    campo = get_recursive_attr(instance, campo)
                    linha_horizontal.append("Sim" if campo else "Não")
                    continue

                if campo == "eh_despesa_reconhecida_pela_associacao":
                    campo = get_recursive_attr(instance, campo)
                    linha_horizontal.append("Sim" if campo else "Não")
                    continue

                if campo == "data_transacao":
                    campo = get_recursive_attr(instance, campo)
                    data_transacao_formatada = campo.strftime("%d/%m/%Y") if campo else ""
                    linha_horizontal.append(data_transacao_formatada)
                    continue

                if campo == "valor_total":
                    campo = get_recursive_attr(instance, campo)
                    valor_total_formatado = str(campo).replace(".", ",") if campo is not None else ''
                    linha_horizontal.append(valor_total_formatado)
                    continue
                    
                if campo == "valor_original":
                    campo = get_recursive_attr(instance, campo)
                    valor_original_formatado = str(campo).replace(".", ",") if campo is not None else ''
                    linha_horizontal.append(valor_original_formatado)
                    continue
                    
                if campo == "valor_recursos_proprios":
                    campo = get_recursive_attr(instance, campo)
                    valor_recursos_proprios_formatado = str(campo).replace(".", ",") if campo is not None else ''
                    linha_horizontal.append(valor_recursos_proprios_formatado)
                    continue

                if campo == "data_documento":
                    campo = get_recursive_attr(instance, campo)
                    data_documento_formatada = campo.strftime("%d/%m/%Y") if campo else ""
                    linha_horizontal.append(data_documento_formatada)
                    continue

                if campo == "numero_boletim_de_ocorrencia":
                    campo = get_recursive_attr(instance, campo)
                    linha_horizontal.append(campo if campo else "")
                    continue

                if campo == "retem_imposto":
                    campo = get_recursive_attr(instance, campo)
                    linha_horizontal.append("Sim" if campo else "Não")
                    continue

                if campo == "saida_recurso_externo":
                    campo = instance.valor_recursos_proprios > 0
                    linha_horizontal.append("Sim" if campo else "Não")
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

                if campo == "motivos":
                    if len(instance.outros_motivos_pagamento_antecipado) > 0:
                        motivos.append(instance.outros_motivos_pagamento_antecipado)
                    linha_horizontal.append('')
                    continue

                if campo == "uuid":
                    campo = get_recursive_attr(instance, campo)
                    linha_horizontal.append(str(campo))
                    continue

                campo = get_recursive_attr(instance, campo)
                linha_horizontal.append(campo)
            
            if len(motivos) > 0:
                for motivo in motivos:
                    linha_nova = linha_horizontal.copy()
                    linha_nova[19] = str(motivo)
                    logger.info(f"Escrevendo linha {linha_nova} de despesas, despesa id: {instance.id}.")
                    linhas_vertical.append(linha_nova)
            else:
                logger.info(f"Escrevendo linha {linha_horizontal} de despesas, despesa id: {instance.id}.")
                linhas_vertical.append(linha_horizontal)
            
            logger.info(f"Finalizando extração de dados de despesas, despesa id: {instance.id}.")

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