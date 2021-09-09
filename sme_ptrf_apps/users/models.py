import base64
import uuid

from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.db.models import CharField
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from sme_ptrf_apps.core.models import Unidade
from sme_ptrf_apps.core.models_abstracts import ModeloIdNome

from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from django.db.models.signals import m2m_changed


class Visao(ModeloIdNome):
    history = AuditlogHistoryField()

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Visão'
        verbose_name_plural = 'Visões'


class Grupo(Group):
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
    groups = models.ManyToManyField(
        Grupo,
        verbose_name=_('grupos'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="user_set",
        related_query_name="user",
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

    def add_unidade_se_nao_existir(self, codigo_eol):
        if not self.unidades.filter(codigo_eol=codigo_eol).exists():
            unidade = Unidade.objects.get(codigo_eol=codigo_eol)
            self.unidades.add(unidade)
            self.save()

    def remove_unidade_se_existir(self, codigo_eol):
        if self.unidades.filter(codigo_eol=codigo_eol).exists():
            unidade = Unidade.objects.get(codigo_eol=codigo_eol)
            self.unidades.remove(unidade)
            self.save()

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




