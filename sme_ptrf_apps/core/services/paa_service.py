import logging

from django.contrib.staticfiles.storage import staticfiles_storage
from django.template.loader import get_template
from django.http import HttpResponse

from weasyprint import HTML, CSS

logger = logging.getLogger(__name__)

def gerar_arquivo_pdf_levantamento_prioridades_paa(dados):
  logger.info('Iniciando task gerar_pdf_levantamento_prioridades_paa')
  
  html_template = get_template('pdf/paa/pdf_levantamento_prioridades_paa.html')
  rendered_html = html_template.render({'dados': dados, 'base_static_url': staticfiles_storage.location})
  
  pdf_file = HTML(
      string=rendered_html,
      base_url=staticfiles_storage.location
  ).write_pdf(
      stylesheets=[CSS(staticfiles_storage.location + '/css/pdf-levantamento-prioridades-paa.css')]
  )

  response = HttpResponse(pdf_file, content_type='application/pdf')
  response['Content-Disposition'] = 'attachment; filename="paa_levantamento_prioridades.pdf"'

  return response