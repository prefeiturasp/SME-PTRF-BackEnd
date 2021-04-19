import csv
import datetime
import logging

from django.contrib.auth import get_user_model

from sme_ptrf_apps.core.models import Unidade
from sme_ptrf_apps.users.models import Visao

from sme_ptrf_apps.core.models.arquivo import DELIMITADOR_PONTO_VIRGULA, DELIMITADOR_VIRGULA, ERRO, PROCESSADO_COM_ERRO, SUCESSO

from sme_ptrf_apps.users.models import Grupo

logger = logging.getLogger(__name__)

User = get_user_model()

__DELIMITADORES = {',': DELIMITADOR_VIRGULA, ';': DELIMITADOR_PONTO_VIRGULA}

__LOGIN = 0         # Username
__VISAO = 1         # Visão
__EOL_UNIDADE = 2   # Código EOL da unidade a ser vinculada ao usuário
__EMAIL = 3         # Email do usuário
__GRUPOS = 4        # Nomes dos grupos de acesso separados por '|'
__NOME = 5          # Nome do usuario
__SERVIDOR_S_N = 6  # "S" para servidores e "N" para Não servidores

def checa_visao(v):
    return v in ['UE', 'DRE', 'SME']


def get_nomes_grupos(linha):
    try:
        str_grupos = linha[__GRUPOS]
        if str_grupos:
            nomes_grupos = str_grupos.split('|') if '|' in str_grupos else [str_grupos, ]
        else:
            nomes_grupos = []
    except IndexError:
        nomes_grupos = []

    return nomes_grupos


def dados_usuario(row):
    return {
        "login" : row[__LOGIN].strip(),
        "visao": row[__VISAO].strip(),
        "eol_unidade": row[__EOL_UNIDADE].strip(),
        "email": row[__EMAIL].strip(),
        "grupos": get_nomes_grupos(row),
        "nome": row[__NOME].strip(),
        "servidor_s_n": row[__SERVIDOR_S_N].strip(),
    }

def processa_importacao_usuarios(reader, arquivo):
    from sme_ptrf_apps.users.services import SmeIntegracaoException, SmeIntegracaoService
    from requests import ConnectTimeout, ReadTimeout

    logs = ""
    try:
        importados = 0
        erros = 0
        for index, row in enumerate(reader):
            if index == 0: continue

            logger.info('Linha %s: %s', index, row)

            try:
                usuario_dados = dados_usuario(row)
            except Exception as e:
                msg_erro = f'Erro {str(e)} ao tentar carregar a linha {index}.'
                logger.error(msg_erro)
                logs = f"{logs}\n{msg_erro}"
                erros += 1

            # Unidade de vínculo
            unidade = Unidade.objects.filter(codigo_eol=usuario_dados['eol_unidade']).first()
            if not unidade:
                msg_erro = f"Associação para o código eol {usuario_dados['eol_unidade']} não encontrado. linha: {index}"
                logger.info(msg_erro)
                logs = f"{logs}\n{msg_erro}"
                erros += 1
                continue

            # Visão
            if not checa_visao(usuario_dados['visao']):
                msg_erro = f"Visão ({usuario_dados['visao']}) definida na linha {index} não está entre as definidas (UE, DRE, SME) no PTRF."
                logger.info(msg_erro)
                logs = f"{logs}\n{msg_erro}"
                erros += 1
                continue

            visao = Visao.objects.filter(nome=usuario_dados['visao']).first()

            if not visao:
                visao = Visao.objects.create(nome=usuario_dados['visao'])

            # Email
            try:
                novo_email = usuario_dados['email']
            except IndexError:
                novo_email = ""

            if novo_email and not valid_email(novo_email):
                msg_erro = f'O email {novo_email} do usuário {usuario_dados["login"]} não é válido.'
                logger.error(msg_erro)
                logs = f"{logs}\n{msg_erro}"
                erros += 1
                novo_email = ""

            # Cria ou Recupera usuário no Admin
            u = User.objects.filter(username=usuario_dados['login']).first()
            if not u:
                u = User.objects.create(username=usuario_dados['login'], email=novo_email)

            # Verifica se usuário já existe no CoreSSO e cria se não existir
            try:
                info_user_core = SmeIntegracaoService.usuario_core_sso_or_none(login=usuario_dados['login'])
                if not info_user_core:
                    SmeIntegracaoService.cria_usuario_core_sso(
                        login=usuario_dados['login'],
                        nome=usuario_dados['nome'],
                        email=u.email if u.email else usuario_dados['email'],
                        e_servidor=usuario_dados['servidor_s_n'] == "S"
                    )

            except SmeIntegracaoException as e:
                msg_erro = f'Erro {str(e)} ao tentar consultar ou criar usuário {usuario_dados["login"]} no CoreSSO.'
                logger.error(msg_erro)
                logs = f"{logs}\n{msg_erro}"
                erros += 1

            # Atualiza email no CoreSSO se for um novo e-mail
            if novo_email:
                try:
                    SmeIntegracaoService.redefine_email(u.username, novo_email)
                    u.email = novo_email

                except SmeIntegracaoException as e:
                    msg_erro = f'Erro {str(e)} ao tentar atualizar o e-mail do usuário {usuario_dados["login"]} no CoreSSO.'
                    logger.error(msg_erro)
                    logs = f"{logs}\n{msg_erro}"
                    erros += 1

                except ReadTimeout:
                    msg_erro = f'Erro de ReadTimeout ao tentar atualizar o e-mail do usuário {usuario_dados["login"]} no CoreSSO.'
                    logger.error(msg_erro)
                    logs = f"{logs}\n{msg_erro}"
                    erros += 1

                except ConnectTimeout:
                    msg_erro = f'Erro de ConnectTimeout ao tentar atualizar o e-mail do usuário {usuario_dados["login"]} no CoreSSO.'
                    logger.error(msg_erro)
                    logs = f"{logs}\n{msg_erro}"
                    erros += 1

                # Vincula unidade ao usuário
                if not u.unidades.filter(codigo_eol=usuario_dados['eol_unidade']).first():
                    u.unidades.add(unidade)

                # Vincula visões ao usuário no Admin
                if not u.visoes.filter(nome=row[__VISAO].strip()).first():
                    u.visoes.add(visao)

                # Atribuir a visão do usuário no CoreSSO
                if visao:
                    SmeIntegracaoService.atribuir_perfil_coresso(login=u.username, visao=visao.nome)

                # Gravação dos grupos de acesso do usuário
                nomes_grupos = get_nomes_grupos(row)
                grupos = []
                for nome_grupo in nomes_grupos:
                    try:
                        grupo = Grupo.objects.get(name=nome_grupo)
                        grupos.append(grupo)
                    except Grupo.DoesNotExist:
                        msg_erro = f'Não encontrado grupo com o nome {nome_grupo}. Usuário {usuario_dados["login"]}.'
                        logger.error(msg_erro)
                        logs = f"{logs}\n{msg_erro}"
                        erros += 1
                if grupos:
                    u.groups.clear()
                    for grupo in grupos:
                        u.groups.add(grupo)

                u.save()
                logger.info('Usuário %s criado/atualizado com sucesso.', usuario_dados['login'])
                importados += 1


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


def valid_email(string):
    pos = string.find("@")
    dot = string.rfind(".")
    if pos < 1:
        return False
    if dot < pos + 2:
        return False
    if dot + 2 >= len(string):
        return False
    return True
