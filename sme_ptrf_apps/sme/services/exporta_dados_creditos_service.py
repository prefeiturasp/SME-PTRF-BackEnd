import csv
import datetime, time
import logging

from tempfile import NamedTemporaryFile
from typing import BinaryIO

from django.utils.timezone import make_aware
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
from sme_ptrf_apps.core.models.ambiente import Ambiente


CABECALHO_RECEITA = [
        ('Código EOL', 'associacao__unidade__codigo_eol'),
        ('Nome Unidade', 'associacao__unidade__nome'),
        ('Nome Associação', 'associacao__nome'),
        ('DRE', 'associacao__unidade__dre__nome'),
        ('ID do crédito', 'id'),
        ('Data do crédito', 'data'),
        ('Valor do crédito', 'valor'),
        ('ID da Conta Associação', 'conta_associacao__id'),
        ('ID do tipo de Conta', 'conta_associacao__tipo_conta__id'),
        ('Nome do tipo de Conta', 'conta_associacao__tipo_conta__nome'),
        ('ID da Ação Associação', 'acao_associacao__id'),
        ('ID da Ação', 'acao_associacao__acao__id'),
        ('Nome da Ação', 'acao_associacao__acao__nome'),
        ('ID do tipo de receita', 'tipo_receita__id'),
        ('Nome do tipo de receita', 'tipo_receita__nome'),
        ('ID da categoria de receita', 'categoria_receita'),
        ('Nome da categoria de receita', (APLICACAO_NOMES, 'categoria_receita')),
        ('ID do detalhe de tipo de receita', 'detalhe_tipo_receita__id'),
        ('Nome do detalhe de tipo de receita', 'detalhe_tipo_receita__nome'),
        ('Detalhe (outros)', 'detalhe_outros'),
        ('ID do período de devolução ao tesouro', 'referencia_devolucao__id'),
        ('Referência do Período da Prestação de contas da devolução ao tesouro', 'referencia_devolucao__referencia'),
        ('ID da despesa referente a saída de recurso externo', 'saida_do_recurso__id'),
        ('ID da despesa estornada (no caso de estorno)', 'rateio_estornado__id'),
        ('Motivos para estorno (no caso de estorno)', 'outros_motivos_estorno'),
        ('Data e hora de criação do registro', 'criado_em'),
        ('Data e hora da última atualização do registro', 'alterado_em'),
        ('Data e hora de inativação', 'data_e_hora_de_inativacao'),
        ('Status do crédito', 'status'),
        ('UUID do crédito', 'uuid'),
    ],
CABECALHO_MOTIVOS_ESTORNO = [
        ('ID do crédito (estorno)', ('id', 'motivos_estorno')),
        ('ID do motivo de estorno', 'id'),
        ('Descrição do motivo de estorno', 'motivo')
    ],


logger = logging.getLogger(__name__)


def get_informacoes_download(data_inicio, data_final):
    """
    Retorna uma string com as informações do download conforme a data de início e final de extração.
    """

    data_inicio = datetime.datetime.strptime(data_inicio, "%Y-%m-%d").strftime("%d/%m/%Y") if data_inicio else None
    data_final = datetime.datetime.strptime(data_final, "%Y-%m-%d").strftime("%d/%m/%Y") if data_final else None

    if data_inicio and data_final:
        return f"Filtro aplicado: {data_inicio} a {data_final} (data de criação do registro)"

    if data_inicio and not data_final:
        return f"Filtro aplicado: A partir de {data_inicio} (data de criação do registro)"

    if data_final and not data_inicio:
        return f"Filtro aplicado: Até {data_final} (data de criação do registro)"

    return ""


class ExportacoesDadosCreditosService:

    def __init__(self, **kwargs) -> None:
        self.queryset = kwargs.get('queryset', None)
        self.data_inicio = kwargs.get('data_inicio', None)
        self.data_final = kwargs.get('data_final', None)
        self.nome_arquivo = kwargs.get('nome_arquivo', None)
        self.user = kwargs.get('user', None)
        self.objeto_arquivo_download = None
        self.ambiente = self.get_ambiente

    @property
    def get_ambiente(self):
        ambiente = Ambiente.objects.first()
        return ambiente.prefixo if ambiente else ""

    def exporta_creditos_principal(self):
        self.cria_registro_central_download()
        self.cabecalho = CABECALHO_RECEITA[0]
        self.filtra_range_data('criado_em')
        self.exporta_credito_csv()

    def cria_rodape(self, write):
        rodape = []
        texto_info_arquivo_gerado = self.texto_info_arquivo_gerado()

        rodape.append(" ")
        write.writerow(rodape)
        rodape.clear()

        rodape.append(texto_info_arquivo_gerado)
        write.writerow(rodape)
        rodape.clear()

        rodape.append(get_informacoes_download(self.data_inicio, self.data_final))
        write.writerow(rodape)
        rodape.clear()

    def texto_info_arquivo_gerado(self):
        data_hora_geracao = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
        texto = f"Arquivo gerado via {self.ambiente} pelo usuário {self.user} em {data_hora_geracao}"

        return texto

    def exporta_creditos_motivos_estorno(self):
        self.cria_registro_central_download()
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

                motivos = list(instance.motivos_estorno.all())

                for _, campo in self.cabecalho:
                    # Removendo ponto e vírgula e substituindo por vírgula
                    if campo == "associacao__unidade__nome":
                        campo = get_recursive_attr(instance, campo)
                        linha.append(campo.replace(";", ",") if campo else "")
                        continue

                    if campo == 'associacao__nome':
                        campo = get_recursive_attr(instance, campo)
                        linha.append(campo.replace(";", ",") if campo else "")
                        continue

                    if campo == "associacao__unidade__dre__nome":
                        campo = get_recursive_attr(instance, campo)
                        linha.append(campo.replace(";", ",") if campo else "")
                        continue

                    if campo == "conta_associacao__tipo_conta__nome":
                        campo = get_recursive_attr(instance, campo)
                        linha.append(campo.replace(";", ",") if campo else "")
                        continue

                    if campo == "acao_associacao__acao__nome":
                        campo = get_recursive_attr(instance, campo)
                        linha.append(campo.replace(";", ",") if campo else "")
                        continue

                    if campo == "tipo_receita__nome":
                        campo = get_recursive_attr(instance, campo)
                        linha.append(campo.replace(";", ",") if campo else "")
                        continue

                    if campo == "detalhe_tipo_receita__nome":
                        campo = get_recursive_attr(instance, campo)
                        linha.append(campo.replace(";", ",") if campo else "")
                        continue

                    if campo == "detalhe_outros":
                        campo = get_recursive_attr(instance, campo)
                        linha.append(campo.replace(";", ",") if campo else "")
                        continue

                    if campo == 'data':
                        campo = getattr(instance, campo)
                        linha.append(datetime.datetime.strftime(campo, "%d/%m/%Y"))

                    elif campo == 'valor':
                        campo = str(getattr(instance, campo)).replace(".", ",")
                        linha.append(campo)

                    elif campo == 'outros_motivos_estorno':
                        motivo_string = '; '.join(str(motivo) for motivo in motivos)
                        if(len(motivo_string)):
                            motivo_string = motivo_string + '; ' + instance.outros_motivos_estorno
                        elif(len(instance.outros_motivos_estorno)):
                            motivo_string = instance.outros_motivos_estorno
                        linha.append(motivo_string.replace(";", ","))

                    elif isinstance(campo, tuple) and campo[1] == 'categoria_receita':
                        linha.append(campo[0][getattr(instance, campo[1])])

                    elif type(campo) == tuple and getattr(instance, campo[1]).__class__.__name__ == 'ManyRelatedManager':
                        for instance_m2m in getattr(instance, campo[1]).all():
                            linha.append(getattr(instance, campo[0]))
                            linha.append(getattr(instance_m2m, self.cabecalho[1][1]))

                            motivo_estorno_descricao = getattr(instance_m2m, self.cabecalho[2][1])
                            linha.append(motivo_estorno_descricao.replace(";", ",") if motivo_estorno_descricao else "")
                            write.writerow(linha)
                            linha.clear()

                    elif self.cabecalho != CABECALHO_MOTIVOS_ESTORNO[0]:
                        linha.append(get_recursive_attr(instance, campo))

                logger.info(f"Escrevendo linha {linha} do crédito {instance.id}.")
                write.writerow(linha) if linha else None
                linha.clear()

            self.cria_rodape(write)

            self.envia_arquivo_central_download(tmp)

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
        logger.info(f"Criando registro na central de download")

        obj = gerar_arquivo_download(
            self.user,
            self.nome_arquivo,
            informacoes=get_informacoes_download(self.data_inicio, self.data_final)
        )
        self.objeto_arquivo_download = obj

    def envia_arquivo_central_download(self, tmp) -> None:
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
