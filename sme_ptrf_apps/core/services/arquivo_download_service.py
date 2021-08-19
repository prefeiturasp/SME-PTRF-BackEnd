from sme_ptrf_apps.core.models.arquivos_download import ArquivoDownload
from django.contrib.auth import get_user_model


def gerar_arquivo_download(username, identificador):
    usuario = get_user_model().objects.get(username=username)
    obj_arquivo_download = ArquivoDownload.objects.create(
                    identificador=identificador,
                    arquivo=None,
                    status=ArquivoDownload.STATUS_EM_PROCESSAMENTO,
                    msg_erro="",
                    lido=False,
                    central_de_downloads=True,
                    usuario=usuario
                )

    obj_arquivo_download.save()

    return obj_arquivo_download


def atualiza_arquivo_download(obj_arquivo_download, filename):
    obj_arquivo_download.arquivo = filename
    obj_arquivo_download.status = ArquivoDownload.STATUS_CONCLUIDO
    obj_arquivo_download.save()


def atualiza_arquivo_download_erro(obj_arquivo_download, msg_erro):
    obj_arquivo_download.status = ArquivoDownload.STATUS_ERRO
    obj_arquivo_download.msg_erro = str(msg_erro)
    obj_arquivo_download.save()
