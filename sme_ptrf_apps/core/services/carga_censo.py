import csv
import logging
import datetime


from ..models import Associacao, Unidade, Censo
from ..models.arquivo import (
    DELIMITADOR_PONTO_VIRGULA, 
    DELIMITADOR_VIRGULA,
    PENDENTE,
    SUCESSO,
    ERRO,
    PROCESSADO_COM_ERRO)

logger = logging.getLogger(__name__)

__DELIMITADORES = {',': DELIMITADOR_VIRGULA, ';': DELIMITADOR_PONTO_VIRGULA}


class ProcessaCenso:
    __EOL_UE = 0
    __QUANTIDADE_ALUNOS = 1
    __ANO = 2


    logs = ""


    @classmethod
    def processa_censo(cls, reader, arquivo):
        logger.info(f'Carregando arquivo do censo...')
        erros = 0
        importadas = 0

        for lin, row in enumerate(reader):
            if lin == 0:
                continue  # Pula cabeçalho.

            logger.info(f'Linha {lin}: {row}')

            if not all(row):
                logger.info(f"Pulando linha {lin} que está vazia.")
                continue

            unidade = Unidade.objects.filter(codigo_eol=row[cls.__EOL_UE]).first()
            
            if not unidade:
                msg_erro = f'Unidade Não encontrada para código eol ({row[cls.__EOL_UE]}) na linha {lin}.'
                logger.error(msg_erro)
                cls.logs = f"{cls.logs}\n{msg_erro}"
                erros += 1
                continue

            quantidade_alunos = row[cls.__QUANTIDADE_ALUNOS]

            if isinstance(quantidade_alunos, int):
                msg_erro = f'Quantidade de alunos não tem um tipo permitido ({quantidade_alunos}) na linha {lin}.'
                logger.error(msg_erro)
                cls.logs = f"{cls.logs}\n{msg_erro}"
                erros += 1
                continue

            ano = row[cls.__ANO]

            if len(ano) != 4:
                msg_erro = f'O ano deve ter o formato AAAA e não {quantidade_alunos} na linha {lin}.'
                logger.error(msg_erro)
                cls.logs = f"{cls.logs}\n{msg_erro}"
                erros += 1
                continue

            censo = Censo.objects.create(unidade=unidade, quantidade_alunos=quantidade_alunos, ano=ano)

            if censo:
                importadas += 1
                logger.info("Censo Criado com sucesso: %s", censo)

        if importadas > 0 and erros > 0:
            arquivo.status = PROCESSADO_COM_ERRO
        elif importadas == 0:
            arquivo.status = ERRO
        else:
            arquivo.status = SUCESSO

        cls.logs = f"{cls.logs}\nImportadas {importadas} dados de censo. Erro na importação de {erros} dados do censo."
        logger.info(f'Importadas {importadas} dados de censo. Erro na importação de {erros} dados do censo.')
        
        arquivo.log = cls.logs
        arquivo.save()
        cls.logs = ""
        return importadas, erros


def carrega_censo(arquivo):
    logger.info("Processando arquivo %s", arquivo.identificador)
    arquivo.ultima_execucao = datetime.datetime.now()
    imports, erros = 0, 0

    try:
        with open(arquivo.conteudo.path, 'r', encoding="utf-8") as f:
            sniffer = csv.Sniffer().sniff(f.readline())
            f.seek(0)
            if __DELIMITADORES[sniffer.delimiter] != arquivo.tipo_delimitador:
                msg_erro = f"Formato definido ({arquivo.tipo_delimitador}) é diferente do formato do arquivo csv ({__DELIMITADORES[sniffer.delimiter]})"
                logger.error(msg_erro)
                arquivo.status = ERRO
                arquivo.log = msg_erro
                arquivo.save()
                return

            reader = csv.reader(f, delimiter=sniffer.delimiter)
            imports, erros = ProcessaCenso.processa_censo(reader, arquivo)
    except Exception as err:
        logger.info("Erro ao processar censo: %s", str(err))
        arquivo.log = "Erro ao processar censo: %s" % str(err)

        if imports > 0 and erros > 0:
            arquivo.status = PROCESSADO_COM_ERRO
        elif imports == 0:
            arquivo.status = ERRO

        arquivo.save()
