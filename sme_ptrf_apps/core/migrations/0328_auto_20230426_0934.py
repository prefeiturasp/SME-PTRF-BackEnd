# Generated by Django 2.2.28 on 2023-04-26 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0327_merge_20230420_1252'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='analiselancamentoprestacaoconta',
            constraint=models.UniqueConstraint(condition=models.Q(despesa__isnull=True), fields=('analise_prestacao_conta', 'receita'), name='unique_constraint_analise_pc_e_receita'),
        ),
        migrations.AddConstraint(
            model_name='analiselancamentoprestacaoconta',
            constraint=models.UniqueConstraint(condition=models.Q(receita__isnull=True), fields=('analise_prestacao_conta', 'despesa'), name='unique_constraint_analise_pc_e_despesa'),
        ),
    ]
