# Generated by Django 3.2.21 on 2023-10-10 13:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0355_alter_associacao_cnpj'),
    ]

    operations = [
        migrations.AddField(
            model_name='transferenciaeol',
            name='periodo_inicial_associacao',
            field=models.ForeignKey(blank=True, help_text='Indique o período inicial para a nova associação. Deixe vazio, se não quiser indicar um período inicial.', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='core.periodo', verbose_name='período inicial'),
        ),
    ]
