# Generated by Django 4.2.11 on 2025-03-07 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('receitas', '0050_alter_tiporeceita_unidades'),
    ]

    operations = [
        migrations.AddField(
            model_name='tiporeceita',
            name='detalhes',
            field=models.ManyToManyField(blank=True, to='receitas.detalhetiporeceita'),
        ),
    ]
