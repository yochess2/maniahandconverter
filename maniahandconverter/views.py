from django.shortcuts import render
from django.views import View, generic
from django.http import JsonResponse, HttpResponse

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import HH, HHJson, HHNew
from .controllers import (
    handle_get_hh,
    handle_get_new_hh,
    handle_get_hh_obj,
    handle_create_new_hh,
    handle_delete,
    handle_sign_s3,
    handle_create_hh_json,
    handle_create_all_models,
    handle_create_more_new_hh,
)

import os

def index(request):
    return render(request,'index.html',context={})

@login_required
def get_hh(request, **kwargs):
    return HttpResponse(handle_get_hh(kwargs['pk'], request.user), content_type='text/plain')

@login_required
def get_new_hh(request, **kwargs):
    return HttpResponse(handle_get_new_hh(kwargs['pk'],request.user), content_type='text/plain')

@login_required
def get_hh_obj(request, **kwargs):
    return HttpResponse(handle_get_hh_obj(kwargs['pk'],request.user), content_type='text/plain')

class HistoryView(LoginRequiredMixin, generic.ListView):
    model = HHJson
    paginate_by = 20
    template_name = 'history.html'

    def get_queryset(self):
        return HHJson.objects.filter(hh__active=True,hh__user=self.request.user)

class HistoryDetailView(LoginRequiredMixin, generic.DetailView):
    model = HHJson
    template_name = 'history_detail.html'

    def post(self, reqeust, **kwargs):
        hero_id = self.request.POST.get('hero_id')
        data = handle_create_new_hh(hero_id,self.request.user)
        return JsonResponse(data)

    def put(self, request, **kwargs):
        return JsonResponse(handle_delete(kwargs['pk'], self.request.user))

    def get_queryset(self):
        return HHJson.objects.filter(hh__active=True,hh__user=self.request.user)

# after User clicks upload, hh model is created, and
#   - path is local/unconverted in production, and
#   - path is media/unconverted in deployment
# returns the signature to upload to s3
def sign_s3(request, **kwargs):
    if not request.user.is_authenticated:
        return HttpResponse(status=403)

    file_name       = request.GET.get('file_name')
    file_type       = request.GET.get('file_type')
    file_size       = request.GET.get('file_size')
    file_path, ext  = os.path.splitext(file_name)
    return JsonResponse(handle_sign_s3(file_name, file_type, file_size, ext, request.user))

class FileUploadView(LoginRequiredMixin, View):
    def get(self, request):
        return render(self.request, 'upload.html')

    def post(self, request):
        post_type   = self.request.POST.get('type')

        # After file is uploaded to s3,
        #   1. hh model is updated to uploaded
        #   2. hhjson is created
        #      - file is stored on s3
        #      - file contains ... write stuff here ...
        # returns hh_json_id
        if post_type == "sync1":
            hh_id       = self.request.POST.get('hh_id')
            key         = self.request.POST.get('key')
            data        = handle_create_hh_json(hh_id, key, request.user)
        # After hh object is saved, models are created:
        #   1. player models
        #   2. game models
        #   3. hhjson_player models
        #   4. hhjson_player_game models
        elif post_type == "sync2":
            hh_json_id  = self.request.POST.get('hh_json_id')
            data        = handle_create_all_models(hh_json_id,request.user)

        # If all goes well, user ships in a hero parameter,
        #   then a converted file is created
        # returns a link to the converted file
        elif post_type == "convert":
            hh_json_id  = self.request.POST.get('hh_json_id')
            hero        = self.request.POST.get('hero')
            data        = handle_create_more_new_hh(hh_json_id, hero, request.user)

        return JsonResponse(data)

class NonMavensConverter(LoginRequiredMixin, View):
    def get(self, request):
        return render(self.request, 'nonmavens.html')

    # def post(self, request):
    #     return JsonResponse({})

def unsaved(request, **kwargs):
    return HttpResponse(200);
