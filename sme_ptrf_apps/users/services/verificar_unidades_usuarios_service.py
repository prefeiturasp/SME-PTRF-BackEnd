import logging
from sme_ptrf_apps.users.services import GestaoUsuarioService
from django.contrib.auth import get_user_model
from sme_ptrf_apps.users.models import UnidadeEmSuporte

User = get_user_model()
logger = logging.getLogger(__name__)


class VerificaUnidadesUsuariosService:

    def __init__(self):
        self.usuarios = User.objects.all()

    def iniciar_processo(self):
        for usuario in self.usuarios:
            logger.info(f"Iniciando o processo para o usuario: {usuario}")
            gestao_usuario = GestaoUsuarioService(usuario=usuario)
            gestao_usuario.valida_unidades_do_usuario()

