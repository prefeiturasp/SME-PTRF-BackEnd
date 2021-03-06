import base64
import uuid

from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.db.models import CharField
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from sme_ptrf_apps.core.choices import RepresentacaoCargo
from sme_ptrf_apps.core.models import Unidade
from sme_ptrf_apps.core.models_abstracts import ModeloIdNome

class Visao(ModeloIdNome):

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Visão'
        verbose_name_plural = 'Visões'


class Grupo(Group):
    descricao = models.TextField(blank=True, default='')
    visoes = models.ManyToManyField(Visao, blank=True)

    @classmethod
    def grupo_por_nome(cls, nome):
        q = cls.objects.filter(nome=nome)
        return q.first() if q.exists() else None


class User(AbstractUser):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, null=True)
    name = CharField(_("Nome do usuário"), blank=True, max_length=255)
    hash_redefinicao = models.TextField(blank=True, default='',
                                        help_text='Campo utilizado para registrar hash na redefinição de senhas.')

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

    def add_unidade_se_nao_existir(self, unidade):
        if not self.unidades.filter(nome=unidade).first():
            unidade_obj = Unidade.objects.filter(codigo_eol=unidade).first()
            if unidade_obj:
                self.unidades.add(unidade_obj)
                self.save()

    @classmethod
    def criar_usuario(cls, dados):
        """ Recebe dados de usuário incluindo as listas de unidades, visões e grupos vinculados a ele e cria o usuário
        vinculando a eles as unidades, visões e grupos de acesso.
        """
        visao = dados.pop('visao')
        visao_obj = Visao.objects.filter(nome=visao).first()

        unidade = dados.pop('unidade')
        unidade_obj = Unidade.objects.filter(codigo_eol=unidade).first()

        groups = dados.pop('groups')

        user = cls.objects.create(**dados)

        user.visoes.add(visao_obj)
        user.groups.add(*groups)

        if visao != "SME" and unidade_obj:
            user.unidades.add(unidade_obj)

        user.save()

        return user

    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
