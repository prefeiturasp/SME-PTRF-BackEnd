import logging
from sme_ptrf_apps.users.services import GestaoUsuarioService
from django.contrib.auth import get_user_model
from sme_ptrf_apps.users.models import UnidadeEmSuporte

User = get_user_model()
logger = logging.getLogger(__name__)


class VerificaUnidadesUsuariosService:

    def __init__(self):
        self.usuarios = User.objects.all()

    @staticmethod
    def unidade_em_suporte(unidade, usuario):
        return UnidadeEmSuporte.objects.filter(unidade=unidade, user=usuario).exists()

    def valida_unidades(self, usuario):
        gestao_usuario = GestaoUsuarioService(usuario=usuario)

        unidades_vinculadas = usuario.unidades.all()
        unidades_que_tem_direito = gestao_usuario.unidades_do_usuario()

        for unidade_vinculada in unidades_vinculadas:
            if self.unidade_em_suporte(unidade=unidade_vinculada, usuario=usuario):
                logger.info(f"A {unidade_vinculada} está em suporte para o usuário: {usuario}, portanto será ignorada")
                continue

            unidade_com_direito = [u for u in unidades_que_tem_direito if
                                   str(unidade_vinculada.uuid) == u["uuid_unidade"]]

            if not unidade_com_direito:
                gestao_usuario.desabilitar_acesso(unidade=unidade_vinculada)
                gestao_usuario.remover_grupos_acesso_apos_remocao_acesso_unidade(unidade=unidade_vinculada, visao_base="SME")

        if gestao_usuario.usuario_possui_visao(visao="SME"):
            sme = [u for u in unidades_que_tem_direito if "SME" == u["uuid_unidade"]]

            if not sme:
                gestao_usuario.desabilitar_acesso(unidade="SME")
                gestao_usuario.remover_grupos_acesso_apos_remocao_acesso_unidade(unidade="SME", visao_base="SME")

    def iniciar_processo(self):
        for usuario in self.usuarios:
            logger.info(f"Iniciando o processo para o usuario: {usuario}")
            self.valida_unidades(usuario=usuario)
