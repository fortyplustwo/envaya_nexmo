from django.conf.urls import patterns, include, url
from .backend import EnvayaSMSIncomingBackend 

urlpatterns = patterns('',
    (r'^$',  EnvayaSMSIncomingBackend.as_view(backend_name='envaya_nexmo')),
)
 
