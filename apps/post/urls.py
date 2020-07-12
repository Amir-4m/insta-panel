from django.urls import path

from apps.post.views import publish, get_location

urlpatterns = [
    path('<int:id>/publish/', publish, name='publish'),
    path('get-location/', get_location, name='location')
]
