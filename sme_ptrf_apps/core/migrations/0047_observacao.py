# Generated by Django 2.2.10 on 2020-07-02 20:49

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0046_auto_20200625_1112'),
    ]

    operations = [
        migrations.CreateModel(
            name='Observacao',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('alterado_em', models.DateTimeField(auto_now=True, verbose_name='Alterado em')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('texto', models.TextField(blank=True, max_length=600, null=True, verbose_name='Texto')),
                ('acao_associacao', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='observacoes_da_acao', to='core.AcaoAssociacao')),
                ('prestacao_conta', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='observacoes_da_prestacao', to='core.PrestacaoConta')),
            ],
            options={
                'verbose_name': 'observação',
                'verbose_name_plural': 'observações',
            },
        ),
    ]
