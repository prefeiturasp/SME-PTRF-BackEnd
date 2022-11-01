import base64
import uuid
import logging

from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.db.models import CharField
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from sme_ptrf_apps.core.models import Unidade
from sme_ptrf_apps.core.models_abstracts import ModeloIdNome, ModeloBase

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from django.db.models.signals import m2m_changed

logger = logging.getLogger(__name__)


class Visao(ModeloIdNome):
    history = AuditlogHistoryField()

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Visão'
        verbose_name_plural = 'Visões'


class Grupo(Group):
    """
    Uma melhor abordagem teria sido, em vez de extender Group, simplesmente criar uma relação one-to-one com Group e
    acessar a partir dele os campos extras quando necessário. Assim não teríamos que manter no Admin duas entidades
    distintas Group e Grupo. Mas, optei por manter essa solução para não ter que lidar com perda de dados na migração
    em produção.
    """
    history = AuditlogHistoryField()
    descricao = models.TextField(blank=True, default='')
    visoes_log = models.TextField(blank=True, help_text='Visões do grupo (audtilog)')
    visoes = models.ManyToManyField(Visao, blank=True)

    @classmethod
    def grupo_por_nome(cls, nome):
        q = cls.objects.filter(nome=nome)
        return q.first() if q.exists() else None


class User(AbstractUser):
    history = AuditlogHistoryField()
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, null=True)
    name = CharField(_("Nome do usuário"), blank=True, max_length=255)
    hash_redefinicao = models.TextField(blank=True, default='',
                                        help_text='Campo utilizado para registrar hash na redefinição de senhas.')
    visoes_log = models.TextField(blank=True, help_text='Visões do usuário (audtilog)')
    unidades_log = models.TextField(blank=True, help_text='Unidades do usuário (audtilog)')
    groups_log = models.TextField(blank=True, help_text='Grupos do usuário (audtilog)')

    unidades = models.ManyToManyField(Unidade, blank=True)
    visoes = models.ManyToManyField(Visao, blank=True)

    # Esse campo é apenas para fazer backup do antigo campo groups. Depois será removido.
    grupos = models.ManyToManyField(
        Grupo,
        verbose_name=_('grupos'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="usuarios",
        related_query_name="usuario",
    )

    e_servidor = models.BooleanField("servidor?", default=False)

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

    @property
    def create_hash(self):
        hash_encode = base64.b64encode(str(self.uuid).encode('utf-8') + str(self.username).encode('utf-8'))
        return hash_encode.decode('utf-8')

    def validar_hash(self, hash_encode):
        if hash_encode == self.create_hash:
            return True
        return False

    def add_visao_se_nao_existir(self, visao):
        if not self.visoes.filter(nome=visao).first():
            visao_obj = Visao.objects.filter(nome=visao).first()
            if visao_obj:
                self.visoes.add(visao_obj)
                self.save()
                logger.info(f'Visão {visao_obj} adicionada para o usuário {self}.')

    def remove_visao_se_existir(self, visao):
        if self.visoes.filter(nome=visao).exists():
            visao_obj = Visao.objects.get(nome=visao)
            self.visoes.remove(visao_obj)
            self.save()
            logger.info(f'Visão {visao} removida do usuário {self}.')

    def add_unidade_se_nao_existir(self, codigo_eol):
        if not self.unidades.filter(codigo_eol=codigo_eol).exists():
            unidade = Unidade.objects.get(codigo_eol=codigo_eol)
            self.unidades.add(unidade)
            self.save()
            logger.info(f'Unidade {codigo_eol} adicionada para o usuário {self}.')

    def remove_unidade_se_existir(self, codigo_eol):
        if self.unidades.filter(codigo_eol=codigo_eol).exists():
            unidade = Unidade.objects.get(codigo_eol=codigo_eol)
            self.unidades.remove(unidade)
            self.save()
            logger.info(f'Unidade {codigo_eol} removida do usuário {self}.')

    @classmethod
    def criar_usuario(cls, dados):
        """ Recebe dados de usuário incluindo as listas de unidades, visões e grupos vinculados a ele e cria o usuário
        vinculando a eles as unidades, visões e grupos de acesso.
        """
        visao = dados.pop('visao') if 'visao' in dados else None
        visao_obj = Visao.objects.filter(nome=visao).first() if visao else None

        visoes = dados.pop('visoes') if 'visoes' in dados else None

        unidade = dados.pop('unidade')
        unidade_obj = Unidade.objects.filter(codigo_eol=unidade).first() if unidade else None

        groups = dados.pop('groups')

        user = cls.objects.create(**dados)

        if visao_obj:
            user.visoes.add(visao_obj)
        elif visoes:
            user.visoes.add(*visoes)

        user.groups.add(*groups)

        if unidade_obj:
            user.unidades.add(unidade_obj)

        user.save()

        return user

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    # def __str__(self):
    #     return f"Nome: {self.name}, RF: {self.username}"

# signals para gravação de log de campos many to many modelo User
def m2m_changed_visoes(sender, **kwargs):
    instance = kwargs["instance"]
    action = kwargs["action"]

    if action == "post_add":
        lista = []
        for visao in instance.visoes.all():
            lista.append(visao.nome)

        instance.visoes_log = lista
        instance.save()

    elif action == "post_remove":
        lista = []
        for visao in instance.visoes.all():
            lista.append(visao.nome)

        instance.visoes_log = lista
        instance.save()


def m2m_changed_unidades(sender, **kwargs):
    instance = kwargs["instance"]
    action = kwargs["action"]

    if action == "post_add":
        lista = []
        for unidade in instance.unidades.all():
            lista.append(unidade.nome)

        instance.unidades_log = lista
        instance.save()

    elif action == "post_remove":
        lista = []
        for unidade in instance.unidades.all():
            lista.append(unidade.nome)

        instance.unidades_log = lista
        instance.save()


def m2m_changed_groups(sender, **kwargs):
    instance = kwargs["instance"]
    action = kwargs["action"]

    if action == "post_add":
        lista = []
        for grupo in instance.groups.all():
            lista.append(grupo.name)

        instance.groups_log = lista
        instance.save()

    elif action == "post_remove":
        lista = []
        for grupo in instance.groups.all():
            lista.append(grupo.name)

        instance.groups_log = lista
        instance.save()


m2m_changed.connect(m2m_changed_visoes, sender=User.visoes.through)
m2m_changed.connect(m2m_changed_unidades, sender=User.unidades.through)
m2m_changed.connect(m2m_changed_groups, sender=User.groups.through)

auditlog.register(User)


# signals para gravação de log de campos many to many modelo Grupo
def m2m_changed_group_visoes(sender, **kwargs):
    instance = kwargs["instance"]
    action = kwargs["action"]

    if action == "post_add":
        lista = []
        for visao in instance.visoes.all():
            lista.append(visao.nome)

        instance.visoes_log = lista
        instance.save()

    elif action == "post_remove":
        lista = []
        for visao in instance.visoes.all():
            lista.append(visao.nome)

        instance.visoes_log = lista
        instance.save()


m2m_changed.connect(m2m_changed_group_visoes, sender=Grupo.visoes.through)

auditlog.register(Grupo)
auditlog.register(Visao)


class UnidadeEmSuporte(ModeloBase):
    history = AuditlogHistoryField()

    unidade = models.ForeignKey(
        'core.Unidade',
        on_delete=models.CASCADE,
        related_name="acessos_de_suporte",
        to_field="codigo_eol",
    )

    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name="acessos_de_suporte",
    )

    def __str__(self):
        return f'Unidade {self.unidade.codigo_eol} em suporte por {self.user.username}. ID:{self.id}'

    class Meta:
        verbose_name = 'Unidade em suporte'
        verbose_name_plural = 'Unidades em suporte'
        unique_together = ('unidade', 'user',)
