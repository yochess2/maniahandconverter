from django.shortcuts import render
from django.views import View, generic
from django.http import JsonResponse, HttpResponse
from django.core.files import File

from .forms import HHForm
from .converters import create_hh_object, create_hh_details
from .controllers import create_hh
from .models import HH

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

        if files is None:
            return JsonResponse({'is_valid':False})

        hhForm = HHForm(self.request.POST, self.request.FILES)
        if hhForm.is_valid() == False:
            return JsonResponse({'is_valid':False})

        hh = hhForm.save(commit=False)
        hh_obj = create_hh_object(hh)
        create_hh(hh, hh_obj)
        # create_json_file(hh, hh_obj)

        return JsonResponse({
            'is_valid':True,
            'hh_obj':hh_obj,
            'csrf':csrf,
            'players':hh_obj['players']
        })

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
    hh = HH.objects.get(id=kwargs['pk'])
    hh_obj = create_hh_object(hh)
    text = create_hh_details(hh_obj)
    return HttpResponse(text, content_type='text/plain')
