import csv
import logging
import datetime

from text_unidecode import unidecode

from brazilnum.cnpj import validate_cnpj, format_cnpj

from ..models import AcaoAssociacao, Associacao, Acao
from ..models.arquivo import (
    DELIMITADOR_PONTO_VIRGULA,
    DELIMITADOR_VIRGULA,
    SUCESSO,
    ERRO,
    PROCESSADO_COM_ERRO)

from sme_ptrf_apps.users.services.sme_integracao_service import SmeIntegracaoService

from sme_ptrf_apps.core.choices.tipos_unidade import TIPOS_CHOICE

logger = logging.getLogger(__name__)


class CargaAcoesAssociacaoException(Exception):
    pass


class CargaAcoesAssociacoesService:
    __EOL = 0
    __ACAO = 1
    __STATUS = 2

    __CABECALHOS = {
        __EOL: "Código EOL",
        __ACAO: "Ação",
        __STATUS: "Status",
    }

    __DELIMITADORES = {',': DELIMITADOR_VIRGULA, ';': DELIMITADOR_PONTO_VIRGULA}

    __logs = ""
    __importados = 0
    __erros = 0

    __dados_acao_associacao = None
    __linha_index = 0

    def inicializa_log(self):
        self.__logs = ""
        self.__importados = 0
        self.__erros = 0

    def loga_erro_carga_acao_associacao(self, mensagem_erro, linha=0):
        mensagem = f'Linha:{linha} {mensagem_erro}'
        logger.error(mensagem)
        self.__logs = f"{self.__logs}\n{mensagem}"
        self.__erros += 1

    def loga_sucesso_carga_acao_associacao(self):
        mensagem = f'Ação de associação {self.__dados_acao_associacao["eol_unidade"]} criado/atualizado com sucesso.'
        logger.info(mensagem)
        self.__importados += 1

    def carrega_e_valida_dados_acao_associacao(self, linha_conteudo, linha_index):
        logger.info('Linha %s: %s', linha_index, linha_conteudo)

        eol_unidade = linha_conteudo[self.__EOL].strip()
        acao = linha_conteudo[self.__ACAO].strip()
        status = linha_conteudo[self.__STATUS].strip()

        self.__linha_index = linha_index

        self.__dados_acao_associacao = {
            'eol_unidade': eol_unidade,
            'acao': acao,
            'status': status,
            'associacao_obj': None,
            'acao_obj': None,
        }

        return self.__dados_acao_associacao

    def atualiza_status_arquivo(self, arquivo):
        if self.__importados > 0 and self.__erros > 0:
            arquivo.status = PROCESSADO_COM_ERRO
        elif self.__importados == 0:
            arquivo.status = ERRO
        else:
            arquivo.status = SUCESSO

        resultado = f"{self.__importados} linha(s) importada(s) com sucesso. {self.__erros} erro(s) reportado(s)."
        self.__logs = f"{self.__logs}\n{resultado}"
        logger.info(resultado)

        arquivo.log = self.__logs
        arquivo.save()

    @classmethod
    def verifica_estrutura_cabecalho(cls, cabecalho):
        estrutura_correta = True
        for coluna, nome in cls.__CABECALHOS.items():
            titulo_coluna_arquivo = unidecode(cabecalho[coluna])
            titulo_coluna_modelo = unidecode(nome)
            if titulo_coluna_arquivo != titulo_coluna_modelo:
                msg_erro = (f'Título da coluna {coluna} errado. Encontrado "{cabecalho[coluna]}". '
                            f'Deveria ser "{nome}". Confira o arquivo com o modelo.')
                raise CargaAcoesAssociacaoException(msg_erro)

        return estrutura_correta

    def cria_ou_atualiza_acao_associacao(self):
        acao_associacao, created = AcaoAssociacao.objects.get_or_create(
            associacao=self.__dados_acao_associacao['associacao_obj'],
            acao=self.__dados_acao_associacao['acao_obj'],
            defaults={
                'status': self.__dados_acao_associacao['status']
            },
        )

        if created:
            logger.info(f'Criada Ação de Associacao {str(acao_associacao)}')
        else:
            if acao_associacao.status != self.__dados_acao_associacao['status']:
                acao_associacao.status = self.__dados_acao_associacao['status']
                acao_associacao.save()
            else:
                raise CargaAcoesAssociacaoException("A ação já foi criada para a unidade educacional")


        return acao_associacao
    
    def valida_codigo_eol_e_associacao(self):
        eol = self.__dados_acao_associacao["eol_unidade"]
        associacao = Associacao.objects.filter(unidade__codigo_eol=eol).first()
        if not associacao:
            raise CargaAcoesAssociacaoException("Código EOL não existe")
        self.__dados_acao_associacao["associacao_obj"] = associacao
    
    def valida_acao(self):
        acao_nome = self.__dados_acao_associacao["acao"]
        acao = Acao.objects.filter(nome__iexact=acao_nome).first()
        if not acao:
            raise CargaAcoesAssociacaoException("Ação não existe")
        self.__dados_acao_associacao["acao_obj"] = acao
    
    def valida_status(self):
        status = self.__dados_acao_associacao["status"]
        if not AcaoAssociacao.STATUS_NOMES.get(status.upper()):
            raise CargaAcoesAssociacaoException(f"Status {status} inválido")
        self.__dados_acao_associacao["status"] = status.upper()

    def processa_acoes_associacoes(self, reader, arquivo):
        self.inicializa_log()
        try:
            for index, linha in enumerate(reader):
                if index == 0:
                    self.verifica_estrutura_cabecalho(cabecalho=linha)
                    continue
                try:
                    self.carrega_e_valida_dados_acao_associacao(linha_conteudo=linha, linha_index=index)
                    self.valida_codigo_eol_e_associacao()
                    self.valida_acao()
                    self.valida_status()
                    acao_associacao = self.cria_ou_atualiza_acao_associacao()
                    if acao_associacao:
                        self.loga_sucesso_carga_acao_associacao()
                except Exception as e:
                    self.loga_erro_carga_acao_associacao(f'Houve um erro na carga dessa linha: {str(e)}', index)
                    continue

            self.atualiza_status_arquivo(arquivo)

        except Exception as e:
            self.loga_erro_carga_acao_associacao(str(e))
            self.atualiza_status_arquivo(arquivo)

    def carrega_acoes_associacoes(self, arquivo):
        logger.info("Processando arquivo %s", arquivo.identificador)
        arquivo.ultima_execucao = datetime.datetime.now()
        try:
            with open(arquivo.conteudo.path, 'r', encoding="utf-8") as f:
                sniffer = csv.Sniffer().sniff(f.readline())
                f.seek(0)
                if self.__DELIMITADORES[sniffer.delimiter] != arquivo.tipo_delimitador:
                    msg_erro = (f"Formato definido ({arquivo.tipo_delimitador}) é diferente do formato "
                                f"do arquivo csv ({self.__DELIMITADORES[sniffer.delimiter]})")
                    self.loga_erro_carga_acao_associacao(msg_erro)
                    self.atualiza_status_arquivo(arquivo)
                    return

                reader = csv.reader(f, delimiter=sniffer.delimiter)
                self.processa_acoes_associacoes(reader, arquivo)

        except Exception as err:
            self.loga_erro_carga_acao_associacao(f"Erro ao processar associações: {str(err)}")
            self.atualiza_status_arquivo(arquivo)
