from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dre', '0081_merge_20260514_1000'),
    ]

    operations = [
        migrations.AddField(
            model_name='lauda',
            name='arquivo_lauda_pdf',
            field=models.FileField(blank=True, null=True, upload_to='', verbose_name='Arquivo Lauda (PDF)'),
        ),
        migrations.AlterField(
            model_name='lauda',
            name='arquivo_lauda_txt',
            field=models.FileField(
                blank=True,
                help_text='Texto utilizado por fluxos legados; a publicação passa a priorizar o PDF.',
                null=True,
                upload_to='',
                verbose_name='Arquivo Lauda (TXT legado)',
            ),
        ),
    ]
