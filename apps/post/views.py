from django.http import JsonResponse

from apps.insta_panel.api.api import API
from apps.post.models import InstagramAccount

api = API()


def publish():
    pass


def get_location(request, *args, **kwargs):
    page = InstagramAccount.objects.first()
    longitude, latitude = request.GET.get('longitude'), request.GET.get('latitude')
    if latitude and longitude:
        api.login(page.username, page.password, ask_for_code=True)
        location_data = api.location_search(float(latitude), float(longitude)).json().get('venues')
        res = JsonResponse(location_data, safe=False)
        return res
