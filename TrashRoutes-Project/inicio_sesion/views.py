from django.http import HttpResponse
from django.template import loader

<<<<<<< HEAD
# Create your views here.
# JEJE
#M
=======

def inicio(request):
    template = loader.get_template('inicio_sesion/html.html')
    return HttpResponse(template.render())
>>>>>>> a2c5ab71f268c68c28b1cb23ccc15bb22450d49c
