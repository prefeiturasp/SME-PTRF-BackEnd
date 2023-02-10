import csv
import logging
from datetime import datetime

from text_unidecode import unidecode


from sme_ptrf_apps.despesas.models import Despesa
from sme_ptrf_apps.core.models import (
    TipoDevolucaoAoTesouro,
    PrestacaoConta,
    SolicitacaoAcertoLancamento,
    DevolucaoAoTesouro,
    SolicitacaoDevolucaoAoTesouro
)

from ..models.arquivo import (
    DELIMITADOR_PONTO_VIRGULA,
    DELIMITADOR_VIRGULA,
    SUCESSO,
    ERRO,
    PROCESSADO_COM_ERRO)

logger = logging.getLogger(__name__)


class CargaDevolcuoesTesouroException(Exception):
    pass


class CargaDevolucoesTesouroService:
    EOL_UE = 0
    NOME_ASSOCIACAO = 1
    PC_ID = 2
    PERIODO_REF = 3
    DESPESA_ID = 4
    NUMERO_DOC = 5
    DATA_DEVOLUCAO = 6
    VALOR_DEVOLUCAO = 7
    TIPO_DEVOLUCAO_NOME = 8

    CABECALHOS = {
        EOL_UE: "codigo_eol",
        NOME_ASSOCIACAO: "nome",
        PC_ID: "pc_id",
        PERIODO_REF: "referencia",
        DESPESA_ID: "despesa_id",
        NUMERO_DOC: "numero_documento",
        DATA_DEVOLUCAO: "data_devolucao",
        VALOR_DEVOLUCAO: "valor_devolucao",
        TIPO_DEVOLUCAO_NOME: "tipo_devolucao",
    }

    DELIMITADORES = {',': DELIMITADOR_VIRGULA, ';': DELIMITADOR_PONTO_VIRGULA}

    logs = ""
    importados = 0
    erros = 0

    linha_index = 0

    def __init__(self):
        self.dados_devolucao = {}

    def inicializa_log(self):
        self.logs = ""
        self.importados = 0
        self.erros = 0

    def loga_erro_carga_devolucao(self, mensagem_erro, linha=0):
        mensagem = f'Linha:{linha} {mensagem_erro}'
        logger.error(mensagem)
        self.logs = f"{self.logs}\n{mensagem}"
        self.erros += 1

    def loga_sucesso_carga_devolucao(self):
        mensagem = f'Devolução ao tesouro Eol:{self.dados_devolucao["prestacao_conta"].associacao.unidade.codigo_eol} PC:{self.dados_devolucao["prestacao_conta"].periodo.referencia} criado/atualizado com sucesso.'
        logger.info(mensagem)
        self.importados += 1

    def carrega_e_valida_dados_devolucao(self, linha_conteudo, linha_index):
        logger.info('Linha %s: %s', linha_index, linha_conteudo)

        # Define a Prestação de Contas
        try:
            pc_id = int(linha_conteudo[self.PC_ID].strip())
        except ValueError:
            raise CargaDevolcuoesTesouroException(f'O id da PC {linha_conteudo[self.PC_ID].strip()} é inválido. Devolução não criada.')

        try:
            prestacao_conta = PrestacaoConta.objects.get(id=pc_id)
        except PrestacaoConta.DoesNotExist:
            raise CargaDevolcuoesTesouroException(f'Não encontrada uma PC de id {pc_id}. Devolução não criada.')

        # Define a Despesa
        try:
            despesa_id = int(linha_conteudo[self.DESPESA_ID].strip())
        except ValueError:
            raise CargaDevolcuoesTesouroException(f'O id de despesa {linha_conteudo[self.DESPESA_ID].strip()} é inválido. Devolução não criada.')

        try:
            despesa = Despesa.objects.get(id=despesa_id)
        except Despesa.DoesNotExist:
            raise CargaDevolcuoesTesouroException(f'Não encontrada uma despesa de id {despesa_id}. Devolução não criada.')

        # Define a Data e Valor da Devolução ao tesouro
        try:
            if str(linha_conteudo[self.DATA_DEVOLUCAO]).strip(" "):
                data_devolucao = datetime.strptime(str(linha_conteudo[self.DATA_DEVOLUCAO]).strip(" "), '%d/%m/%Y')
            else:
                data_devolucao = None
        except Exception:
            raise CargaDevolcuoesTesouroException(f'A data de devolução {linha_conteudo[self.DATA_DEVOLUCAO].strip()} é inválida. Devolução não criada.')

        try:
            valor_devolucao = float(str(linha_conteudo[self.VALOR_DEVOLUCAO].strip()).replace(',', '.'))
        except Exception:
            raise CargaDevolcuoesTesouroException(f'O valor da devolução {linha_conteudo[self.VALOR_DEVOLUCAO].strip()} é inválido. Devolução não criada.')

        # Define o tipo de devolução
        tipo_devolucao_nome = linha_conteudo[self.TIPO_DEVOLUCAO_NOME].strip()
        tipo_devolucao = TipoDevolucaoAoTesouro.objects.filter(nome=tipo_devolucao_nome).first()
        if not tipo_devolucao:
            raise CargaDevolcuoesTesouroException(
                f'Não encontrado tipo de devolução com o nome {tipo_devolucao_nome}. Devolução não criada.')

        # Verifica se já existe uma devolução ao tesouro para a PC e Despesa
        devolucao_existente = DevolucaoAoTesouro.objects.filter(
            prestacao_conta=prestacao_conta,
            despesa=despesa,
        ).first()

        if devolucao_existente:
            raise CargaDevolcuoesTesouroException(
                f'Devolução ao Tesouro já existe id {devolucao_existente.id}. Devolução não criada.')

        # Define as solicitações de devolução
        solicitacoes = SolicitacaoAcertoLancamento.objects.filter(
            analise_lancamento__analise_prestacao_conta__prestacao_conta=prestacao_conta,
            analise_lancamento__despesa=despesa,
            tipo_acerto__categoria="DEVOLUCAO"
        ).order_by('id').all()

        if not solicitacoes:
            raise CargaDevolcuoesTesouroException(
                f'Solicitação de acerto não encontrada pc: {prestacao_conta.id} despesa: {despesa}. Devolução não criada.')

        # Verifica se já existem solicitações de devolução ao tesouro criadas para as solicitações de acerto
        for solicitacao in solicitacoes:
            if hasattr(solicitacao, 'solicitacao_devolucao_ao_tesouro'):
                raise CargaDevolcuoesTesouroException(
                    f'Já existe uma solicitação de devolução ao tesouro para a solicitação de acerto {solicitacao.id}. Solicitação de devolução não criada.')

        self.linha_index = linha_index

        self.dados_devolucao = {
            'prestacao_conta': prestacao_conta,
            'despesa': despesa,
            'data_devolucao': data_devolucao,
            'valor_devolucao': valor_devolucao,
            'tipo_devolucao': tipo_devolucao,
            'solicitacoes_acerto_lancamento': solicitacoes,
        }

        return self.dados_devolucao

    def cria_devolucao_ao_tesouro_e_atualiza_solicitacao(self):

        devolucao_ao_tesouro = None
        if self.dados_devolucao['data_devolucao']:
            # Cria a devolução ao tesouro apenas se a data de devolução for informada
            devolucao_ao_tesouro = DevolucaoAoTesouro.objects.create(
                prestacao_conta=self.dados_devolucao['prestacao_conta'],
                tipo=self.dados_devolucao['tipo_devolucao'],
                data=self.dados_devolucao['data_devolucao'],
                despesa=self.dados_devolucao['despesa'],
                valor=self.dados_devolucao['valor_devolucao'],
                motivo="*recuperado",
                visao_criacao="DRE",
                devolucao_total=self.dados_devolucao['valor_devolucao'] == self.dados_devolucao['despesa'].valor_total
            )

        for solicitacao in self.dados_devolucao['solicitacoes_acerto_lancamento']:
            solicitacao.devolucao_ao_tesouro = devolucao_ao_tesouro
            solicitacao.save()

            SolicitacaoDevolucaoAoTesouro.objects.create(
                solicitacao_acerto_lancamento=solicitacao,
                tipo=self.dados_devolucao['tipo_devolucao'],
                devolucao_total=self.dados_devolucao['valor_devolucao'] == self.dados_devolucao['despesa'].valor_total,
                valor=self.dados_devolucao['valor_devolucao'],
                motivo="*recuperado",
            )

    def atualiza_status_arquivo(self, arquivo):
        if self.importados > 0 and self.erros > 0:
            arquivo.status = PROCESSADO_COM_ERRO
        elif self.importados == 0:
            arquivo.status = ERRO
        else:
            arquivo.status = SUCESSO

        resultado = f"{self.importados} linha(s) importada(s) com sucesso. {self.erros} erro(s) reportado(s)."
        self.logs = f"{self.logs}\n{resultado}"
        logger.info(resultado)

        arquivo.log = self.logs
        arquivo.save()

    @classmethod
    def verifica_estrutura_cabecalho(cls, cabecalho):
        estrutura_correta = True
        for coluna, nome in cls.CABECALHOS.items():
            titulo_coluna_arquivo = unidecode(cabecalho[coluna])
            titulo_coluna_modelo = unidecode(nome)
            if titulo_coluna_arquivo != titulo_coluna_modelo:
                msg_erro = (f'Título da coluna {coluna} errado. Encontrado "{cabecalho[coluna]}". '
                            f'Deveria ser "{nome}". Confira o arquivo com o modelo.')
                raise CargaDevolcuoesTesouroException(msg_erro)

        return estrutura_correta

    def processa_devolucoes(self, reader, arquivo):
        self.inicializa_log()

        try:
            for index, linha in enumerate(reader):
                if index == 0:
                    self.verifica_estrutura_cabecalho(cabecalho=linha)
                    continue

                try:
                    self.carrega_e_valida_dados_devolucao(linha_conteudo=linha, linha_index=index)

                    self.cria_devolucao_ao_tesouro_e_atualiza_solicitacao()

                    self.loga_sucesso_carga_devolucao()

                except Exception as e:
                    self.loga_erro_carga_devolucao(f'Houve um erro na carga dessa linha:{str(e)}', index)
                    continue

            self.atualiza_status_arquivo(arquivo)

        except Exception as e:
            self.loga_erro_carga_devolucao(str(e))
            self.atualiza_status_arquivo(arquivo)

    def carrega_devolucoes_tesouro(self, arquivo):
        logger.info("Processando arquivo %s", arquivo.identificador)
        arquivo.ultima_execucao = datetime.now()

        try:
            with open(arquivo.conteudo.path, 'r', encoding="utf-8") as f:
                sniffer = csv.Sniffer().sniff(f.readline())
                f.seek(0)
                if self.DELIMITADORES[sniffer.delimiter] != arquivo.tipo_delimitador:
                    msg_erro = (f"Formato definido ({arquivo.tipo_delimitador}) é diferente do formato "
                                f"do arquivo csv ({self.DELIMITADORES[sniffer.delimiter]})")
                    self.loga_erro_carga_devolucao(msg_erro)
                    self.atualiza_status_arquivo(arquivo)
                    return

                reader = csv.reader(f, delimiter=sniffer.delimiter)
                self.processa_devolucoes(reader, arquivo)

        except Exception as err:
            self.loga_erro_carga_devolucao(f"Erro ao processar devoluções ao tesouro: {str(err)}")
            self.atualiza_status_arquivo(arquivo)
