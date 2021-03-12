from django.db import models

"""
Esses modelos existem apenas para criação das permissions usadas
para a gestão de acesso de cada funcionalidade da aplicação.

Nenhuma tabela será criada para esses modelos no banco de dados.

Cada modelo representa uma funcionalidade da aplicação e define as permissões usadas nessa funcionalidade.
"""


class FuncSmePainelParametrizacoes(models.Model):

    class Meta:
        managed = False  # No database table creation.
        default_permissions = ()  # disable "add", "change", "delete" and "view" default permissions

        verbose_name = "[SME] Painel de Parametrizacoes"
        verbose_name_plural = "[SME] Painel de Parametrizacoes"

        permissions = (
            ('access_painel_parametrizacoes', '[SME] Pode acessar o Painel de parametrizações.'),
        )


class FuncSmeAcompanhamentoDePc(models.Model):

    class Meta:
        managed = False  # No database table creation.
        default_permissions = ()  # disable "add", "change", "delete" and "view" default permissions

        verbose_name = "[SME] Acompanhamento de PC"
        verbose_name_plural = "[SME] Acompanhamento de PC"

        permissions = (
            ('access_acompanhamento_pc_sme', '[SME] Pode acessar o Acompanhamento de PC.'),
        )


class FuncSmeGestaoPerfis(models.Model):

    class Meta:
        managed = False  # No database table creation.
        default_permissions = ()  # disable "add", "change", "delete" and "view" default permissions

        verbose_name = "[SME] Gestão de perfis"
        verbose_name_plural = "[SME] Gestão de perfis"

        permissions = (
            ('access_gestao_perfis_sme', '[SME] Pode acessar Gestão de Perfis da SME.'),
        )


class FuncSmeArquivosCarga(models.Model):

    class Meta:
        managed = False  # No database table creation.
        default_permissions = ()  # disable "add", "change", "delete" and "view" default permissions

        verbose_name = "[SME] Arquivos de carga"
        verbose_name_plural = "[SME] Arquivos de carga"

        permissions = (
            ('access_arquivos_carga', '[SME] Pode acessar Arquivos de Carga em parametrizações.'),
        )
