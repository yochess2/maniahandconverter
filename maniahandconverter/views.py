from django.shortcuts import render
from django.views import View, generic
from django.http import JsonResponse, HttpResponse
from django.core.files import File

from .converters import create_hh_object, create_hh_details, parse_hh_json
from .controllers import save_hh_models, save_hh_file, save_hh_models, post4
from .models import HH

import time, json

def index(request):
    return render(
        request,
        'index.html',
        context={},
    )

class FileUploadView(View):

    def get(self, request):
        return render(self.request, 'upload.html')

    def post(self, request):
        csrf = request.POST.get('csrfmiddlewaretoken')
        files = self.request.FILES.get('file')
        hh_id = self.request.POST.get('hh_id')
        hh_json_id = self.request.POST.get('hh_json_id')
        hero = self.request.POST.get('hero')
        data = { 'is_valid': False }

        if files is not None:
            save_hh_file(self, request, csrf, data)
        elif hh_id is not None:
            save_hh_models(self, request, csrf, hh_id, data)
        elif hh_json_id is not None:
            post3(self, request, csrf, hh_json_id, data)
        elif hero is not None:
            post4(self, request, csrf, hero, data)

        return JsonResponse(data)

class HistoryView(generic.ListView):
    model = HH
    paginate_by = 20
    template_name = 'history.html'

class HistoryDetailView(generic.DetailView):
    model = HH
    template_name = 'history_detail.html'

    def get_context_data(self, **kwargs):
        context = super(HistoryDetailView, self).get_context_data(**kwargs)
        return context

    def post(self, reqeust, **kwargs):
        hero = self.request.POST.get('hero')
        hh = HH.objects.get(id=kwargs['pk'])
        hhjson = hh.hhjson_set.all()[0]
        hh_obj = parse_hh_json(hhjson.file)

        # create_hh(hh_obj, hero)



        return JsonResponse({'is_valid': True, 'hero': hero})

def get_hh(request, **kwargs):
    hh = HH.objects.get(id=kwargs['pk'])
    return HttpResponse(hh.file.read(), content_type='text/plain')

def get_hh_obj(request, **kwargs):
    hh = HH.objects.get(id=kwargs['pk'])
    hhjson = hh.hhjson_set.all()[0]
    hh_obj = parse_hh_json(hhjson.file)
    text = create_hh_details(hh_obj)
    return HttpResponse(text, content_type='text/plain')
