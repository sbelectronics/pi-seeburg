from django.conf.urls import patterns, url

from seeburg_ui import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^insertQuarter$', views.insertQuarter, name='insertQuarter'),
    url(r'^insertDime$', views.insertDime, name='insertDime'),
    url(r'^insertNickel$', views.insertNickel, name='insertNickel'),
    url(r'^getStatus$', views.getStatus, name='getStatus'),
)
