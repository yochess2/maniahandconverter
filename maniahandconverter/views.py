from django.shortcuts import render
from django.views import View, generic
from django.http import JsonResponse, HttpResponse
from django.core.files import File

from .forms import HHForm
from .converters import create_hh_object, create_hh_details, parse_hh_json
from .controllers import save_hh, create_json_file
from .models import HH, HHJson

import time, json

def index(request):
    return render(
        request,
        'index.html',
        context={},
    )

def post1(self, request, csrf, data):
    hhForm = HHForm(self.request.POST, self.request.FILES)
    if hhForm.is_valid() == True:
        a = time.time()
        hh = hhForm.save()
        b = time.time()
        print('post1: ', b - a)
        data['is_valid'] = True
        data['hh_id'] = hh.id
        data['csrf'] = csrf

def post2(self, request, csrf, hh_id, data):
    hh = HH.objects.get(id=hh_id)
    a = time.time()
    hh_obj = create_hh_object(hh)
    b = time.time()
    print('post2a: ', b - a)
    hh_json = create_json_file(hh, hh_obj)
    c = time.time()
    print('post2b: ', c - b)
    data['is_valid'] = True
    data['csrf'] = csrf
    data['hh_json_id'] = hh_json.id

def post3(self, request, csrf, hh_json_id, data):
    hh_json = HHJson.objects.get(id=hh_json_id)
    a = time.time()
    hh_obj = parse_hh_json(hh_json.file)
    save_hh(hh_json.hh, hh_obj)
    b = time.time()
    print('post3: ', b - a)
    data['is_valid'] = True
    data['csrf'] = csrf
    data['players'] = hh_obj['players']

def post4(self, request, csrf, hero, data):
    data['is_valid'] = True
    data['hero'] = hero

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
            post1(self, request, csrf, data)
        elif hh_id is not None:
            post2(self, request, csrf, hh_id, data)
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

def get_hh(request, **kwargs):
    hh = HH.objects.get(id=kwargs['pk'])
    return HttpResponse(hh.file.read(), content_type='text/plain')

def get_hh_obj(request, **kwargs):
    file = HHJson.objects.get(hh=kwargs['pk']).file
    hh_obj = parse_hh_json(file)
    text = create_hh_details(hh_obj)
    return HttpResponse(text, content_type='text/plain')
