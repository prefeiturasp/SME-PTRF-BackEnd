# Generated by Django 2.2.10 on 2023-04-18 10:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0324_parametros_desconsiderar_associacoes_nao_iniciadas'),
    ]

    operations = [
        migrations.CreateModel(
            name='FuncSmeEncerrarAssociacao',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': '[SME] Encerrar Associação',
                'verbose_name_plural': '[SME] Encerrar Associações',
                'permissions': (('change_encerrar_associacoes', '[SME] Pode encerrar associações'),),
                'managed': False,
                'default_permissions': (),
            },
        ),
    ]