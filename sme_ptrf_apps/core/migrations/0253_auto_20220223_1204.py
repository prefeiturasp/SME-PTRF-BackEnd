# Generated by Django 2.2.10 on 2022-02-23 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0252_merge_20220214_0832'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prestacaoconta',
            name='status',
            field=models.CharField(choices=[('NAO_APRESENTADA', 'Não apresentada'), ('NAO_RECEBIDA', 'Não recebida'), ('RECEBIDA', 'Recebida'), ('EM_ANALISE', 'Em análise'), ('DEVOLVIDA', 'Devolvida para acertos'), ('DEVOLVIDA_RETORNADA', 'Apresentada após acertos'), ('DEVOLVIDA_RECEBIDA', 'Recebida após acertos'), ('APROVADA', 'Aprovada'), ('APROVADA_RESSALVA', 'Aprovada com ressalvas'), ('REPROVADA', 'Reprovada'), ('EM_PROCESSAMENTO', 'Em processamento')], default='NAO_APRESENTADA', max_length=20, verbose_name='status'),
        ),
    ]
