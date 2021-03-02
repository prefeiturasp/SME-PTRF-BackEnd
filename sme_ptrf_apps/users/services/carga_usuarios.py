import csv
import datetime
import logging

from django.contrib.auth import get_user_model

from sme_ptrf_apps.core.models import Unidade
from sme_ptrf_apps.users.models import Visao

from sme_ptrf_apps.core.models.arquivo import DELIMITADOR_PONTO_VIRGULA, DELIMITADOR_VIRGULA, ERRO, PROCESSADO_COM_ERRO, SUCESSO

logger = logging.getLogger(__name__)

User = get_user_model()

__DELIMITADORES = {',': DELIMITADOR_VIRGULA, ';': DELIMITADOR_PONTO_VIRGULA}

__RF = 0  # Username
__VISAO = 1
__EOL_UNIDADE = 2
__EMAIL = 3


def checa_visao(v):
    return v in ['UE', 'DRE', 'SME']


def processa_importacao_usuarios(reader, arquivo):
    from sme_ptrf_apps.users.services import SmeIntegracaoException, SmeIntegracaoService
    from requests import ConnectTimeout, ReadTimeout

    logs = ""
    try:
        importados = 0
        erros = 0
        for index, row in enumerate(reader):
            if index != 0:
                logger.info('Linha %s: %s', index, row)

                unidade = Unidade.objects.filter(codigo_eol=row[__EOL_UNIDADE].strip()).first()

                if unidade:
                    if not checa_visao(row[__VISAO].strip()):
                        msg_erro = f"Visão ({row[__VISAO].strip()}) definida na linha {index} não está entre as definidas (UE, DRE, SME) no PTRF."
                        logger.info(msg_erro)
                        logs = f"{logs}\n{msg_erro}"
                        erros += 1
                        continue

                    visao = Visao.objects.filter(nome=row[__VISAO].strip()).first()

                    if not visao:
                        visao = Visao.objects.create(nome=row[__VISAO].strip())

                    u = User.objects.filter(username=row[__RF].strip()).first()
                    if not u:
                        u = User.objects.create(username=row[__RF].strip(), email=row[__EMAIL].strip())

                    try:
                        SmeIntegracaoService.redefine_email(u.username, row[__EMAIL].strip())
                        u.email = row[__EMAIL].strip()

                    except SmeIntegracaoException as e:
                        msg_erro = f'Erro {str(e)} ao tentar atualizar o e-mail do usuário {row[__RF].strip()} no CoreSSO.'
                        logger.error(msg_erro)
                        logs = f"{logs}\n{msg_erro}"
                        erros += 1

                    except ReadTimeout:
                        msg_erro = f'Erro de ReadTimeout ao tentar atualizar o e-mail do usuário {row[__RF].strip()} no CoreSSO.'
                        logger.error(msg_erro)
                        logs = f"{logs}\n{msg_erro}"
                        erros += 1

                    except ConnectTimeout:
                        msg_erro = f'Erro de ConnectTimeout ao tentar atualizar o e-mail do usuário {row[__RF].strip()} no CoreSSO.'
                        logger.error(msg_erro)
                        logs = f"{logs}\n{msg_erro}"
                        erros += 1

                    if not u.unidades.filter(codigo_eol=row[__EOL_UNIDADE].strip()).first():
                        u.unidades.add(unidade)

                    if not u.visoes.filter(nome=row[__VISAO].strip()).first():
                        u.visoes.add(visao)
                    u.save()
                    logger.info('Usuário para o rf %s criado/atualizado com sucesso.', row[__RF].strip())
                    importados += 1
                    continue

                msg_erro = f"Associação para o código eol {row[__EOL_UNIDADE].strip()} não encontrado. linha: {index}"
                logger.info(msg_erro)
                logs = f"{logs}\n{msg_erro}"
                erros += 1

        if importados > 0 and erros > 0:
            arquivo.status = PROCESSADO_COM_ERRO
        elif importados == 0:
            arquivo.status = ERRO
        else:
            arquivo.status = SUCESSO

        logs = f"{logs}\nImportados {importados} usuários. Erro na importação de {erros} usuários."
        logger.info(f'Importados {importados} usuários. Erro na importação de {erros} usuários.')

        arquivo.log = logs
        arquivo.save()
    except Exception as e:
        logging.info('Error: %s', str(e))
        arquivo.log = f'Error: {str(e)}'
        arquivo.status = ERRO
        arquivo.save()


def carrega_usuarios(arquivo):
    logger.info('Carregando arquivo de usuários.')
    arquivo.ultima_execucao = datetime.datetime.now()

    try:
        with open(arquivo.conteudo.path, 'r', encoding="utf-8") as f:
            sniffer = csv.Sniffer().sniff(f.readline())
            f.seek(0)
            if __DELIMITADORES[sniffer.delimiter] != arquivo.tipo_delimitador:
                msg_erro = f"Formato definido ({arquivo.tipo_delimitador}) é diferente do formato do arquivo csv ({__DELIMITADORES[sniffer.delimiter]})"
                logger.info(msg_erro)
                arquivo.status = ERRO
                arquivo.log = msg_erro
                arquivo.save()
                return

            reader = csv.reader(f, delimiter=sniffer.delimiter)
            processa_importacao_usuarios(reader, arquivo)
    except Exception as err:
        logger.info("Erro ao processar usuários: %s", str(err))
        arquivo.log = "Erro ao processar usuários."
        arquivo.save()
