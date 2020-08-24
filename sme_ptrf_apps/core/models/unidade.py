from django.core.validators import MinLengthValidator
from django.db import models

from ..models_abstracts import TemNome, ModeloBase
from .validators import cnpj_validation


class Unidade(ModeloBase, TemNome):
    # Tipo de Unidade Choices
    TIPOS_CHOICE = (
        ('ADM', 'ADM'),
        ('DRE', 'DRE'),
        ('IFSP', 'IFSP'),
        ('CMCT', 'CMCT'),
        ('CECI', 'CECI'),
        ('CEI', 'CEI'),
        ('CEMEI', 'CEMEI'),
        ('CIEJA', 'CIEJA'),
        ('EMEBS', 'EMEBS'),
        ('EMEF', 'EMEF'),
        ('EMEFM', 'EMEFM'),
        ('EMEI', 'EMEI'),
        ('CEU', 'CEU'),
    )

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

    qtd_alunos = models.PositiveSmallIntegerField('Quantidade de alunos', default=0)

    diretor_nome = models.CharField('Nome do diretor da unidade', max_length=160, blank=True, default='')

    dre_cnpj = models.CharField(
        "CNPJ da DRE", max_length=20, validators=[cnpj_validation]
        , blank=True, null=True, default=""
    )

    dre_diretor_regional_rf = models.CharField('RF do diretor regional ', max_length=10, blank=True, null=True, default="")

    dre_diretor_regional_nome = models.CharField('Nome do diretor regional', max_length=160, blank=True, default='')

    dre_designacao_portaria = models.CharField('Designação portaria', max_length=160, blank=True, default='')

    dre_designacao_ano = models.CharField('Designação ano', max_length=10, blank=True, default='')

    def __str__(self):
        return self.nome

    @property
    def nome_com_tipo(self):
        return f'{self.tipo_unidade} {self.nome}'

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

    class Meta:
        verbose_name = 'Unidade'
        verbose_name_plural = 'Unidades'
