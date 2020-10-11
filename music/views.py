from django.db.models import Q
from django.http import HttpResponse

import math

from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from music.models import User, Music, MusicLocation
from music.serializers import MusicLocadtionSerializer

from rest_framework.decorators import action, api_view





def ping(request):
    return HttpResponse('pong')


def _getBoundsFromLatLng(lat, lng):
    # 5km 구간
    lat_change = 5 / 111.2
    lng_change = abs(math.cos(lat * (math.pi / 180)))
    bounds = {
        "lat_min": lat - lat_change,
        "lng_min": lng - lng_change,
        "lat_max": lat + lat_change,
        "lng_max": lng + lng_change
    }
    return bounds
# GET /musics
@api_view(['GET'])
def get_musics(request):
    longitude = request.GET.get('longitude')
    latitude = request.GET.get('latitude')

    if request.method == 'GET':


        LC = _getBoundsFromLatLng(float(longitude), float(latitude))
        qs = MusicLocation.objects.filter(
            latitude__range=(LC['lat_min'], LC['lat_max'])
        ).filter(
            longitude__range=(LC['lng_min'], LC['lng_max'])
        ).values('music__name', 'longitude', 'latitude', 'modified')

    return HttpResponse(qs)



@api_view(['POST', 'GET'])
def post_user_memory(request, zeppeto_hash_code):

    if request.method == 'POST':

        # POST	/users/{zeppeto_hash_code}/music
        # 	request	longitude
        # 		latitude
        # 		sing_name
        user = User.objects.filter(zeppeto_hash_code=zeppeto_hash_code).first()
        data = request.data
        music = Music.objects.filter(name=data['music_name']).first()
        if not music:
            return HttpResponse('음악이 없습니다, 음악을 등록해주세요')
        music_location = MusicLocation.objects.create(user=user, music=music, longitude=data['longitude'], latitude=data['latitude'])
        music_location.save()

        return HttpResponse('success')

    if request.method == 'GET':
        user = MusicLocation.objects.select_related('user').filter(user__zeppeto_hash_code=zeppeto_hash_code).values('music__name', 'user__musiclocation__latitude','music__musiclocation__longitude','modified')
        return Response(user)
