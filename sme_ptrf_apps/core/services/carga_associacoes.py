import csv
import logging
import datetime

from brazilnum.cnpj import validate_cnpj, format_cnpj

from ..models import Associacao, Unidade
from ..models.arquivo import (
    DELIMITADOR_PONTO_VIRGULA,
    DELIMITADOR_VIRGULA,
    SUCESSO,
    ERRO,
    PROCESSADO_COM_ERRO)

logger = logging.getLogger(__name__)

__DELIMITADORES = {',': DELIMITADOR_VIRGULA, ';': DELIMITADOR_PONTO_VIRGULA}


class ProcessaAssociacoes:
    __EOL_UE = 0
    __NOME_UE = 1
    __EOL_DRE = 2
    __NOME_DRE = 3
    __SIGLA_DRE = 4
    __NOME_ASSOCIACAO = 5
    __CNPJ_ASSOCIACAO = 6

    __CABECALHOS = {
        __EOL_UE: "Código EOL UE",
        __NOME_UE: "Nome UE",
        __EOL_DRE: "Código EOL DRE",
        __NOME_DRE: "Nome da DRE UE",
        __SIGLA_DRE: "Sigla DRE",
        __NOME_ASSOCIACAO: "Nome da associação",
        __CNPJ_ASSOCIACAO: "CNPJ da associação",
    }

    logs = ""

    @classmethod
    def cabecalho_correto(cls, cabecalho):
        estrutura_correta = True
        for coluna, nome in cls.__CABECALHOS.items():
            if cabecalho[coluna] != nome:
                msg_erro = (f'Título da coluna {coluna} errado. Encontrado "{cabecalho[coluna]}". '
                            f'Deveria ser "{nome}". Confira o arquivo com o modelo.')
                logger.error(msg_erro)
                cls.logs = f"{cls.logs}\n{msg_erro}"
                estrutura_correta = False
                break
        return estrutura_correta

    @classmethod
    def processa_associacoes(cls, reader, arquivo):
        cls.logs = ""

        logger.info(f'Carregando arquivo de associações...')

        importadas = 0
        erros = 0
        for lin, row in enumerate(reader):
            if lin == 0:
                # Verifica se o cabeçalho está correto. Caso contrário interrompe o processamento.
                if cls.cabecalho_correto(cabecalho=row):
                    continue  # Pula o cabeçalho e continua.
                else:
                    break

            logger.debug(f'Linha {lin}: {row}')

            dre = cls.cria_ou_atualiza_dre_from_row(row)
            unidade = cls.cria_ou_atualiza_unidade_from_row(row, dre, lin)
            associacao = cls.cria_ou_atualiza_associacao_from_row(row, unidade, lin)

            if associacao:
                importadas += 1
            else:
                erros += 1

        if importadas > 0 and erros > 0:
            arquivo.status = PROCESSADO_COM_ERRO
        elif importadas == 0:
            arquivo.status = ERRO
        else:
            arquivo.status = SUCESSO

        cls.logs = f"{cls.logs}\nImportadas {importadas} associações. Erro na importação de {erros} associações."
        logger.info(f'Importadas {importadas} associações. Erro na importação de {erros} associações.')

        arquivo.log = cls.logs
        arquivo.save()

    @classmethod
    def cria_ou_atualiza_dre_from_row(cls, row):
        eol_dre = row[cls.__EOL_DRE]
        dre, created = Unidade.objects.update_or_create(
            codigo_eol=eol_dre,
            defaults={
                'tipo_unidade': 'DRE',
                'dre': None,
                'sigla': row[cls.__SIGLA_DRE],
                'nome': row[cls.__NOME_DRE]
            },
        )
        if created:
            logger.info(f'Criada DRE {dre.nome}')

        return dre

    @classmethod
    def cria_ou_atualiza_unidade_from_row(cls, row, dre, lin):
        eol_unidade = row[cls.__EOL_UE]
        tipo_unidade, _, nome_unidade = row[cls.__NOME_UE].partition(" ")

        if (tipo_unidade, tipo_unidade) not in Unidade.TIPOS_CHOICE:
            msg_erro = f'Tipo de unidade inválido ({tipo_unidade}) na linha {lin}. Trocado para EMEF.'
            logger.error(msg_erro)
            cls.logs = f"{cls.logs}\n{msg_erro}"
            tipo_unidade = 'EMEF'

        unidade, created = Unidade.objects.update_or_create(
            codigo_eol=eol_unidade,
            defaults={
                'tipo_unidade': tipo_unidade,
                'dre': dre,
                'sigla': '',
                'nome': nome_unidade
            },
        )
        if created:
            logger.info(f'Criada Unidade {unidade.nome}')

        return unidade

    @classmethod
    def cria_ou_atualiza_associacao_from_row(cls, row, unidade, lin):
        cnpj = row[cls.__CNPJ_ASSOCIACAO]
        if cnpj and not validate_cnpj(cnpj):
            msg_erro = f'CNPJ inválido ({cnpj}) na linha {lin}. Associação não criada.'
            logger.error(msg_erro)
            cls.logs = f"{cls.logs}\n{msg_erro}"
            return None

        cnpj = format_cnpj(cnpj) if cnpj else ""

        associacao, created = Associacao.objects.update_or_create(
            cnpj=cnpj,
            defaults={
                'unidade': unidade,
                'nome': row[cls.__NOME_ASSOCIACAO],
            },
        )

        if created:
            logger.info(f'Criada Associacao {associacao.nome}')

        return associacao


def carrega_associacoes(arquivo):
    logger.info("Processando arquivo %s", arquivo.identificador)
    arquivo.ultima_execucao = datetime.datetime.now()

    try:
        with open(arquivo.conteudo.path, 'r', encoding="utf-8") as f:
            sniffer = csv.Sniffer().sniff(f.readline())
            f.seek(0)
            if __DELIMITADORES[sniffer.delimiter] != arquivo.tipo_delimitador:
                msg_erro = (f"Formato definido ({arquivo.tipo_delimitador}) é diferente do formato "
                            f"do arquivo csv ({__DELIMITADORES[sniffer.delimiter]})")
                logger.error(msg_erro)
                arquivo.status = ERRO
                arquivo.log = msg_erro
                arquivo.save()
                return

            reader = csv.reader(f, delimiter=sniffer.delimiter)
            ProcessaAssociacoes.processa_associacoes(reader, arquivo)
    except Exception as err:
        logger.info("Erro ao processar associações: %s", str(err))
        arquivo.log = "Erro ao processar associações"
        arquivo.save()
