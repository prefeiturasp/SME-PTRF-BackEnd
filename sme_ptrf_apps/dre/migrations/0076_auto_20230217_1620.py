# Generated by Django 2.2.10 on 2023-02-17 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dre', '0075_consolidadodre_pcs_do_consolidado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consolidadodre',
            name='pcs_do_consolidado',
            field=models.ManyToManyField(blank=True, related_name='consolidados_dre_da_prestacao_de_contas', to='core.PrestacaoConta'),
        ),
    ]
