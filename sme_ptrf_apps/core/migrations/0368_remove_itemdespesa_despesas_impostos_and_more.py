# Generated by Django 4.2.7 on 2023-12-27 07:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0367_alter_notificacao_categoria"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="itemdespesa",
            name="despesas_impostos",
        ),
        migrations.AddField(
            model_name="itemdespesa",
            name="info_imposto_retido",
            field=models.TextField(
                blank=True,
                default=None,
                help_text="Ex: <2222;01/09/2022;10.00>",
                null=True,
                verbose_name="Informações que o imposto gerado utiliza no template (imposto retido)",
            ),
        ),
        migrations.AddField(
            model_name="itemdespesa",
            name="info_retencao_imposto",
            field=models.TextField(
                blank=True,
                default=None,
                help_text="Ex: <10.00;01/01/2023> Obs: Utilize quebra de linha quando houver mais de um registro",
                null=True,
                verbose_name="Informações que a despesa geradora utiliza no template (retenção de imposto)",
            ),
        ),
        migrations.AlterField(
            model_name="itemdespesa",
            name="categoria_despesa",
            field=models.CharField(
                choices=[
                    ("DEMONSTRADA", "Demonstrada"),
                    ("NAO_DEMONSTRADA", "Não Demonstrada"),
                    (
                        "NAO_DEMONSTRADA_PERIODO_ANTERIOR",
                        "Não demonstrada periodo anterior",
                    ),
                    ("NAO_DEFINIDO", "Categoria não definida"),
                ],
                default="NAO_DEFINIDO",
                max_length=50,
                verbose_name="Categoria despesa",
            ),
        ),
    ]
