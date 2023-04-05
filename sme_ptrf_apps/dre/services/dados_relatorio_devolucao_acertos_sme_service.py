
from datetime import datetime

import logging

logger = logging.getLogger(__name__)


class DadosRelatorioDevolucaoAcertosSme:

    def __init__(self, analise_consolidado, previa, username):
        self.analise_consolidado = analise_consolidado
        self.previa = previa
        self.username = username
        self.consolidado_dre = analise_consolidado.consolidado_dre

        self.info_cabecalho = self.__info_cabecalho()
        self.dados_dre = self.__dados_dre()
        self.dados_documentos = self.__dados_documentos()
        self.dados_comentarios = self.__dados_comentarios()
        self.dados_responsavel_analise = self.__dados_responsavel_analise()
        self.blocos = self.__blocos()
        self.info_rodape = self.__info_rodape()

        self.__set_dados_relatorio()


    def __info_cabecalho(self):
        info_cabecalho = {
            'periodo_referencia': self.consolidado_dre.periodo.referencia,
            'data_inicio_periodo': self.consolidado_dre.periodo.data_inicio_realizacao_despesas,
            'data_fim_periodo': self.consolidado_dre.periodo.data_fim_realizacao_despesas,
            'tipo_relatorio': self.consolidado_dre.referencia
        }

        return info_cabecalho


    def __dados_dre(self):
        dados_dre = {
            'nome_dre': self.__formata_nome(self.consolidado_dre.dre),
            'cnpj': self.consolidado_dre.dre.dre_cnpj,
            'data_devolucao_sme': self.__get_data_devolucao_sme(self.analise_consolidado),
            'prazo_devolucao_dre': self.__get_prazo_devolucao_dre(self.analise_consolidado)
        }

        return dados_dre


    def __dados_documentos(self):
        lista_documentos = self.consolidado_dre.documentos_detalhamento(self.analise_consolidado)
        lista_documentos_com_ajustes = [documento for documento in lista_documentos
                                        if documento['analise_documento_consolidado_dre']['resultado'] == "AJUSTE"]

        return lista_documentos_com_ajustes


    def __dados_comentarios(self):
        comentarios = self.consolidado_dre.comentarios_de_analise_do_consolidado_dre.filter(
            notificado=True).order_by('ordem')

        return comentarios

    def __dados_responsavel_analise(self):
        responsavel = self.consolidado_dre.responsavel_pela_analise.name

        return responsavel

    def __blocos(self):
        dados = {}
        numero_bloco = 1

        dados[f'identificacao_dre'] = f'Bloco {numero_bloco} - Identificação da DRE'

        if self.dados_documentos:
            numero_bloco = numero_bloco + 1
            dados[f'acertos_documentos'] = f'Bloco {numero_bloco} - Acertos nos documentos'

        if self.dados_comentarios:
            numero_bloco = numero_bloco + 1
            dados[f"comentarios"] = f'Bloco {numero_bloco} - Comentários notificados'

        if self.dados_responsavel_analise:
            numero_bloco = numero_bloco + 1
            dados[f"responsavel"] = f'Bloco {numero_bloco} - Responsável pela Análise'

        return dados


    def __info_rodape(self):
        data_geracao = datetime.now().strftime("%d/%m/%Y às %H:%M")
        tipo_texto = "Prévia gerada" if self.previa else "Documento final gerado"
        quem_gerou = "" if self.username == "" else f"pelo usuário {self.username}"

        texto = f"SME, {tipo_texto} {quem_gerou}, via SIG_ESCOLA, em {data_geracao}."

        return texto


    @staticmethod
    def __get_data_devolucao_sme(analise_consolidado):
        if analise_consolidado.data_devolucao:
            return analise_consolidado.data_devolucao
        else:
            return "-"

    @staticmethod
    def __get_prazo_devolucao_dre(analise_consolidado):
        if analise_consolidado.data_limite:
            date_limite = datetime.strptime(analise_consolidado.data_limite, '%Y-%m-%d').date()
            return date_limite
        else:
            return "-"

    @staticmethod
    def __formata_nome(dre):
        if dre:
            nome_dre = dre.nome.upper()
            if "DIRETORIA REGIONAL DE EDUCACAO" in nome_dre:
                nome_dre = nome_dre.replace("DIRETORIA REGIONAL DE EDUCACAO", "")
                nome_dre = nome_dre.strip()
                return nome_dre
            else:
                return nome_dre
        else:
            return ""


    # Metodo principal
    def __set_dados_relatorio(self):
        self.dados_relatorio = {
            'info_cabecalho': self.info_cabecalho,
            'dados_dre': self.dados_dre,
            'dados_documentos': self.dados_documentos,
            'dados_comentarios': self.dados_comentarios,
            'dados_responsavel_analise': self.dados_responsavel_analise,
            'blocos': self.blocos,
            'info_rodape': self.info_rodape
        }



class DadosRelatorioDevolucaoAcertosSmeService:

    @classmethod
    def dados_relatorio_devolucao_acerto(cls, analise_consolidado, previa, username):
        return DadosRelatorioDevolucaoAcertosSme(
            analise_consolidado=analise_consolidado, previa=previa, username=username
        ).dados_relatorio
