import csv
import logging
from datetime import datetime
from django.core.files import File
from sme_ptrf_apps.core.models.ambiente import Ambiente
from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload
from sme_ptrf_apps.core.models.devolucao_ao_tesouro import DevolucaoAoTesouro
from sme_ptrf_apps.core.models.solicitacao_acerto_lancamento import SolicitacaoAcertoLancamento
from sme_ptrf_apps.core.services.arquivo_download_service import (
    gerar_arquivo_download
)
from sme_ptrf_apps.utils.built_in_custom import get_recursive_attr

from tempfile import NamedTemporaryFile

logger = logging.getLogger(__name__)

CABECALHO = [
        ('Código EOL', 'solicitacao_acerto_lancamento__analise_lancamento__analise_prestacao_conta__prestacao_conta__associacao__unidade__codigo_eol'),
        ('Nome Unidade', 'solicitacao_acerto_lancamento__analise_lancamento__analise_prestacao_conta__prestacao_conta__associacao__unidade__nome'),
        ('Nome Associação', 'solicitacao_acerto_lancamento__analise_lancamento__analise_prestacao_conta__prestacao_conta__associacao__nome'),
        ('Referência do Período da PC', 'solicitacao_acerto_lancamento__analise_lancamento__analise_prestacao_conta__prestacao_conta__periodo__referencia'),
        ('Status da PC', 'solicitacao_acerto_lancamento__analise_lancamento__analise_prestacao_conta__prestacao_conta__status'),
        ('ID da despesa','solicitacao_acerto_lancamento__analise_lancamento__despesa__id'),
        ('Número do documento','solicitacao_acerto_lancamento__analise_lancamento__despesa__numero_documento'),
        ('Tipo do documento', 'solicitacao_acerto_lancamento__analise_lancamento__despesa__tipo_documento__nome'),
        ('Data do documento', 'solicitacao_acerto_lancamento__analise_lancamento__despesa__data_documento'),
        ('CPF_CNPJ do fornecedor', 'solicitacao_acerto_lancamento__analise_lancamento__despesa__cpf_cnpj_fornecedor'),
        ('Nome do fornecedor', 'solicitacao_acerto_lancamento__analise_lancamento__despesa__nome_fornecedor'),
        ('Tipo de transação', 'solicitacao_acerto_lancamento__analise_lancamento__despesa__tipo_transacao__nome'),
        ('Número do documento da transação', 'solicitacao_acerto_lancamento__analise_lancamento__despesa__documento_transacao'),
        ('Data da transação', 'solicitacao_acerto_lancamento__analise_lancamento__despesa__data_transacao'),
        ('Valor (Despeza)', 'solicitacao_acerto_lancamento__analise_lancamento__despesa__valor_original'),
        ('Valor realizado (Despesa)', 'solicitacao_acerto_lancamento__analise_lancamento__despesa__valor_total'),
        ('Tipo de aplicação do recurso', 'aplicacao_recurso'),
        ('Nome do Tipo de Custeio','tipo_custeio'),
        ('Descrição da especificação de Material ou Serviço','desc_material_serv'),
        ('Nome do tipo de Conta','nome_tipo_conta'),
        ('Nome da Ação','nome_acao'),
        ('Valor (Rateios)','valor_rateio'),
        ('Valor realizado (Rateio)','valor_realizado'),
        ('Tipo de devolução','tipo_id'),
        ('Descrição do Tipo de devolução','tipo_nome'),
        ('Motivo','motivo'),
        ('É devolução total?','devolucao_total'),
        ('Valor (Devolução)','valor'),
        ('Data de devolução ao tesouro','data'),
        ('Justificativa (não realização)','justificativa')
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
        self.objeto_arquivo_download = None

    @property 
    def get_ambiente(self): 
        ambiente = Ambiente.objects.first() 
        return ambiente.prefixo if ambiente else ""

    def exporta_devolucao_tesouro_pc(self):
        self.cria_registro_central_download()
        self.filtra_range_data('criado_em')
        self.exporta_devolucao_tesouro_pc_csv()

    def exporta_devolucao_tesouro_pc_csv(self):
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

            devolucao_ao_tesouro = DevolucaoAoTesouro.objects.filter(despesa_id=instance.solicitacao_acerto_lancamento.analise_lancamento.despesa.id).first()

            rateios = list(instance.solicitacao_acerto_lancamento.analise_lancamento.despesa.rateios.all())

            for _, campo in self.cabecalho:

                if campo == 'aplicacao_recurso' or campo == 'tipo_custeio' or campo == 'desc_material_serv' or campo == 'nome_tipo_conta' or campo == 'nome_acao' or campo == 'valor_rateio' or campo == 'valor_realizado':
                    linha_horizontal.append('')
                elif campo == 'solicitacao_acerto_lancamento__analise_lancamento__despesa__data_documento':
                    campo = get_recursive_attr(instance, campo)
                    data_doc_formatado = campo.strftime("%d/%m/%Y") if campo is not None else ''
                    linha_horizontal.append(data_doc_formatado)
                elif campo == 'solicitacao_acerto_lancamento__analise_lancamento__despesa__data_transacao':
                    campo = get_recursive_attr(instance, campo)
                    data_tran_formatado = campo.strftime("%d/%m/%Y") if campo is not None else ''
                    linha_horizontal.append(data_tran_formatado)
                elif campo == 'solicitacao_acerto_lancamento__analise_lancamento__despesa__valor_original':
                    campo = get_recursive_attr(instance, campo)
                    valor_original_formatado = str(campo).replace(".", ",") if campo is not None else ''
                    linha_horizontal.append(valor_original_formatado)
                elif campo == 'solicitacao_acerto_lancamento__analise_lancamento__despesa__valor_total':
                    campo = get_recursive_attr(instance, campo)
                    valor_total_formatado = str(campo).replace(".", ",") if campo is not None else ''
                    linha_horizontal.append(valor_total_formatado)
                elif campo == 'tipo_id':
                    linha_horizontal.append(devolucao_ao_tesouro.tipo.id if devolucao_ao_tesouro is not None else '')
                elif campo == 'tipo_nome':
                    linha_horizontal.append(devolucao_ao_tesouro.tipo.nome if devolucao_ao_tesouro is not None else '')
                elif campo == 'motivo':
                    linha_horizontal.append(devolucao_ao_tesouro.motivo if devolucao_ao_tesouro is not None else '')
                elif campo == 'devolucao_total':
                    if devolucao_ao_tesouro is not None:   
                        linha_horizontal.append('Sim' if devolucao_ao_tesouro.devolucao_total else 'Não')
                    else:
                        linha_horizontal.append('')
                elif campo == 'valor':
                    linha_horizontal.append(str(devolucao_ao_tesouro.valor).replace(".", ",") if devolucao_ao_tesouro is not None else '')
                elif campo == 'data':
                    data_formatada = devolucao_ao_tesouro.data.strftime("%d/%m/%Y") if devolucao_ao_tesouro is not None and devolucao_ao_tesouro.data is not None else ''
                    linha_horizontal.append(data_formatada)
                elif campo == 'justificativa':
                    linha_horizontal.append(instance.solicitacao_acerto_lancamento.justificativa if instance.solicitacao_acerto_lancamento.justificativa is not None else '')
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
    
    def cria_registro_central_download(self): 
        logger.info(f"Criando registro na central de download") 
        obj = gerar_arquivo_download( 
            self.user, 
            self.nome_arquivo ) 
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

        write.writerow([])
        rodape.append(texto)
        write.writerow(rodape)
        rodape.clear()
        