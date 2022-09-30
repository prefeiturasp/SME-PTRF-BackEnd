from sme_ptrf_apps.core.services.prestacao_contas_services import (lancamentos_da_prestacao)
from ..api.serializers.analise_documento_prestacao_conta_serializer import AnaliseDocumentoPrestacaoContaRetrieveSerializer
from datetime import date
from ...utils.numero_ordinal import formata_numero_ordinal
from sme_ptrf_apps.core.models import TipoAcertoLancamento
from datetime import datetime

import logging

logger = logging.getLogger(__name__)


class DadosRelatorioAposAcertos:
    def __init__(self, analise_prestacao_conta, previa, usuario):
        self.categoria_devolucao = TipoAcertoLancamento.CATEGORIA_DEVOLUCAO

        self.analise_prestacao_conta = analise_prestacao_conta
        self.previa = previa
        self.usuario = usuario

        self.info_cabecalho = self.__info_cabecalho()
        self.dados_associacao = self.__dados_associacao()
        self.dados_lancamentos = self.__dados_lancamentos()
        self.dados_documentos = self.__dados_documentos()
        self.blocos = self.__blocos()
        self.rodape = self.__rodape()

        self.__set_dados_relatorio()

    def __info_cabecalho(self):
        info_cabecalho = {
            'periodo_referencia': self.analise_prestacao_conta.prestacao_conta.periodo.referencia,
            'data_inicio_periodo': self.analise_prestacao_conta.prestacao_conta.periodo.data_inicio_realizacao_despesas,
            'data_fim_periodo': self.analise_prestacao_conta.prestacao_conta.periodo.data_fim_realizacao_despesas
        }

        return info_cabecalho

    def __dados_associacao(self):
        dados_associacao = {
            'nome_associacao': self.analise_prestacao_conta.prestacao_conta.associacao.nome,
            'cnpj_associacao': self.analise_prestacao_conta.prestacao_conta.associacao.cnpj,
            'codigo_eol_associacao': self.analise_prestacao_conta.prestacao_conta.associacao.unidade.codigo_eol,
            'nome_dre': self.__formata_nome(self.analise_prestacao_conta.prestacao_conta.associacao),
            'data_devolucao_dre': self.__get_data_devolucao_dre(self.analise_prestacao_conta),
            'prazo_devolucao_associacao': self.__get_prazo_devolucao_associacao(self.analise_prestacao_conta)
        }

        return dados_associacao

    def __dados_lancamentos(self):
        dados_lancamentos = []

        for conta in self.analise_prestacao_conta.prestacao_conta.associacao.contas.all():
            lancamentos = lancamentos_da_prestacao(
                analise_prestacao_conta=self.analise_prestacao_conta,
                conta_associacao=conta,
                com_ajustes=True
            )

            if lancamentos:
                dados = {
                    'nome_conta': conta.tipo_conta.nome,
                    'lancamentos': lancamentos
                }

                dados_lancamentos.append(dados)

        return dados_lancamentos

    def __dados_documentos(self):
        documentos = self.analise_prestacao_conta.analises_de_documento.filter(resultado='AJUSTE').all().order_by(
            'tipo_documento_prestacao_conta__nome')
        dados_documentos = AnaliseDocumentoPrestacaoContaRetrieveSerializer(documentos, many=True).data

        return dados_documentos

    def __blocos(self):
        dados = {}
        numero_bloco = 1

        dados[f'identificacao_associacao'] = f'Bloco {numero_bloco} - Identificação da Associação da Unidade Educacional'

        if self.dados_lancamentos:
            numero_bloco = numero_bloco + 1
            dados[f'acertos_lancamentos'] = f'Bloco {numero_bloco} - Acertos nos lançamentos'

        if self.dados_documentos:
            numero_bloco = numero_bloco + 1
            dados[f'acertos_documentos'] = f'Bloco {numero_bloco} - Acertos nos documentos'

        return dados

    def __rodape(self):
        associacao = self.analise_prestacao_conta.prestacao_conta.associacao
        data_geracao = datetime.now().strftime("%d/%m/%Y ás %H:%M")
        tipo_texto = "Prévia gerada" if self.previa else "Documento gerado"
        quem_gerou = "" if self.usuario == "" else f"pelo usuário {self.usuario}"

        texto = f"{associacao.nome}, {tipo_texto} {quem_gerou}, via SIG_ESCOLA em {data_geracao}."

        return texto

    @staticmethod
    def __formata_nome(associacao):
        if associacao.unidade.dre:
            nome_dre = associacao.unidade.dre.nome.upper()
            if "DIRETORIA REGIONAL DE EDUCACAO" in nome_dre:
                nome_dre = nome_dre.replace("DIRETORIA REGIONAL DE EDUCACAO", "")
                nome_dre = nome_dre.strip()
                return nome_dre
            else:
                return nome_dre
        else:
            return ""

    @staticmethod
    def __get_data_devolucao_dre(analise_prestacao_conta):
        if analise_prestacao_conta.devolucao_prestacao_conta:
            return analise_prestacao_conta.devolucao_prestacao_conta.data
        else:
            return "-"

    @staticmethod
    def __get_prazo_devolucao_associacao(analise_prestacao_conta):
        if analise_prestacao_conta.devolucao_prestacao_conta:
            return analise_prestacao_conta.devolucao_prestacao_conta.data_limite_ue
        else:
            return "-"

    # Metodo principakl
    def __set_dados_relatorio(self):
        self.dados_relatorio = {
            'categoria_devolucao': self.categoria_devolucao,
            'info_cabecalho': self.info_cabecalho,
            'dados_associacao': self.dados_associacao,
            'dados_lancamentos': self.dados_lancamentos,
            'dados_documentos': self.dados_documentos,
            'blocos': self.blocos,
            'rodape': self.rodape
        }


class DadosRelatorioAposAcertosService:

    @classmethod
    def dados_relatorio_apos_acerto(cls, analise_prestacao_conta, previa, usuario):
        return DadosRelatorioAposAcertos(
            analise_prestacao_conta=analise_prestacao_conta, previa=previa, usuario=usuario
        ).dados_relatorio
