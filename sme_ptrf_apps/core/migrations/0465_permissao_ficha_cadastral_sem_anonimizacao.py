from django.db import migrations


def criar_permissao_ficha_cadastral(apps, schema_editor):
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    content_type, _ = ContentType.objects.get_or_create(
        app_label="core",
        model="funcuemembrosdaassociacao",
    )
    Permission.objects.get_or_create(
        content_type=content_type,
        codename="access_ficha_cadastral_sem_anonimizacao",
        defaults={"name": "[UE] Pode acessar a Ficha Cadastral sem anonimização."},
    )


def remover_permissao_ficha_cadastral(apps, schema_editor):
    Permission = apps.get_model("auth", "Permission")
    ContentType = apps.get_model("contenttypes", "ContentType")

    content_type = ContentType.objects.filter(
        app_label="core",
        model="funcuemembrosdaassociacao",
    ).first()
    if content_type:
        Permission.objects.filter(
            content_type=content_type,
            codename="access_ficha_cadastral_sem_anonimizacao",
        ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0464_altera_nomenclatura_motivo_reprovacao_para_rejeicao"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="funcuemembrosdaassociacao",
            options={
                "default_permissions": (),
                "managed": False,
                "permissions": (
                    ("access_membros_da_associacao", "[UE] Pode acessar Membros da Associação."),
                    ("change_membros_da_associacao", "[UE] Pode editar Membros da Associação."),
                    ("access_ficha_cadastral_sem_anonimizacao", "[UE] Pode acessar a Ficha Cadastral sem anonimização."),
                ),
                "verbose_name": "[UE] Membro da Associação",
                "verbose_name_plural": "[UE] Membros da Associação",
            },
        ),
        migrations.RunPython(criar_permissao_ficha_cadastral, remover_permissao_ficha_cadastral),
    ]
