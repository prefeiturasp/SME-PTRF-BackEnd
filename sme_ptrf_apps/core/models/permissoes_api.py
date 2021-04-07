from django.db import models

"""
Esses modelos existem apenas para criação das permissions usadas
para a gestão de acesso de cada recurso na API da aplicação.

Nenhuma tabela será criada para esses modelos no banco de dados.

Cada modelo representa um recurso da API e define as permissões para esse recurso.
"""


class ApiPermissoesPerfis(models.Model):

    class Meta:
        managed = False  # No database table creation.
        default_permissions = ()  # disable "add", "change", "delete" and "view" default permissions

        verbose_name = "[API] Permissões Leitura e Gravação"
        verbose_name_plural = "[API] Permissões Leitura e Gravação"

        permissions = (
            ('ue_leitura', '[API.UE] Pode ler da API com perfil de UE.'),
            ('ue_gravacao', '[API.UE] Pode gravar na API com perfil de UE.'),
            ('dre_leitura', '[API.DRE] Pode ler da API com perfil de DRE.'),
            ('dre_gravacao', '[API.DRE] Pode gravar na API com perfil de DRE.'),
            ('sme_leitura', '[API.SME] Pode ler da API com perfil de SME.'),
            ('sme_gravacao', '[API.SME] Pode gravar na API com perfil de SME.'),
        )
