import logging
from celery import shared_task

import csv
from tempfile import NamedTemporaryFile
from django.core.files import File

from sme_ptrf_apps.core.models import ArquivoDownload
from sme_ptrf_apps.core.services.arquivo_download_service import gerar_arquivo_download
from sme_ptrf_apps.users.services import GestaoUsuarioService, SmeIntegracaoService

from django.contrib.auth import get_user_model

User = get_user_model()

logger = logging.getLogger(__name__)


def criar_registro_central_download(user, apenas_nao_permitidos=None):
    logger.info(f"Criando registro na central de download")

    if apenas_nao_permitidos:
        identificador_do_arquivo = 'dados_usuarios_e_unidades_apenas_nao_permitidos.csv'
    else:
        identificador_do_arquivo = 'dados_usuarios_e_unidades_todos_os_acessos.csv'

    obj = gerar_arquivo_download(
        user,
        identificador_do_arquivo,
        ''
    )

    objeto_arquivo_download = obj

    return objeto_arquivo_download


def gerar_arquivo_csv(result_todos_usuarios, objeto_arquivo_download):
    csv_file = 'dados_usuarios_e_unidades_de_acesso.csv'

    with NamedTemporaryFile(mode="r+", newline='', encoding='utf-8', prefix=csv_file, suffix='.csv') as tmp:

        writer = csv.writer(tmp.file, delimiter=",")

        # Cabeçalho
        headers = [
            'Login do Usuário',
            'Nome do Usuário',
            'É Servidor',
            'Visão',
            'Unidades Vinculadas ao Usuário (cod_eol)',
            'Unidades Vinculadas ao Usuário (nome)',
            'Unidades Vinculadas ao Usuário (tipo unidade)',
            'É Membro',
            'Pode Acessar',
            'Unidade de Lotação (nome)',
            'Unidade de Lotação (cod_eol)',
            'Unidade de Exercício (nome)',
            'Unidade de Exercício (cod_eol)'
        ]

        writer.writerow(headers)

        # Escrever dados
        for item in result_todos_usuarios:
            writer.writerow(item)

        logger.info(f"Arquivo CSV criado com sucesso! {tmp}")

        try:
            logger.info("Salvando arquivo download...")
            objeto_arquivo_download.arquivo.save(
                name=objeto_arquivo_download.identificador,
                content=File(tmp)
            )
            objeto_arquivo_download.status = ArquivoDownload.STATUS_CONCLUIDO
            objeto_arquivo_download.save()
            logger.info("Arquivo salvo com sucesso...")

        except Exception as e:
            objeto_arquivo_download.status = ArquivoDownload.STATUS_ERRO
            objeto_arquivo_download.msg_erro = str(e)
            objeto_arquivo_download.save()
            logger.error("Erro arquivo download...")


def retornar_info_unidade_lotacao(usuario):
    if usuario.e_servidor:
        try:
            info = SmeIntegracaoService.get_info_lotacao_e_exercicio_do_servidor(usuario.username)
        except:
            info = {}
    else:
        info = {}

    result = {
        "nome_unidade": "",
        "codigo_unidade": "",
    }

    if info and info['unidadeLotacao']:
        result["nome_unidade"] = info['unidadeLotacao']['nomeUnidade']
        result["codigo_unidade"] = info['unidadeLotacao']['codigo']

    return result


def retornar_info_unidade_exercicio(usuario):
    if usuario.e_servidor:
        try:
            info = SmeIntegracaoService.get_info_lotacao_e_exercicio_do_servidor(usuario.username)
        except:
            info = {}
    else:
        info = {}

    result = {
        "nome_unidade": "",
        "codigo_unidade": "",
    }

    if info and info['unidadeExercicio']:
        result["nome_unidade"] = info['unidadeExercicio']['nomeUnidade']
        result["codigo_unidade"] = info['unidadeExercicio']['codigo']

    return result


def montar_dados_todos_os_acessos():
    usuarios = User.objects.all().order_by('name', 'username')

    result_todos_os_resultados = []

    for usuario in usuarios:

        logger.info(f"Iniciando o processo de verificação para o usuario: {usuario}")

        e_servidor = "sim" if usuario.e_servidor else "não"

        gestao_usuario = GestaoUsuarioService(usuario=usuario)
        tem_visao_sme = gestao_usuario.usuario_possui_visao(visao="SME")
        unidades_que_perdeu_acesso = gestao_usuario.valida_unidades_do_usuario()

        arrays_ids_unidades_que_perdeu_acesso = []
        arrays_nomes_unidades_unidades_que_perdeu_acesso = []

        # Monta array de IDS para verificar as unidades que perdeu acesso
        for u in unidades_que_perdeu_acesso:
            arrays_ids_unidades_que_perdeu_acesso.append(u['cod_eol'])
            arrays_nomes_unidades_unidades_que_perdeu_acesso.append(u['nome_unidade'])

        for i, unidade in enumerate(usuario.unidades.all()):
            em_suporte = gestao_usuario.unidade_em_suporte(unidade=unidade)
            if not em_suporte:
                result = []
                result.append(usuario.username)
                result.append(usuario.name)
                result.append(e_servidor)

                if unidade.tipo_unidade == "DRE":
                    result.append("DRE")
                else:
                    result.append("UE")

                result.append(unidade.codigo_eol)
                result.append(unidade.nome)
                result.append(unidade.tipo_unidade)

                membro = gestao_usuario.usuario_membro_associacao_na_unidade(unidade=unidade)
                if membro:
                    result.append("sim")
                else:
                    result.append("não")

                if unidade.codigo_eol in arrays_ids_unidades_que_perdeu_acesso:
                    result.append("não")
                else:
                    result.append("sim")

                dados_unidade_lotacao = retornar_info_unidade_lotacao(usuario=usuario)
                result.append(dados_unidade_lotacao['nome_unidade'])
                result.append(dados_unidade_lotacao['codigo_unidade'])

                dados_unidade_exercicio = retornar_info_unidade_exercicio(usuario=usuario)
                result.append(dados_unidade_exercicio['nome_unidade'])
                result.append(dados_unidade_exercicio['codigo_unidade'])

                result_todos_os_resultados.append(result)

        if tem_visao_sme:
            result_sme = []
            result_sme.append(usuario.username)
            result_sme.append(usuario.name)
            result_sme.append(e_servidor)
            result_sme.append("SME")
            result_sme.append('')
            result_sme.append('Secretaria Municipal de Educação')
            result_sme.append('SME')
            result_sme.append('não')
            if "Secretaria Municipal de Educação" in arrays_nomes_unidades_unidades_que_perdeu_acesso:
                result_sme.append('não')
            else:
                result_sme.append('sim')

            dados_unidade_lotacao = retornar_info_unidade_lotacao(usuario=usuario)
            result_sme.append(dados_unidade_lotacao['nome_unidade'])
            result_sme.append(dados_unidade_lotacao['codigo_unidade'])

            dados_unidade_exercicio = retornar_info_unidade_exercicio(usuario=usuario)
            result_sme.append(dados_unidade_exercicio['nome_unidade'])
            result_sme.append(dados_unidade_exercicio['codigo_unidade'])

            result_todos_os_resultados.append(result_sme)

    return result_todos_os_resultados


def montar_dados_apenas_nao_permitidos():
    usuarios = User.objects.all().order_by('name', 'username')

    result_todos_os_resultados = []

    for usuario in usuarios:

        logger.info(f"Iniciando o processo de verificação para o usuario: {usuario}")

        e_servidor = "sim" if usuario.e_servidor else "não"

        gestao_usuario = GestaoUsuarioService(usuario=usuario)
        tem_visao_sme = gestao_usuario.usuario_possui_visao(visao="SME")
        unidades_que_perdeu_acesso = gestao_usuario.valida_unidades_do_usuario()

        arrays_ids_unidades_que_perdeu_acesso = []
        arrays_nomes_unidades_unidades_que_perdeu_acesso = []

        # Monta array de IDS para verificar as unidades que perdeu acesso
        for u in unidades_que_perdeu_acesso:
            arrays_ids_unidades_que_perdeu_acesso.append(u['cod_eol'])
            arrays_nomes_unidades_unidades_que_perdeu_acesso.append(u['nome_unidade'])

        for i, unidade in enumerate(usuario.unidades.all()):

            if unidade.codigo_eol in arrays_ids_unidades_que_perdeu_acesso:

                em_suporte = gestao_usuario.unidade_em_suporte(unidade=unidade)

                if not em_suporte:
                    result = []
                    result.append(usuario.username)
                    result.append(usuario.name)
                    result.append(e_servidor)

                    if unidade.tipo_unidade == "DRE":
                        result.append("DRE")
                    else:
                        result.append("UE")

                    result.append(unidade.codigo_eol)
                    result.append(unidade.nome)
                    result.append(unidade.tipo_unidade)

                    membro = gestao_usuario.usuario_membro_associacao_na_unidade(unidade=unidade)
                    if membro:
                        result.append("sim")
                    else:
                        result.append("não")

                    # Pode acessar
                    result.append("não")

                    dados_unidade_lotacao = retornar_info_unidade_lotacao(usuario=usuario)
                    result.append(dados_unidade_lotacao['nome_unidade'])
                    result.append(dados_unidade_lotacao['codigo_unidade'])

                    dados_unidade_exercicio = retornar_info_unidade_exercicio(usuario=usuario)
                    result.append(dados_unidade_exercicio['nome_unidade'])
                    result.append(dados_unidade_exercicio['codigo_unidade'])

                    result_todos_os_resultados.append(result)

        if tem_visao_sme:
            if "Secretaria Municipal de Educação" in arrays_nomes_unidades_unidades_que_perdeu_acesso:
                result_sme = []
                result_sme.append(usuario.username)
                result_sme.append(usuario.name)
                result_sme.append(e_servidor)
                result_sme.append("SME")
                result_sme.append('')
                result_sme.append('Secretaria Municipal de Educação')
                result_sme.append('SME')
                result_sme.append('não')
                result_sme.append('não')

                dados_unidade_lotacao = retornar_info_unidade_lotacao(usuario=usuario)
                result_sme.append(dados_unidade_lotacao['nome_unidade'])
                result_sme.append(dados_unidade_lotacao['codigo_unidade'])

                dados_unidade_exercicio = retornar_info_unidade_exercicio(usuario=usuario)
                result_sme.append(dados_unidade_exercicio['nome_unidade'])
                result_sme.append(dados_unidade_exercicio['codigo_unidade'])

                result_todos_os_resultados.append(result_sme)

    return result_todos_os_resultados


@shared_task(
    retry_backoff=2,
    retry_kwargs={'max_retries': 8},
    time_limet=333333,
    soft_time_limit=333333
)
def verificar_usuarios_e_suas_unidades_de_exercicio_atuais_async(user, apenas_nao_permitidos=None):
    logger.info(
        f"Iniciando o processo de verificar usuários e suas unidades. Relatório sera enviado para o usuario: {user}")

    if apenas_nao_permitidos and apenas_nao_permitidos == 'sim':
        objeto_arquivo_download = criar_registro_central_download(user=user,
                                                                  apenas_nao_permitidos=apenas_nao_permitidos)
        logger.info(f"Parâmetro apenas_nao_permitidos passado, chamando método montar_dados_apenas_nao_permitidos()")
        result = montar_dados_apenas_nao_permitidos()
    else:
        logger.info(f"Parâmetro apenas_nao_permitidos NÃO passado, chamando método montar_dados_todos_os_acessos()")
        objeto_arquivo_download = criar_registro_central_download(user=user)
        result = montar_dados_todos_os_acessos()

    logger.info(f"Resultado da Query | {result}")

    gerar_arquivo_csv(result, objeto_arquivo_download)
