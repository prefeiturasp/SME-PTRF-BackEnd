import csv
import datetime
import logging

from django.core.files import File
from django.db.models import QuerySet
from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload
from sme_ptrf_apps.core.services.arquivo_download_service import (
    gerar_arquivo_download
)
from sme_ptrf_apps.receitas.tipos_aplicacao_recurso_receitas import (
    APLICACAO_NOMES
)
from sme_ptrf_apps.utils.built_in_custom import get_recursive_attr
from tempfile import NamedTemporaryFile
from typing import BinaryIO


CABECALHO_RECEITA = [
        ('Código EOL', 'associacao__unidade__codigo_eol'),
        ('Nome Unidade', 'associacao__unidade__nome'),
        ('Nome Associação', 'associacao__nome'),
        ('ID do crédito', 'id'),
        ('Data do crédito', 'data'),
        ('Valor do crédito', 'valor'),
        ('ID da Conta Associação', 'associacao__id'),
        ('ID do tipo de Conta', 'conta_associacao__tipo_conta__id'),
        ('Nome do tipo de Conta', 'conta_associacao__tipo_conta__nome'),
        ('ID da Ação Associação', 'acao_associacao__id'),
        ('ID da Ação', 'acao_associacao__acao__id'),
        ('Nome da Ação', 'acao_associacao__acao__nome'),
        ('ID do tipo de receita', 'tipo_receita__id'),
        ('Nome do tipo de receita', 'tipo_receita__nome'),
        ('ID da categoria de receita', 'tipo_receita__id'),
        ('Nome da categoria de receita', 'tipo_receita__nome'),
        ('ID do detalhe de tipo de receita', 'categoria_receita'),
        ('Nome do detalhe de tipo de receita', (APLICACAO_NOMES, 'categoria_receita')),
        ('Detalhe (outros)', 'tipo_receita__id'),
        ('ID do período de devolução ao tesouro', 'tipo_receita__nome'),
        ('Referência do Período da Prestação de contas da devolução ao tesouro', 'referencia_devolucao__referencia'),
        ('ID da despesa referente a saída de recurso externo', 'saida_do_recurso__id'),
        ('ID da despesa estornada (no caso de estorno)', 'rateio_estornado__id'),
        ('Outros motivos para estorno (no caso de estorno)', 'outros_motivos_estorno'),
        ('Data e hora de criação do registro', 'criado_em'),
        ('Data e hora da última atualização do registro', 'alterado_em'),
        ('UUID do crédito', 'uuid'),
    ],
CABECALHO_MOTIVOS_ESTORNO = [
        ('ID do crédito (estorno)', ('id', 'motivos_estorno')),
        ('ID do motivo de estorno', 'id'),
        ('Descrição do motivo de estorno', 'motivo')
    ],


logger = logging.getLogger(__name__)


class ExportacoesDadosCreditosService:

    def __init__(self, **kwargs) -> None:
        self.queryset = kwargs.get('queryset', None)
        self.data_inicio = kwargs.get('data_inicio', None)
        self.data_final = kwargs.get('data_final', None)
        self.nome_arquivo = kwargs.get('nome_arquivo', None)
        self.user = kwargs.get('user', None)

    def exporta_creditos_principal(self):
        self.cabecalho = CABECALHO_RECEITA[0]
        self.filtra_range_data('data')
        self.exporta_credito_csv()

    def exporta_creditos_motivos_estorno(self):
        self.cabecalho = CABECALHO_MOTIVOS_ESTORNO[0]
        self.filtra_range_data('data')
        self.exporta_credito_csv()

    def exporta_credito_csv(self) -> BinaryIO:
        linha = []
        with NamedTemporaryFile(
            mode="r+",
            newline='',
            encoding='utf-8',
            prefix=self.nome_arquivo,
            suffix='.csv'
        ) as tmp:
            write = csv.writer(tmp.file, delimiter=";")
            write.writerow([cabecalho[0] for cabecalho in self.cabecalho])

            for instance in self.queryset:
                for _, campo in self.cabecalho:

                    if campo == 'data':
                        campo = getattr(instance, campo)
                        linha.append(datetime.datetime.strftime(campo, "%d/%m/%Y"))

                    elif campo == 'valor':
                        campo = str(getattr(instance, campo)).replace(".", ",")
                        linha.append(campo)

                    elif isinstance(campo, tuple) and campo[1] == 'categoria_receita':
                        linha.append(campo[0][getattr(instance, campo[1])])

                    elif type(campo) == tuple and getattr(instance, campo[1]).__class__.__name__ == 'ManyRelatedManager':
                        for instance_m2m in getattr(instance, campo[1]).all():
                            linha.append(getattr(instance, campo[0]))
                            linha.append(getattr(instance_m2m, self.cabecalho[1][1]))
                            linha.append(getattr(instance_m2m, self.cabecalho[2][1]))
                            write.writerow(linha)
                            linha.clear()

                    elif self.cabecalho != CABECALHO_MOTIVOS_ESTORNO[0]:
                        linha.append(get_recursive_attr(instance, campo))

                logger.info(f"Escrevendo linha {linha} do crédito {instance.id}.")
                write.writerow(linha) if linha else None
                linha.clear()
            self.envia_arquivo_central_download(tmp)

    def filtra_range_data(self, field) -> QuerySet:
        if self.data_inicio and self.data_final:
            self.queryset = self.queryset.filter(
                **{f'{field}__range': [self.data_inicio, self.data_final]}
            )
        elif self.data_inicio and not self.data_final:
            self.queryset = self.queryset.filter(
                **{f'{field}__gt': self.data_inicio}
            )
        elif self.data_final and not self.data_inicio:
            self.queryset = self.queryset.filter(
                **{f'{field}__lt': self.data_final}
            )
        return self.queryset

    def envia_arquivo_central_download(self, tmp) -> None:
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
