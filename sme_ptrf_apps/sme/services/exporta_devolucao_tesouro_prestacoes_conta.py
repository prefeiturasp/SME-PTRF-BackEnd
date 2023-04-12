import csv
import logging
from datetime import datetime
from django.core.files import File
from sme_ptrf_apps.core.models.ambiente import Ambiente
from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload
from sme_ptrf_apps.core.models.solicitacao_acerto_lancamento import SolicitacaoAcertoLancamento
from sme_ptrf_apps.core.services.arquivo_download_service import (
    gerar_arquivo_download
)
from sme_ptrf_apps.utils.built_in_custom import get_recursive_attr

from tempfile import NamedTemporaryFile

logger = logging.getLogger(__name__)

CABECALHO = [
        ('Código EOL', 'prestacao_conta__associacao__unidade__codigo_eol'),
        ('Nome Unidade', 'prestacao_conta__associacao__unidade__nome'),
        ('Nome Associação', 'prestacao_conta__associacao__nome'),
        ('Referência do Período da PC', 'prestacao_conta__periodo__referencia'),
        ('Status da PC', 'prestacao_conta__status'),
        ('ID da despesa','despesa__id'),
        ('Número do documento','despesa__numero_documento'),
        ('Tipo do documento', 'despesa__tipo_documento__nome'),
        ('Data do documento', 'despesa__data_documento'),
        ('CPF_CNPJ do fornecedor', 'despesa__cpf_cnpj_fornecedor'),
        ('Nome do fornecedor', 'despesa__nome_fornecedor'),
        ('Tipo de transação', 'despesa__tipo_transacao__nome'),
        ('Número do documento da transação', 'despesa__documento_transacao'),
        ('Data da transação', 'despesa__data_transacao'),
        ('Valor (Despeza)', 'despesa__valor_original'),
        ('Valor realizado (Despesa)', 'despesa__valor_total'),
        ('Tipo de aplicação do recurso', 'aplicacao_recurso'),
        ('Nome do Tipo de Custeio','tipo_custeio'),
        ('Descrição da especificação de Material ou Serviço','desc_material_serv'),
        ('Nome do tipo de Conta','nome_tipo_conta'),
        ('Nome da Ação','nome_acao'),
        ('Valor (Rateios)','valor_rateio'),
        ('Valor realizado (Rateio)','valor_realizado'),
        ('Tipo de devolução','tipo__id'),
        ('Descrição do Tipo de devolução','tipo__nome'),
        ('Motivo','motivo'),
        ('É devolução total?','devolucao_total'),
        ('Valor (Devolução)','valor'),
        ('Data de devolução ao tesouro','data'),
    ],


class ExportacoesDevolucaoTesouroPrestacoesContaService:
    
    def __init__(self, **kwargs):
        self.queryset = kwargs.get('queryset', None)
        self.data_inicio = kwargs.get('data_inicio', None)
        self.data_final = kwargs.get('data_final', None)
        self.nome_arquivo = kwargs.get('nome_arquivo', None)
        self.user = kwargs.get('user', None)
        self.cabecalho = CABECALHO[0]
        self.ambiente = self.get_ambiente

    @property 
    def get_ambiente(self): 
        ambiente = Ambiente.objects.first() 
        return ambiente.prefixo if ambiente else ""

    def exporta_devolucao_tesouro_pc(self):
        self.filtra_range_data('criado_em')
        self.exporta_devolucao_tesouro_pc()

    def exporta_devolucao_tesouro_pc(self):
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
            linha_horizontal = []
            rateios = list(instance.despesa.rateios.all())

            for _, campo in self.cabecalho:

                if campo == 'aplicacao_recurso' or campo == 'tipo_custeio' or campo == 'desc_material_serv' or campo == 'nome_tipo_conta' or campo == 'nome_acao' or campo == 'valor_rateio' or campo == 'valor_realizado':
                    linha_horizontal.append('')
                elif campo == 'despesa__data_documento':
                    campo = get_recursive_attr(instance, campo)
                    data_doc_formatado = campo.strftime("%d/%m/%Y")
                    linha_horizontal.append(data_doc_formatado)
                elif campo == 'despesa__data_transacao':
                    campo = get_recursive_attr(instance, campo)
                    data_tran_formatado = campo.strftime("%d/%m/%Y")
                    linha_horizontal.append(data_tran_formatado)
                elif campo == 'data':
                    campo = get_recursive_attr(instance, campo)
                    data_formatado = campo.strftime("%d/%m/%Y")
                    linha_horizontal.append(data_formatado)
                elif campo == 'despesa__valor_original':
                    campo = get_recursive_attr(instance, campo)
                    valor_original_formatado = str(campo).replace(".", ",")
                    linha_horizontal.append(valor_original_formatado)
                elif campo == 'despesa__valor_total':
                    campo = get_recursive_attr(instance, campo)
                    valor_total_formatado = str(campo).replace(".", ",")
                    linha_horizontal.append(valor_total_formatado)
                elif campo == 'valor':
                    campo = get_recursive_attr(instance, campo)
                    valor_formatado = str(campo).replace(".", ",")
                    linha_horizontal.append(valor_formatado)
                elif campo == 'devolucao_total':
                    campo = get_recursive_attr(instance, campo)
                    linha_horizontal.append('Sim' if campo else 'Não')
                else:
                    campo = get_recursive_attr(instance, campo)
                    linha_horizontal.append(campo)

            if len(rateios) > 0:
                for rateio in rateios:
                    linha_nova = linha_horizontal.copy()
                    linha_nova[16] = rateio.aplicacao_recurso if rateio.aplicacao_recurso else ''
                    linha_nova[17] = rateio.tipo_custeio.nome if rateio.tipo_custeio else ''
                    linha_nova[18] = rateio.especificacao_material_servico.descricao if rateio.especificacao_material_servico else ''
                    linha_nova[19] = rateio.conta_associacao.tipo_conta.nome if rateio.conta_associacao else ''
                    linha_nova[20] = rateio.acao_associacao.acao.nome if rateio.acao_associacao else ''
                    linha_nova[21] = str(rateio.valor_rateio).replace(".", ",") if rateio.valor_rateio else ''
                    linha_nova[22] = str(rateio.valor_original).replace(".", ",") if rateio.valor_original else ''
                    
                    logger.info(f"Escrevendo linha {linha_nova} de status de prestação de conta de custeio {instance.id}.")
                    linhas_vertical.append(linha_nova)
            else:
                logger.info(f"Escrevendo linha {linha_horizontal} de status de prestação de conta de custeio {instance.id}.")
                linhas_vertical.append(linha_horizontal) 

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
    
    def envia_arquivo_central_download(self, tmp):
        logger.info("Gerando arquivo download...")
        obj_arquivo_download = gerar_arquivo_download(
            self.user,
            self.nome_arquivo
        )

        try:
            logger.info("Salvando arquivo download...")
            obj_arquivo_download.arquivo.save(
                name=obj_arquivo_download.identificador,
                content=File(tmp)
            )
            obj_arquivo_download.status = ArquivoDownload.STATUS_CONCLUIDO
            obj_arquivo_download.save()
            logger.info("Arquivo salvo com sucesso...")

        except Exception as e:
            obj_arquivo_download.status = ArquivoDownload.STATUS_ERRO
            obj_arquivo_download.msg_erro = str(e)
            obj_arquivo_download.save()
            logger.error("Erro arquivo download...")

    def texto_rodape(self):
        data_hora_geracao = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
        texto = f"Arquivo gerado pelo {self.ambiente} em {data_hora_geracao}"

        return texto

    def cria_rodape(self, write):
        rodape = []
        texto = self.texto_rodape()

        write.writerow([])
        rodape.append(texto)
        write.writerow(rodape)
        rodape.clear()
        