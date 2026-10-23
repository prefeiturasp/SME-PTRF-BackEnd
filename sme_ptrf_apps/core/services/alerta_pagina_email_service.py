import logging
from html import unescape
from django.template.loader import render_to_string

from datetime import date
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import QuerySet
from django.utils.html import strip_tags

from sme_ptrf_apps.users.tasks.enviar_email_nova_notificacao import (
    TEMPLATE_EMAIL_NOVA_NOTIFICACAO,
    contexto_email_nova_notificacao,
)
from sme_ptrf_apps.core.models import AlertaPagina, Unidade
from sme_ptrf_apps.core.services.alerta_pagina_service import AlertaPaginaService
from sme_ptrf_apps.core.services.notificacao_services import enviar_email_nova_notificacao

logger = logging.getLogger(__name__)
User = get_user_model()

MOTIVO_FORA_DA_DATA = 'A data de disparo não é hoje.'
MOTIVO_JA_DISPARADO = 'O e-mail desta ocorrência já foi disparado.'
MOTIVO_INATIVO = 'O alerta está inativo.'
MOTIVO_SEM_ENVIO_EMAIL = 'O envio de e-mail não está habilitado.'


class AlertaPaginaEmailService:

    @staticmethod
    def assunto_do_email(alerta: AlertaPagina) -> str:
        """Assunto do e-mail do alerta; usa a categoria quando o assunto não foi informado."""
        return alerta.assunto_email or alerta.get_categoria_display()

    @staticmethod
    def descricao_do_email(alerta: AlertaPagina) -> str:
        """Texto do alerta sem tags HTML, como é enviado no corpo do e-mail."""
        return strip_tags(unescape(alerta.texto))

    @classmethod
    def corpo_html_do_email(cls, alerta: AlertaPagina, nome: str = 'Nome do Usuário', login: str = '0000000') -> str:
        """Renderiza o HTML do e-mail do alerta para um usuário fictício."""
        contexto = contexto_email_nova_notificacao(
            username=login, nome=nome, descricao=cls.descricao_do_email(alerta))
        return render_to_string(f'email/{TEMPLATE_EMAIL_NOVA_NOTIFICACAO}', contexto)

    @staticmethod
    def avaliar_disparo(alerta: AlertaPagina, hoje: date) -> tuple[date | None, str | None]:
        """Avalia se o alerta deve disparar e-mails na data informada.

        Returns:
            Tupla ``(ocorrencia, motivo_nao_disparo)``; o motivo é ``None`` quando o alerta deve disparar.
        """
        ocorrencia = AlertaPaginaService.ocorrencia_mais_recente(alerta.data_disparo, hoje)
        if not alerta.ativo:
            return ocorrencia, MOTIVO_INATIVO
        if not alerta.enviar_email:
            return ocorrencia, MOTIVO_SEM_ENVIO_EMAIL
        if ocorrencia != hoje:
            return ocorrencia, MOTIVO_FORA_DA_DATA
        if alerta.ultimo_envio_email_em == ocorrencia:
            return ocorrencia, MOTIVO_JA_DISPARADO
        return ocorrencia, None

    @classmethod
    def simular_disparo_do_alerta(cls, alerta: AlertaPagina, hoje: date, tamanho_amostra: int = 5) -> dict:
        """Prévia do disparo de e-mail de um alerta na data informada, sem enviar nem gravar dados."""

        ocorrencia, motivo = cls.avaliar_disparo(alerta, hoje)
        destinatarios = cls.usuarios_destinatarios(alerta)
        logins = destinatarios.order_by('username').values_list('username', flat=True)[:tamanho_amostra]
        return {
            'alerta': alerta,
            'ocorrencia': ocorrencia,
            'dispara': motivo is None,
            'motivo_nao_disparo': motivo,
            'total_destinatarios': destinatarios.count(),
            'grupos': [grupo.name for grupo in alerta.grupos_email.all()],
            'amostra_logins': list(logins),
            'assunto': cls.assunto_do_email(alerta),
            'corpo_html': cls.corpo_html_do_email(alerta),
        }

    @staticmethod
    def usuarios_destinatarios(alerta: AlertaPagina) -> QuerySet:
        """Usuários ativos dos grupos do alerta com ao menos uma unidade UE que possui o recurso"""
        unidades_ue_do_recurso = (
            Unidade.objects
            .exclude(tipo_unidade__in=Unidade.TIPOS_UNIDADES_NAO_PERTENCENTES_A_GRUPO_UE)
            .filter(associacoes__periodos_iniciais__recurso=alerta.recurso)
        )
        return User.objects.filter(
            is_active=True,
            groups__in=alerta.grupos_email.all(),
            unidades__in=unidades_ue_do_recurso,
        ).distinct()

    @classmethod
    def registrar_disparos_do_dia(cls, hoje: date | None = None) -> list[tuple[int, int]]:
        hoje = hoje or AlertaPaginaService.data_de_hoje()
        disparos = []

        with transaction.atomic():
            alertas = (
                AlertaPagina.objects
                .select_for_update()
                .ativos()
                .com_envio_de_email()
                .select_related('recurso')
            )
            for alerta in alertas:
                ocorrencia, motivo_nao_disparo = cls.avaliar_disparo(alerta, hoje)

                if motivo_nao_disparo:
                    continue

                alerta.ultimo_envio_email_em = ocorrencia
                alerta.save(update_fields=['ultimo_envio_email_em'])

                disparos.extend((alerta.pk, usuario_id) for usuario_id in
                                cls.usuarios_destinatarios(alerta).values_list('id', flat=True))
            logger.info(f'{len(disparos)} alertas de email disparados para fila de envio.')
        return disparos

    @classmethod
    def enviar_para_usuario(cls, alerta_id: int, usuario_id) -> bool:
        """Enviar o e-mail do alerta para um usuário. Retorna ``False`` se alerta ou usuário não existirem."""
        try:
            alerta: AlertaPagina = AlertaPagina.objects.get(id=alerta_id)
            usuario = User.objects.get(id=usuario_id)
            # TODO: Checar se usuário/alerta já foram enviados na tabela de logs de envios
        except (AlertaPagina.DoesNotExist, User.DoesNotExist):
            logger.warning('Alerta %s ou usuário %s não encontrado para envio de e-mail.', alerta_id, usuario_id)
            return False

        enviado = enviar_email_nova_notificacao(
            usuario=usuario,
            titulo=cls.assunto_do_email(alerta),
            descricao=cls.descricao_do_email(alerta),
        )

        if enviado:
            # TODO: Salvar em uma nova tabela de alertas enviados
            # a ideia é contornar uma possível queda do serviço Celery e garantir a entrega
            ...

        return bool(enviado)
