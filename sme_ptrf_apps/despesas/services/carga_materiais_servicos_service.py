import csv
import logging
from datetime import datetime

from text_unidecode import unidecode

from sme_ptrf_apps.despesas.models.especificacao_material_servico import EspecificacaoMaterialServico
from sme_ptrf_apps.despesas.models.tipo_custeio import TipoCusteio

from ...core.models.arquivo import (
    DELIMITADOR_PONTO_VIRGULA,
    DELIMITADOR_VIRGULA,
    SUCESSO,
    ERRO,
    PROCESSADO_COM_ERRO)

logger = logging.getLogger(__name__)

class CargaMateriaisServicosException(Exception):
    pass

class CargaMateriaisServicosService:
    ID = 0
    DESCRICAO = 1
    APLICACAO = 2
    ID_TIPO_CUSTEIO = 3
    ATIVA = 4

    CABECALHOS = {
        ID: "ID",
        DESCRICAO: "Descrição",
        APLICACAO: "Aplicação",
        ID_TIPO_CUSTEIO: "ID do tipo de Custeio",
        ATIVA: "Ativa"
    }

    DELIMITADORES = {',': DELIMITADOR_VIRGULA, ';': DELIMITADOR_PONTO_VIRGULA}

    logs = ""
    importados = 0
    erros = 0

    linha_index = 0

    def __init__(self):
        self.dados_materiais_servicos = {}

    
    def inicializa_log(self):
        self.logs = ""
        self.importados = 0
        self.erros = 0

    def loga_erro_carga_materiais_servicos(self, mensagem_erro, linha=0):
        mensagem = f'Linha: {linha} Erro: {mensagem_erro}'
        logger.error(mensagem)
        self.logs = f"{self.logs}\n{mensagem}"
        self.erros += 1

    def loga_sucesso_carga_materiais_servicos(self):
        mensagem = f'Registro de especificação de material e serviço criado/atualizado com sucesso.'
        logger.info(mensagem)
        self.importados += 1

    def carrega_e_valida_dados_tipo_custeio(self, linha_conteudo, linha_index):
        try:
            if linha_conteudo[self.ID_TIPO_CUSTEIO].strip():
                id_tipo_custeio = int(linha_conteudo[self.ID_TIPO_CUSTEIO].strip())

                TipoCusteio.objects.get(id=id_tipo_custeio)
        except TipoCusteio.DoesNotExist:
            raise CargaMateriaisServicosException(f'O id do tipo de custeio {linha_conteudo[self.ID_TIPO_CUSTEIO].strip()} é inválido. Registro de material/serviço não criado.')
        
        
        if linha_conteudo[self.APLICACAO].strip() == 'CUSTEIO' and not linha_conteudo[self.ID_TIPO_CUSTEIO].strip():
            raise CargaMateriaisServicosException(f'Aplicação de custeio está sem o campo ID preenchido. Registro de material/serviço não criado.')
        
        id_custeio = None
        if linha_conteudo[self.APLICACAO].strip() == 'CUSTEIO':
            id_custeio = linha_conteudo[self.ID_TIPO_CUSTEIO].strip() if linha_conteudo[self.ID_TIPO_CUSTEIO].strip() else None

        self.linha_index = linha_index

        self.dados_materiais_servicos = {
            'id': int(linha_conteudo[self.ID].strip()) if linha_conteudo[self.ID].strip() else None,
            'descricao': linha_conteudo[self.DESCRICAO].strip(),
            'aplicacao_recurso': linha_conteudo[self.APLICACAO].strip(),
            'tipo_custeio_id': id_custeio,
            'ativa': True if linha_conteudo[self.ATIVA].strip() == 'Sim' else False,
        }

        logger.info(self.dados_materiais_servicos)
        return self.dados_materiais_servicos

    def cria_ou_atualiza_especificacao_material_servico(self):
        if self.dados_materiais_servicos['id']:
            EspecificacaoMaterialServico.objects.update_or_create(
                id= self.dados_materiais_servicos['id'],
                defaults=self.dados_materiais_servicos
            )
        else:
            EspecificacaoMaterialServico.objects.create(
                descricao= self.dados_materiais_servicos['descricao'] ,
                aplicacao_recurso= self.dados_materiais_servicos['aplicacao_recurso'] ,
                tipo_custeio_id= self.dados_materiais_servicos['tipo_custeio_id'] ,
                ativa= self.dados_materiais_servicos['ativa'] ,
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
                raise CargaMateriaisServicosException(msg_erro)

        return estrutura_correta
        
    def processa_materiais_servicos(self, reader, arquivo):
        self.inicializa_log()

        try:
            for index, linha in enumerate(reader):
                if index == 0:
                    self.verifica_estrutura_cabecalho(cabecalho=linha)
                    continue
            
                try:
                    self.carrega_e_valida_dados_tipo_custeio(linha_conteudo=linha, linha_index=index)

                    self.cria_ou_atualiza_especificacao_material_servico()

                    self.loga_sucesso_carga_materiais_servicos()

                except Exception as e:
                    self.loga_erro_carga_materiais_servicos(f'Houve um erro na carga dessa linha:{str(e)}', index)
                    continue
            
            self.atualiza_status_arquivo(arquivo)
        
        except Exception as e:
            self.loga_erro_carga_materiais_servicos(str(e))
            self.atualiza_status_arquivo(arquivo)

    def carrega_materiais_servicos(self, arquivo):
        logger.info("Processando arquivo %s", arquivo.identificador)
        arquivo.ultima_execucao = datetime.now()

        try:
            with open(arquivo.conteudo.path, 'r', encoding="utf-8")as f:
                sniffer = csv.Sniffer().sniff(f.readline())
                f.seek(0)
                if self.DELIMITADORES[sniffer.delimiter] != arquivo.tipo_delimitador:
                    msg_erro = (f"Formato definido ({arquivo.tipo_delimitador}) é diferente do formato "
                                f"do arquivo csv ({self.DELIMITADORES[sniffer.delimiter]})")
                    self.loga_erro_carga_materiais_servicos(msg_erro)
                    self.atualiza_status_arquivo(arquivo)
                    return

                reader = csv.reader(f, delimiter=sniffer.delimiter)
                self.processa_materiais_servicos(reader, arquivo)

        except Exception as err:
            self.loga_erro_carga_materiais_servicos(f"Erro ao processar materiais e serviços: {str(err)}")
            self.atualiza_status_arquivo(arquivo)