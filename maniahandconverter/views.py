from django.shortcuts import render
from django.views import View, generic
from django.http import JsonResponse, HttpResponse
from django.core.files import File

from .converters import create_hh_object, create_hh_details, parse_hh_json
from .controllers import save_hh_models, handle_hh_file, handle_hh_obj, handle_hh_models, handle_new_hh_history, handle_new_hh_detail
from .models import HH, HHJson, HHNew, HHJson_Player

import time, json, boto3, os

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
            handle_hh_file(self, request, csrf, data)
        elif hh_id is not None:
            handle_hh_obj(self, request, csrf, hh_id, data)
        elif hh_json_id is not None and hero is None:
            handle_hh_models(self, request, csrf, hh_json_id, data)
        elif hero is not None:
            # refactor this in the future...
            handle_new_hh_history(self, request, csrf, hh_json_id, hero, data)

        return JsonResponse(data)

class HistoryView(generic.ListView):
    model = HHJson
    paginate_by = 20
    template_name = 'history.html'

class HistoryDetailView(generic.DetailView):
    model = HHJson
    template_name = 'history_detail.html'

    def post(self, reqeust, **kwargs):
        hero = self.request.POST.get('hero')
        data = { 'is_valid': False}
        hero_id = self.request.POST.get('hero_id')
        hh_id = kwargs['pk']

        handle_new_hh_detail(hero_id, hh_id, data)
        return JsonResponse(data)

def get_hh(request, **kwargs):
    hh = HH.objects.get(id=kwargs['pk'])
    return HttpResponse(hh.file.read(), content_type='text/plain')

def get_hh_obj(request, **kwargs):
    hh = HH.objects.get(id=kwargs['pk'])
    hhjson = hh.hhjson_set.all()[0]
    hh_obj = parse_hh_json(hhjson.file)
    text = create_hh_details(hh_obj)
    return HttpResponse(text, content_type='text/plain')

def get_new_hh(request, **kwargs):
    new_hh = HHNew.objects.get(id=kwargs['pk'])
    return HttpResponse(new_hh.file.read(), content_type='text/plain')

def sign_s3(request, **kwargs):

    S3_BUCKET = os.environ.get('S3_BUCKET')
    file_name = request.GET.get('file_name')
    file_type = request.GET.get('file_type')

    s3 = boto3.client('s3')
    presigned_post = s3.generate_presigned_post(
        Bucket = S3_BUCKET,
        Key = file_name,
        Fields = {"acl": "public-read", "Content-Type": file_type},
        Conditions = [
          {"acl": "public-read"},
          {"Content-Type": file_type}
        ],
        ExpiresIn = 3600
    )
    data = json.dumps({
        'data': presigned_post,
        'url': 'https://%s.s3.amazonaws.com/%s' % (S3_BUCKET, file_name)
    })
    return HttpResponse(data, content_type="application/json")

class FileUploadView_2(View):
    def get(self, request):
        return render(self.request, 'upload_2.html')

    def post(self, request):
        data = {};

        return JsonResponse(data)
