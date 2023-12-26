# Generated by Django 4.2.7 on 2023-12-20 08:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0364_parametros_permite_saldo_acoes_negativo"),
    ]

    operations = [
        migrations.AlterField(
            model_name="demonstrativofinanceiro",
            name="status",
            field=models.CharField(
                choices=[
                    ("EM_PROCESSAMENTO", "Em processamento"),
                    ("CONCLUIDO", "Geração concluída"),
                    ("A_PROCESSAR", "A processar"),
                ],
                default="CONCLUIDO",
                max_length=20,
                verbose_name="status",
            ),
        ),
        migrations.AlterField(
            model_name="relacaobens",
            name="status",
            field=models.CharField(
                choices=[
                    ("EM_PROCESSAMENTO", "Em processamento"),
                    ("CONCLUIDO", "Geração concluída"),
                    ("A_PROCESSAR", "A processar"),
                ],
                default="CONCLUIDO",
                max_length=20,
                verbose_name="status",
            ),
        ),
    ]