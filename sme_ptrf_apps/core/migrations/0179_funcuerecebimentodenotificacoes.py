# Generated by Django 2.2.10 on 2021-06-15 11:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0178_auto_20210614_1825'),
    ]

    operations = [
        migrations.CreateModel(
            name='FuncUeRecebimentoDeNotificacoes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': '[UE] Recebimento de notificações',
                'verbose_name_plural': '[UE] Recebimento de notificações',
                'permissions': (('recebe_notificacao_inicio_periodo_prestacao_de_contas', '[UE] Pode receber Notificação Início Período Prestação De Contas.'),),
                'managed': False,
                'default_permissions': (),
            },
        ),
    ]
