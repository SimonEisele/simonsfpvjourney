from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic.base import RedirectView
import os

FRONTEND_URL = os.getenv('FRONTEND_URL', 'https://simonsfpvjourney-frontend.onrender.com').rstrip('/')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('videos.urls')),
    # Route direct browser hits on backend domain to the SPA frontend.
    re_path(
        r'^(?!(api(?:/|$)|admin(?:/|$)))(?P<path>.*)$',
        RedirectView.as_view(
            url=f'{FRONTEND_URL}/%(path)s',
            permanent=False,
            query_string=True,
        ),
    ),
]
