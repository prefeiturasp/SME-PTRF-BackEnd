# Generated by Django 2.2.10 on 2023-01-10 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dre', '0071_merge_20221221_1328'),
    ]

    operations = [
        migrations.AddField(
            model_name='consolidadodre',
            name='gerou_uma_retificacao',
            field=models.BooleanField(default=False, verbose_name='Já gerou uma retificação?'),
        ),
    ]
