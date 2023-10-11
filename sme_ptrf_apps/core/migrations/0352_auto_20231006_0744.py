# Generated by Django 3.2.21 on 2023-10-06 07:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0351_update_data_de_inicio_da_conta_de_associacao'),
    ]

    operations = [
        migrations.AddField(
            model_name='transferenciaeol',
            name='comportamento_contas',
            field=models.CharField(choices=[('TRANSFERE_SELECIONADA', 'Transferir apenas o tipo de conta selecionada e inativa-la na associação original.'), ('COPIA_TODAS', 'Copiar todas as contas da associação original para a nova associação mantendo-as ativas em ambas.')], default='TRANSFERE_SELECIONADA', help_text='O que deseja fazer com as contas da associação original?', max_length=30, verbose_name='Comportamento quanto às contas'),
        ),
        migrations.AlterField(
            model_name='transferenciaeol',
            name='tipo_conta_transferido',
            field=models.ForeignKey(help_text='Tipo de conta que será transferido para a nova unidade, caso o comportamento de transferência seja escolhido.', on_delete=django.db.models.deletion.PROTECT, to='core.tipoconta'),
        ),
    ]