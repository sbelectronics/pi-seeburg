from django.shortcuts import render
from django.template import RequestContext, loader
import json

from seeburg_manager import glo_seeburg

# Create your views here.

from django.http import HttpResponse

def index(request):
    template = loader.get_template('seeburg_ui/index.html')
    context = RequestContext(request, {});
    return HttpResponse(template.render(context))

def insertQuarter(request):
    glo_seeburg.insert_quarter()

    return HttpResponse("okey dokey")

def insertDime(request):
    glo_seeburg.insert_dime()

    return HttpResponse("okey dokey")

def insertNickel(request):
    glo_seeburg.insert_nickel()

    return HttpResponse("okey dokey")


def getStatus(request):
    result = {}

    return HttpResponse(json.dumps(result), content_type='application/javascript')
