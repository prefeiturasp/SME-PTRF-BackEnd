# Generated by Django 2.2.10 on 2022-10-10 14:47

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('dre', '0053_auto_20220926_1508'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentoAdicional',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=160, verbose_name='Nome')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Criado em')),
                ('alterado_em', models.DateTimeField(auto_now=True, verbose_name='Alterado em')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('arquivo', models.FileField(blank=True, null=True, upload_to='', verbose_name='Arquivo')),
            ],
            options={
                'verbose_name': 'Documento adicional',
                'verbose_name_plural': 'Documentos Adicionais',
                'unique_together': {('nome',)},
            },
        ),
    ]