from django.contrib.auth import get_user_model
from django.db import models

from sme_ptrf_apps.core.models_abstracts import ModeloBase

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog


class NotificacaoCreateException(Exception):
    pass


class Notificacao(ModeloBase):
    history = AuditlogHistoryField()

    # Tipos de Notificação
    TIPO_NOTIFICACAO_ALERTA = 'ALERTA'
    TIPO_NOTIFICACAO_INFORMACAO = 'INFORMACAO'
    TIPO_NOTIFICACAO_URGENTE = 'URGENTE'
    TIPO_NOTIFICACAO_AVISO = 'AVISO'

    TIPO_NOTIFICACAO_NOMES = {
        TIPO_NOTIFICACAO_ALERTA: 'Alerta',
        TIPO_NOTIFICACAO_INFORMACAO: 'Informação',
        TIPO_NOTIFICACAO_URGENTE: 'Urgente',
        TIPO_NOTIFICACAO_AVISO: 'Aviso',
    }

    TIPO_NOTIFICACAO_CHOICES = (
        (TIPO_NOTIFICACAO_ALERTA, TIPO_NOTIFICACAO_NOMES[TIPO_NOTIFICACAO_ALERTA]),
        (TIPO_NOTIFICACAO_INFORMACAO, TIPO_NOTIFICACAO_NOMES[TIPO_NOTIFICACAO_INFORMACAO]),
        (TIPO_NOTIFICACAO_URGENTE, TIPO_NOTIFICACAO_NOMES[TIPO_NOTIFICACAO_URGENTE]),
        (TIPO_NOTIFICACAO_AVISO, TIPO_NOTIFICACAO_NOMES[TIPO_NOTIFICACAO_AVISO]),
    )

    # Categorias de Notificação
    CATEGORIA_NOTIFICACAO_COMENTARIO_PC = 'COMENTARIO_PC'
    CATEGORIA_NOTIFICACAO_ELABORACAO_PC = 'ELABORACAO_PC'
    CATEGORIA_NOTIFICACAO_ANALISE_PC = 'ANALISE_PC'
    CATEGORIA_NOTIFICACAO_DEVOLUCAO_PC = 'DEVOLUCAO_PC'

    CATEGORIA_NOTIFICACAO_NOMES = {
        CATEGORIA_NOTIFICACAO_COMENTARIO_PC: 'Comentário na prestação de contas',
        CATEGORIA_NOTIFICACAO_ELABORACAO_PC: 'Elaboração de PC',
        CATEGORIA_NOTIFICACAO_ANALISE_PC: 'Análise de PC',
        CATEGORIA_NOTIFICACAO_DEVOLUCAO_PC: 'Devolução de PC para ajustes',
    }

    CATEGORIA_NOTIFICACAO_CHOICES = (
        (CATEGORIA_NOTIFICACAO_COMENTARIO_PC, CATEGORIA_NOTIFICACAO_NOMES[CATEGORIA_NOTIFICACAO_COMENTARIO_PC]),
        (CATEGORIA_NOTIFICACAO_ELABORACAO_PC, CATEGORIA_NOTIFICACAO_NOMES[CATEGORIA_NOTIFICACAO_ELABORACAO_PC]),
        (CATEGORIA_NOTIFICACAO_ANALISE_PC, CATEGORIA_NOTIFICACAO_NOMES[CATEGORIA_NOTIFICACAO_ANALISE_PC]),
        (CATEGORIA_NOTIFICACAO_DEVOLUCAO_PC, CATEGORIA_NOTIFICACAO_NOMES[CATEGORIA_NOTIFICACAO_DEVOLUCAO_PC]),
    )

    # Remetentes de Notificação
    REMETENTE_NOTIFICACAO_SISTEMA = 'SISTEMA'
    REMETENTE_NOTIFICACAO_DRE = 'DRE'
    REMETENTE_NOTIFICACAO_SME = 'SME'

    REMETENTE_NOTIFICACAO_NOMES = {
        REMETENTE_NOTIFICACAO_SISTEMA: 'Sistema',
        REMETENTE_NOTIFICACAO_DRE: 'DRE',
        REMETENTE_NOTIFICACAO_SME: 'SME',
    }

    REMETENTE_NOTIFICACAO_CHOICES = (
        (REMETENTE_NOTIFICACAO_SISTEMA, REMETENTE_NOTIFICACAO_NOMES[REMETENTE_NOTIFICACAO_SISTEMA]),
        (REMETENTE_NOTIFICACAO_DRE, REMETENTE_NOTIFICACAO_NOMES[REMETENTE_NOTIFICACAO_DRE]),
        (REMETENTE_NOTIFICACAO_SME, REMETENTE_NOTIFICACAO_NOMES[REMETENTE_NOTIFICACAO_SME]),
    )

    tipo = models.CharField(
        'Tipo',
        max_length=15,
        choices=TIPO_NOTIFICACAO_CHOICES,
        default=TIPO_NOTIFICACAO_INFORMACAO,
    )

    categoria = models.CharField(
        'Categoria',
        max_length=15,
        choices=CATEGORIA_NOTIFICACAO_CHOICES,
        default=CATEGORIA_NOTIFICACAO_COMENTARIO_PC,
    )

    remetente = models.CharField(
        'Remetente',
        max_length=15,
        choices=REMETENTE_NOTIFICACAO_CHOICES,
        default=REMETENTE_NOTIFICACAO_SISTEMA,
    )

    titulo = models.CharField("Título", max_length=100, default='', blank=True)

    descricao = models.CharField("Descrição", max_length=300, default='', blank=True)

    hora = models.TimeField("Hora", editable=False, auto_now_add=True)

    lido = models.BooleanField("Foi Lido?", default=False)

    usuario = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, default='', blank=True, null=True)

    unidade = models.ForeignKey('Unidade', on_delete=models.CASCADE, related_name="notificacoes_da_unidade",
                                to_field="codigo_eol", blank=True, null=True)

    prestacao_conta = models.ForeignKey('PrestacaoConta', on_delete=models.CASCADE,
                                        related_name='notificacoes_da_prestacao', blank=True, null=True)

    class Meta:
        verbose_name = "Notificação"
        verbose_name_plural = "05.0) Notificações"

    def __str__(self):
        return self.titulo

    @classmethod
    def tipos_to_json(cls):
        result = []
        for choice in cls.TIPO_NOTIFICACAO_CHOICES:
            status = {
                'id': choice[0],
                'nome': choice[1]
            }
            result.append(status)
        return result

    @classmethod
    def categorias_to_json(cls):
        result = []
        for choice in cls.CATEGORIA_NOTIFICACAO_CHOICES:
            status = {
                'id': choice[0],
                'nome': choice[1]
            }
            result.append(status)
        return result

    @classmethod
    def remetentes_to_json(cls):
        result = []
        for choice in cls.REMETENTE_NOTIFICACAO_CHOICES:
            status = {
                'id': choice[0],
                'nome': choice[1]
            }
            result.append(status)
        return result

    @classmethod
    def notificar(
        cls,
        tipo,
        categoria,
        remetente,
        titulo,
        descricao,
        usuario,
        renotificar=True,
        enviar_email=False,
        unidade=None,
        prestacao_conta=None,
    ):

        from sme_ptrf_apps.core.services.notificacao_services.enviar_email_notificacao import enviar_email_nova_notificacao
        from sme_ptrf_apps.core.models import Parametros

        if enviar_email:
            # Caso a opção seja de enviar e-mail, verifica se a parametrização não desligou o envio de e-mails
            enviar_email = Parametros.get().enviar_email_notificacao

        if tipo not in cls.TIPO_NOTIFICACAO_NOMES.keys():
            raise NotificacaoCreateException(f'Tipo {tipo} não é um tipo válido.')

        if categoria not in cls.CATEGORIA_NOTIFICACAO_NOMES.keys():
            raise NotificacaoCreateException(f'Categoria {categoria} não é uma categoria válida.')

        if remetente not in cls.REMETENTE_NOTIFICACAO_NOMES.keys():
            raise NotificacaoCreateException(f'Remetente {remetente} não é um remetente válido.')

        if not titulo:
            raise NotificacaoCreateException(f'O título não pode ser vazio.')

        if not usuario:
            raise NotificacaoCreateException(f'É necessário definir o usuário destinatário.')

        if not renotificar:
            notificacao_existente = cls.objects.filter(
                tipo=tipo,
                categoria=categoria,
                remetente=remetente,
                titulo=titulo,
                usuario=usuario,
            )

        if renotificar or not notificacao_existente:
            cls.objects.create(
                tipo=tipo,
                categoria=categoria,
                remetente=remetente,
                titulo=titulo,
                descricao=descricao,
                usuario=usuario,
                unidade=unidade,
                prestacao_conta=prestacao_conta,
            )

        if (renotificar or not notificacao_existente) and enviar_email:
            enviar_email_nova_notificacao(usuario=usuario, titulo=titulo, descricao=descricao)


auditlog.register(Notificacao)
