from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^upload/$', views.FileUploadView.as_view(), name='file-upload'),
    url(r'^upload_2/$', views.FileUploadView_2.as_view(), name='file-upload-2'),
    url(r'^history/$', views.HistoryView.as_view(), name='hh-list'),
    url(r'^history/(?P<pk>\d+)/$', views.HistoryDetailView.as_view(), name='history-detail'),
    url(r'^hh/(?P<pk>\d+)/$', views.get_hh, name='get-hh'),
    url(r'^obj/(?P<pk>\d+)/$', views.get_hh_obj, name='get-hh-obj'),
    url(r'^new/(?P<pk>\d+)/$', views.get_new_hh, name='get-new-hh'),
    url(r'^sign_s3/$', views.sign_s3, name='sign-s3'),
]
