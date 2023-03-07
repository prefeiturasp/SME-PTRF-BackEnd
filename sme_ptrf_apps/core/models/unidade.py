from django.core.validators import MinLengthValidator
from django.db import models

from .validators import cnpj_validation
from ..models_abstracts import TemNome, ModeloBase
from auditlog.models import AuditlogHistoryField
from auditlog.registry import auditlog
from ..choices.tipos_unidade import TIPOS_CHOICE


class DresManager(models.Manager):
    def get_queryset(self):
        return super(DresManager, self).get_queryset().filter(tipo_unidade='DRE')


class Unidade(ModeloBase, TemNome):
    history = AuditlogHistoryField()

    tipo_unidade = models.CharField(max_length=10, choices=TIPOS_CHOICE, default='ADM')
    codigo_eol = models.CharField(max_length=6, validators=[MinLengthValidator(6)], primary_key=True, unique=True)
    dre = models.ForeignKey('Unidade', on_delete=models.PROTECT, related_name='unidades_da_dre', to_field="codigo_eol",
                            blank=True, null=True, limit_choices_to={'tipo_unidade': 'DRE'})
    sigla = models.CharField(max_length=4, blank=True, default='')

    cep = models.CharField('CEP', max_length=20, blank=True, default='')
    tipo_logradouro = models.CharField('Tipo de Logradouro', max_length=50, blank=True, default='')
    logradouro = models.CharField('Logradouro', max_length=255, blank=True, default='')
    bairro = models.CharField('Bairro', max_length=255, blank=True, default='')
    numero = models.CharField('Numero', max_length=255, blank=True, default='')
    complemento = models.CharField('Complemento', max_length=255, blank=True, default='')

    telefone = models.CharField('Telefone', max_length=20, blank=True, default='')

    email = models.EmailField("E-mail", max_length=254, blank=True, default='')

    diretor_nome = models.CharField('Nome do diretor da unidade', max_length=160, blank=True, default='')

    dre_cnpj = models.CharField(
        "CNPJ da DRE", max_length=20, validators=[cnpj_validation]
        , blank=True, null=True, default=""
    )

    dre_diretor_regional_rf = models.CharField('RF do diretor regional ', max_length=10, blank=True, null=True, default="")

    dre_diretor_regional_nome = models.CharField('Nome do diretor regional', max_length=160, blank=True, default='')

    dre_designacao_portaria = models.CharField('Designação portaria', max_length=160, blank=True, default='')

    dre_designacao_ano = models.CharField('Designação ano', max_length=10, blank=True, default='')

    objects = models.Manager()  # Manager Padrão
    dres = DresManager()

    def __str__(self):
        return self.nome

    @property
    def nome_com_tipo(self):
        return f'{self.tipo_unidade} {self.nome}'

    @property
    def nome_dre(self):
        return f'{self.dre.nome}'

    @classmethod
    def tipos_unidade_to_json(cls):
        result = []
        for choice in cls.TIPOS_CHOICE:
            tipo_unidade = {
                'id': choice[0],
                'nome': choice[1]
            }
            result.append(tipo_unidade)
        return result

    @classmethod
    def dres_to_json(cls):
        return [{'uuid': str(u.uuid), 'nome': f"{u.tipo_unidade} {u.nome}"} for u in cls.dres.all()]

    @property
    def qtd_alunos(self):
        censo = self.censos.order_by('-ano').first()
        return censo.quantidade_alunos if censo else 0

    class Meta:
        verbose_name = 'Unidade'
        verbose_name_plural = '06.0) Unidades'


auditlog.register(Unidade)
