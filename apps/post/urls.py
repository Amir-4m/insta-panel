from django.urls import path

from apps.post.views import publish

urlpatterns = [
    path('<int:id>/publish/', publish, name='publish')
]

