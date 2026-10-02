from django.http import HttpResponse
from django.template import loader


def inicio(request):
    template = loader.get_template('html.html')
    return HttpResponse(template.render())
