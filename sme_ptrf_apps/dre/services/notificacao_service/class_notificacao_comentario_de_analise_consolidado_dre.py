from sme_ptrf_apps.core.models import Notificacao
from sme_ptrf_apps.dre.models import ComentarioAnaliseConsolidadoDRE, Comissao, MembroComissao
from django.contrib.auth import get_user_model
from .class_notificacao_service import NotificacaoService
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class NotificacaoComentarioDeAnaliseConsolidadoDre(NotificacaoService):
    def __init__(self, dre, periodo, comentarios, enviar_email):
        super().__init__(dre, periodo, comentarios, enviar_email)

    def notificar(self):

        comentarios_list = [ComentarioAnaliseConsolidadoDRE.by_uuid(uuid) for uuid in self.comentarios]

        tipo = Notificacao.TIPO_NOTIFICACAO_AVISO
        categoria = Notificacao.CATEGORIA_NOTIFICACAO_COMENTARIO_CONSOLIDADO_DRE
        remetente = Notificacao.REMETENTE_NOTIFICACAO_SME
        titulo = f"Comentário feito em seu relatório consolidado de {self.periodo.referencia}."

        recurso = self.periodo.recurso
        comissao_exame_contas = Comissao.get_comissao_responsavel_analise_pc_por_recurso(recurso)

        if comissao_exame_contas:

            # Criando uma lista de RF's para selecionar o objeto User com cada RF
            lista_de_rf = [membro.rf for membro in MembroComissao.objects.filter(comissoes=comissao_exame_contas,
                                                                                 dre=self.dre)]

            # Define destinatários
            usuarios = User.objects.filter(username__in=lista_de_rf)

            if usuarios:
                for usuario in usuarios:
                    for comentario in comentarios_list:
                        Notificacao.notificar(
                            tipo=tipo,
                            categoria=categoria,
                            remetente=remetente,
                            titulo=titulo,
                            descricao=comentario.comentario,
                            usuario=usuario,
                            renotificar=True,
                            enviar_email=self.enviar_email,
                            unidade=self.dre,
                        )

                        comentario.set_comentario_notificado()

                    logger.info("Notificações criadas com sucesso.")
                return True
            else:
                logger.info("Não existem usuários a serem notificados.")
                return False
        else:
            logger.info("Não existe comissão de exame de contas criada.")
            return False
