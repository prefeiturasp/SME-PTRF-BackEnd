import csv
import logging
from datetime import datetime
from django.core.files import File
from sme_ptrf_apps.core.models.ambiente import Ambiente
from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload
from sme_ptrf_apps.core.services.arquivo_download_service import (
    gerar_arquivo_download
)
from sme_ptrf_apps.utils.built_in_custom import get_recursive_attr

from tempfile import NamedTemporaryFile

logger = logging.getLogger(__name__)

CABECALHO = [
        ('Código EOL', 'associacao__unidade__codigo_eol'),
        ('Nome Unidade', 'associacao__unidade__nome'),
        ('Nome Associação', 'associacao__nome'),
        ('Referência do Período da PC', 'periodo__referencia'),
        ('Status da PC', 'status'),
        ('Descrição do motivo aprovação com ressalvas', 'motivos_aprovacao_ressalva'),
        ('Recomendações da aprovação com resalvas', 'recomendacoes'),
        ('Descrição do motivo de reprovação', 'motivos_reprovacao'),
    ],

class ExportacoesStatusPrestacoesContaService:
    
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

    def exporta_status_prestacoes_conta(self):
        self.filtra_range_data('criado_em')
        self.exporta_status_prestacoes_conta_csv()

    def exporta_status_prestacoes_conta_csv(self):
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

            status = ''
            motivos = []

            for _, campo in self.cabecalho:

                if campo != 'motivos_reprovacao' and campo != 'motivos_aprovacao_ressalva':
                    campo = get_recursive_attr(instance, campo)
                    linha_horizontal.append(campo)
                elif campo == 'motivos_aprovacao_ressalva' or campo == 'motivos_reprovacao':
                    linha_horizontal.append('')

                if campo == 'motivos_aprovacao_ressalva' and getattr(instance, 'status') == 'APROVADA_RESSALVA':
                    status = 'APROVADA_RESSALVA'
                    motivosAprovacaoRessalva = instance.motivos_aprovacao_ressalva.values_list('motivo', flat=True)
                    if len(motivosAprovacaoRessalva) > 0:
                        for motivoAprovacaoRessalva in motivosAprovacaoRessalva:
                            motivos.append(motivoAprovacaoRessalva) 
                        
                    outros_motivos = getattr(instance, 'outros_motivos_aprovacao_ressalva')
                    if outros_motivos.strip():
                        motivos.append(outros_motivos)

                if campo == 'motivos_reprovacao' and getattr(instance, 'status') == 'REPROVADA':
                    status = 'REPROVADA'
                    motivosReprovacao = instance.motivos_reprovacao.values_list('motivo', flat=True)
                    if len(motivosReprovacao) > 0:
                        for motivoReprovacao in motivosReprovacao:
                            motivos.append(motivoReprovacao)

                    outros_motivos = getattr(instance, 'outros_motivos_reprovacao')
                    if outros_motivos.strip():
                        motivos.append(outros_motivos)
                    
            if len(motivos) > 0:
                for motivo in motivos:
                    linha_nova = linha_horizontal.copy()
                    if status == 'APROVADA_RESSALVA':
                        linha_nova[5] = motivo
                    else:
                        linha_nova[7] = motivo
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
        