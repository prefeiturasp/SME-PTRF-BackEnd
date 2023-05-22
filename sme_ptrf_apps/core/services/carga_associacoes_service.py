import csv
import logging
import datetime

from text_unidecode import unidecode

from brazilnum.cnpj import validate_cnpj, format_cnpj

from ..models import Associacao, Unidade
from ..models.arquivo import (
    DELIMITADOR_PONTO_VIRGULA,
    DELIMITADOR_VIRGULA,
    SUCESSO,
    ERRO,
    PROCESSADO_COM_ERRO)

from sme_ptrf_apps.users.services.sme_integracao_service import SmeIntegracaoService

from sme_ptrf_apps.core.choices.tipos_unidade import TIPOS_CHOICE

logger = logging.getLogger(__name__)


class CargaAssociacaoException(Exception):
    pass


class CargaAssociacoesService:
    __EOL_UE = 0
    __NOME_ASSOCIACAO = 1
    __CNPJ_ASSOCIACAO = 2

    __CABECALHOS = {
        __EOL_UE: "Codigo EOL UE",
        __NOME_ASSOCIACAO: "Nome da associacao",
        __CNPJ_ASSOCIACAO: "CNPJ da associacao",
    }

    __DELIMITADORES = {',': DELIMITADOR_VIRGULA, ';': DELIMITADOR_PONTO_VIRGULA}

    __logs = ""
    __importados = 0
    __erros = 0

    __dados_associacao = None
    __linha_index = 0

    def inicializa_log(self):
        self.__logs = ""
        self.__importados = 0
        self.__erros = 0

    def loga_erro_carga_associacao(self, mensagem_erro, linha=0):
        mensagem = f'Linha:{linha} {mensagem_erro}'
        logger.error(mensagem)
        self.__logs = f"{self.__logs}\n{mensagem}"
        self.__erros += 1

    def loga_sucesso_carga_associacao(self):
        mensagem = f'Associação {self.__dados_associacao["eol_unidade"]} criado/atualizado com sucesso.'
        logger.info(mensagem)
        self.__importados += 1

    def carrega_e_valida_dados_associacao(self, linha_conteudo, linha_index):
        logger.info('Linha %s: %s', linha_index, linha_conteudo)

        eol_unidade = linha_conteudo[self.__EOL_UE].strip()
        nome = linha_conteudo[self.__NOME_ASSOCIACAO].strip()
        cnpj = linha_conteudo[self.__CNPJ_ASSOCIACAO].strip()

        if cnpj and not validate_cnpj(cnpj):
            raise CargaAssociacaoException(f'CNPJ inválido ({cnpj}). Associação não criada.')

        cnpj = format_cnpj(cnpj) if cnpj else ""

        self.__linha_index = linha_index

        self.__dados_associacao = {
            'eol_unidade': eol_unidade,
            'nome': nome,
            'cnpj': cnpj,
            'tipo_unidade': "",
            'ue_obj': None,
            'associacao-obj': None,
        }

        return self.__dados_associacao

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
                raise CargaAssociacaoException(msg_erro)

        return estrutura_correta

    @staticmethod
    def cria_ou_atualiza_dre(dados_dre):

        dre, created = Unidade.objects.update_or_create(
            codigo_eol=dados_dre["codigoDRE"],
            defaults={
                'tipo_unidade': 'DRE',
                'dre': None,
                'sigla': dados_dre["siglaDRE"][-2],
                'nome': dados_dre["nomeDRE"]
            },
        )
        if created:
            logger.info(f'Criada DRE {dre.nome}')

        return dre

    @staticmethod
    def cria_ou_atualiza_ue(codigo_eol, dados_ue):

        ue, created = Unidade.objects.update_or_create(
            codigo_eol=codigo_eol,
            defaults=dados_ue,
        )
        if created:
            logger.info(f'Criada Unidade {ue.nome}')

        return ue

    def get_dados_dre_e_ue_da_api_eol(self):
        dados_dre = None
        dados_ue = None
        try:
            result_api_eol = SmeIntegracaoService.get_dados_unidade_eol(codigo_eol=self.__dados_associacao['eol_unidade'])
            result_api_eol = result_api_eol.json()
            if result_api_eol:

                dados_dre = {
                    'codigoDRE': result_api_eol["codigoDRE"].strip(),
                    'siglaDRE': result_api_eol["siglaDRE"].strip(),
                    'nomeDRE': result_api_eol["nomeDRE"].strip(),
                }

                if dados_dre["codigoDRE"] is None:
                    raise CargaAssociacaoException(
                        f"A API do EOL não retornou as informações da DRE da UE {self.__dados_associacao['eol_unidade']}.")

                dados_ue = {
                    'nome': result_api_eol.get('nome').strip() if result_api_eol.get('nome') else '',
                    'email': result_api_eol.get('email') or '',
                    'telefone': result_api_eol.get('telefone').strip()[:20] if result_api_eol.get('telefone') else '',
                    'numero': result_api_eol.get('numero').strip() if result_api_eol.get('numero') else '',
                    'tipo_logradouro': result_api_eol.get('tipoLogradouro').strip() if result_api_eol.get('tipoLogradouro') else '',
                    'logradouro': result_api_eol.get('logradouro').strip() if result_api_eol.get('logradouro') else '',
                    'bairro': result_api_eol.get('bairro').strip() if result_api_eol.get('bairro') else '',
                    'cep': f"{result_api_eol['cep']:0>8}" or '',
                    'tipo_unidade': result_api_eol.get('siglaTipoEscola').strip() if result_api_eol.get('siglaTipoEscola') else 'CEU'
                }
            else:
                raise CargaAssociacaoException(
                    f"API não retornou dados para a unidade {self.__dados_associacao['eol_unidade']}.")

        except Exception as err:
            logger.info("Erro ao Atualizar dados pessoais da unidade %s", err)

        if (dados_ue['tipo_unidade'], dados_ue['tipo_unidade']) not in TIPOS_CHOICE:
            msg_erro = f'Tipo de unidade inválido ({dados_ue["tipo_unidade"]}) na linha {self.__linha_index}. Trocado para EMEF.'
            self.loga_erro_carga_associacao(mensagem_erro=msg_erro, linha=self.__linha_index)
            dados_ue['tipo_unidade'] = 'EMEF'

        return dados_dre, dados_ue

    def cria_ou_atualiza_ue_e_dre(self):

        dados_dre, dados_ue = self.get_dados_dre_e_ue_da_api_eol()

        dados_ue['dre'] = self.cria_ou_atualiza_dre(dados_dre=dados_dre)

        self.__dados_associacao['ue_obj'] = self.cria_ou_atualiza_ue(
            codigo_eol=self.__dados_associacao['eol_unidade'],
            dados_ue=dados_ue
        )

    def cria_ou_atualiza_associacao(self):

        associacao, created = Associacao.objects.get_or_create(
            cnpj=self.__dados_associacao['cnpj'],
            defaults={
                'unidade': self.__dados_associacao['ue_obj'],
                'nome': self.__dados_associacao['nome'],
            },
        )

        if created:
            logger.info(f'Criada Associacao {associacao.nome}')
        else:
            if associacao.encerrada:
                msg_erro = f'A associação foi encerrada em {associacao.data_de_encerramento.strftime("%d/%m/%Y")}.'
                self.loga_erro_carga_associacao(mensagem_erro=msg_erro, linha=self.__linha_index)
                return None
            else:
                associacao.unidade = self.__dados_associacao['ue_obj']
                associacao.nome = self.__dados_associacao['nome']
                associacao.save()

        self.__dados_associacao['associacao_obj'] = associacao

        return associacao

    def processa_associacoes(self, reader, arquivo):
        self.inicializa_log()

        try:
            for index, linha in enumerate(reader):
                if index == 0:
                    self.verifica_estrutura_cabecalho(cabecalho=linha)
                    continue

                try:
                    self.carrega_e_valida_dados_associacao(linha_conteudo=linha, linha_index=index)
                    self.cria_ou_atualiza_ue_e_dre()
                    associacao = self.cria_ou_atualiza_associacao()
                    if associacao:
                        self.loga_sucesso_carga_associacao()
                except Exception as e:
                    self.loga_erro_carga_associacao(f'Houve um erro na carga dessa linha:{str(e)}', index)
                    continue

            self.atualiza_status_arquivo(arquivo)

        except Exception as e:
            self.loga_erro_carga_associacao(str(e))
            self.atualiza_status_arquivo(arquivo)

    def carrega_associacoes(self, arquivo):
        logger.info("Processando arquivo %s", arquivo.identificador)
        arquivo.ultima_execucao = datetime.datetime.now()

        try:
            with open(arquivo.conteudo.path, 'r', encoding="utf-8") as f:
                sniffer = csv.Sniffer().sniff(f.readline())
                f.seek(0)
                if self.__DELIMITADORES[sniffer.delimiter] != arquivo.tipo_delimitador:
                    msg_erro = (f"Formato definido ({arquivo.tipo_delimitador}) é diferente do formato "
                                f"do arquivo csv ({self.__DELIMITADORES[sniffer.delimiter]})")
                    self.loga_erro_carga_associacao(msg_erro)
                    self.atualiza_status_arquivo(arquivo)
                    return

                reader = csv.reader(f, delimiter=sniffer.delimiter)
                self.processa_associacoes(reader, arquivo)

        except Exception as err:
            self.loga_erro_carga_associacao(f"Erro ao processar associações: {str(err)}")
            self.atualiza_status_arquivo(arquivo)
