# Generated by Django 2.2.28 on 2023-05-05 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0329_auto_20230503_1452'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membroassociacao',
            name='cargo_educacao',
            field=models.CharField(blank=True, default='', max_length=125, null=True, verbose_name='Cargo Educação'),
        ),
    ]