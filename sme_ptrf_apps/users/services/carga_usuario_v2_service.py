import csv
import datetime
import logging

from django.contrib.auth import get_user_model

from sme_ptrf_apps.core.models import Unidade
from sme_ptrf_apps.users.models import Visao, AcessoConcedidoSme

from sme_ptrf_apps.core.models.arquivo import DELIMITADOR_PONTO_VIRGULA, DELIMITADOR_VIRGULA, ERRO, PROCESSADO_COM_ERRO, SUCESSO

from sme_ptrf_apps.users.models import Grupo

from sme_ptrf_apps.users.services import GestaoUsuarioService
from brazilnum.cpf import validate_cpf

logger = logging.getLogger(__name__)

User = get_user_model()


class CargaUsuarioException(Exception):
    pass


class CargaUsuariosGestaoUsuarioService:
    __DELIMITADORES = {',': DELIMITADOR_VIRGULA, ';': DELIMITADOR_PONTO_VIRGULA}

    __LOGIN = 0  # Username
    __VISAO = 1  # Visão
    __EOL_UNIDADE = 2  # Código EOL da unidade a ser vinculada ao usuário
    __EMAIL = 3  # Email do usuário
    __GRUPOS = 4  # Nomes dos grupos de acesso separados por '|'
    __NOME = 5  # Nome do usuario
    __SERVIDOR_S_N = 6  # "S" para servidores e "N" para Não servidores
    __PODE_ACESSAR_SME_S_N = 7  # "S" para pode acessar e "N" para não pode acessar
    __ACESSO_CONCEDIDO_SME_S_N = 8  # "S" para acesso concedido e "N" para acesso não concedido

    __logs = ""
    __importados = 0
    __erros = 0

    def inicializa_log(self):
        self.__logs = ""
        self.__importados = 0
        self.__erros = 0

    def loga_erro_carga_usuario(self, mensagem_erro, linha=0):
        mensagem = f'Linha:{linha} {mensagem_erro}'
        logger.error(mensagem)
        self.__logs = f"{self.__logs}\n{mensagem}"
        self.__erros += 1

    def loga_sucesso_carga_usuario(self, dados_usuario):
        mensagem = f'Usuário {dados_usuario["login"]} criado/atualizado com sucesso.'
        logger.info(mensagem)
        self.__importados += 1

    def get_nomes_grupos(self, linha):
        try:
            str_grupos = linha[self.__GRUPOS]
            if str_grupos:
                nomes_grupos = str_grupos.split('|') if '|' in str_grupos else [str_grupos, ]
            else:
                nomes_grupos = []
        except IndexError:
            nomes_grupos = []

        return nomes_grupos

    def carrega_e_valida_dados_usuarios(self, linha, index):
        logger.info('Linha %s: %s', index, linha)

        __login = linha[self.__LOGIN].strip()
        __visao = linha[self.__VISAO].strip().upper()
        __eol_unidade = linha[self.__EOL_UNIDADE].strip()
        __email = linha[self.__EMAIL].strip()
        __grupos = self.get_nomes_grupos(linha)
        __nome = linha[self.__NOME].strip()
        __servidor_s_n = linha[self.__SERVIDOR_S_N].strip().upper()
        __pode_acessar_sme_s_n = linha[self.__PODE_ACESSAR_SME_S_N].strip().upper()
        __acesso_concedido_sme_s_n = linha[self.__ACESSO_CONCEDIDO_SME_S_N].strip().upper()

        # Valida servidor_s_n
        if __servidor_s_n not in ('S', 'N'):
            raise CargaUsuarioException(f"Servidor_S_N ({__servidor_s_n}) não é válido. Deveria ser S ou N.")

        # Valida __pode_acessar_sme_s_n
        if __pode_acessar_sme_s_n not in ('S', 'N'):
            raise CargaUsuarioException(
                f"Pode_Acessar_SME_S_N ({__pode_acessar_sme_s_n}) não é válido. Deveria ser S ou N.")

        # Valida __acesso_concedido_sme_s_n
        if __acesso_concedido_sme_s_n not in ('S', 'N'):
            raise CargaUsuarioException(
                f"Acesso_Concedido_SME_S_N ({__acesso_concedido_sme_s_n}) não é válido. Deveria ser S ou N.")

        # Busca Unidade
        if __eol_unidade:
            unidade = Unidade.objects.filter(codigo_eol=__eol_unidade).first()
            if not unidade:
                raise CargaUsuarioException(f"Associação para o código eol {__eol_unidade} não encontrado. linha: {index}")
        else:
            unidade = None

        # Busca/Cria/Valida visão
        if __visao in ['UE', 'DRE', 'SME']:
            visao, criada = Visao.objects.get_or_create(nome=__visao)
            if criada:
                logger.info(f"Criada visão {__visao}.")
        else:
            if __visao:
                raise CargaUsuarioException(f"Visão ({__visao}) definida na linha {index} não é válida. Deveria ser UE, DRE ou SME.")
            else:
                visao = None

        # Valida e-mail
        if __email and not valid_email(__email):
            raise CargaUsuarioException( f"Email ({__email}) definida na linha {index} não é válido.")

        # Valida grupos
        grupos_objs = []
        for nome_grupo in __grupos:
            try:
                grupo = Grupo.objects.get(name=nome_grupo)
                grupos_objs.append(grupo)
            except Grupo.DoesNotExist:
                self.loga_erro_carga_usuario(f'Não encontrado grupo com o nome {nome_grupo}. Usuário {__login}.', index)

        servidor = True if __servidor_s_n == 'S' else False
        acesso_concedido_sme = True if __acesso_concedido_sme_s_n == 'S' else False
        pode_acessar_sme = True if __pode_acessar_sme_s_n == 'S' else False
        possui_eol_unidade = True if __eol_unidade else False

        if servidor:
            self.valida_acesso_usuario_servidor(
                acesso_concedido_sme=acesso_concedido_sme,
                visao=visao,
                username=__login,
                unidade_csv=unidade,
                pode_acessar_sme=pode_acessar_sme,
                possui_eol_unidade=possui_eol_unidade
            )
        else:
            self.valida_acesso_usuario_nao_servidor(
                acesso_concedido_sme=acesso_concedido_sme,
                visao=visao,
                username=__login,
                unidade_csv=unidade,
                pode_acessar_sme=pode_acessar_sme,
                possui_eol_unidade=possui_eol_unidade
            )

        return {
            "login": __login,
            "visao": __visao,
            "visao_obj": visao,
            "eol_unidade": __eol_unidade,
            "unidade_obj": unidade,
            "email": __email,
            "grupos": __grupos,
            "grupos_objs": grupos_objs,
            "nome": __nome,
            "servidor_s_n": __servidor_s_n,
            "pode_acessar_sme_s_n": __pode_acessar_sme_s_n,
            "acesso_concedido_sme_s_n": __acesso_concedido_sme_s_n,
        }

    def cria_ou_atualiza_usuario_admin(self, dados_usuario):
        e_servidor = (dados_usuario["servidor_s_n"] == "S")
        acesso_concedido_sme = (dados_usuario["acesso_concedido_sme_s_n"] == "S")
        pode_acessar_sme = (dados_usuario["pode_acessar_sme_s_n"] == "S")

        usuario, criado = User.objects.get_or_create(
            username=dados_usuario["login"],
            defaults={
                'email': dados_usuario["email"] if dados_usuario["email"] else "",
                'name': dados_usuario["nome"],
                'e_servidor': e_servidor
            },
        )

        if criado:
            logger.info(f"Criado usuário no Admin {dados_usuario['login']}.")

        salvar_usuario = False

        if not criado and dados_usuario["email"] and usuario.email != dados_usuario["email"]:
            usuario.email = dados_usuario["email"]
            salvar_usuario = True
            logger.info(f"Atualizado e-mail do usuário no Admin {dados_usuario['login']}, {dados_usuario['email']}.")

        if dados_usuario["eol_unidade"] and not usuario.unidades.filter(codigo_eol=dados_usuario['eol_unidade']).first():
            usuario.unidades.add(dados_usuario["unidade_obj"])
            salvar_usuario = True
            logger.info(f"Unidade {dados_usuario['eol_unidade']} vinculada ao usuário {dados_usuario['login']}.")

        if dados_usuario["visao"] and not usuario.visoes.filter(nome=dados_usuario['visao']).first():
            usuario.visoes.add(dados_usuario['visao_obj'])
            salvar_usuario = True
            logger.info(f"Visão {dados_usuario['visao']} vinculada ao usuário {dados_usuario['login']} no Admin.")

        if dados_usuario['grupos_objs']:
            usuario.groups.clear()
            for grupo in dados_usuario['grupos_objs']:
                usuario.groups.add(grupo)
            salvar_usuario = True
            logger.info(f"Grupo(s) {dados_usuario['grupos']} vinculado(s) ao usuário {dados_usuario['login']} no Admin.")

        if acesso_concedido_sme:
            AcessoConcedidoSme.criar_acesso_se_nao_existir(unidade=dados_usuario["unidade_obj"], user=usuario)

        if pode_acessar_sme:
            usuario.pode_acessar_sme = True
            salvar_usuario = True
            logger.info(f"Atualizado a flag pode_acessar_sme para {pode_acessar_sme} do usuário {dados_usuario['login']}")

        if salvar_usuario:
            usuario.save()

        return usuario

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

    def processa_importacao_usuarios(self, reader, arquivo):
        from sme_ptrf_apps.users.services.usuario_core_sso_service import cria_ou_atualiza_usuario_core_sso

        self.inicializa_log()
        try:
            for index, linha in enumerate(reader):
                if index == 0: continue

                try:
                    dados_usuario = self.carrega_e_valida_dados_usuarios(linha, index)
                    self.cria_ou_atualiza_usuario_admin(dados_usuario)
                    cria_ou_atualiza_usuario_core_sso(dados_usuario)
                    self.loga_sucesso_carga_usuario(dados_usuario)
                except Exception as e:
                    self.loga_erro_carga_usuario(str(e), index)
                    continue

            self.atualiza_status_arquivo(arquivo)

        except Exception as e:
            self.loga_erro_carga_usuario(str(e))
            self.atualiza_status_arquivo(arquivo)

    def carrega_usuarios(self, arquivo):
        from sme_ptrf_apps.core.models.arquivo import DELIMITADOR_PONTO_VIRGULA, DELIMITADOR_VIRGULA

        __DELIMITADORES = {',': DELIMITADOR_VIRGULA, ';': DELIMITADOR_PONTO_VIRGULA}

        logger.info('Carregando arquivo de usuários.')
        arquivo.ultima_execucao = datetime.datetime.now()

        try:
            with open(arquivo.conteudo.path, 'r', encoding="utf-8") as f:
                sniffer = csv.Sniffer().sniff(f.readline())
                f.seek(0)
                if __DELIMITADORES[sniffer.delimiter] != arquivo.tipo_delimitador:
                    msg_erro = f"Formato definido ({arquivo.tipo_delimitador}) é diferente do formato do arquivo csv " \
                               f"({__DELIMITADORES[sniffer.delimiter]})"
                    self.loga_erro_carga_usuario(msg_erro)
                    self.atualiza_status_arquivo(arquivo)

                    return

                reader = csv.reader(f, delimiter=sniffer.delimiter)
                logger.info(f"aqui vou chamar o processamento")
                self.processa_importacao_usuarios(reader, arquivo)
        except Exception as err:
            self.loga_erro_carga_usuario(f"Erro ao processar usuários: {str(err)}")
            self.atualiza_status_arquivo(arquivo)

    @staticmethod
    def valida_acesso_usuario_servidor(acesso_concedido_sme, visao, username, unidade_csv, pode_acessar_sme, possui_eol_unidade):
        if visao.nome == 'SME':
            if possui_eol_unidade:
                raise CargaUsuarioException(f"Acesso não autorizado para a visão SME a partir do código EOL.")

            unidade_exercicio_lotacao = GestaoUsuarioService.get_info_unidade_exercicio_lotacao(username=username)

            # Existem casos em que não é encontrado unidade exercicio ou lotação
            if unidade_exercicio_lotacao is None:
                raise CargaUsuarioException(
                    f"Usuário não autorizado na unidade. Servidor em exercício em outra unidade.")

            permite_administrativa = GestaoUsuarioService.get_se_permite_tipo_unidade_administrativa(
                codigo_eol=unidade_exercicio_lotacao["codigo"]
            )

            if not permite_administrativa and not pode_acessar_sme:
                raise CargaUsuarioException(
                    f"Usuário não autorizado na unidade. Servidor em exercício em outra unidade.")

        else:
            if not acesso_concedido_sme:
                unidade_exercicio_lotacao = GestaoUsuarioService.get_info_unidade_exercicio_lotacao(username=username)

                # Existem casos em que não é encontrado unidade exercicio ou lotação
                if unidade_exercicio_lotacao is None:
                    raise CargaUsuarioException(
                        f"Usuário não autorizado na unidade. Servidor em exercício em outra unidade.")

                if unidade_csv.codigo_eol != unidade_exercicio_lotacao["codigo"]:
                    raise CargaUsuarioException(
                        f"Usuário não autorizado na unidade. Servidor em exercício em outra unidade.")

                if visao.nome == 'UE':
                    if not unidade_csv.tipo_unidade_pertence_a_grupo_ue():
                        raise CargaUsuarioException(
                                f"Usuário não autorizado na unidade. A unidade não pertence a visão indicada.")

                if visao.nome == 'DRE':
                    if not unidade_csv.tipo_unidade == 'DRE':
                        raise CargaUsuarioException(
                                f"Usuário não autorizado na unidade. A unidade não pertence a visão indicada.")

    @staticmethod
    def valida_acesso_usuario_nao_servidor(acesso_concedido_sme, visao, username, unidade_csv, pode_acessar_sme, possui_eol_unidade):
        if not validate_cpf(username):
            raise CargaUsuarioException(f"Cpf não é válido")

        if visao.nome == 'UE':
            if not acesso_concedido_sme:
                membro_associacao_na_unidade = GestaoUsuarioService.get_se_usuario_membro_associacao_na_unidade(
                    unidade=unidade_csv,
                    username=username,
                    e_servidor=False
                )

                logger.info(f"membro_associacao_na_unidade {membro_associacao_na_unidade}")

                if not membro_associacao_na_unidade:
                    raise CargaUsuarioException(
                        f"Usuário não autorizado na unidade. Usuário não é membro da APM.")

                if not unidade_csv.tipo_unidade_pertence_a_grupo_ue():
                    raise CargaUsuarioException(
                        f"Usuário não autorizado na unidade. A unidade não pertence a visão indicada.")

        elif visao.nome == 'DRE':
            if acesso_concedido_sme:
                if not unidade_csv.tipo_unidade == 'DRE':
                    raise CargaUsuarioException(
                            f"Usuário não autorizado na unidade. A unidade não pertence a visão indicada.")
            else:
                raise CargaUsuarioException(f"Usuário não autorizado na unidade.")

        elif visao.nome == 'SME':
            if possui_eol_unidade:
                raise CargaUsuarioException(f"Acesso não autorizado para a visão SME a partir do código EOL.")

            if not pode_acessar_sme:
                raise CargaUsuarioException(f"Usuário não autorizado na unidade.")

            if acesso_concedido_sme:
                raise CargaUsuarioException(
                    f"Não é permitido conceder acesso para a visão SME para usuário não servidor.")

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
