# Generated by Django 4.2.20 on 2025-05-20 14:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0407_funcuesituacaopatrimonial"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="categoriapdde",
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name="receitaprevistapaa",
            name="acao_associacao",
        ),
        migrations.RemoveField(
            model_name="recursopropriopaa",
            name="associacao",
        ),
        migrations.RemoveField(
            model_name="recursopropriopaa",
            name="fonte_recurso",
        ),
        migrations.DeleteModel(
            name="AcaoPdde",
        ),
        migrations.DeleteModel(
            name="CategoriaPdde",
        ),
        migrations.DeleteModel(
            name="FonteRecursoPaa",
        ),
        migrations.DeleteModel(
            name="ReceitaPrevistaPaa",
        ),
        migrations.DeleteModel(
            name="RecursoProprioPaa",
        ),
    ]
