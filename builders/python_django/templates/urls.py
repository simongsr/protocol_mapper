from django.conf.urls import url

from . import views

urlpatterns = [
    {% for funcname, url in urls.items() %}
    url(r'^{{ url }}$', views.{{ funcname }}),
    {% endfor %}
]

