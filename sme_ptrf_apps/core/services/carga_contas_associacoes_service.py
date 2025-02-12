import csv
import logging
import datetime

from text_unidecode import unidecode

from ..models import Associacao, ContaAssociacao, TipoConta
from ..models.arquivo import (
    DELIMITADOR_PONTO_VIRGULA,
    DELIMITADOR_VIRGULA,
    SUCESSO,
    ERRO,
    PROCESSADO_COM_ERRO)

logger = logging.getLogger(__name__)


class CargaContaAssociacaoException(Exception):
    pass


class CargaContasAssociacoesService:
    __EOL_UE = 0
    __TIPO_CONTA = 1
    __STATUS = 2
    __BANCO = 3
    __AGENCIA = 4
    __CONTA = 5
    __CARTAO = 6
    __DATA_INICIO = 7

    __CABECALHOS = {
        __EOL_UE: "Código eol",
        __TIPO_CONTA: "Tipo de conta",
        __STATUS: "Status",
        __BANCO: "Nome do banco",
        __AGENCIA: "N° da agência",
        __CONTA: "N° da conta",
        __CARTAO: "N° Cartão",
        __DATA_INICIO: "Data de início da conta"
    }

    __DELIMITADORES = {',': DELIMITADOR_VIRGULA, ';': DELIMITADOR_PONTO_VIRGULA}

    __logs = ""
    __importados = 0
    __erros = 0

    __dados_conta_associacao = None
    __linha_index = 0

    def inicializa_log(self):
        self.__logs = ""
        self.__importados = 0
        self.__erros = 0

    def loga_erro_carga_conta_associacao(self, mensagem_erro, linha=0):
        mensagem = f'Linha {linha}: {mensagem_erro}'
        logger.error(mensagem)
        self.__logs = f"{self.__logs}\n{mensagem}"
        self.__erros += 1

    def loga_sucesso_carga_conta_associacao(self):
        mensagem = f'Conta de Associação {self.__dados_conta_associacao["eol_unidade"]} criado/atualizado com sucesso.'
        logger.info(mensagem)
        self.__importados += 1

    def carrega_e_valida_dados_conta_associacao(self, linha_conteudo, linha_index):
        logger.info('Linha %s: %s', linha_index, linha_conteudo)
        self.__linha_index = linha_index

        def _strip(value):
            return (value or '').strip()

        eol_unidade = _strip(linha_conteudo[self.__EOL_UE])
        tipo_conta = _strip(linha_conteudo[self.__TIPO_CONTA])
        status = _strip(linha_conteudo[self.__STATUS])
        banco_nome = _strip(linha_conteudo[self.__BANCO])
        agencia = _strip(linha_conteudo[self.__AGENCIA])
        numero_conta = _strip(linha_conteudo[self.__CONTA])
        numero_cartao = _strip(linha_conteudo[self.__CARTAO])
        data_inicio = _strip(linha_conteudo[self.__DATA_INICIO])

        self.__dados_conta_associacao = {
            'eol_unidade': eol_unidade,
            'tipo_conta': tipo_conta,
            'status': status,
            'banco_nome': banco_nome,
            'agencia': agencia,
            'numero_conta': numero_conta,
            'numero_cartao': numero_cartao,
            'data_inicio': data_inicio,
        }

        return self.__dados_conta_associacao

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
                raise CargaContaAssociacaoException(msg_erro)
        return estrutura_correta

    def valida_formato_data(self, data_str):
        data_obj = datetime.datetime.strptime(data_str, "%d/%m/%Y")
        data_model = data_obj.strftime("%Y-%m-%d")
        return data_model

    def valida_codigo_eol(self):
        codigo_eol = self.__dados_conta_associacao['eol_unidade']
        if not codigo_eol:
            msg_erro = f'Coluna {self.__CABECALHOS.get(self.__EOL_UE)} preenchimento obrigatório.'
            self.loga_erro_carga_conta_associacao(mensagem_erro=msg_erro, linha=self.__linha_index)
            return None

        # Código EOL (validar se o código EOL existe e está ativo).
        # Exibir mensagem de erro: Código EOL não existe.
        associacao = Associacao.objects.filter(unidade__codigo_eol=codigo_eol).first()
        if not associacao:
            msg_erro = f'{self.__CABECALHOS.get(self.__EOL_UE)} não existe: {codigo_eol}.'
            self.loga_erro_carga_conta_associacao(mensagem_erro=msg_erro, linha=self.__linha_index)
            return None

        self.__dados_conta_associacao['associacao'] = associacao

        return associacao

    def valida_tipo_conta(self):
        # Tipo de conta (validar se a conta informada consta no cadastro de tipos de conta).
        # Exibir mensagem de erro: Tipo de conta não existe.
        tipo_conta = self.__dados_conta_associacao['tipo_conta']
        if not tipo_conta:
            msg_erro = f'Coluna {self.__CABECALHOS.get(self.__TIPO_CONTA)} preenchimento obrigatório.'
            self.loga_erro_carga_conta_associacao(mensagem_erro=msg_erro, linha=self.__linha_index)
            return None

        model_tipo_conta = TipoConta.objects.filter(nome=tipo_conta).first()
        if not model_tipo_conta:
            msg_erro = f'{self.__CABECALHOS.get(self.__TIPO_CONTA)} {tipo_conta} não existe.'
            self.loga_erro_carga_conta_associacao(mensagem_erro=msg_erro, linha=self.__linha_index)
            return None

        self.__dados_conta_associacao['tipo_conta'] = model_tipo_conta

        return model_tipo_conta

    def valida_status(self):
        # Status (Ativa ou Inativa)
        status = self.__dados_conta_associacao['status']
        if not status:
            msg_erro = f'Coluna {self.__CABECALHOS.get(self.__STATUS)} preenchimento obrigatório.'
            self.loga_erro_carga_conta_associacao(mensagem_erro=msg_erro, linha=self.__linha_index)
            return None

        choices_values = [v for _, v in ContaAssociacao.STATUS_NOMES.items()]
        STATUS_NOMES_INVERTIDO = {v: k for k, v in ContaAssociacao.STATUS_NOMES.items()}
        if status not in choices_values:
            msg_erro = f'Status inválido: \"{status}\". As opções disponíveis são: {", ".join(choices_values)}. '
            self.loga_erro_carga_conta_associacao(mensagem_erro=msg_erro, linha=self.__linha_index)
            return None

        status = STATUS_NOMES_INVERTIDO.get(status)
        self.__dados_conta_associacao['status'] = status

        return status

    def valida_banco(self):
        status = self.__dados_conta_associacao['banco_nome']
        if not status:
            msg_erro = f'Coluna {self.__CABECALHOS.get(self.__STATUS)} preenchimento obrigatório.'
            self.loga_erro_carga_conta_associacao(mensagem_erro=msg_erro, linha=self.__linha_index)
            return None

        self.__dados_conta_associacao['banco_nome'] = status

        return status

    def valida_agencia(self):
        status = self.__dados_conta_associacao['agencia']
        if not status:
            msg_erro = f'Coluna {self.__CABECALHOS.get(self.__AGENCIA)} preenchimento obrigatório.'
            self.loga_erro_carga_conta_associacao(mensagem_erro=msg_erro, linha=self.__linha_index)
            return None

        self.__dados_conta_associacao['agencia'] = status

        return status

    def valida_numero_conta(self):
        status = self.__dados_conta_associacao['numero_conta']
        if not status:
            msg_erro = f'Coluna {self.__CABECALHOS.get(self.__CONTA)} preenchimento obrigatório.'
            self.loga_erro_carga_conta_associacao(mensagem_erro=msg_erro, linha=self.__linha_index)
            return None

        self.__dados_conta_associacao['numero_conta'] = status

        return status

    def valida_numero_cartao(self):
        status = self.__dados_conta_associacao['numero_cartao']
        if not status:
            msg_erro = f'Coluna {self.__CABECALHOS.get(self.__CARTAO)} preenchimento obrigatório.'
            self.loga_erro_carga_conta_associacao(mensagem_erro=msg_erro, linha=self.__linha_index)
            return None

        self.__dados_conta_associacao['numero_cartao'] = status

        return status

    def valida_data_inicio(self):
        # Data de início da conta (Validar o formato da data informada(Formato: DD/MM/AAAA).
        # Exibir mensagem de erro: Data informada fora do padrão.
        data_inicio = self.__dados_conta_associacao['data_inicio']
        if not data_inicio:
            msg_erro = f'Coluna {self.__CABECALHOS.get(self.__DATA_INICIO)} preenchimento obrigatório.'
            self.loga_erro_carga_conta_associacao(mensagem_erro=msg_erro, linha=self.__linha_index)
            return None

        try:
            data_inicio = self.valida_formato_data(data_inicio)
        except Exception:
            msg_erro = f'{self.__CABECALHOS.get(self.__DATA_INICIO)} informada fora do padrão (DD/MM/AAAA).'
            self.loga_erro_carga_conta_associacao(mensagem_erro=msg_erro, linha=self.__linha_index)
            return None
        self.__dados_conta_associacao['data_inicio'] = data_inicio

        return data_inicio

    def valida_campos(self):
        validacoes = (
            self.valida_codigo_eol,
            self.valida_tipo_conta,
            self.valida_status,
            self.valida_banco,
            self.valida_agencia,
            self.valida_numero_conta,
            self.valida_numero_cartao,
            self.valida_data_inicio,
        )

        for valida_campo in validacoes:
            if not valida_campo():
                return None
        return True

    def cria_ou_atualiza_conta_associacao(self):
        if not self.valida_campos():
            return None

        conta_associacao, created = ContaAssociacao.objects.get_or_create(
            associacao=self.__dados_conta_associacao['associacao'],
            tipo_conta=self.__dados_conta_associacao['tipo_conta'],
            status=self.__dados_conta_associacao['status'],
            defaults={
                'banco_nome': self.__dados_conta_associacao['banco_nome'],
                'agencia': self.__dados_conta_associacao['agencia'],
                'numero_conta': self.__dados_conta_associacao['numero_conta'],
                'data_inicio': self.__dados_conta_associacao['data_inicio'],
            },
        )

        if created:
            logger.info(f'Criada ContaAssociacao {conta_associacao.tipo_conta} - ' +
                        f'{conta_associacao.banco_nome} - {conta_associacao.agencia} - {conta_associacao.numero_conta}')
        else:
            conta_associacao.banco_nome = self.__dados_conta_associacao['banco_nome']
            conta_associacao.agencia = self.__dados_conta_associacao['agencia']
            conta_associacao.numero_conta = self.__dados_conta_associacao['numero_conta']
            conta_associacao.data_inicio = self.__dados_conta_associacao['data_inicio']
            conta_associacao.save()

        self.__dados_conta_associacao['conta_associacao_obj'] = conta_associacao

        return conta_associacao

    def processa_contas_associacoes(self, reader, arquivo):
        self.inicializa_log()
        try:
            self.processa_linhas(reader)
        except Exception as e:
            self.loga_erro_carga_conta_associacao(str(e))
        finally:
            self.atualiza_status_arquivo(arquivo)

    def processa_linhas(self, reader):
        for index, linha in enumerate(reader):
            if not linha:
                continue

            if index == 0:
                self.verifica_estrutura_cabecalho(cabecalho=linha)
                continue

            self.processa_linha_conteudo(linha, index)

    def processa_linha_conteudo(self, linha, index):
        try:
            self.carrega_e_valida_dados_conta_associacao(linha_conteudo=linha, linha_index=index)
            conta_associacao = self.cria_ou_atualiza_conta_associacao()
            if conta_associacao:
                self.loga_sucesso_carga_conta_associacao()
        except Exception as e:
            self.loga_erro_carga_conta_associacao(f'Houve um erro na carga dessa linha: {str(e)}', index)

    def carrega_contas_associacoes(self, arquivo):
        logger.info("Processando arquivo %s", arquivo.identificador)
        arquivo.ultima_execucao = datetime.datetime.now()

        try:
            with open(arquivo.conteudo.path, 'r', encoding="utf-8") as f:
                sniffer = csv.Sniffer().sniff(f.readline())
                f.seek(0)
                if self.__DELIMITADORES[sniffer.delimiter] != arquivo.tipo_delimitador:
                    msg_erro = (f"Formato definido ({arquivo.tipo_delimitador}) é diferente do formato "
                                f"do arquivo csv ({self.__DELIMITADORES[sniffer.delimiter]})")
                    self.loga_erro_carga_conta_associacao(msg_erro)
                    self.atualiza_status_arquivo(arquivo)
                    return

                reader = csv.reader(f, delimiter=sniffer.delimiter)
                self.processa_contas_associacoes(reader, arquivo)

        except Exception as err:
            self.loga_erro_carga_conta_associacao(f"Erro ao processar contas de associações: {str(err)}")
            self.atualiza_status_arquivo(arquivo)
